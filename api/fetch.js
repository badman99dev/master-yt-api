// /api/fetch.js
const express = require('express');
const { getVideoDetails, getComments, getTranscript, getChannelDetails, performSearch } = require('./_lib/helpers');

const app = express();

app.get('/api/fetch', async (req, res) => {
    const { id: videoId, channel: channelId, search: query, fields } = req.query;
    
    if (!videoId && !channelId && !query) {
        return res.status(400).json({ error: "An 'id', 'channel', or 'search' parameter is required." });
    }

    const fieldList = fields ? fields.split(',').map(f => f.trim()) : [];
    const tasks = [];
    const responseKeys = [];

    if (query) {
        tasks.push(performSearch(query));
        responseKeys.push('searchResults');
    }
    if (videoId) {
        if (fieldList.includes('details')) { tasks.push(getVideoDetails(videoId)); responseKeys.push('details'); }
        if (fieldList.includes('comments')) { tasks.push(getComments(videoId)); responseKeys.push('comments'); }
        if (fieldList.includes('transcript')) { tasks.push(getTranscript(videoId)); responseKeys.push('transcript'); }
    }
    if (channelId && fieldList.includes('channel')) {
        tasks.push(getChannelDetails(channelId));
        responseKeys.push('channel');
    }

    if (tasks.length === 0) {
        return res.status(400).json({ error: "No valid fields or parameters provided." });
    }

    try {
        const results = await Promise.all(tasks);
        const finalResponse = {};
        responseKeys.forEach((key, index) => {
            finalResponse[key] = results[index];
        });
        return res.status(200).json(finalResponse);
    } catch (error) {
        return res.status(500).json({ error: "Failed to fetch data.", details: error.message });
    }
});

module.exports = app;
