// /api/_lib/helpers.js
const axios = require('axios');

const INVIDIOUS_API_BASE = "https://inv.perditum.com/api/v1";

// --- Data Fetching Functions ---
const getVideoDetails = async (videoId) => axios.get(`${INVIDIOUS_API_BASE}/videos/${videoId}`).then(res => res.data);
const getComments = async (videoId) => axios.get(`${INVIDIOUS_API_BASE}/comments/${videoId}`).then(res => res.data);
const getChannelDetails = async (channelId) => axios.get(`${INVIDIOUS_API_BASE}/authors/${channelId}`).then(res => res.data);
const performSearch = async (query) => axios.get(`${INVIDIOUS_API_BASE}/search?q=${query}&type=video`).then(res => res.data);

const getTranscript = async (videoId) => {
    try {
        const captionsUrl = `${INVIDIOUS_API_BASE}/videos/${videoId}?fields=captions`;
        const { data: captionsData } = await axios.get(captionsUrl);
        if (!captionsData.captions || captionsData.captions.length === 0) {
            return { error: "No captions available." };
        }
        const transcriptPath = captionsData.captions[0].url;
        const baseUrl = INVIDIOUS_API_BASE.split('/api/v1')[0];
        const fullTranscriptUrl = `${baseUrl}${transcriptPath}`;
        const { data: transcript } = await axios.get(fullTranscriptUrl);
        return transcript;
    } catch (error) {
        return { error: "Failed to fetch transcript." };
    }
};

// --- Formatting Functions ---
const formatNumber = (num) => {
    try { return new Intl.NumberFormat('en-US').format(num); }
    catch { return "N/A"; }
};
const formatDate = (dateString) => {
    try { return new Date(dateString).toLocaleDateString('en-CA'); } // YYYY-MM-DD format
    catch { return "N/A"; }
};

// --- LLM Report Generator ---
const generateLlmReport = async (videoId) => {
    try {
        const [details, comments] = await Promise.all([
            getVideoDetails(videoId),
            getComments(videoId)
        ]);

        let channelDetails = {};
        if (details.authorId) {
            try { channelDetails = await getChannelDetails(details.authorId); }
            catch (e) { /* Ignore if channel details fail */ }
        }

        let transcriptText = "Transcript not available.";
        const transcriptData = await getTranscript(videoId);
        if (!transcriptData.error && transcriptData.lines) {
            transcriptText = transcriptData.lines.map(line => `(${(line.start / 1000).toFixed(2)}s) ${line.text}`).join('\n');
        }

        let topCommentsText = "No comments available.";
        if (comments.comments && comments.comments.length > 0) {
            topCommentsText = comments.comments
                .sort((a, b) => (b.likeCount || 0) - (a.likeCount || 0))
                .slice(0, 3)
                .map(c => `- Top Comment (${formatNumber(c.likeCount || 0)} likes): ${c.content || ''}`.trim())
                .join('\n');
        }
        
        return `**YouTube Video Analysis Report**
**1. Basic Information:**
- Title: ${details.title || 'N/A'}
- Views: ${formatNumber(details.viewCount || 0)}
- Likes: ${formatNumber(details.likeCount || 0)}
- Uploaded On: ${formatDate(details.published)}
**2. Channel Details:**
- Channel Name: ${details.author || 'N/A'}
- Subscribers: ${formatNumber(channelDetails.subCount || 0)}
- Channel ID: ${details.authorId || 'N/A'}
**3. Video Description:**
${details.description || 'No description.'}
**4. Video Transcript (What is being said):**
${transcriptText}
**5. Public Opinion (Top Comments Summary):**
${topCommentsText}
--- End of Report ---`.trim();

    } catch (error) {
        return `Error: Failed to generate report for video ID ${videoId}. Reason: ${error.message}`;
    }
};

module.exports = {
    getVideoDetails, getComments, getTranscript, getChannelDetails, performSearch, generateLlmReport
};
