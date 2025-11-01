# api/routes.py
import asyncio
import aiohttp
# Response ko text/plain format me bhejne ke liye import karo
from flask import Blueprint, request, jsonify, Response 

# Naye handler ko import karo
from .llm_handler import generate_llm_report
# ... (baki imports waise hi rahenge) ...

# ... (master_fetch function waise hi rahega) ...

# YAHAN NAYA ENDPOINT ADD KARO
@api_blueprint.route('/analyze_video')
async def analyze_video_for_llm():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "A video 'id' parameter is required."}), 400

    async with aiohttp.ClientSession() as session:
        report = await generate_llm_report(session, video_id)
    
    # Report ko plain text me bhejo taaki padhne me aasan ho
    return Response(report, mimetype='text/plain; charset=utf-8')
