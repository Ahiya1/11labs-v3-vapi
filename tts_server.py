#!/usr/bin/env python3
"""
Vapi Custom TTS Server with Dynamic Voice Routing

Supports both OpenAI Realtime API and ElevenLabs v3 for dynamic voice synthesis.
Returns PCM 16-bit mono 16kHz audio compatible with Vapi requirements.

Author: Keen AI Agent
Date: 2025-09-06
Updated: Fixed OpenAI Realtime API modalities and added timing metrics
"""

import os
import asyncio
import base64
import json
import logging
import time
from typing import Optional, Dict, Any
from io import BytesIO

import numpy as np
from fastapi import FastAPI, HTTPException, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import websockets
from pydub import AudioSegment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_REALTIME_MODEL = os.getenv("OPENAI_REALTIME_MODEL", "gpt-realtime")
OPENAI_REALTIME_VOICE = os.getenv("OPENAI_REALTIME_VOICE", "alloy")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_v3")
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
    version="1.0.2"
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

async def synthesize_with_openai_realtime(text: str, voice_settings: Optional[Dict] = None) -> tuple[bytes, float]:
    """
    Synthesize speech using OpenAI Realtime API.
    Returns tuple of (audio_data, generation_time_seconds)
    """
    start_time = time.time()
    
    try:
        uri = f"wss://api.openai.com/v1/realtime?model={OPENAI_REALTIME_MODEL}"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }

        audio_chunks = []
        # FIX: use list of tuples for extra_headers
        async with websockets.connect(uri, extra_headers=list(headers.items())) as websocket:
            voice_to_use = voice_settings.get("voice", OPENAI_REALTIME_VOICE) if voice_settings else OPENAI_REALTIME_VOICE

            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],  # FIXED: Include both text and audio modalities
                    "instructions": f"You are a Hebrew-speaking sales assistant. Please convert the following Hebrew text to natural Hebrew speech: {text}",
                    "voice": voice_to_use,
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
            _ = await websocket.recv()  # consume confirmation

            text_input = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": text}]
                }
            }
            await websocket.send(json.dumps(text_input))

            # FIXED: Include both text and audio modalities in response
            response_create = {
                "type": "response.create", 
                "response": {
                    "modalities": ["text", "audio"]
                }
            }
            await websocket.send(json.dumps(response_create))

            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    event = json.loads(message)

                    if event.get("type") == "response.audio.delta":
                        audio_data = base64.b64decode(event["delta"])
                        audio_chunks.append(audio_data)

                    elif event.get("type") == "response.audio.done":
                        logger.info("OpenAI Realtime audio generation completed")
                        break

                    elif event.get("type") == "error":
                        raise Exception(f"OpenAI API error: {event.get('error', {})}")

                except asyncio.TimeoutError:
                    logger.warning("OpenAI Realtime API timeout")
                    break
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("OpenAI Realtime API connection closed")
                    break

        if not audio_chunks:
            raise Exception("No audio received from OpenAI Realtime API")

        combined_audio = b''.join(audio_chunks)
        logger.info(f"Received {len(combined_audio)} bytes from OpenAI Realtime API")
        
        processed_audio = convert_to_pcm_16khz_mono(combined_audio, source_format="pcm", source_rate=24000)
        generation_time = time.time() - start_time
        
        return processed_audio, generation_time

    except Exception as e:
        logger.error(f"OpenAI Realtime synthesis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI Realtime synthesis failed: {str(e)}")

async def synthesize_with_elevenlabs_v3(text: str, voice_settings: Optional[Dict] = None) -> tuple[bytes, float]:
    """
    Synthesize speech using ElevenLabs v3 API.
    Returns tuple of (audio_data, generation_time_seconds)
    """
    start_time = time.time()
    
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"

        default_voice_settings = {
            "stability": 0.5,  # FIXED: must be one of 0.0, 0.5, 1.0
            "similarity_boost": 0.85,
            "style": 0.6,
            "use_speaker_boost": True
        }

        if voice_settings:
            default_voice_settings.update(voice_settings)

        # Ensure stability is valid
        if default_voice_settings.get("stability") not in [0.0, 0.5, 1.0]:
            logger.warning(f"Invalid stability value {default_voice_settings['stability']}, defaulting to 0.5")
            default_voice_settings["stability"] = 0.5

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

        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise HTTPException(status_code=response.status_code, detail=f"ElevenLabs API error: {error_text.decode()}")

                audio_chunks = [chunk async for chunk in response.aiter_bytes() if chunk]
                if not audio_chunks:
                    raise Exception("No audio received from ElevenLabs API")

                combined_audio = b''.join(audio_chunks)
                logger.info(f"Received {len(combined_audio)} bytes from ElevenLabs API")
                
                generation_time = time.time() - start_time
                return combined_audio, generation_time

    except Exception as e:
        logger.error(f"ElevenLabs synthesis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ElevenLabs synthesis failed: {str(e)}")

# API endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        version="1.0.2",
        supported_modes=["realtime", "v3"],
        timestamp=datetime.utcnow().isoformat(),
        api_versions={
            "openai_realtime": OPENAI_REALTIME_MODEL,
            "elevenlabs": "v1",
            "elevenlabs_model": ELEVENLABS_MODEL_ID,
            "vapi_compatibility": "2025"
        }
    )

@app.post("/synthesize")
async def synthesize_speech(
    request: TTSRequest,
    x_vapi_secret: Optional[str] = Header(None, alias="X-VAPI-SECRET")
):
    if x_vapi_secret != VAPI_SECRET:
        raise HTTPException(status_code=401, detail="Invalid X-VAPI-SECRET header")

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if request.mode not in ["realtime", "v3"]:
        raise HTTPException(status_code=400, detail="Mode must be 'realtime' or 'v3'")

    try:
        if request.mode == "realtime":
            audio_data, _ = await synthesize_with_openai_realtime(request.message, request.voice_settings)
        else:
            audio_data, _ = await synthesize_with_elevenlabs_v3(request.message, request.voice_settings)

        return Response(
            content=audio_data,
            media_type="audio/raw",
            headers={
                "Content-Type": "audio/raw",
                "X-Audio-Format": "pcm_s16le",
                "X-Audio-Rate": "16000",
                "X-Audio-Channels": "1",
                "Content-Length": str(len(audio_data))
            }
        )

    except Exception as e:
        logger.error(f"Synthesis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

@app.post("/test")
async def test_synthesis(request: TTSRequest):
    try:
        if request.mode == "realtime":
            audio_data, generation_time = await synthesize_with_openai_realtime(request.message, request.voice_settings)
        else:
            audio_data, generation_time = await synthesize_with_elevenlabs_v3(request.message, request.voice_settings)

        return {
            "success": True,
            "mode": request.mode,
            "audio_size_bytes": len(audio_data),
            "generation_time_seconds": round(generation_time, 3),  # FIXED: Added missing field
            "message": "Audio generated successfully",
            "sample_rate": "16kHz",
            "format": "PCM 16-bit mono"
        }

    except Exception as e:
        return {
            "success": False, 
            "error": str(e), 
            "mode": request.mode,
            "generation_time_seconds": 0
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
