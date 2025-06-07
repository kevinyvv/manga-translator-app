from flask import Blueprint, jsonify

hello_bp = Blueprint('hello', __name__)

@hello_bp.route('/hello')
def hello():
    return jsonify(message="Hello from Flask!")