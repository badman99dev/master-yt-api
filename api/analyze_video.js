// /api/analyze_video.js
const express = require('express');
const { generateLlmReport } = require('./_lib/helpers');

const app = express();

app.get('/api/analyze_video', async (req, res) => {
    const { id: videoId } = req.query;

    if (!videoId) {
        return res.status(400).type('text/plain').send("Error: A video 'id' parameter is required.");
    }

    const report = await generateLlmReport(videoId);
    
    res.setHeader('Content-Type', 'text/plain; charset=utf-8');
    return res.status(200).send(report);
});

module.exports = app;
