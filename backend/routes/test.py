from flask import Blueprint, request, send_file, jsonify
import numpy as np
import cv2
import io
import asyncio

from process.test import test_xd
from process.main import process_image


test_bp = Blueprint('test', __name__)

@test_bp.route('/test')
def test():
    return jsonify(message=test_xd())


@test_bp.route('/process', methods=['POST'])
def process_endpoint():
    file = request.files['image']
    npimg = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    result = asyncio.run(process_image(image))
    # Return image as response
    return send_file(
        io.BytesIO(result["image_bytes"]),
        mimetype='image/png'
    )