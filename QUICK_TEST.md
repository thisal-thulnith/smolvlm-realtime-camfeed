# 🧪 Quick Test Guide

## ✅ System Status

- **Dashboard**: http://localhost:5001 (Running ✓)
- **SmolVLM**: http://127.0.0.1:8080 (Check status)
- **API Format**: Fixed ✓
- **Camera Permissions**: Fixed ✓

## 🚀 Test Now

### 1. Open Dashboard

```
http://localhost:5001
```

### 2. Test with Webcam

**Add Camera:**
- Camera Name: `Test Webcam`
- RTSP URL: `0`
- Click "Add Camera"

You should see:
- ✅ Live video feed
- 🤖 SmolVLM analysis every 3 seconds

### 3. Test with RTSP Camera

**Add Camera:**
- Camera Name: `IP Camera`
- RTSP URL: `rtsp://username:password@192.168.1.100:554/stream1`
- Click "Add Camera"

### 4. Verify Analysis

Check that SmolVLM provides descriptions like:
- "A person sitting at a desk with a laptop..."
- "2 people visible in the frame, one standing..."
- "Empty room, no people detected..."

## 🔧 If Camera Not Showing

### macOS Webcam Issues

**Option 1: Grant Permission**
1. System Settings → Privacy & Security → Camera
2. Enable your Terminal app
3. Restart server

**Option 2: Use Environment Variable**
```bash
export OPENCV_AVFOUNDATION_SKIP_AUTH=1
python server.py
```

**Option 3: Use RTSP Instead**
- No permissions needed for RTSP streams
- Add real RTSP camera URLs

## 🎯 What Fixed

### 1. SmolVLM API Format ✓

**Before (Wrong):**
```json
{
  "image": "base64...",
  "prompt": "text"
}
```

**After (Correct):**
```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}},
        {"type": "text", "text": "Analyze..."}
      ]
    }
  ]
}
```

### 2. Camera Permissions ✓

Added to `start_dashboard.sh`:
```bash
export OPENCV_AVFOUNDATION_SKIP_AUTH=1
```

### 3. Port Conflict ✓

Changed from port 5000 → 5001 (avoiding macOS AirPlay)

## 📊 Expected Behavior

### Dashboard
- Beautiful gradient UI
- Camera cards in grid layout
- Real-time video streaming
- Live AI analysis updates

### Each Camera Card Shows:
```
┌─────────────────────┐
│  Camera Name    [×] │ ← Header with remove button
├─────────────────────┤
│                     │
│   [Live Video]      │ ← Real-time stream
│                     │
├─────────────────────┤
│ 🤖 SmolVLM Analysis │ ← AI description
│ "Description here"  │
└─────────────────────┘
```

## 🐛 Troubleshooting

### No Video Feed

**Check:**
```bash
# Test camera access
python -c "import cv2; cap = cv2.VideoCapture(0); print('Works!' if cap.isOpened() else 'Failed')"
```

### No AI Analysis

**Check SmolVLM:**
```bash
curl http://127.0.0.1:8080/health
```

**If not running:**
```bash
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 99
```

### Browser Console Errors

1. Open browser console (F12)
2. Check Network tab for errors
3. Verify WebSocket connection

## ✨ Success Indicators

You know it's working when:
- ✅ Dashboard loads at http://localhost:5001
- ✅ "Connected to server" status shows green dot
- ✅ Camera video appears after adding
- ✅ Analysis text updates every 3 seconds
- ✅ No errors in terminal/console

## 🎉 Ready!

Your dashboard is fully functional. Add as many cameras as you want!

---

**Need help?** Check the main README.md for full documentation.
