#!/usr/bin/env python3
"""
TTS Server Startup Script

Quick start script for the Vapi Custom TTS Server with dynamic voice routing.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed."""
    try:
        import fastapi
        import uvicorn
        import httpx
        import websockets
        import pydub
        import numpy
        import dotenv
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e.name}")
        print("Run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment variables are set."""
    required_vars = [
        "OPENAI_API_KEY",
        "ELEVENLABS_API_KEY", 
        "ELEVENLABS_VOICE_ID",
        "VAPI_PRIVATE_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Create a .env file based on .env.example")
        return False
    
    print("✅ All environment variables are set")
    return True

def main():
    """Start the TTS server."""
    print("🚀 Starting Vapi Custom TTS Server...")
    print("="*50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Get server configuration
    port = int(os.getenv("SERVER_PORT", "8000"))
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    
    print(f"🌐 Server will start on http://{host}:{port}")
    print(f"📊 Health check: http://{host}:{port}/health")
    print(f"🧪 Test endpoint: http://{host}:{port}/test")
    print(f"🎯 Main endpoint: http://{host}:{port}/synthesize")
    print("="*50)
    
    try:
        # Start the server
        import uvicorn
        uvicorn.run(
            "tts_server:app",
            host=host,
            port=port,
            reload=os.getenv("ENVIRONMENT", "development") == "development",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
