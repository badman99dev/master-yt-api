# /api/index.py
# --- The All-in-One Master API File (Quart Version) ---

import asyncio
import aiohttp
# CHANGE 1: Import Quart instead of Flask
from quart import Quart, request, jsonify, Response 
from datetime import datetime

# ==============================================================================
# 1. CREATE THE QUART APP INSTANCE AT THE VERY TOP
# ==============================================================================
# CHANGE 2: Create a Quart app instead of a Flask app
app = Quart(__name__)


# (REST OF THE FILE IS EXACTLY THE SAME)
# (SCROLL DOWN)
# ...
# ...
# ...

# ==============================================================================
# 2. CONFIGURATION
# ==============================================================================
INVIDIOUS_API_BASE = "https://inv.perditum.com/api/v1"

# ==============================================================================
# 3. HELPER FUNCTIONS (No changes needed here)
# ==============================================================================

# ... (all your helper functions are perfect, no need to change them) ...

async def get_video_details(session, video_id):
    url = f"{INVIDIOUS_API_BASE}/videos/{video_id}"
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()

async def get_comments(session, video_id):
    url = f"{INVIDIOUS_API_BASE}/comments/{video_id}"
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()

async def get_transcript(session, video_id):
    captions_url = f"{INVIDIOUS_API_BASE}/videos/{video_id}?fields=captions"
    async with session.get(captions_url) as r:
        r.raise_for_status()
        data = await r.json()
        if not data.get('captions'):
            return {"error": "No captions available."}
        
        transcript_path = data['captions'][0]['url']
        base_url = INVIDIOUS_API_BASE.split('/api/v1')[0]
        full_transcript_url = f"{base_url}{transcript_path}"
        
        async with session.get(full_transcript_url) as tr:
            tr.raise_for_status()
            return await tr.json()

async def get_channel_details(session, channel_id):
    url = f"{INVIDIOUS_API_BASE}/authors/{channel_id}"
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()

async def perform_search(session, query):
    url = f"{INVIDIOUS_API_BASE}/search?q={query}&type=video"
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()

def format_number(num):
    try: return f"{int(num):,}"
    except (ValueError, TypeError): return "N/A"

def format_date(date_string):
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-m-d')
    except: return "N/A"

async def generate_llm_report(session, video_id):
    tasks = {'details': get_video_details(session, video_id), 'comments': get_comments(session, video_id)}
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    data = dict(zip(tasks.keys(), results))

    if isinstance(data.get('details'), Exception):
        return f"Error: Could not fetch video details. Reason: {data['details']}"

    details = data.get('details', {})
    comments_data = data.get('comments', {})
    
    channel_details = {}
    if details.get('authorId'):
        try: channel_details = await get_channel_details(session, details['authorId'])
        except Exception: pass

    transcript_text = "Transcript not available."
    try:
        transcript_json = await get_transcript(session, video_id)
        if 'error' not in transcript_json and transcript_json.get('lines'):
            transcript_text = "\n".join([f"({line['start']:.2f}s) {line['text']}" for line in transcript_json['lines']])
    except Exception: pass

    top_comments_text = "No comments available."
    if not isinstance(comments_data, Exception) and comments_data.get('comments'):
        sorted_comments = sorted(comments_data['comments'], key=lambda c: c.get('likeCount', 0), reverse=True)[:3]
        top_comments_text = "\n".join([f"- Top Comment ({format_number(c.get('likeCount', 0))} likes): {c.get('content', '').strip()}" for c in sorted_comments])

    return f"""**YouTube Video Analysis Report**
**1. Basic Information:**
- Title: {details.get('title', 'N/A')}
- Views: {format_number(details.get('viewCount', 0))}
- Likes: {format_number(details.get('likeCount', 0))}
- Uploaded On: {format_date(details.get('published', ''))}
**2. Channel Details:**
- Channel Name: {details.get('author', 'N/A')}
- Subscribers: {format_number(channel_details.get('subCount', 0))}
- Channel ID: {details.get('authorId', 'N/A')}
**3. Video Description:**
{details.get('description', 'No description.').strip()}
**4. Video Transcript (What is being said):**
{transcript_text}
**5. Public Opinion (Top Comments Summary):**
{top_comments_text}
--- End of Report ---""".strip()

# ==============================================================================
# 4. QUART ROUTING (No other changes needed, API is the same)
# ==============================================================================

@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
async def handler(path):
    if path == 'analyze_video':
        video_id = request.args.get('id')
        if not video_id:
            return Response("Error: A video 'id' parameter is required.", status=400, mimetype='text/plain')
        async with aiohttp.ClientSession() as session:
            report = await generate_llm_report(session, video_id)
        return Response(report, mimetype='text/plain; charset=utf-8')
    else:
        video_id = request.args.get('id')
        channel_id = request.args.get('channel')
        query = request.args.get('search')
        fields = [f.strip() for f in request.args.get('fields', '').split(',') if f]

        if not any([video_id, channel_id, query]):
            return jsonify({"error": "An 'id', 'channel', or 'search' parameter is required."}), 400

        tasks, response_keys = [], []
        async with aiohttp.ClientSession() as session:
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
            if query:
                tasks.append(perform_search(session, query))
                response_keys.append('search_results')

            if not tasks:
                return jsonify({"error": "No valid fields or parameters provided."}), 400

            results = await asyncio.gather(*tasks, return_exceptions=True)

        final_response = {}
        for key, result in zip(response_keys, results):
            if isinstance(result, Exception):
                final_response[key] = {"error": f"Failed to fetch {key}", "details": str(result)}
            else:
                final_response[key] = result
        # Note: Quart's jsonify might behave differently, let's keep it simple
        # For Quart, it's better to return the dict directly in many cases
        return jsonify(final_response)
