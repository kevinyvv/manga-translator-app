import logging
import colorlog
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

# Set up colored logging for the whole app
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
    secondary_log_colors={}
))
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

for noisy in ["werkzeug", "httpx", "google_genai"]:
    logging.getLogger(noisy).setLevel(logging.WARNING)
    
app = Flask(__name__)
CORS(app)
# swagger is at 127.0.0.1/apidocs/
Swagger(app)

# Register blueprints
from routes.hello import hello_bp
app.register_blueprint(hello_bp, url_prefix='/api')

from routes.test import test_bp
app.register_blueprint(test_bp, url_prefix='')


if __name__ == '__main__':
    app.run(debug=True)