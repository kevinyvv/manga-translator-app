from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register blueprints
from routes.hello import hello_bp
app.register_blueprint(hello_bp, url_prefix='/api')

from routes.test import test_bp
app.register_blueprint(test_bp, url_prefix='')


if __name__ == '__main__':
    app.run(debug=True)