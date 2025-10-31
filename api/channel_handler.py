# api/channel_handler.py
from .config import INVIDIOUS_API_BASE

async def get_channel_details(session, channel_id):
    """Fetches details for a channel (banner, videos, etc.)."""
    url = f"{INVIDIOUS_API_BASE}/authors/{channel_id}"
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()
