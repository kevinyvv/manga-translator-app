import argparse
import os
import json
import asyncio
import cv2
import base64
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import logging
import colorlog
from dotenv import load_dotenv
load_dotenv()

from process.text_extraction import MangaTextExtractor  
from process.translator import MangaTranslator
from process.text_render import MangaTextRenderer
from process.inpaint import Inpainter


def test_xd():
    return "yup, this is a test endpoint!"

async def process_image(
    image: np.ndarray,
    text_extractor,
    translator,
    renderer,
    inpainter,
    source_lang="ja",
    target_lang="en",
    translation_method="genai",
    inpaint_method="opencv",
    conf_threshold=0.25,
    debug=False,
    font_path="fonts/Anime.otf"
) -> dict:
    """
    Process a complete manga image using modular components:
    1. Detect speech bubbles
    2. Extract and translate text
    3. Segment all text from the image
    4. Create inpainted image with no text
    5. Add translated text to the inpainted image
    
    Args:
        image_path (str): Path to input image
        output_path (str): Path to save output image
        source_lang (str): Source language code
        target_lang (str): Target language code
        conf_threshold (float): Confidence threshold for YOLO
        debug (bool): Whether to show debug visualizations
        font_path (str): Path to custom font file
        
    Returns:
        dict: Results summary
    """
    # Read original image
    original_image = image

    # Step 1: Detect speech bubbles
    bubbles, _ = text_extractor.detect_bubbles(image, conf_threshold) # change to use image
    
    _, img_encoded = cv2.imencode('.png', original_image)
    encoded_image_str = base64.b64encode(img_encoded.tobytes()).decode('utf-8')

    # Skip processing if no bubbles found
    if not bubbles:
         return {
        "status": "skipped",
        "bubbles_count": len(bubbles),
        "text_extracted": 0,
        "image_bytes": encoded_image_str,
        "translated_data": []
        }

    # Step 2: Generate text mask using text segmentation
    text_mask = text_extractor.segment_text(original_image)

    # Step 3: Extract text from bubbles
    text_data = text_extractor.extract_text(original_image, bubbles, source_lang=source_lang)
    
    # Step 4: Translate text
    translated_data = await translator.translate(text_data, source_lang, target_lang, translation_method=translation_method, manga_title=None)
    
    # Step 5: Create inpainted image (text removed)
    inpainted_image = inpainter.inpaint(original_image, text_mask, method=inpaint_method)
    
    # Step 6: Add translated text to inpainted image
    # Convert to PIL for text rendering
    pil_image = Image.fromarray(cv2.cvtColor(inpainted_image, cv2.COLOR_BGR2RGB))
    
    # Prepare bubble information for renderer
    bubbles_with_text = []
    for item in translated_data:
        if "translated_text" in item and item["translated_text"].strip():
            bubbles_with_text.append(item)
    
    # Render text into bubbles
    result_pil = renderer.render_text_in_bubbles(pil_image, bubbles_with_text, auto_style=True)
    
    # Convert back to OpenCV format
    result_image = cv2.cvtColor(np.array(result_pil), cv2.COLOR_RGB2BGR)
    _, img_encoded = cv2.imencode('.png', result_image)
    img_bytes = img_encoded.tobytes()

    encoded_image_str = base64.b64encode(img_bytes).decode('utf-8')

    return {
        "status": "success",
        "bubbles_count": len(bubbles),
        "text_extracted": sum(1 for item in text_data if item["text"]),
        "image_bytes": encoded_image_str,
        "translated_data": translated_data
    }
