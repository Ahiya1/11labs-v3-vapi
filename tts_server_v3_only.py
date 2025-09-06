#!/usr/bin/env python3
"""
VAPI Custom TTS Server - ElevenLabs V3 Only Mode

A specialized version of the TTS server that ONLY supports ElevenLabs V3,
removing OpenAI Realtime to meet the specific requirements.

Author: Keen AI Agent  
Date: 2025-09-06
"""

import os
import asyncio
import json
import logging
import time
from typing import Optional, Dict, Any
from io import BytesIO

from fastapi import FastAPI, HTTPException, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from pydub import AudioSegment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_v3")
VAPI_SECRET = os.getenv("VAPI_SECRET", "your-vapi-secret-here")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# Validate required environment variables
required_vars = ["ELEVENLABS_API_KEY", "ELEVENLABS_VOICE_ID"]
for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")

# FastAPI app initialization
app = FastAPI(
    title="VAPI Custom TTS Server - ElevenLabs V3 Only",
    description="Specialized TTS server for VAPI with ElevenLabs V3 exclusively",
    version="2.0.0"
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
class VAPIMessage(BaseModel):
    type: str
    text: str
    sampleRate: int = 24000
    timestamp: Optional[int] = None
    call: Optional[Dict[str, Any]] = None
    assistant: Optional[Dict[str, Any]] = None
    customer: Optional[Dict[str, Any]] = None

class VAPIRequest(BaseModel):
    message: VAPIMessage

class HealthResponse(BaseModel):
    status: str
    version: str
    supported_modes: list
    timestamp: str
    api_versions: Dict[str, str]
    mode_restriction: str

# Audio processing utilities
def convert_to_pcm_16khz_mono(audio_data: bytes, source_format: str = "pcm", source_rate: int = 16000) -> bytes:
    """
    Convert audio data to PCM 16-bit mono 16kHz format required by VAPI.
    """
    try:
        if source_format == "pcm" and source_rate == 16000:
            # Already in the correct format
            return audio_data
            
        if source_format == "pcm":
            audio = AudioSegment(
                data=audio_data,
                sample_width=2,
                frame_rate=source_rate,
                channels=1
            )
        else:
            audio = AudioSegment.from_file(BytesIO(audio_data), format=source_format)

        if audio.channels > 1:
            audio = audio.set_channels(1)
        if audio.frame_rate != 16000:
            audio = audio.set_frame_rate(16000)
        audio = audio.set_sample_width(2)
        return audio.raw_data

    except Exception as e:
        logger.error(f"Audio conversion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audio conversion failed: {str(e)}")

async def synthesize_with_elevenlabs_v3(text: str, voice_settings: Optional[Dict] = None) -> tuple[bytes, float]:
    """
    Synthesize speech using ElevenLabs v3 API.
    Returns tuple of (audio_data, generation_time_seconds)
    """
    start_time = time.time()
    
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"

        default_voice_settings = {
            "stability": 0.75,
            "similarity_boost": 0.85,
            "style": 0.6,
            "use_speaker_boost": True
        }

        if voice_settings:
            default_voice_settings.update(voice_settings)

        # Ensure stability is valid for ElevenLabs
        stability = default_voice_settings.get("stability", 0.75)
        if stability not in [0.0, 0.25, 0.5, 0.75, 1.0]:
            logger.warning(f"Invalid stability value {stability}, defaulting to 0.75")
            default_voice_settings["stability"] = 0.75

        payload = {
            "text": text,
            "model_id": ELEVENLABS_MODEL_ID,
            "language_code": "he",
            "voice_settings": default_voice_settings,
            "output_format": "pcm_16000",
            "optimize_streaming_latency": 2
        }

        headers = {
            "Accept": "application/octet-stream",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }

        logger.info(f"Synthesizing Hebrew text with ElevenLabs V3: '{text[:50]}...'")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(f"ElevenLabs API error {response.status_code}: {error_text.decode()}")
                    raise HTTPException(status_code=response.status_code, detail=f"ElevenLabs API error: {error_text.decode()}")

                audio_chunks = [chunk async for chunk in response.aiter_bytes() if chunk]
                if not audio_chunks:
                    raise Exception("No audio received from ElevenLabs API")

                combined_audio = b''.join(audio_chunks)
                logger.info(f"Received {len(combined_audio)} bytes from ElevenLabs V3 API")
                
                generation_time = time.time() - start_time
                logger.info(f"ElevenLabs V3 synthesis completed in {generation_time:.2f}s")
                return combined_audio, generation_time

    except Exception as e:
        logger.error(f"ElevenLabs V3 synthesis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ElevenLabs V3 synthesis failed: {str(e)}")

# API endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        supported_modes=["v3"],  # Only V3 mode
        timestamp=datetime.utcnow().isoformat(),
        api_versions={
            "elevenlabs": "v1",
            "elevenlabs_model": ELEVENLABS_MODEL_ID,
            "vapi_compatibility": "2025"
        },
        mode_restriction="ElevenLabs V3 Only - OpenAI Realtime Disabled"
    )

@app.post("/synthesize")
async def synthesize_speech(
    request: VAPIRequest,
    x_vapi_secret: Optional[str] = Header(None, alias="X-VAPI-SECRET")
):
    """Main synthesis endpoint for VAPI integration - ElevenLabs V3 only"""
    
    # Validate VAPI secret
    if x_vapi_secret != VAPI_SECRET:
        logger.warning(f"Invalid VAPI secret provided: {x_vapi_secret}")
        raise HTTPException(status_code=401, detail="Invalid X-VAPI-SECRET header")

    # Validate message type
    if request.message.type != "voice-request":
        raise HTTPException(status_code=400, detail="Invalid message type. Expected 'voice-request'")

    if not request.message.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    logger.info(f"VAPI synthesis request - Text: '{request.message.text[:100]}...'")
    logger.info(f"Sample rate: {request.message.sampleRate}")
    if request.message.call:
        logger.info(f"Call ID: {request.message.call.get('id')}")

    try:
        # Always use ElevenLabs V3 - no mode selection
        audio_data, generation_time = await synthesize_with_elevenlabs_v3(request.message.text, None)

        logger.info(f"Returning {len(audio_data)} bytes of PCM audio to VAPI")
        
        return Response(
            content=audio_data,
            media_type="application/octet-stream",
            headers={
                "Content-Type": "application/octet-stream",
                "X-Audio-Format": "pcm_s16le",
                "X-Audio-Rate": "16000",
                "X-Audio-Channels": "1",
                "X-Generation-Time": str(round(generation_time, 3)),
                "X-Voice-Provider": "elevenlabs_v3",
                "Content-Length": str(len(audio_data))
            }
        )

    except Exception as e:
        logger.error(f"Synthesis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

# Legacy request model for backward compatibility
class TTSRequest(BaseModel):
    message: str
    voice_settings: Optional[Dict[str, Any]] = None
    sample_rate: int = 16000

@app.post("/test")
async def test_synthesis(request: TTSRequest):
    """Test endpoint for development - ElevenLabs V3 only"""
    try:
        audio_data, generation_time = await synthesize_with_elevenlabs_v3(request.message, request.voice_settings)

        return {
            "success": True,
            "mode": "v3",  # Always V3
            "audio_size_bytes": len(audio_data),
            "generation_time_seconds": round(generation_time, 3),
            "message": "Audio generated successfully with ElevenLabs V3",
            "sample_rate": "16kHz",
            "format": "PCM 16-bit mono",
            "voice_provider": "elevenlabs_v3",
            "model_id": ELEVENLABS_MODEL_ID,
            "voice_id": ELEVENLABS_VOICE_ID
        }

    except Exception as e:
        return {
            "success": False, 
            "error": str(e), 
            "mode": "v3",
            "generation_time_seconds": 0,
            "voice_provider": "elevenlabs_v3"
        }

@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "name": "VAPI Custom TTS Server - ElevenLabs V3 Only",
        "version": "2.0.0",
        "description": "Specialized TTS server for VAPI with ElevenLabs V3 exclusively",
        "endpoints": {
            "/health": "Health check",
            "/synthesize": "Main synthesis endpoint (VAPI)",
            "/test": "Test synthesis endpoint"
        },
        "supported_modes": ["v3"],
        "voice_provider": "elevenlabs_v3",
        "restrictions": [
            "OpenAI Realtime mode disabled",
            "ElevenLabs V3 only",
            "Hebrew language optimized",
            "VAPI integration focused"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting VAPI TTS Server - ElevenLabs V3 Only Mode")
    logger.info(f"Server restrictions: V3 mode only, no OpenAI Realtime")
    logger.info(f"Voice ID: {ELEVENLABS_VOICE_ID}")
    logger.info(f"Model ID: {ELEVENLABS_MODEL_ID}")
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
