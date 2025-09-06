# 🚂 Railway Deployment Guide

This guide will help you deploy your Vapi Hebrew Assistant TTS Server to Railway.

## 📋 Prerequisites

- Railway account (sign up at [railway.app](https://railway.app))
- GitHub repository containing this code
- API keys for OpenAI, ElevenLabs, and Vapi

## 🚀 Quick Deployment Steps

### 1. Deploy from GitHub

1. Go to [Railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway will automatically detect it's a Python app and use Nixpacks

### 2. Configure Environment Variables

In your Railway project dashboard, go to the **Variables** tab and add these required environment variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
OPENAI_REALTIME_MODEL=gpt-realtime
OPENAI_REALTIME_VOICE=alloy

# ElevenLabs Configuration
ELEVENLABS_API_KEY=sk_your-actual-elevenlabs-key-here
ELEVENLABS_VOICE_ID=your-actual-voice-id-here
ELEVENLABS_MODEL_ID=eleven_v3

# Vapi Configuration
VAPI_PRIVATE_KEY=your-actual-vapi-private-key-here
VAPI_SECRET=your-strong-custom-secret-for-tts-endpoint

# Server Configuration (Optional - Railway sets PORT automatically)
SERVER_HOST=0.0.0.0
ENVIRONMENT=production
```

### 3. Deployment Configuration Files

The following files have been created to ensure proper Railway deployment:

- **`Procfile`**: Defines the start command for the web service
- **`railway.toml`**: Railway-specific configuration
- **`runtime.txt`**: Specifies Python version
- **`.env.example`**: Template for environment variables

### 4. Verify Deployment

Once deployed, Railway will provide you with a URL like:
`https://your-project-name.up.railway.app`

**Test your deployment:**

```bash
# Test health endpoint
curl https://your-project-name.up.railway.app/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.2",
  "supported_modes": ["realtime", "v3"],
  "timestamp": "2025-09-06T...",
  "api_versions": {
    "openai_realtime": "gpt-realtime",
    "elevenlabs": "v1",
    "elevenlabs_model": "eleven_v3",
    "vapi_compatibility": "2025"
  }
}
```

## 🔧 Configuration Details

### Procfile
```
web: uvicorn tts_server:app --host 0.0.0.0 --port $PORT
```

This tells Railway to:
- Run the web service using uvicorn
- Load the FastAPI app from `tts_server.py`
- Bind to all interfaces (0.0.0.0)
- Use Railway's automatically assigned PORT

### railway.toml
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn tts_server:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[environments.production]
OPENAI_REALTIME_MODEL = "gpt-realtime"
OPENAI_REALTIME_VOICE = "alloy"
ELEVENLABS_MODEL_ID = "eleven_v3"
SERVER_HOST = "0.0.0.0"
ENVIRONMENT = "production"
```

This provides:
- Explicit builder specification
- Start command definition
- Restart policy for reliability
- Production environment defaults

## 🎯 Update Vapi Assistant Configuration

Once deployed, update your Vapi assistant configuration:

### For ElevenLabs v3 (High Quality)
```json
{
  "voice": {
    "provider": "custom-voice",
    "url": "https://your-project-name.up.railway.app/synthesize",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-VAPI-SECRET": "your-vapi-secret-from-env-vars"
    },
    "body": {
      "message": "{{message}}",
      "mode": "v3",
      "voice_settings": {
        "style": 0.6,
        "stability": 0.75,
        "similarity_boost": 0.85,
        "use_speaker_boost": true
      }
    }
  }
}
```

### For OpenAI Realtime (Low Latency)
```json
{
  "voice": {
    "provider": "custom-voice",
    "url": "https://your-project-name.up.railway.app/synthesize",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-VAPI-SECRET": "your-vapi-secret-from-env-vars"
    },
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

## 🧪 Testing Your Deployment

### Health Check
```bash
curl https://your-project-name.up.railway.app/health
```

### Test ElevenLabs v3 Mode
```bash
curl -X POST https://your-project-name.up.railway.app/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "שלום עולם, זה מבחן של המערכת",
    "mode": "v3",
    "voice_settings": {
      "style": 0.6,
      "stability": 0.75
    }
  }'
```

### Test OpenAI Realtime Mode
```bash
curl -X POST https://your-project-name.up.railway.app/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "בדיקה מהירה של המערכת",
    "mode": "realtime",
    "voice_settings": {
      "voice": "alloy"
    }
  }'
```

### Expected Test Response
```json
{
  "success": true,
  "mode": "v3",
  "audio_size_bytes": 12800,
  "generation_time_seconds": 0.85,
  "message": "Audio generated successfully",
  "sample_rate": "16kHz",
  "format": "PCM 16-bit mono"
}
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Build Failed
- Check that all required files are committed to Git
- Verify `requirements.txt` is present and contains all dependencies
- Check Railway build logs for specific errors

#### 2. App Won't Start
- Verify `Procfile` is present and correctly formatted
- Check that environment variables are set in Railway dashboard
- Review deployment logs in Railway dashboard

#### 3. Health Check Fails
- Ensure your Railway URL is accessible
- Check that the `/health` endpoint returns 200
- Verify all required environment variables are configured

#### 4. Voice Synthesis Errors
- Verify API keys are correctly set in Railway environment variables
- Check that your OpenAI key has Realtime API access
- Ensure ElevenLabs subscription supports the required features

### Viewing Logs

1. Go to your Railway project dashboard
2. Click on your service
3. Go to the **"Deployments"** tab
4. Click on the latest deployment
5. View the **"Build"** and **"Deploy"** logs

### Environment Variables Checklist

Make sure ALL these variables are set in Railway:

- [ ] `OPENAI_API_KEY` (starts with sk-proj- or sk-)
- [ ] `OPENAI_REALTIME_MODEL` (should be "gpt-realtime")
- [ ] `OPENAI_REALTIME_VOICE` (should be "alloy" or other valid voice)
- [ ] `ELEVENLABS_API_KEY` (starts with sk_)
- [ ] `ELEVENLABS_VOICE_ID` (your specific voice ID)
- [ ] `ELEVENLABS_MODEL_ID` (should be "eleven_v3")
- [ ] `VAPI_PRIVATE_KEY` (your Vapi private key)
- [ ] `VAPI_SECRET` (strong custom secret, min 20 characters)

## 📊 Monitoring

### Railway Metrics
Railway provides built-in monitoring:
- CPU usage
- Memory usage
- Network traffic
- Response times

### External Monitoring
You can also set up external monitoring:
- **UptimeRobot**: Monitor `/health` endpoint
- **Pingdom**: Website monitoring
- **New Relic**: Application performance monitoring

### Setting up UptimeRobot
1. Go to [UptimeRobot.com](https://uptimerobot.com)
2. Create a new monitor
3. Monitor type: HTTP(s)
4. URL: `https://your-project-name.up.railway.app/health`
5. Monitoring interval: 5 minutes
6. Add alert contacts (email/SMS)

## 💡 Pro Tips

1. **Use Railway CLI for easier deployments**:
   ```bash
   npm install -g @railway/cli
   railway login
   railway link
   railway up
   ```

2. **Enable auto-deployments**:
   Railway can automatically deploy when you push to your main branch

3. **Monitor costs**:
   Railway charges based on usage. Monitor your monthly costs in the dashboard

4. **Use custom domains**:
   You can add your own domain in Railway project settings

5. **Scale as needed**:
   Railway automatically scales based on traffic

## 🎉 You're Ready!

Your Vapi Hebrew Assistant TTS Server is now deployed on Railway!

**Next steps:**
1. Test all endpoints
2. Update your Vapi assistant configuration
3. Set up monitoring
4. Test with actual phone calls
5. Monitor performance and costs

**Support:**
- Railway documentation: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [railway.app/discord](https://railway.app/discord)
- Project documentation: See README.md and DEPLOYMENT.md

---

**Happy deploying! 🚂✨**