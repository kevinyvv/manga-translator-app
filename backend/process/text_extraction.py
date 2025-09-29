# Standard library imports
import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
import sys
import json
import time
import argparse
import asyncio
from pathlib import Path
import pdb
import logging
from loguru import logger

import numpy as np
import torch
from safetensors.torch import load_file
from skimage.morphology import binary_dilation, square

import cv2
from PIL import Image, ImageDraw, ImageFont, ImageOps
import matplotlib.pyplot as plt

from googletrans import Translator
# monkey patch for manga_ocr
os.environ["MPS_DISABLED"] = "1"   # disable mps entirely
from manga_ocr import MangaOcr
from ultralytics import YOLO

from google import genai
from google.genai import types

from io import BytesIO

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class MangaTextExtractor:
    def __init__(self, translator_method="google",  mask_dilation_radius=3):
        """
        Initialize the manga translator
        
        Args:
            translator_method (str): Translation method ('google' or 'deepl')
            mask_dilation_radius (int): Radius for mask dilation
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        # self.logger.setLevel(logging.DEBUG)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(script_dir, "..", "models")

        # bubble detection
        try:
            self.logger.info("Loading bubble detection model")
            bubble_prefix = os.path.join(models_dir, "detect_bubble")
            # bubble_yaml = bubble_prefix + ".yaml"
            # bubble_weights = bubble_prefix + ".safetensors"
            bubble_model = bubble_prefix + ".pt"

            # init YOLO model from YAML
            self.bubble_detection_model = YOLO(bubble_model)

            # load safetensors weights
            # bubble_state = load_file(bubble_weights)
            # self.bubble_detection_model.model.load_state_dict(bubble_state)
        except Exception as e:
            self.logger.warning(f"Failed to load bubble detection model: {e}")
            self.bubble_detection_model = None

        # text segmenter
        try:
            self.logger.info("Loading text segmenter model")
            seg_prefix = os.path.join(models_dir, "comic-text-segmenter")
            # seg_yaml = seg_prefix + ".yaml"
            # seg_weights = seg_prefix + ".safetensors"
            seg_model = seg_prefix + ".pt"

            self.segmenter = YOLO(seg_model)  # load model from .pt directly

            # seg_state = load_file(seg_weights)
            # self.segmenter.model.load_state_dict(seg_state)
        except Exception as e:
            self.logger.warning(f"Failed to load text segmenter model: {e}")
            self.segmenter = None
        # Configure OCR
        
        # supress the logs from mangaocr
        logging.getLogger("transformers").setLevel(logging.ERROR)
        logger.remove() # loguru logger, not to be confused with self.logger - from logging module
        self.mocr = MangaOcr()
        with open("utils/languages.json", "r") as f:
            self.languages = json.load(f)

        
    def google_ocr(self, image: Image, source_lang: str = "ja") -> str:
        """
        Perform OCR using Google Translate API
        
        Args:
            image (PIL.Image): Image to perform OCR on
            source_lang (str): Source language code
            
        Returns:
            str: Extracted text
        """
        prompt = f"""
            Please extract the {self.languages.get(source_lang, source_lang)} text from the following image.
            Return only the extracted text without any additional comments or formatting.
            If there is no text, return an empty string.
            """
            # print(prompt)
            
            # translate using GenAI
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes.getvalue(),
                        mime_type="image/png"
                    ),
                    prompt,
                ]
            )
            extracted_text = response.text
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            extracted_text = ""
        
        return extracted_text

    def detect_bubbles(self, image: np.ndarray, conf_threshold=0.75):
        """
        Detect speech bubbles in the image
        
        Args:
            image_path (str): Path to the input image
            conf_threshold (float): Confidence threshold for YOLO detections
            
        Returns:
            list: List of detected bubble bounding boxes [x, y, w, h]
            numpy.ndarray: The original image
        """
        # Read the image
        if image is None:
            raise ValueError(f"Could not read image")
        
        # If bubble detection model is available, use it
        if self.bubble_detection_model:

            results = self.bubble_detection_model(image, conf=conf_threshold, device="cpu")[0]
            
            # Process detections
            bubbles = []
            for box in results.boxes:
                # Extract coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                # Convert to x, y, w, h format
                x = int(x1)
                y = int(y1)
                w = int(x2 - x1)
                h = int(y2 - y1)
                
                bubbles.append([x, y, w, h])

        # fallback method, but won't work well
        else:
            # Fallback to basic contour detection
            self.logger.debug("Using fallback contour detection method")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply binary threshold
            _, binary = cv2.threshold(blurred, 220, 255, cv2.THRESH_BINARY)
            
            # Invert binary image (so speech bubbles are white)
            binary_inv = cv2.bitwise_not(binary)
            
            # Dilate to close gaps in bubble boundaries
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(binary_inv, kernel, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by area and shape
            bubbles = []
            min_area = 1000  # Minimum area to be considered a speech bubble
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < min_area:
                    continue
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check aspect ratio (not too narrow)
                aspect_ratio = w / h
                if aspect_ratio < 0.2 or aspect_ratio > 5:
                    continue
                
                bubbles.append([x, y, w, h])
        
        logger.debug(f"Detected {len(bubbles)} speech bubbles")
        return bubbles, image

    def segment_text(self, image: np.ndarray) -> np.ndarray: 
        """
        Segment text areas in the image using the text segmenter model
        
        Args:
            image (numpy.ndarray): The original image
            
        Returns:
            numpy.ndarray: Binary mask of text areas
        """
        results = self.segmenter(image, device="cpu")
        mask = results[0].masks.data.cpu().numpy()  # shape: (N, H_mask, W_mask)

        binary_mask = np.zeros_like(image[:, :, 0], dtype=np.uint8)
        H, W = binary_mask.shape

        for m in mask:
            # Resize each mask to match original image shape
            resized_mask = cv2.resize(m, (W, H), interpolation=cv2.INTER_NEAREST)
            binary_mask[resized_mask > 0.5] = 255  # apply threshold

        return binary_mask
    
    def extract_text(self, image: np.ndarray, bubbles: list, source_lang: str = "ja" ) -> list:
        """
        Extract text from speech bubbles using OCR
        
        Args:
            image (numpy.ndarray): The original image
            bubbles (list): List of bubble bounding boxes [x, y, w, h]
            
        Returns:
            list: List of dictionaries with bubble info and extracted text
        """
        text_results = []
        
        # Process each bubble
        for i, (x, y, w, h) in enumerate(bubbles):
            # Extract ROI (Region of Interest)
            # Ensure coordinates are within image bounds
            img_h, img_w = image.shape[:2]
            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(img_w, x + w)
            y2 = min(img_h, y + h)
            
            if x2 <= x1 or y2 <= y1:  # Skip if ROI is invalid
                logger.debug(f"Skipping invalid bubble ROI: {(x, y, w, h)}")
                continue
                
            bubble_roi = image[y1:y2, x1:x2]
            
            # Convert ROI to grayscale
            gray_roi = cv2.cvtColor(bubble_roi, cv2.COLOR_BGR2GRAY)
            
            # Apply additional preprocessing for better OCR
            # Increase contrast
            _, binary_roi = cv2.threshold(gray_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Apply slight blur to reduce noise
            processed_roi = cv2.GaussianBlur(binary_roi, (3, 3), 0)
            
            # Perform OCR using MangaOcr
            try:
                img = Image.fromarray(processed_roi)
                if source_lang == "ja":
                    text = self.mocr(img)
                else:
                    # for non-japanese languages use a different ocr model (gemini right now)
                    text = self.google_ocr(img, source_lang)
                # Clean up the text (remove extra whitespace and newlines)
                text = ' '.join(text.strip().split())
            except Exception as e:
                self.logger.warning(f"OCR error for bubble {i+1}: {e}")
                text = ""

            # Add to results
            text_results.append({
                "bubble_id": i + 1,
                "bbox": [x, y, w, h],
                "text": text
            })
            
            self.logger.debug(f"Bubble {i+1}: '{text}'")
        
        return text_results
 