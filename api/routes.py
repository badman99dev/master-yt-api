# api/routes.py
import asyncio
import aiohttp
from flask import Blueprint, request, jsonify

# Saare handler functions import karo
from .video_handler import get_video_details, get_comments, get_transcript
from .channel_handler import get_channel_details
from .search_handler import perform_search

# Flask Blueprint banate hain
api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/fetch')
async def master_fetch():
    # User se parameters lo
    video_id = request.args.get('id')
    channel_id = request.args.get('channel')
    query = request.args.get('search')
    fields = [f.strip() for f in request.args.get('fields', '').split(',') if f]

    if not any([video_id, channel_id, query]):
        return jsonify({"error": "An 'id', 'channel', or 'search' parameter is required."}), 400

    tasks = []
    response_keys = []

    async with aiohttp.ClientSession() as session:
        # User ne jo-jo maanga hai, uske tasks banao
        if 'details' in fields and video_id:
            tasks.append(get_video_details(session, video_id))
            response_keys.append('details')
        if 'comments' in fields and video_id:
            tasks.append(get_comments(session, video_id))
            response_keys.append('comments')
        if 'transcript' in fields and video_id:
            tasks.append(get_transcript(session, video_id))
            response_keys.append('transcript')
        if 'channel' in fields and channel_id:
            tasks.append(get_channel_details(session, channel_id))
            response_keys.append('channel')
        if query: # Search hamesha primary parameter rahega
            tasks.append(perform_search(session, query))
            response_keys.append('search_results')

        if not tasks:
            return jsonify({"error": "No valid fields or parameters provided."}), 400

        # Saare tasks parallel me run karo
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Final response taiyar karo
    final_response = {}
    for key, result in zip(response_keys, results):
        if isinstance(result, Exception):
            final_response[key] = {"error": f"Failed to fetch {key}", "details": str(result)}
        else:
            final_response[key] = result
            
    return jsonify(final_response)
