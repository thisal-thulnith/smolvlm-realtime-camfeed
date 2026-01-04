"""
RTSP Camera Dashboard Server
Real-time CCTV monitoring with SmolVLM analysis
"""

import cv2
import base64
import threading
import time
import requests
from io import BytesIO
from PIL import Image
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smolvlm-dashboard-secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Camera storage
cameras = {}  # {camera_id: {url, cap, thread, active, last_frame, last_analysis}}
camera_counter = 0

# SmolVLM Configuration
SMOLVLM_ENDPOINT = "http://127.0.0.1:8080"
ANALYSIS_INTERVAL = 3  # Analyze every 3 seconds


class CameraStream:
    """Handles RTSP stream capture and analysis."""

    def __init__(self, camera_id, rtsp_url, name="Camera"):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.name = name
        self.cap = None
        self.active = False
        self.thread = None
        self.last_frame = None
        self.last_analysis = "Initializing..."
        self.last_analysis_time = 0

    def start(self):
        """Start the camera stream."""
        self.active = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        logger.info(f"Started camera {self.camera_id}: {self.name}")

    def stop(self):
        """Stop the camera stream."""
        self.active = False
        if self.thread:
            self.thread.join(timeout=5)
        if self.cap:
            self.cap.release()
        logger.info(f"Stopped camera {self.camera_id}")

    def _capture_loop(self):
        """Main capture loop."""
        retry_count = 0
        max_retries = 3

        while self.active:
            try:
                # Connect to stream
                if self.cap is None or not self.cap.isOpened():
                    logger.info(f"Connecting to {self.name} at {self.rtsp_url}")

                    # Handle webcam (0, 1, etc.) vs RTSP URL
                    if self.rtsp_url.isdigit():
                        self.cap = cv2.VideoCapture(int(self.rtsp_url))
                    else:
                        self.cap = cv2.VideoCapture(self.rtsp_url)

                    if not self.cap.isOpened():
                        logger.error(f"Failed to open stream for {self.name}")
                        retry_count += 1
                        if retry_count >= max_retries:
                            self.last_analysis = f"❌ Connection failed after {max_retries} attempts"
                            socketio.emit('analysis_update', {
                                'camera_id': self.camera_id,
                                'analysis': self.last_analysis
                            })
                            time.sleep(10)
                            retry_count = 0
                        time.sleep(5)
                        continue

                    retry_count = 0
                    self.last_analysis = "✅ Connected, analyzing..."

                # Read frame
                ret, frame = self.cap.read()

                if not ret or frame is None:
                    logger.warning(f"Failed to read frame from {self.name}")
                    self.cap.release()
                    self.cap = None
                    continue

                # Store frame
                self.last_frame = frame.copy()

                # Emit frame to connected clients
                self._emit_frame(frame)

                # Analyze with SmolVLM periodically
                current_time = time.time()
                if current_time - self.last_analysis_time > ANALYSIS_INTERVAL:
                    self._analyze_frame(frame)
                    self.last_analysis_time = current_time

                # Control frame rate
                time.sleep(0.1)  # ~10 FPS

            except Exception as e:
                logger.error(f"Error in capture loop for {self.name}: {e}")
                if self.cap:
                    self.cap.release()
                    self.cap = None
                time.sleep(5)

    def _emit_frame(self, frame):
        """Encode and emit frame to clients."""
        try:
            # Resize for display (keep aspect ratio)
            height, width = frame.shape[:2]
            max_width = 640
            if width > max_width:
                scale = max_width / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))

            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_b64 = base64.b64encode(buffer).decode('utf-8')

            # Emit to clients
            socketio.emit('frame_update', {
                'camera_id': self.camera_id,
                'frame': frame_b64
            })
            logger.info(f"✓ Emitted frame for {self.camera_id}, size: {len(frame_b64)} bytes")

        except Exception as e:
            logger.error(f"Error emitting frame: {e}")

    def _analyze_frame(self, frame):
        """Analyze frame with SmolVLM."""
        try:
            # Convert frame to base64
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            buffer = BytesIO()
            pil_image.save(buffer, format="JPEG", quality=85)
            buffer.seek(0)
            image_b64 = base64.b64encode(buffer.read()).decode('utf-8')

            # Call SmolVLM with correct API format
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": "Analyze this CCTV camera feed as a security officer. Provide a brief 1-2 sentence description of what you see, number of people (if any), and any notable activity. Be concise and factual."
                            }
                        ]
                    }
                ],
                "max_tokens": 150,
                "temperature": 0.1
            }

            response = requests.post(
                f"{SMOLVLM_ENDPOINT}/v1/chat/completions",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                analysis = "No analysis available"

                if "choices" in result and len(result["choices"]) > 0:
                    analysis = result["choices"][0]["message"]["content"]
                elif "response" in result:
                    analysis = result["response"]
                else:
                    analysis = str(result)

                self.last_analysis = analysis

                # Emit analysis update
                socketio.emit('analysis_update', {
                    'camera_id': self.camera_id,
                    'analysis': analysis
                })

                logger.info(f"✓ Emitted analysis for {self.camera_id}: {analysis[:50]}...")
            else:
                error_msg = f"SmolVLM error: {response.status_code}"
                self.last_analysis = error_msg
                logger.error(error_msg)

        except Exception as e:
            error_msg = f"Analysis error: {str(e)}"
            self.last_analysis = error_msg
            logger.error(f"Error analyzing frame for {self.name}: {e}")


@app.route('/')
def index():
    """Serve the dashboard."""
    return render_template('dashboard.html')


@app.route('/test.html')
def test():
    """Serve the test page."""
    return render_template('test.html')


@app.route('/api/cameras', methods=['GET'])
def get_cameras():
    """Get list of all cameras."""
    camera_list = []
    for cam_id, cam in cameras.items():
        camera_list.append({
            'id': cam_id,
            'name': cam.name,
            'url': cam.rtsp_url,
            'active': cam.active,
            'last_analysis': cam.last_analysis
        })
    return jsonify(camera_list)


@app.route('/api/cameras', methods=['POST'])
def add_camera():
    """Add a new camera."""
    global camera_counter

    data = request.json
    rtsp_url = data.get('url', '')
    name = data.get('name', f'Camera {camera_counter + 1}')

    if not rtsp_url:
        return jsonify({'error': 'RTSP URL is required'}), 400

    camera_counter += 1
    camera_id = f"cam_{camera_counter}"

    # Create and start camera stream
    camera = CameraStream(camera_id, rtsp_url, name)
    cameras[camera_id] = camera
    camera.start()

    return jsonify({
        'id': camera_id,
        'name': name,
        'url': rtsp_url,
        'active': True
    })


@app.route('/api/cameras/<camera_id>', methods=['DELETE'])
def remove_camera(camera_id):
    """Remove a camera."""
    if camera_id in cameras:
        cameras[camera_id].stop()
        del cameras[camera_id]
        return jsonify({'success': True})
    return jsonify({'error': 'Camera not found'}), 404


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info('🔌 Client connected via WebSocket')
    emit('connection_response', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info('🔌 Client disconnected from WebSocket')


@socketio.on('request_frame')
def handle_frame_request(data):
    """Handle frame request from client."""
    camera_id = data.get('camera_id')
    if camera_id in cameras:
        cam = cameras[camera_id]
        if cam.last_frame is not None:
            cam._emit_frame(cam.last_frame)


if __name__ == '__main__':
    print("=" * 70)
    print("🎥 RTSP Camera Dashboard Server")
    print("=" * 70)
    print()
    print("Server starting on http://localhost:5001")
    print()
    print("Features:")
    print("  ✓ Add unlimited RTSP cameras")
    print("  ✓ Real-time video streaming")
    print("  ✓ SmolVLM analysis every 3 seconds")
    print("  ✓ Web-based dashboard")
    print()
    print("Make sure SmolVLM is running at http://127.0.0.1:8080")
    print()
    print("=" * 70)
    print()

    socketio.run(app, host='0.0.0.0', port=5001, debug=False)
