# Standard library imports
import os
import sys
import json
import time
import argparse
import asyncio
from pathlib import Path
import pdb
import logging

# Third-party imports - Data processing & mathematical operations
import numpy as np
import torch
from skimage.morphology import binary_dilation, square

# Third-party imports - Image processing
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageOps
import matplotlib.pyplot as plt

# local imports
from .utils.inpainting import (
    norm_img,
    get_cache_path_by_url,
    load_jit_model,
    download_model
)

class Inpainter:
    """
    Supports both OpenCV and LaMa inpainting for manga images.
    """
    def __init__(self, mask_dilation_radius=3, lama_device='cpu'):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.mask_dilation_radius = mask_dilation_radius

        # LaMa model setup
        self.lama_model_path = os.environ.get(
            "LAMA_MODEL_PATH",
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'anime-manga-big-lama.pt'))
        )
        self.lama_model_md5 = os.environ.get("LAMA_MODEL_MD5", "29f284f36a0a510bcacf39ecf4c4d54f")
        self.lama_device = lama_device
        self.lama_model = load_jit_model(self.lama_model_path, self.lama_device, self.lama_model_md5)

    def simple_inpaint(self, image, text_mask):
        self.logger.info("Starting simple inpainting process (OpenCV)")
        print("starting simple inpainting process")
        if len(text_mask.shape) == 3:
            text_mask = cv2.cvtColor(text_mask, cv2.COLOR_BGR2GRAY)
        text_mask = text_mask.astype(np.uint8)
        return cv2.inpaint(image, text_mask, 3, cv2.INPAINT_TELEA)

    def lama_inpaint(self, image, text_mask):
        self.logger.info("Starting LaMa inpainting process")
        print("starting LaMa inpainting process")
        # LaMa expects RGB images and mask in [0,1]
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mask = text_mask
        orig_h, orig_w = image.shape[:2]

        # Pad image and mask to be multiples of 8
        from .utils.inpainting import pad_img_to_modulo
        pad_mod = 8
        image_padded = pad_img_to_modulo(image, pad_mod)
        mask_padded = pad_img_to_modulo(mask, pad_mod)

        image_norm = norm_img(image_padded)
        mask_norm = norm_img(mask_padded)
        mask_norm = (mask_norm > 0) * 1
        image_tensor = torch.from_numpy(image_norm).unsqueeze(0).to(self.lama_device)
        mask_tensor = torch.from_numpy(mask_norm).unsqueeze(0).to(self.lama_device)
        with torch.no_grad():
            inpainted = self.lama_model(image_tensor, mask_tensor)
        result = inpainted[0].permute(1, 2, 0).detach().cpu().numpy()
        result = np.clip(result * 255, 0, 255).astype("uint8")
        # Crop result back to original size
        result_cropped = result[:orig_h, :orig_w, :]
        result_cropped = cv2.cvtColor(result_cropped, cv2.COLOR_RGB2BGR)
        return result_cropped

    def inpaint(self, image, text_mask, method='lama'):
        """
        method: 'opencv' or 'lama'
        """
        if method == 'lama':
            return self.lama_inpaint(image, text_mask)
        else:
            return self.simple_inpaint(image, text_mask)