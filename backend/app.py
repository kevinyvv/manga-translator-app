from flask import Flask

app = Flask(__name__)

# Register blueprints
from routes.hello import hello_bp
app.register_blueprint(hello_bp, url_prefix='/api')


if __name__ == '__main__':
    app.run(debug=True)