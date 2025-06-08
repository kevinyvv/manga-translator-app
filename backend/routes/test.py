from flask import Blueprint, request, send_file, jsonify
import numpy as np
import cv2
import io
import asyncio
import base64

from process.test import test_xd
from process.test import process_image


test_bp = Blueprint('test', __name__)

@test_bp.route('/test')
def test():
    return jsonify(message=test_xd())


@test_bp.route('/process', methods=['POST'])
def process_endpoint():
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
    file = request.files['image']
    npimg = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    result = asyncio.run(process_image(image))
    imageb64 = base64.b64encode(result["image_bytes"]).decode('utf-8')
    return jsonify({
        "image": imageb64,
        "text_extracted": result["text_extracted"],
        "translated_data": result["translated_data"]
    })