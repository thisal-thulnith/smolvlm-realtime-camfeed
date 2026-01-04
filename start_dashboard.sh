#!/bin/bash

echo "🎥 RTSP Camera Dashboard Launcher"
echo "=================================="
echo ""
echo "Checking requirements..."
echo ""

# Check if SmolVLM is running
if curl -s http://127.0.0.1:8080/health > /dev/null 2>&1; then
    echo "✓ SmolVLM is running at http://127.0.0.1:8080"
else
    echo "⚠️  SmolVLM is NOT running!"
    echo ""
    echo "Please start SmolVLM first:"
    echo "  llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 99"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "Starting dashboard server..."
echo ""
echo "Access the dashboard at: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Fix macOS camera permissions
export OPENCV_AVFOUNDATION_SKIP_AUTH=1

python server.py
