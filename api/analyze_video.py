# api/analyze_video.py

import asyncio
import aiohttp
from flask import Flask, request, Response

# Import the main helper function
from .llm_handler import generate_llm_report

# This file also gets its own Flask app instance
app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def handler(path):
    # This is the exact same logic from your old analyze_video_for_llm function
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "A video 'id' parameter is required."}), 400

    async with aiohttp.ClientSession() as session:
        report = await generate_llm_report(session, video_id)
    
    return Response(report, mimetype='text/plain; charset=utf-8')
