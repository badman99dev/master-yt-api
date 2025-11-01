# api/video_handler.py
import asyncio
from api.config import INVIDIOUS_API_BASE # <-- IMPORT UPDATED

async def get_video_details(session, video_id):
    """Fetches main details for a video."""
    url = f"{INVIDIOUS_API_BASE}/videos/{video_id}"
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()

async def get_comments(session, video_id):
    """Fetches comments for a video."""
    url = f"{INVIDIOUS_API_BASE}/comments/{video_id}"
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()

async def get_transcript(session, video_id):
    """Fetches transcript/captions for a video."""
    captions_url = f"{INVIDIOUS_API_BASE}/videos/{video_id}?fields=captions"
    async with session.get(captions_url) as r:
        r.raise_for_status()
        data = await r.json()
        if not data.get('captions'):
            return {"error": "No captions available."}
        
        # Note: The original transcript URL was hardcoded. This is better.
        transcript_path = data['captions'][0]['url']
        base_url = INVIDIOUS_API_BASE.split('/api/v1')[0]
        full_transcript_url = f"{base_url}{transcript_path}"
        
        async with session.get(full_transcript_url) as tr:
            tr.raise_for_status()
            return await tr.json()
