# api/search_handler.py
from .config import INVIDIOUS_API_BASE

async def perform_search(session, query):
    """Performs a search query."""
    url = f"{INVIDIOUS_API_BASE}/search?q={query}&type=video"
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()
