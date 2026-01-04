# 🎥 RTSP Camera Dashboard with SmolVLM

Real-time CCTV monitoring dashboard with AI-powered analysis using SmolVLM.

![Dashboard Preview](./demo.png)

## Features

✨ **Add Unlimited Cameras** - Support for any number of RTSP streams or webcams
📹 **Real-time Video** - Live streaming from all cameras
🤖 **AI Analysis** - SmolVLM analyzes each camera feed every 3 seconds
🌐 **Web Dashboard** - Beautiful, responsive web interface
⚡ **Real-time Updates** - WebSocket-based instant updates

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start SmolVLM

```bash
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 99
```

### 3. Start Dashboard Server

```bash
python server.py
```

### 4. Open Dashboard

Open your browser and go to:
```
http://localhost:5000
```

## Usage

### Adding Cameras

**Webcam:**
- Camera Name: `My Webcam`
- RTSP URL: `0` (for default webcam) or `1`, `2`, etc.

**RTSP Camera:**
- Camera Name: `Front Door`
- RTSP URL: `rtsp://username:password@192.168.1.100:554/stream1`

**HTTP Stream:**
- Camera Name: `Parking Lot`
- RTSP URL: `http://192.168.1.100:8080/video`

### Dashboard Features

- **Add Camera**: Enter name and URL, click "Add Camera"
- **View Live Feed**: Each camera shows real-time video
- **AI Analysis**: SmolVLM describes what it sees every 3 seconds
- **Remove Camera**: Click "Remove" to stop and delete a camera

## Architecture

```
┌─────────────┐
│   Browser   │ ← WebSocket Connection
│  Dashboard  │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Flask     │ ← HTTP Server
│   Server    │
└──────┬──────┘
       │
       ├─→ ┌──────────────┐
       │   │ RTSP/Webcam  │ ← OpenCV Capture
       │   │   Streams    │
       │   └──────────────┘
       │
       └─→ ┌──────────────┐
           │   SmolVLM    │ ← AI Analysis
           │ (localhost)  │
           └──────────────┘
```

## Configuration

Edit `server.py` to customize:

```python
SMOLVLM_ENDPOINT = "http://127.0.0.1:8080"  # SmolVLM URL
ANALYSIS_INTERVAL = 3  # Seconds between analysis
```

## API Endpoints

### Get All Cameras
```
GET /api/cameras
```

### Add Camera
```
POST /api/cameras
Body: {"name": "Camera Name", "url": "rtsp://..."}
```

### Remove Camera
```
DELETE /api/cameras/{camera_id}
```

## WebSocket Events

**Server → Client:**
- `frame_update` - New frame from camera
- `analysis_update` - New AI analysis result
- `connection_response` - Connection confirmation

**Client → Server:**
- `connect` - Client connected
- `disconnect` - Client disconnected
- `request_frame` - Request specific frame

## Troubleshooting

### Camera Not Connecting

**RTSP Issues:**
- Verify RTSP URL format: `rtsp://user:pass@ip:port/stream`
- Test with VLC player first
- Check network connectivity
- Ensure correct credentials

**Webcam Issues:**
- Try different IDs: `0`, `1`, `2`
- Check camera permissions
- Close other apps using the camera

### SmolVLM Not Working

```bash
# Test SmolVLM endpoint
curl http://127.0.0.1:8080/health
```

If not responding:
```bash
# Restart SmolVLM
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 99
```

### Performance Issues

**Too many cameras:**
- Reduce `ANALYSIS_INTERVAL` in `server.py`
- Lower video resolution in camera settings
- Use more powerful hardware

**Slow analysis:**
- Check SmolVLM GPU usage
- Reduce number of concurrent cameras
- Increase analysis interval

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never expose to the internet** without authentication
2. **Use HTTPS** in production
3. **Secure camera credentials** - don't hardcode passwords
4. **Firewall rules** - restrict access to trusted IPs
5. **Regular updates** - keep dependencies updated

## Production Deployment

### Using Gunicorn (Production)

```bash
pip install gunicorn eventlet
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 server:app
```

### Using Docker

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "server.py"]
```

Build and run:
```bash
docker build -t rtsp-dashboard .
docker run -p 5000:5000 rtsp-dashboard
```

### Using Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Tech Stack

- **Backend**: Flask + SocketIO
- **Video**: OpenCV
- **AI**: SmolVLM (via llama.cpp)
- **Frontend**: HTML5 + JavaScript + WebSocket
- **Streaming**: Real-time WebSocket frames

## Performance

- **Video Latency**: < 1 second
- **AI Analysis**: Every 3 seconds per camera
- **Max Cameras**: Limited by system resources
- **Frame Rate**: ~10 FPS per camera

## Credits

- **SmolVLM**: HuggingFace vision-language model
- **llama.cpp**: Local LLM inference
- **OpenCV**: Video capture and processing
- **Flask**: Web framework

## License

MIT License - Free to use and modify

## Support

For issues or questions:
1. Check SmolVLM is running at port 8080
2. Verify camera URLs are correct
3. Check browser console for errors
4. Review server logs for details

---

**Status**: Production Ready 🚀
**Version**: 1.0
**Date**: 2025-12-31
# smolvlm-realtime-camfeed
