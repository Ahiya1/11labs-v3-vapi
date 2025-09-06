# 🌟 Vapi Assistant with Dynamic Voice Routing

A sophisticated Hebrew sales assistant powered by Vapi with dynamic voice routing between OpenAI Realtime API and ElevenLabs v3.

## 🎯 Features

- **🗣️ Hebrew Sales Agent**: Professional Hebrew-speaking sales assistant with culturally-aware communication
- **🔄 Dynamic Voice Routing**: Switch between OpenAI Realtime (low-latency) and ElevenLabs v3 (expressive) voices
- **📞 Full Vapi Integration**: Complete compatibility with Vapi Dashboard, APIs, and call management
- **🎨 Expressive Speech**: Support for natural, emotionally-aware Hebrew speech synthesis
- **📊 Call Analytics**: Full access to Vapi's call logs, recordings, and metrics
- **🔧 Easy Configuration**: Simple JSON configs for different voice modes

## 🏗️ Architecture

```
User ↔ Vapi (STT, infra) ↔ Custom TTS Server ↔ [OpenAI Realtime OR ElevenLabs v3] ↔ Audio Output
```

- **Vapi**: Handles call infrastructure, speech-to-text, conversation flow
- **Custom TTS Server**: Routes voice synthesis requests dynamically
- **OpenAI Realtime**: Low-latency speech-to-speech for real-time conversations
- **ElevenLabs v3**: High-quality, expressive multilingual TTS with Hebrew support

## 📋 Prerequisites

### API Keys Required
- **OpenAI API Key**: For Realtime API access
- **ElevenLabs API Key**: For v3 TTS access (Pro tier recommended for PCM support)
- **Vapi Private Key**: For assistant creation and management

### System Requirements
- Python 3.8+
- Public server/domain for TTS endpoint
- SSL certificate (required by Vapi)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd f-voice-assistant-vapi

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` with your API keys:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_REALTIME_MODEL=gpt-4o-realtime-preview

# ElevenLabs Configuration
ELEVENLABS_API_KEY=sk_your-key-here
ELEVENLABS_VOICE_ID=your-voice-id-here

# Vapi Configuration
VAPI_PRIVATE_KEY=your-vapi-private-key-here
VAPI_SECRET=your-custom-secret-for-tts

# Server Configuration
SERVER_PORT=8000
```

### 3. Start the TTS Server

```bash
# Option 1: Using the startup script
python start_server.py

# Option 2: Direct uvicorn
uvicorn tts_server:app --host 0.0.0.0 --port 8000
```

### 4. Test the Server

```bash
# Run comprehensive tests
python test_server.py

# Test health endpoint
curl http://localhost:8000/health
```

### 5. Deploy to Production

#### Using Railway/Render/Heroku:

1. Set environment variables in your platform
2. Deploy the code
3. Note your public URL (e.g., `https://your-app.railway.app`)

#### Using VPS/Cloud Server:

```bash
# Install dependencies
sudo apt update && sudo apt install python3 python3-pip nginx certbot

# Setup SSL with Let's Encrypt
sudo certbot --nginx -d your-domain.com

# Run with systemd or PM2
# See deployment section for full details
```

### 6. Create Vapi Assistant

#### Option A: Vapi Dashboard

1. Go to [Vapi Dashboard](https://dashboard.vapi.ai)
2. Create new assistant
3. Paste configuration from `vapi_assistant_config.json`
4. Update the `url` field with your server domain
5. Update the `X-VAPI-SECRET` header with your secret

#### Option B: API Creation

```bash
curl -X POST https://api.vapi.ai/assistant \
  -H "Authorization: Bearer YOUR_VAPI_PRIVATE_KEY" \
  -H "Content-Type: application/json" \
  -d @vapi_assistant_config.json
```

## 🎛️ Voice Mode Configuration

### ElevenLabs v3 Mode (Default)

**Best for**: Expressive, natural-sounding Hebrew speech with emotional range

```json
{
  "voice": {
    "provider": "custom-voice",
    "url": "https://your-domain.com/synthesize",
    "body": {
      "message": "{{message}}",
      "mode": "v3",
      "voice_settings": {
        "stability": 0.75,
        "similarity_boost": 0.85,
        "style": 0.6
      }
    }
  }
}
```

### OpenAI Realtime Mode

**Best for**: Ultra-low latency, real-time conversations

```json
{
  "voice": {
    "provider": "custom-voice",
    "url": "https://your-domain.com/synthesize",
    "body": {
      "message": "{{message}}",
      "mode": "realtime",
      "voice_settings": {
        "voice": "alloy",
        "speed": 1.0
      }
    }
  }
}
```

## 🔧 API Reference

### Health Check

```bash
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "supported_modes": ["realtime", "v3"],
  "timestamp": "2025-09-06T12:00:00.000Z",
  "api_versions": {
    "openai_realtime": "gpt-4o-realtime-preview-2024-10-01",
    "elevenlabs": "v1",
    "vapi_compatibility": "2025"
  }
}
```

### Synthesis Endpoint

```bash
POST /synthesize
Content-Type: application/json
X-VAPI-SECRET: your-secret-here

{
  "message": "שלום, איך אתה?",
  "mode": "v3",
  "voice_settings": {}
}
```

**Response**: Raw PCM audio (16kHz, 16-bit, mono)

### Test Endpoint

```bash
POST /test
Content-Type: application/json

{
  "message": "בדיקת מערכת",
  "mode": "realtime"
}
```

**Response**:
```json
{
  "success": true,
  "mode": "realtime",
  "audio_size_bytes": 12800,
  "generation_time_seconds": 0.85,
  "message": "Audio generated successfully",
  "sample_rate": "16kHz",
  "format": "PCM 16-bit mono"
}
```

## 🎭 Hebrew Sales Agent

The assistant embodies **דן כהן**, a professional Hebrew-speaking sales agent with:

### Characteristics
- **Native Hebrew Speaker**: Fluent, natural Hebrew communication
- **Cultural Awareness**: Understanding of Israeli business culture and mentality
- **Professional Experience**: 10+ years in B2B sales
- **Personality**: Direct but respectful, energetic but not pushy

### Communication Style
- **Directness**: Israelis appreciate straight talk
- **Efficiency**: Get to the point quickly
- **Empathy**: Understand business pain points
- **Persistence**: Don't give up after first "no"

### Sample Conversation Flow

```
🤖 שלום יוסי, דן כהן מחברת טכנולוגיה מתקדמת. 
האמת? לא התקשרתי למכור לך כלום היום.
התקשרתי כי ראיתי שאתם מתמודדים עם אתגרים בניהול הלקוחות,
ויש לי רעיון איך זה יכול לחסוך לכם זמן ולהגדיל את המכירות.
יש לך דקתיים שאני אסביר בקצרה?

👤 בסדר, אני מקשיב.

🤖 מעולה! ספר לי, איך אתם מטפלים היום בפניות לקוחות?
```

## 📊 Performance & Latency

| Mode | Latency | Quality | Best For |
|------|---------|---------|----------|
| **Realtime** | ~200ms | Good | Real-time conversations, quick responses |
| **ElevenLabs v3** | ~800ms | Excellent | Presentations, expressive content |

## 🚀 Deployment Options

### 1. Railway (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### 2. Render

1. Connect GitHub repository
2. Set environment variables
3. Deploy as Web Service

### 3. VPS Deployment

```bash
# Clone repository
git clone <repo-url> /opt/tts-server
cd /opt/tts-server

# Install Python dependencies
pip3 install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/tts-server.service > /dev/null <<EOF
[Unit]
Description=TTS Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/tts-server
Environment=PATH=/usr/bin:/usr/local/bin
EnvironmentFile=/opt/tts-server/.env
ExecStart=/usr/local/bin/uvicorn tts_server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable tts-server
sudo systemctl start tts-server

# Setup Nginx reverse proxy
sudo tee /etc/nginx/sites-available/tts-server > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/tts-server /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Setup SSL
sudo certbot --nginx -d your-domain.com
```

## 🧪 Testing Your Setup

### 1. Local Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test v3 synthesis
curl -X POST http://localhost:8000/test \
  -H "Content-Type: application/json" \
  -d '{"message": "שלום עולם", "mode": "v3"}'

# Test realtime synthesis
curl -X POST http://localhost:8000/test \
  -H "Content-Type: application/json" \
  -d '{"message": "בדיקה מהירה", "mode": "realtime"}'
```

### 2. Vapi Integration Testing

1. Create assistant in Vapi Dashboard
2. Use "Test Call" feature
3. Check call logs for any errors
4. Monitor server logs for synthesis requests

### 3. Production Monitoring

```bash
# Check service status
sudo systemctl status tts-server

# View logs
sudo journalctl -u tts-server -f

# Monitor server resources
htop
```

## 🔍 Troubleshooting

### Common Issues

#### 1. "Invalid X-VAPI-SECRET header"
- Ensure `VAPI_SECRET` in `.env` matches Vapi config
- Check header name is exactly `X-VAPI-SECRET`

#### 2. "No audio received from OpenAI Realtime API"
- Verify OpenAI API key has Realtime access
- Check internet connectivity
- Monitor OpenAI service status

#### 3. "ElevenLabs API error"
- Confirm ElevenLabs subscription supports PCM output (Pro tier+)
- Verify voice ID exists and is accessible
- Check API quota limits

#### 4. "SSL Certificate Required"
- Vapi requires HTTPS endpoints
- Use Let's Encrypt, Cloudflare, or hosting platform SSL

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python start_server.py

# Or in .env file:
LOG_LEVEL=DEBUG
```

### Log Analysis

```bash
# Check synthesis requests
grep "Synthesizing with mode" /var/log/tts-server.log

# Monitor response times
grep "Successfully generated" /var/log/tts-server.log

# Track errors
grep "ERROR" /var/log/tts-server.log
```

## 📈 Optimization Tips

### Performance
1. **Use CDN**: Deploy server close to users
2. **Enable Caching**: Cache common phrases
3. **Connection Pooling**: Reuse HTTP connections
4. **Rate Limiting**: Prevent API quota exhaustion

### Cost Optimization
1. **Smart Mode Selection**: Use Realtime for quick responses, v3 for quality
2. **Text Preprocessing**: Remove unnecessary characters before synthesis
3. **Batch Processing**: Group multiple requests when possible
4. **Monitor Usage**: Track API costs regularly

## 🔐 Security Considerations

1. **Environment Variables**: Never commit API keys to version control
2. **HTTPS Only**: Always use SSL in production
3. **Rate Limiting**: Implement request rate limiting
4. **Secret Rotation**: Regularly update VAPI_SECRET
5. **Access Logs**: Monitor for unauthorized access attempts

## 📚 Additional Resources

- [Vapi Documentation](https://docs.vapi.ai)
- [OpenAI Realtime API Docs](https://platform.openai.com/docs/guides/realtime)
- [ElevenLabs API Reference](https://elevenlabs.io/docs/api-reference)
- [Hebrew TTS Best Practices](https://elevenlabs.io/docs/speech-synthesis/prompting)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🆘 Support

For support:
1. Check the troubleshooting section above
2. Review server logs for error messages
3. Test with the provided test scripts
4. Open an issue with detailed information

---

**Happy Voice Calling! 📞🎉**

Built with ❤️ for the Hebrew-speaking community and powered by cutting-edge AI voice technology.