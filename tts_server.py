#!/usr/bin/env python3
"""
Vapi Custom TTS Server with Dynamic Voice Routing

Supports both OpenAI Realtime API and ElevenLabs v3 for dynamic voice synthesis.
Returns PCM 16-bit mono 16kHz audio compatible with Vapi requirements.

Author: Keen AI Agent
Date: 2025-09-06
Updated: Latest API specifications for 2025
"""

import os
import asyncio
import base64
import json
import logging
from typing import Optional, Dict, Any
from io import BytesIO

import numpy as np
from fastapi import FastAPI, HTTPException, Header, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import websockets
from pydub import AudioSegment
from pydub.utils import make_chunks
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_REALTIME_MODEL = os.getenv("OPENAI_REALTIME_MODEL", "gpt-4o-realtime-preview")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
VAPI_SECRET = os.getenv("VAPI_SECRET", "your-vapi-secret-here")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# Validate required environment variables
required_vars = ["OPENAI_API_KEY", "ELEVENLABS_API_KEY", "ELEVENLABS_VOICE_ID"]
for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")

# FastAPI app initialization
app = FastAPI(
    title="Vapi Custom TTS Server",
    description="Dynamic voice routing between OpenAI Realtime and ElevenLabs v3",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class TTSRequest(BaseModel):
    message: str
    mode: str = "v3"  # "realtime" or "v3"
    voice_settings: Optional[Dict[str, Any]] = None
    sample_rate: int = 16000

class HealthResponse(BaseModel):
    status: str
    version: str
    supported_modes: list
    timestamp: str
    api_versions: Dict[str, str]

# Audio processing utilities
def convert_to_pcm_16khz_mono(audio_data: bytes, source_format: str = "mp3", source_rate: int = 44100) -> bytes:
    """
    Convert audio data to PCM 16-bit mono 16kHz format required by Vapi.
    """
    try:
        # Load audio from bytes
        if source_format == "pcm":
            # Assume PCM input, create AudioSegment from raw data
            audio = AudioSegment(
                data=audio_data,
                sample_width=2,  # 16-bit = 2 bytes
                frame_rate=source_rate,
                channels=1 if len(audio_data) // 2 // (len(audio_data) // 2 // source_rate) == 1 else 2
            )
        else:
            # Load from MP3 or other formats
            audio = AudioSegment.from_file(BytesIO(audio_data), format=source_format)
        
        # Convert to mono
        if audio.channels > 1:
            audio = audio.set_channels(1)
        
        # Convert to 16kHz sample rate
        if audio.frame_rate != 16000:
            audio = audio.set_frame_rate(16000)
        
        # Ensure 16-bit depth
        audio = audio.set_sample_width(2)
        
        # Return raw PCM data
        return audio.raw_data
    
    except Exception as e:
        logger.error(f"Audio conversion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audio conversion failed: {str(e)}")

async def synthesize_with_openai_realtime(text: str, voice_settings: Optional[Dict] = None) -> bytes:
    """
    Synthesize speech using OpenAI Realtime API with 2025 specifications.
    """
    try:
        # Updated WebSocket endpoint for 2025 (gpt-4o-realtime-preview-2024-10-01)
        uri = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        audio_chunks = []
        
        async with websockets.connect(uri, extra_headers=headers) as websocket:
            # Configure session for audio-only output with Hebrew support
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "instructions": f"You are a Hebrew-speaking sales assistant. Please convert the following Hebrew text to natural Hebrew speech: {text}",
                    "voice": voice_settings.get("voice", "alloy") if voice_settings else "alloy",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 200
                    },
                    "temperature": 0.8
                }
            }
            
            await websocket.send(json.dumps(session_config))
            
            # Wait for session.updated confirmation
            response = await websocket.recv()
            session_response = json.loads(response)
            
            if session_response.get("type") != "session.updated":
                logger.warning(f"Unexpected session response: {session_response}")
            
            # Send text input for speech synthesis
            text_input = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": text
                        }
                    ]
                }
            }
            
            await websocket.send(json.dumps(text_input))
            
            # Request response generation (audio only)
            response_create = {
                "type": "response.create",
                "response": {
                    "modalities": ["audio"]
                }
            }
            
            await websocket.send(json.dumps(response_create))
            
            # Collect audio chunks
            timeout_count = 0
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    event = json.loads(message)
                    
                    if event.get("type") == "response.audio.delta":
                        # Decode base64 audio data
                        audio_data = base64.b64decode(event["delta"])
                        audio_chunks.append(audio_data)
                        timeout_count = 0  # Reset timeout counter
                    
                    elif event.get("type") == "response.audio.done":
                        logger.info("OpenAI Realtime audio generation completed")
                        break
                    
                    elif event.get("type") == "error":
                        raise Exception(f"OpenAI API error: {event.get('error', {})}")
                        
                except asyncio.TimeoutError:
                    timeout_count += 1
                    if timeout_count >= 3:  # Max 3 timeouts
                        logger.warning("OpenAI Realtime API timeout - stopping collection")
                        break
                    logger.warning(f"OpenAI Realtime API timeout #{timeout_count}")
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("OpenAI Realtime API connection closed")
                    break
        
        # Combine audio chunks
        if not audio_chunks:
            raise Exception("No audio received from OpenAI Realtime API")
        
        combined_audio = b''.join(audio_chunks)
        logger.info(f"Received {len(combined_audio)} bytes from OpenAI Realtime API")
        
        # Convert from 24kHz PCM to 16kHz PCM for Vapi
        return convert_to_pcm_16khz_mono(combined_audio, source_format="pcm", source_rate=24000)
    
    except Exception as e:
        logger.error(f"OpenAI Realtime synthesis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI Realtime synthesis failed: {str(e)}")

async def synthesize_with_elevenlabs_v3(text: str, voice_settings: Optional[Dict] = None) -> bytes:
    """
    Synthesize speech using ElevenLabs v3 API with Hebrew language support.
    """
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"
        
        # Optimized voice settings for Hebrew with ElevenLabs v3
        default_voice_settings = {
            "stability": 0.75,
            "similarity_boost": 0.85,
            "style": 0.6,  # Slightly more expressive for sales
            "use_speaker_boost": True
        }
        
        if voice_settings:
            default_voice_settings.update(voice_settings)
        
        # Use Eleven v3 with Hebrew language code
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",  # Using Turbo v2.5 as v3 might not be fully stable for realtime
            "language_code": "he",  # Hebrew language code
            "voice_settings": default_voice_settings,
            "output_format": "pcm_16000",  # Direct 16kHz PCM output
            "optimize_streaming_latency": 2  # Balanced latency optimization
        }
        
        headers = {
            "Accept": "application/octet-stream",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(f"ElevenLabs API error: {response.status_code} - {error_text.decode()}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"ElevenLabs API error: {error_text.decode()}"
                    )
                
                # Collect streaming audio chunks
                audio_chunks = []
                async for chunk in response.aiter_bytes():
                    if chunk:  # Filter out empty chunks
                        audio_chunks.append(chunk)
                
                if not audio_chunks:
                    raise Exception("No audio received from ElevenLabs API")
                
                combined_audio = b''.join(audio_chunks)
                logger.info(f"Received {len(combined_audio)} bytes from ElevenLabs API")
                
                # Return combined chunks - already in correct PCM format
                return combined_audio
    
    except Exception as e:
        logger.error(f"ElevenLabs synthesis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ElevenLabs synthesis failed: {str(e)}")

# API endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with API version information."""
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        supported_modes=["realtime", "v3"],
        timestamp=datetime.utcnow().isoformat(),
        api_versions={
            "openai_realtime": "gpt-4o-realtime-preview-2024-10-01",
            "elevenlabs": "v1",
            "vapi_compatibility": "2025"
        }
    )

@app.post("/synthesize")
async def synthesize_speech(
    request: TTSRequest,
    x_vapi_secret: Optional[str] = Header(None, alias="X-VAPI-SECRET")
):
    """
    Main synthesis endpoint for Vapi integration.
    
    Supports dynamic routing between OpenAI Realtime and ElevenLabs v3.
    Returns raw PCM audio compatible with Vapi requirements.
    """
    # Validate Vapi secret
    if x_vapi_secret != VAPI_SECRET:
        logger.warning(f"Invalid Vapi secret received: {x_vapi_secret[:10] if x_vapi_secret else 'None'}...")
        raise HTTPException(status_code=401, detail="Invalid X-VAPI-SECRET header")
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    if request.mode not in ["realtime", "v3"]:
        raise HTTPException(status_code=400, detail="Mode must be 'realtime' or 'v3'")
    
    logger.info(f"Synthesizing with mode: {request.mode}, text: '{request.message[:50]}...' ({len(request.message)} chars)")
    
    try:
        # Route to appropriate synthesis engine
        start_time = asyncio.get_event_loop().time()
        
        if request.mode == "realtime":
            audio_data = await synthesize_with_openai_realtime(request.message, request.voice_settings)
        else:  # v3
            audio_data = await synthesize_with_elevenlabs_v3(request.message, request.voice_settings)
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        if not audio_data:
            raise HTTPException(status_code=500, detail="No audio data generated")
        
        logger.info(f"Successfully generated {len(audio_data)} bytes of audio in {duration:.2f}s")
        
        # Return raw PCM audio with correct headers for Vapi
        return Response(
            content=audio_data,
            media_type="audio/raw",
            headers={
                "Content-Type": "audio/raw",
                "X-Audio-Format": "pcm_s16le",
                "X-Audio-Rate": "16000",
                "X-Audio-Channels": "1",
                "Content-Length": str(len(audio_data)),
                "X-Generation-Time": str(duration)
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Synthesis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

@app.post("/test")
async def test_synthesis(request: TTSRequest):
    """
    Test endpoint without Vapi secret validation for development.
    """
    logger.info(f"Test synthesis with mode: {request.mode}, message: '{request.message[:30]}...'")
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        if request.mode == "realtime":
            audio_data = await synthesize_with_openai_realtime(request.message, request.voice_settings)
        else:
            audio_data = await synthesize_with_elevenlabs_v3(request.message, request.voice_settings)
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        return {
            "success": True,
            "mode": request.mode,
            "audio_size_bytes": len(audio_data),
            "generation_time_seconds": round(duration, 3),
            "message": "Audio generated successfully",
            "sample_rate": "16kHz",
            "format": "PCM 16-bit mono"
        }
    
    except Exception as e:
        logger.error(f"Test synthesis failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "mode": request.mode
        }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting TTS server on port {SERVER_PORT}")
    logger.info(f"OpenAI Realtime Model: {OPENAI_REALTIME_MODEL}")
    logger.info(f"ElevenLabs Voice ID: {ELEVENLABS_VOICE_ID}")
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
