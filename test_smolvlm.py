#!/usr/bin/env python3
"""
Test SmolVLM API and camera capture
"""

import cv2
import base64
import requests
from io import BytesIO
from PIL import Image

# Test 1: Camera Capture
print("=" * 60)
print("TEST 1: Camera Capture")
print("=" * 60)

try:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✓ Camera capture working!")
            print(f"  Frame shape: {frame.shape}")

            # Convert frame to base64 for SmolVLM test
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            buffer = BytesIO()
            pil_image.save(buffer, format="JPEG", quality=85)
            buffer.seek(0)
            image_b64 = base64.b64encode(buffer.read()).decode('utf-8')
            print(f"  Base64 length: {len(image_b64)}")
        else:
            print("✗ Failed to read frame")
        cap.release()
    else:
        print("✗ Failed to open camera")
except Exception as e:
    print(f"✗ Camera error: {e}")

print()

# Test 2: SmolVLM Text-only
print("=" * 60)
print("TEST 2: SmolVLM Text-Only API")
print("=" * 60)

try:
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Hello, respond with 'Working!' if you can read this."
            }
        ],
        "max_tokens": 50
    }

    response = requests.post(
        "http://127.0.0.1:8080/v1/chat/completions",
        json=payload,
        timeout=10
    )

    if response.status_code == 200:
        result = response.json()
        print("✓ SmolVLM text API working!")
        print(f"  Response: {result}")
    else:
        print(f"✗ SmolVLM error: {response.status_code}")
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"✗ SmolVLM connection error: {e}")

print()

# Test 3: SmolVLM with Image (if we got a frame)
print("=" * 60)
print("TEST 3: SmolVLM Image API")
print("=" * 60)

if 'image_b64' in locals():
    try:
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64[:100]}..."  # truncated for display
                            }
                        },
                        {
                            "type": "text",
                            "text": "What do you see in this image?"
                        }
                    ]
                }
            ],
            "max_tokens": 100
        }

        # Use actual full image
        payload["messages"][0]["content"][0]["image_url"]["url"] = f"data:image/jpeg;base64,{image_b64}"

        response = requests.post(
            "http://127.0.0.1:8080/v1/chat/completions",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print("✓ SmolVLM image API working!")
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                print(f"  Analysis: {content}")
            else:
                print(f"  Response: {result}")
        else:
            print(f"✗ SmolVLM error: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"✗ SmolVLM image error: {e}")
else:
    print("⊘ Skipped (no camera frame available)")

print()
print("=" * 60)
print("TESTS COMPLETE")
print("=" * 60)
