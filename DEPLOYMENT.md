# 🚀 Deployment Guide

Complete deployment guide for the Vapi Hebrew Assistant TTS Server with enhanced configuration.

## 📋 Pre-Deployment Checklist

- [ ] All API keys obtained and tested
- [ ] `.env` file configured with production values
- [ ] **NEW**: Model configuration variables set
- [ ] Server tested locally with `python test_server.py`
- [ ] Domain name ready (if using custom domain)
- [ ] SSL certificate plan in place

## 🌍 Deployment Options

### Option 1: Railway (Recommended for beginners)

#### Step 1: Prepare Repository

```bash
# Ensure all files are committed
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### Step 2: Deploy to Railway

1. Go to [Railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect it's a Python app

#### Step 3: Set Environment Variables

In Railway dashboard → Variables tab, add **ALL** these variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-key...
OPENAI_REALTIME_MODEL=gpt-realtime
OPENAI_REALTIME_VOICE=alloy

# ElevenLabs Configuration  
ELEVENLABS_API_KEY=sk_your-key...
ELEVENLABS_VOICE_ID=your-voice-id
ELEVENLABS_MODEL_ID=eleven_v3

# Vapi Configuration
VAPI_PRIVATE_KEY=your-vapi-key
VAPI_SECRET=your-custom-secret

# Server Configuration
SERVER_PORT=8000
```

#### Step 4: Configure Start Command

In Railway dashboard → Settings:
- **Start Command**: `uvicorn tts_server:app --host 0.0.0.0 --port $PORT`
- **Build Command**: `pip install -r requirements.txt`

#### Step 5: Get Your URL

1. Railway will provide a URL like: `https://your-app-name.railway.app`
2. Test your deployment:

```bash
# Test health check
curl https://your-app-name.railway.app/health

# Test v3 mode
curl -X POST https://your-app-name.railway.app/test \
  -H "Content-Type: application/json" \
  -d '{"message": "שלום עולם", "mode": "v3"}'
```

---

### Option 2: Render (Great free tier)

#### Step 1: Create Render Account

1. Go to [Render.com](https://render.com)
2. Sign up with GitHub

#### Step 2: Create Web Service

1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `vapi-hebrew-tts`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn tts_server:app --host 0.0.0.0 --port $PORT`

#### Step 3: Environment Variables

In Render dashboard → Environment, add **ALL** these variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-key...
OPENAI_REALTIME_MODEL=gpt-realtime
OPENAI_REALTIME_VOICE=alloy

# ElevenLabs Configuration
ELEVENLABS_API_KEY=sk_your-key...
ELEVENLABS_VOICE_ID=your-voice-id
ELEVENLABS_MODEL_ID=eleven_v3

# Vapi Configuration
VAPI_PRIVATE_KEY=your-vapi-key
VAPI_SECRET=your-custom-secret

# Server Configuration
PORT=10000
```

#### Step 4: Deploy

1. Click "Create Web Service"
2. Render will build and deploy automatically
3. Get your URL: `https://your-service-name.onrender.com`

---

### Option 3: VPS/Cloud Server (Advanced)

#### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx -y

# Create user for the application
sudo useradd -m -s /bin/bash ttsserver
sudo usermod -aG sudo ttsserver
```

#### Step 2: Deploy Application

```bash
# Switch to application user
sudo su - ttsserver

# Clone repository
git clone https://github.com/your-username/vapi-hebrew-assistant.git
cd vapi-hebrew-assistant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with ALL required variables
nano .env
```

**Complete .env template for production:**

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-actual-key
OPENAI_REALTIME_MODEL=gpt-realtime
OPENAI_REALTIME_VOICE=alloy

# ElevenLabs Configuration
ELEVENLABS_API_KEY=sk_your-actual-key
ELEVENLABS_VOICE_ID=your-actual-voice-id
ELEVENLABS_MODEL_ID=eleven_v3

# Vapi Configuration
VAPI_PRIVATE_KEY=your-actual-vapi-key
VAPI_SECRET=your-strong-custom-secret-here

# Server Configuration
SERVER_PORT=8000
SERVER_HOST=127.0.0.1

# Environment
ENVIRONMENT=production
```

#### Step 3: Create Systemd Service

```bash
# Exit from ttsserver user
exit

# Create systemd service file
sudo tee /etc/systemd/system/tts-server.service > /dev/null <<EOF
[Unit]
Description=Vapi Hebrew TTS Server
After=network.target

[Service]
Type=simple
User=ttsserver
Group=ttsserver
WorkingDirectory=/home/ttsserver/vapi-hebrew-assistant
Environment=PATH=/home/ttsserver/vapi-hebrew-assistant/venv/bin
EnvironmentFile=/home/ttsserver/vapi-hebrew-assistant/.env
ExecStart=/home/ttsserver/vapi-hebrew-assistant/venv/bin/uvicorn tts_server:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable tts-server
sudo systemctl start tts-server

# Check status
sudo systemctl status tts-server
```

#### Step 4: Configure Nginx

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/tts-server > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Important for large audio responses
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
        client_max_body_size 10M;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/tts-server /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### Step 5: Setup SSL Certificate

```bash
# Get SSL certificate from Let's Encrypt
sudo certbot --nginx -d your-domain.com

# Certbot will automatically update Nginx config for HTTPS

# Test automatic renewal
sudo certbot renew --dry-run
```

#### Step 6: Configure Firewall

```bash
# Enable UFW
sudo ufw enable

# Allow necessary ports
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Check status
sudo ufw status
```

---

### Option 4: DigitalOcean App Platform

#### Step 1: Create App

1. Go to DigitalOcean → Apps
2. Create App → Connect GitHub repository
3. Configure:
   - **Type**: Web Service
   - **Source Directory**: `/`
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `uvicorn tts_server:app --host 0.0.0.0 --port $PORT`

#### Step 2: Environment Variables

Add **ALL** these environment variables in App Platform dashboard:

```bash
OPENAI_API_KEY=sk-proj-your-key...
OPENAI_REALTIME_MODEL=gpt-realtime
OPENAI_REALTIME_VOICE=alloy
ELEVENLABS_API_KEY=sk_your-key...
ELEVENLABS_VOICE_ID=your-voice-id
ELEVENLABS_MODEL_ID=eleven_v3
VAPI_PRIVATE_KEY=your-vapi-key
VAPI_SECRET=your-custom-secret
```

#### Step 3: Deploy

App Platform will automatically build and deploy.

---

## 🔧 Post-Deployment Configuration

### 1. Update Vapi Assistant Configuration

#### Option A: Dashboard Update

1. Go to Vapi Dashboard → Assistants
2. Find your assistant or create new one
3. **For ElevenLabs v3 Mode (Expressive Quality)**:

```json
{
  "voice": {
    "provider": "custom-voice",
    "url": "https://YOUR-DEPLOYED-URL.com/synthesize",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-VAPI-SECRET": "your-vapi-secret-here"
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

4. **For OpenAI Realtime Mode (Low-Latency)**:

```json
{
  "voice": {
    "provider": "custom-voice",
    "url": "https://YOUR-DEPLOYED-URL.com/synthesize",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-VAPI-SECRET": "your-vapi-secret-here"
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

#### Option B: API Update

```bash
curl -X PATCH https://api.vapi.ai/assistant/YOUR_ASSISTANT_ID \
  -H "Authorization: Bearer YOUR_VAPI_PRIVATE_KEY" \
  -H "Content-Type: application/json" \
  -d @vapi_assistant_config.json
```

### 2. Test Deployment

```bash
# Test health endpoint
curl https://YOUR-DEPLOYED-URL.com/health

# Test both modes
curl -X POST https://YOUR-DEPLOYED-URL.com/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "שלום עולם", 
    "mode": "v3",
    "voice_settings": {"style": 0.6}
  }'

curl -X POST https://YOUR-DEPLOYED-URL.com/test \
  -H "Content-Type: application/json" \
  -d '{
    "message": "בדיקה מהירה", 
    "mode": "realtime",
    "voice_settings": {"voice": "alloy"}
  }'
```

### 3. Create Test Call

1. Go to Vapi Dashboard → Assistants
2. Click your assistant → "Test Call"
3. Speak in Hebrew and verify the assistant responds correctly
4. Test both voice modes if you have multiple assistants

---

## 📊 Monitoring & Maintenance

### Health Monitoring

#### Simple HTTP Monitoring

```bash
# Create monitoring script
tee monitor.sh > /dev/null <<EOF
#!/bin/bash
URL="https://YOUR-DEPLOYED-URL.com/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $URL)

if [ $RESPONSE -eq 200 ]; then
    echo "$(date): Server is healthy"
    # Check if response contains expected content
    HEALTH=$(curl -s $URL | jq -r '.status')
    if [ "$HEALTH" = "healthy" ]; then
        echo "$(date): Health check passed with status: healthy"
    else
        echo "$(date): Health check returned unexpected status: $HEALTH"
    fi
else
    echo "$(date): Server is down! Response: $RESPONSE"
    # Add notification logic here (email, Slack, etc.)
fi
EOF

chmod +x monitor.sh

# Add to crontab (check every 5 minutes)
crontab -e
# Add line: */5 * * * * /path/to/monitor.sh >> /var/log/tts-monitor.log 2>&1
```

#### Advanced Monitoring with Voice Mode Testing

```bash
# Create comprehensive test script
tee health_check.sh > /dev/null <<EOF
#!/bin/bash
SERVER_URL="https://YOUR-DEPLOYED-URL.com"
TEST_MESSAGE="בדיקת מערכת"

echo "$(date): Testing server health..."

# Test health endpoint
HEALTH_STATUS=$(curl -s "$SERVER_URL/health" | jq -r '.status')
if [ "$HEALTH_STATUS" != "healthy" ]; then
    echo "$(date): ERROR - Health check failed"
    exit 1
fi

# Test v3 mode
V3_TEST=$(curl -s -X POST "$SERVER_URL/test" \
  -H "Content-Type: application/json" \
  -d '{"message": "'$TEST_MESSAGE'", "mode": "v3"}' | jq -r '.success')

if [ "$V3_TEST" != "true" ]; then
    echo "$(date): ERROR - v3 mode test failed"
    exit 1
fi

# Test realtime mode
RT_TEST=$(curl -s -X POST "$SERVER_URL/test" \
  -H "Content-Type: application/json" \
  -d '{"message": "'$TEST_MESSAGE'", "mode": "realtime"}' | jq -r '.success')

if [ "$RT_TEST" != "true" ]; then
    echo "$(date): ERROR - realtime mode test failed"
    exit 1
fi

echo "$(date): All tests passed successfully"
EOF

chmod +x health_check.sh
```

#### UptimeRobot Setup

1. Go to [UptimeRobot.com](https://uptimerobot.com)
2. Add new monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://YOUR-DEPLOYED-URL.com/health`
   - **Interval**: 5 minutes
   - **Alert Contacts**: Add your email/SMS

### Log Management

#### For VPS Deployment

```bash
# View service logs
sudo journalctl -u tts-server -f

# View recent logs
sudo journalctl -u tts-server -n 100

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Setup log rotation
sudo tee /etc/logrotate.d/tts-server > /dev/null <<EOF
/var/log/tts-server/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        systemctl reload tts-server
    endscript
}
EOF
```

#### For Platform Deployments

- **Railway**: Check logs in dashboard → Deployments tab
- **Render**: Check logs in dashboard → Logs tab
- **Heroku**: Use `heroku logs --tail -a your-app-name`
- **DigitalOcean**: Check Runtime Logs in app dashboard

### Performance Optimization

#### 1. Enable Gzip Compression (Nginx)

```nginx
# Add to your Nginx configuration
http {
    gzip on;
    gzip_types text/plain application/json;
    gzip_min_length 1000;
    
    # Add caching for static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 2. Rate Limiting (Nginx)

```nginx
# Add to nginx.conf http block
http {
    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=tts:10m rate=10r/m;
    limit_req_zone $binary_remote_addr zone=health:10m rate=30r/m;
    
    server {
        location /synthesize {
            limit_req zone=tts burst=5 nodelay;
            # ... rest of config
        }
        
        location /health {
            limit_req zone=health burst=10 nodelay;
            # ... rest of config
        }
    }
}
```

#### 3. Environment-Specific Optimizations

```bash
# Add to .env for production
ENVIRONMENT=production
LOG_LEVEL=INFO

# Optimize for your platform
# Railway: Ensure you're on the right plan for your usage
# Render: Consider upgrading from free tier for better performance
# VPS: Monitor CPU/memory usage and scale accordingly
```

---

## 🔧 Troubleshooting Deployment Issues

### Common Problems

#### 1. "Missing environment variable" errors

```bash
# Check which variables are missing
curl https://YOUR-DEPLOYED-URL.com/health

# Verify all required variables are set:
echo "Required variables:"
echo "- OPENAI_API_KEY"
echo "- OPENAI_REALTIME_MODEL (default: gpt-realtime)"
echo "- OPENAI_REALTIME_VOICE (default: alloy)"
echo "- ELEVENLABS_API_KEY"
echo "- ELEVENLABS_VOICE_ID"
echo "- ELEVENLABS_MODEL_ID (default: eleven_v3)"
echo "- VAPI_SECRET"
```

#### 2. "Port already in use" (VPS)

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 PID

# Or use different port in .env
SERVER_PORT=8080
```

#### 3. "Permission denied" on VPS

```bash
# Fix ownership
sudo chown -R ttsserver:ttsserver /home/ttsserver/vapi-hebrew-assistant

# Fix permissions
chmod +x /home/ttsserver/vapi-hebrew-assistant/start_server.py
```

#### 4. "Model not found" errors

```bash
# Check if environment variables are properly set
# For ElevenLabs
curl -H "xi-api-key: YOUR_API_KEY" https://api.elevenlabs.io/v1/voices

# For OpenAI - verify Realtime access
curl -H "Authorization: Bearer YOUR_OPENAI_KEY" \
     https://api.openai.com/v1/models | grep realtime
```

### Platform-Specific Issues

#### Railway
- **Build fails**: Check Python version matches `runtime.txt` if present
- **Environment variables not loaded**: Ensure they're set in Railway dashboard, not just `.env`
- **Timeout errors**: Consider upgrading plan for better performance

#### Render
- **Free tier sleep**: App sleeps after 15 minutes of inactivity
- **Build time**: Can be slow on free tier, consider upgrading
- **Memory limits**: 512MB on free tier, may need upgrade for heavy usage

#### VPS
- **Firewall blocking**: Check UFW/iptables rules
- **SSL certificate issues**: Verify domain DNS is pointing correctly
- **Service crashes**: Check logs with `journalctl -u tts-server -f`

### Voice Mode Specific Issues

#### Realtime Mode Issues
```bash
# Test OpenAI Realtime access
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "OpenAI-Beta: realtime=v1" \
     "https://api.openai.com/v1/realtime?model=gpt-realtime"

# Check if your key has Realtime access
echo "If you get a 401/403 error, request Realtime API access from OpenAI"
```

#### ElevenLabs v3 Issues
```bash
# Test ElevenLabs API access
curl -H "xi-api-key: $ELEVENLABS_API_KEY" \
     "https://api.elevenlabs.io/v1/user"

# Check if voice ID exists
curl -H "xi-api-key: $ELEVENLABS_API_KEY" \
     "https://api.elevenlabs.io/v1/voices/$ELEVENLABS_VOICE_ID"
```

---

## 🚀 Production Checklist

### Pre-Launch

- [ ] All environment variables configured (including NEW model variables)
- [ ] SSL certificate installed and working
- [ ] Health endpoint returns 200 with correct API versions
- [ ] Both v3 and realtime modes tested with Hebrew content
- [ ] Voice settings optimized for Hebrew
- [ ] Vapi assistant configured with correct URL
- [ ] Test call completed successfully
- [ ] Monitoring setup (UptimeRobot/custom)

### Security

- [ ] API keys secured and not in code
- [ ] `VAPI_SECRET` is unique and strong (minimum 20 characters)
- [ ] HTTPS enforced everywhere  
- [ ] Rate limiting enabled
- [ ] Server access restricted (SSH keys, etc.)
- [ ] Firewall configured properly

### Performance

- [ ] Both voice modes tested for latency
- [ ] Voice quality compared between modes
- [ ] Rate limiting configured appropriately
- [ ] Log rotation setup
- [ ] Resource monitoring in place

### Documentation

- [ ] Team has access to deployment credentials
- [ ] Environment variable documentation updated
- [ ] Voice mode selection guide available
- [ ] Runbook created for common issues
- [ ] Emergency contact list prepared
- [ ] Backup/restore procedures documented

---

**🎉 Congratulations! Your Enhanced Hebrew Assistant is now live and ready for production!**

### 📊 Key Improvements in This Version:
- ✨ **Environment-driven configuration** - No more hardcoded values
- ✨ **Model selection flexibility** - Easy switching between ElevenLabs models
- ✨ **Voice customization** - Configurable voice settings per mode
- ✨ **Enhanced monitoring** - Better health checks and testing
- ✨ **Production-ready** - Comprehensive deployment and maintenance guide

For ongoing support, monitor your logs regularly, keep your dependencies updated, and don't forget to test both voice modes regularly to ensure optimal performance.