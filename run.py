# run.py
from flask import Flask
from api.routes import api_blueprint

def create_app():
    app = Flask(__name__)
    # Hamare API blueprint ko '/api' route par register karo
    app.register_blueprint(api_blueprint, url_prefix='/api')
    return app

app = create_app()

if __name__ == '__main__':
    # Ye sirf local testing ke liye hai
    app.run(debug=True, port=5000)
