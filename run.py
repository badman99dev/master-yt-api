# run.py
from flask import Flask
from flask_cors import CORS  # <--- 1. Isko import karo
from api.routes import api_blueprint

def create_app():
    app = Flask(__name__)
    
    # --- 2. Is line ko add karo ---
    # Iska matlab hai: Is app par kisi bhi origin se request aane do (*)
    CORS(app) 
    
    # Hamare API blueprint ko '/api' route par register karo
    app.register_blueprint(api_blueprint, url_prefix='/api')
    return app

app = create_app()

if __name__ == '__main__':
    # Ye sirf local testing ke liye hai
    app.run(debug=True, port=5000)
