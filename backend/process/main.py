# main.py -- NOT USED RIGHT NOW -- use test.py instead

# usage: python -m process.main --image_path <path_to_image>
import argparse
import os
import json
import asyncio
import cv2
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


async def process_image(image_path, output_path, source_lang="ja", target_lang="en", 
                       conf_threshold=0.25, debug=False, font_path=None):
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
    original_image = cv2.imread(image_path)
    if original_image is None:
        raise ValueError(f"Could not read image from {image_path}")

    # Initialize components
    text_extractor = MangaTextExtractor()
    translator = MangaTranslator()
    renderer = MangaTextRenderer(font_path=font_path)
    inpainter = Inpainter()

    # Step 1: Detect speech bubbles
    bubbles, _ = text_extractor.detect_bubbles(image_path, conf_threshold)
    
    # Skip processing if no bubbles found
    if not bubbles:
        logger.info("No speech bubbles detected. Saving original image.")
        cv2.imwrite(output_path, original_image)
        return {"status": "no_bubbles", "bubbles_count": 0}

    # Step 2: Generate text mask using text segmentation
    text_mask = text_extractor.segment_text(original_image)

    # Step 3: Extract text from bubbles
    text_data = text_extractor.extract_text(original_image, bubbles, source_lang)
    
    # Step 4: Translate text
    translated_data = translator.translate(text_data, source_lang, target_lang, manga_title=None)
    
    # Step 5: Create inpainted image (text removed)
    inpainted_image = inpainter.inpaint(original_image, text_mask, method="lama")
    
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
    
    # Save the result
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    cv2.imwrite(output_path, result_image)
    logger.info(f"Translated image saved to {output_path}")
    
    # Debug visualization if requested
    if debug:
        create_debug_visualization(original_image, text_mask, inpainted_image, 
                                 result_image, image_path, output_path)
    
    # Save text data to JSON for reference
    json_path = os.path.splitext(output_path)[0] + "_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=4)
    
    return {
        "status": "success",
        "bubbles_count": len(bubbles),
        "text_extracted": sum(1 for item in text_data if item["text"]),
        "output_path": output_path,
        "json_path": json_path
    }


def create_debug_visualization(original_image, text_mask, inpainted_image, 
                             result_image, image_path, output_path):
    """Create and save debug visualization"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Original image
    axes[0, 0].imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    axes[0, 0].set_title("Original Image")
    axes[0, 0].axis("off")
    
    # Text mask
    axes[0, 1].imshow(text_mask, cmap='gray')
    axes[0, 1].set_title("Text Mask")
    axes[0, 1].axis("off")
    
    # Inpainted image
    axes[1, 0].imshow(cv2.cvtColor(inpainted_image, cv2.COLOR_BGR2RGB))
    axes[1, 0].set_title("Inpainted Image (Text Removed)")
    axes[1, 0].axis("off")
    
    # Final result
    axes[1, 1].imshow(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
    axes[1, 1].set_title("Final Translated Image")
    axes[1, 1].axis("off")
    
    plt.tight_layout()
    
    # Save debug visualization
    debug_dir = os.path.dirname(os.path.abspath(output_path))
    base_name = os.path.basename(image_path)
    name_without_ext = os.path.splitext(base_name)[0]
    debug_path = os.path.join(debug_dir, f"{name_without_ext}_debug.jpg")
    plt.savefig(debug_path)
    logger.debug(f"Debug visualization saved to {debug_path}")
    plt.close()


# Example usage
if __name__ == "__main__":

    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(reset)s%(message)s",
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'red',
        'ERROR':    'bold_red',
        'CRITICAL': 'purple',
    },
    secondary_log_colors={
    }
    ))
    
    # set the root logger to use the handler
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

    # now create logger for main.py
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    async def main():
        # Example parameters
        logger.info("Starting manga translation pipeline")
        parser = argparse.ArgumentParser(description="Manga Translation Pipeline")
        parser.add_argument("--image_path", type=str, required=True, help="Path to the input image")
        
        args = parser.parse_args()

        os.makedirs("output", exist_ok=True)
        base_name = os.path.basename(args.image_path)
        output_path = os.path.join("output", f"translated_{base_name}")

        # Process the image
        result = await process_image(
            image_path=args.image_path,
            output_path=output_path,
            source_lang="ja",
            target_lang="en",
            conf_threshold=0.25,
            debug=True,
            font_path="fonts/Anime.otf"  # Optional custom font
        )
        
        logger.warning(f"Processing result: {result}")
    
    # Run the async main function
    asyncio.run(main())