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

# Third-party imports - OCR & Translation
import pytesseract
from googletrans import Translator
from manga_ocr import MangaOcr
from ultralytics import YOLO


class MangaTextRenderer:
    """
    Specialized text renderer for manga that places text into detected regions
    """
    
    def __init__(self, font_path=None, default_font_size=24):
        self.logger = logging.getLogger(self.__class__.__name__)
        # self.logger.setLevel(logging.DEBUG)
        
        self.default_font_size = default_font_size
        self.min_font_size = 8
        self.font_path = font_path
        
        # Load font or use default
        try:
            if font_path and os.path.exists(font_path):
                self.default_font = ImageFont.truetype(font_path, default_font_size)
            else:
                self.default_font = ImageFont.load_default()
                self.font_path = None
                self.logger.warning("Using default font as specified font was not found")
        except Exception as e:
            self.logger.error(f"Font loading error: {e}")
            self.default_font = ImageFont.load_default()
            self.font_path = None
        
        # Style configuration
        self.text_color = (0, 0, 0)  # Black text by default
        self.outline_color = None  # No outline by default
        self.shadow_color = None  # No shadow by default
        self.shadow_offset = 2
        self.outline_size = 1
    
    def _create_test_draw(self):
        """Create a draw object for text measurements"""
        test_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        return ImageDraw.Draw(test_img)
        
    def _get_text_size(self, text, font):
        """Get dimensions of text with given font"""
        draw = self._create_test_draw()
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            # Fallback for older PIL versions
            return draw.textsize(text, font=font)
            
    def _get_line_height(self, font):
        """Get line height for the font"""
        _, height = self._get_text_size("AgjpqyQ|", font)
        return height
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within a specific width"""
        words = text.split()
        if not words:
            return []
            
        lines = []
        current_line = words[0]
        
        for word in words[1:]:
            test_line = f"{current_line} {word}"
            width, _ = self._get_text_size(test_line, font)
            
            if width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
                
        lines.append(current_line)
        return lines
    
    def fit_text_in_box(self, text, box_width, box_height, max_font_size=None, min_font_size=None):
        """Find optimal font size and line wrapping to fit text in box"""
        if max_font_size is None:
            max_font_size = self.default_font_size
            
        if min_font_size is None:
            min_font_size = self.min_font_size
            
        margin_ratio = 0.1  # 10% margin
        max_width = box_width * (1 - margin_ratio * 2)
        max_height = box_height * (1 - margin_ratio * 2)
        
        current_size = max_font_size
        best_font = None
        best_lines = []
        
        while current_size >= min_font_size:
            try:
                if self.font_path:
                    font = ImageFont.truetype(self.font_path, current_size)
                else:
                    font = self.default_font
            except Exception:
                current_size -= 2
                continue
                
            lines = self.wrap_text(text, font, max_width)
            
            line_height = self._get_line_height(font)
            line_spacing = line_height * 0.2  # 20% of line height
            total_height = (len(lines) * line_height) + ((len(lines) - 1) * line_spacing)
            
            if total_height <= max_height:
                best_font = font
                best_lines = lines
                self.logger.debug(f"Found suitable font size: {current_size}")
                break
                
            current_size -= 2
            
        if best_font is None:
            if self.font_path:
                best_font = ImageFont.truetype(self.font_path, min_font_size)
            else:
                best_font = self.default_font
                
            best_lines = self.wrap_text(text, best_font, max_width)
            max_lines = int(max_height / (self._get_line_height(best_font) * 1.2))
            best_lines = best_lines[:max_lines]
            
            if len(best_lines) > 0 and len(best_lines) > max_lines:
                best_lines[-1] = best_lines[-1][:best_lines[-1].rfind(' ')] + "..."
        
        return best_font, best_lines, current_size
    
    def set_text_style(self, text_color=(0, 0, 0), outline_color=None, 
                      shadow_color=None, shadow_offset=2, outline_size=1):
        """Set the text rendering style"""
        self.text_color = text_color
        self.outline_color = outline_color
        self.shadow_color = shadow_color
        self.shadow_offset = shadow_offset
        self.outline_size = outline_size
    
    def render_text(self, draw, text, box, font=None, align="center"):
        """Render text within a box with manga styling"""
        x, y, w, h = box
        
        # Auto-fit text if font not provided
        if font is None:
            font, wrapped_lines, _ = self.fit_text_in_box(text, w, h)
            # self.logger.debug(f"Auto-fitted font size: {font.size} for box {box}")
        else:
            # Wrap text using provided font
            wrapped_lines = self.wrap_text(text, font, w * 0.9)
        
        if not wrapped_lines:
            return False
            
        line_height = self._get_line_height(font)
        line_spacing = int(line_height * 0.2)
        total_height = (len(wrapped_lines) * line_height) + (max(0, len(wrapped_lines) - 1) * line_spacing)
        
        # Center text block vertically
        text_y = y + (h - total_height) // 2
        
        # Draw each line
        for line in wrapped_lines:
            line_width, _ = self._get_text_size(line, font)
            
            if align == "center":
                text_x = x + (w - line_width) // 2
            elif align == "right":
                text_x = x + w - line_width - 10
            else:  # left
                text_x = x + 10
            
            # self.logger.debug(f"Auto-fitted font size: {font.size}")
            self._draw_styled_text(draw, (text_x, text_y), line, font)
            text_y += line_height + line_spacing
            
        return True
    
    def _draw_styled_text(self, draw, position, text, font):
        """Draw text with the specified style (shadow, outline, etc.)"""
        x, y = position
        
        # Draw shadow if specified
        if self.shadow_color:
            shadow_pos = (x + self.shadow_offset, y + self.shadow_offset)
            draw.text(shadow_pos, text, font=font, fill=self.shadow_color)
        
        # Draw outline if specified
        if self.outline_color:
            outline = self.outline_size
            for offset_x in range(-outline, outline + 1, outline):
                for offset_y in range(-outline, outline + 1, outline):
                    if offset_x == 0 and offset_y == 0:
                        continue
                    draw.text((x + offset_x, y + offset_y), text, font=font, fill=self.outline_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=self.text_color)
        
    def analyze_bubble_style(self, image, box):
        """Analyze the speech bubble to determine optimal text style"""
        x, y, w, h = box
        region = image.crop((x, y, x+w, y+h))
        region_array = np.array(region)
        
        # Convert to grayscale
        if len(region_array.shape) == 3:
            gray = cv2.cvtColor(region_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = region_array
            
        # Calculate average brightness
        avg_brightness = np.mean(gray)
        
        # Determine text color based on background brightness
        if avg_brightness < 128:
            # Dark background, use light text
            text_color = (255, 255, 255)
            outline_color = (0, 0, 0)
            shadow_color = None  # No shadow on dark background
        else:
            # Light background, use dark text
            text_color = (0, 0, 0)
            outline_color = None
            shadow_color = (150, 150, 150)
            
        # Calculate style settings
        style = {
            "text_color": text_color,
            "outline_color": outline_color,
            "shadow_color": shadow_color,
            "shadow_offset": max(1, int(min(w, h) / 100)),  # Scale with bubble size
            "outline_size": 1
        }
        
        return style
        
    def render_text_in_bubbles(self, image, bubbles_with_text, auto_style=True):
        """Render translated text into multiple speech bubbles"""
        draw = ImageDraw.Draw(image)
        
        for bubble in bubbles_with_text:
            # Skip if no translated text
            if "translated_text" not in bubble or not bubble["translated_text"].strip():
                continue
                
            # Get bubble info
            x, y, w, h = bubble["bbox"]
            text = bubble["translated_text"]
            
            # Create box tuple
            box = (x, y, w, h)
            
            # Auto-detect style if requested
            if auto_style:
                style = self.analyze_bubble_style(image, box)
                self.set_text_style(**style)
            
            # Render text into the bubble
            self.render_text(draw, text, box)
            
        return image
