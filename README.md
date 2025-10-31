# Master YouTube API

A flexible and fast API to fetch data from YouTube via Invidious instances. Built with Flask and Aiohttp for parallel processing.

## Features
- Fetch multiple data points (details, comments, transcript, etc.) in a single request.
- All data fetching is done in parallel for maximum speed.
- Smart endpoint that understands what you need based on parameters.

## API Usage

**Endpoint:** `/api/fetch`

### Parameters:
- `id` (string): The YouTube video ID.
- `channel` (string): The YouTube channel ID.
- `search` (string): The search query.
- `fields` (string, comma-separated): The data you want.
  - **Available for `id`:** `details`, `comments`, `transcript`
  - **Available for `channel`:** `channel`

### Examples:

**Get video details and comments:**
`/api/fetch?id=dQw4w9WgXcQ&fields=details,comments`

**Search for videos:**
`/api/fetch?search=python+tutorial`

**Get channel details:**
`/api/fetch?channel=UC29ju8bIPH5as8OGnQzwJyA&fields=channel`
