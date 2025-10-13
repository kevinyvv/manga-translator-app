from quart import Blueprint, request, send_file, jsonify
import numpy as np
import cv2
import io
import asyncio
import base64

from process.test import test_xd
from process.test import process_image


from process.text_extraction import MangaTextExtractor
from process.translator import MangaTranslator
from process.text_render import MangaTextRenderer
from process.inpaint import Inpainter

print("initializing components")
text_extractor = MangaTextExtractor()
translator = MangaTranslator()
renderer = MangaTextRenderer(font_path="fonts/Anime.otf")
inpainter = Inpainter()
print("initialization complete")


test_bp = Blueprint('test', __name__)

@test_bp.route('/test')
def test():
    return jsonify(message=test_xd())


import logging
logger = logging.getLogger(__name__)

@test_bp.route('/process', methods=['POST'])
async def process_endpoint():
    """
    Process an uploaded image and return the result.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: image
        type: file
        required: true
        description: The image file to process.
    responses:
      200:
        description: Processed image returned as PNG.
        content:
          image/png:
            schema:
              type: string
              format: binary
    """
    files = (await request.files).getlist('image')
    form = await request.form
    source_lang = form.get("source_lang", "ja")
    target_lang = form.get("target_lang", "en")
    translation_method = form.get("translation_method", "genai")
    inpaint_method = form.get("inpaint_method", "opencv")
    logger.debug("target_lang: %s", target_lang)
    
    results = []
    for file in files:
        npimg = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        result = await process_image(image, 
                                           text_extractor=text_extractor,
                                            translator=translator,
                                            renderer=renderer,
                                            inpainter=inpainter,
                                           source_lang=source_lang, 
                                           target_lang=target_lang,
                                           translation_method=translation_method,
                                           inpaint_method=inpaint_method
                                           )
        # imageb64 = base64.b64encode(result["image_bytes"]).decode('utf-8')
        image_bytes = result["image_bytes"]

        img_res = {
            "image": image_bytes,
            "text_extracted": result["text_extracted"],
            "translated_data": result["translated_data"]
        }
        results.append(img_res)
    return jsonify(results)