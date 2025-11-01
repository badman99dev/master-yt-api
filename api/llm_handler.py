# api/llm_handler.py
import aiohttp
import asyncio
from datetime import datetime

# Apne hi doosre handlers se functions import karo
from .video_handler import get_video_details, get_comments, get_transcript
from .channel_handler import get_channel_details

def format_number(num):
    """Numbers ko readable banata hai (e.g., 1000 -> 1,000)"""
    try:
        return f"{int(num):,}"
    except (ValueError, TypeError):
        return "N/A"

def format_date(date_string):
    """ISO date ko readable banata hai"""
    try:
        # Assuming the date is in a standard format like ISO 8601
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except:
        return "N/A"

async def generate_llm_report(session, video_id):
    """
    Saara data fetch karke ek clean, readable text report banata hai.
    """
    # Step 1: Ek saath saara data parallel me fetch karo
    tasks = {
        'details': get_video_details(session, video_id),
        'comments': get_comments(session, video_id)
        # Transcript alag se nikalenge kyunki uske liye pehle details chahiye
    }
    
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    
    data = dict(zip(tasks.keys(), results))

    # Error handling
    if isinstance(data.get('details'), Exception):
        return f"Error: Could not fetch video details for ID {video_id}. Reason: {data['details']}"

    # Saare data ko variables me daalo
    details = data.get('details', {})
    comments_data = data.get('comments', {})
    
    # Ab channel details nikalo
    channel_id = details.get('authorId')
    channel_details = {}
    if channel_id:
        try:
            channel_details = await get_channel_details(session, channel_id)
        except Exception:
            channel_details = {} # Agar fail ho to empty rakho

    # Transcript nikalo
    transcript_text = "Transcript not available."
    try:
        transcript_json = await get_transcript(session, video_id)
        if 'error' not in transcript_json:
            transcript_text = "\n".join([f"({line['start']:.2f}s) {line['text']}" for line in transcript_json.get('lines', [])])
    except Exception:
        pass # Agar fail ho to default text use hoga

    # Top comments nikal kar sort karo
    top_comments_text = "No comments available or failed to fetch."
    if not isinstance(comments_data, Exception) and comments_data.get('comments'):
        sorted_comments = sorted(comments_data['comments'], key=lambda c: c.get('likeCount', 0), reverse=True)[:3]
        top_comments_text = "\n".join([
            f"- **Top Comment ({format_number(c.get('likeCount', 0))} likes):** {c.get('content', '').strip()}"
            for c in sorted_comments
        ])

    # Ab final report banana shuru karo
    report = f"""
**YouTube Video Analysis Report**

**1. Basic Information:**
- **Title:** {details.get('title', 'N/A')}
- **Views:** {format_number(details.get('viewCount', 0))}
- **Likes:** {format_number(details.get('likeCount', 0))}
- **Uploaded On:** {format_date(details.get('published', ''))}

**2. Channel Details:**
- **Channel Name:** {details.get('author', 'N/A')}
- **Subscribers:** {format_number(channel_details.get('subCount', 0))}
- **Channel ID:** {details.get('authorId', 'N/A')}

**3. Video Description:**
{details.get('description', 'No description provided.').strip()}

**4. Video Transcript (What is being said):**
{transcript_text}

**5. Public Opinion (Top Comments Summary):**
The overall sentiment based on top comments seems to be: {comments_data.get('sentiment', 'Neutral') if not isinstance(comments_data, Exception) else 'N/A'}.
{top_comments_text}

**--- End of Report ---**
"""
    return report.strip()
