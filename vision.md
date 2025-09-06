🌟 vision.md – Build a Vapi Assistant with Dynamic Voice Routing
🎯 Mission

Create a Vapi Assistant that:

Acts as a salesperson in Hebrew (using and enhancing hebrew_instructions.md).

Can dynamically use ElevenLabs v3 (expressive, multilingual TTS) or OpenAI Realtime (low-latency speech↔speech) for voice output.

Is fully accessible via the Vapi Dashboard and Vapi API.

At the end, I should be able to:

Open Vapi Dashboard, click “Test Call,” and interact with the assistant.

Choose between Realtime and v3 voice easily (via config flag or query param).

See all calls, logs, and metrics in Vapi as usual.

🗂️ What We Already Have

.env file with:

ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...
OPENAI_API_KEY=...
OPENAI_REALTIME_MODEL=gpt-realtime
VAPI_PRIVATE_KEY=...


hebrew_instructions.md: draft instructions for the agent to behave as a Hebrew-speaking salesperson. These can be enhanced for clarity, persuasion, and naturalness.

🏗️ Architecture
User ↔ Vapi (STT, infra) ↔ Keen-built TTS Server ↔ [OpenAI Realtime OR ElevenLabs v3] ↔ Vapi ↔ User


Vapi handles call infra (SIP, WebRTC, logs, barge-in).

Keen-built server is registered as a "custom-voice" provider.

The server decides:

mode=realtime → use OpenAI Realtime.

mode=v3 → use ElevenLabs v3.

Returns PCM 16-bit mono 16kHz audio to Vapi for playback.

📑 Tasks for Keen

Research the Web

Check the latest OpenAI Realtime APIs (WebRTC, WebSocket, PCM output).

Verify ElevenLabs v3 streaming API details (input/output formats, PCM decoding).

Look at Vapi’s custom-voice documentation to confirm the exact PCM requirements.

Build the Custom TTS Server

Endpoint: POST /synthesize

Input: { "message": "text", "mode": "realtime|v3" }

Output: raw PCM audio (audio/raw, 16kHz, mono).

Auth: verify Vapi’s secret before processing.

Integrate with Vapi

Use .env variables for API keys.

Register assistant in Vapi via API using VAPI_PRIVATE_KEY.

Attach hebrew_instructions.md as the assistant’s system prompt.

Enhance Instructions

Improve hebrew_instructions.md to make the agent more persuasive, natural, and sales-oriented in Hebrew.

Ensure tone is professional, approachable, and fluent.

✅ Deliverables

Server code (FastAPI or Express) with dual routing (Realtime + Eleven v3).

Vapi assistant config JSON, ready to paste into dashboard or create via API.

Enhanced hebrew_instructions.md, optimized for sales conversations.

Documentation: how to switch between Realtime and v3, and how to test.

PAY ATTENTION - THE CURRENT YEAR IS 2025!

THE LAST AGENT STARTED THE WORK BUT DIDN'T FINISH AND COMMIT IT!