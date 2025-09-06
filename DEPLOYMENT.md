# 🚀 Deployment Guide

Complete deployment guide for the Vapi Hebrew Assistant TTS Server.

## 📋 Pre-Deployment Checklist

- [ ] All API keys obtained and tested
- [ ] `.env` file configured with production values
- [ ] Server tested locally with `python test_server.py`
- [ ] Domain name ready (if using custom domain)
- [ ] SSL certificate plan in place

## 🌐 Deployment Options

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

In Railway dashboard:
1. Go to your project → Variables tab
2. Add all variables from your `.env` file:

```
OPENAI_API_KEY=sk-proj-your-key...
ELEVENLABS_API_KEY=sk_your-key...
ELEVENLABS_VOICE_ID=your-voice-id
VAPI_PRIVATE_KEY=your-vapi-key
VAPI_SECRET=your-custom-secret
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
curl https://your-app-name.railway.app/health
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

In Render dashboard → Environment:

```
OPENAI_API_KEY=sk-proj-your-key...
ELEVENLABS_API_KEY=sk_your-key...
ELEVENLABS_VOICE_ID=your-voice-id
VAPI_PRIVATE_KEY=your-vapi-key
VAPI_SECRET=your-custom-secret
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

# Create .env file
nano .env
# Add your environment variables here
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

Add in App Platform dashboard → Settings → Environment Variables.

#### Step 3: Deploy

App Platform will automatically build and deploy.

---

## 🔧 Post-Deployment Configuration

### 1. Update Vapi Assistant Configuration

#### Option A: Dashboard Update

1. Go to Vapi Dashboard → Assistants
2. Find your assistant or create new one
3. Update the voice configuration:

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
      "mode": "v3"
    }
  }
}
```

#### Option B: API Update

```bash
curl -X PATCH https://api.vapi.ai/assistant/YOUR_ASSISTANT_ID \
  -H "Authorization: Bearer YOUR_VAPI_PRIVATE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
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
        "mode": "v3"
      }
    }
  }'
```

### 2. Test Deployment

```bash
# Test health endpoint
curl https://YOUR-DEPLOYED-URL.com/health

# Test synthesis
curl -X POST https://YOUR-DEPLOYED-URL.com/test \
  -H "Content-Type: application/json" \
  -d '{"message": "שלום עולם", "mode": "v3"}'
```

### 3. Create Test Call

1. Go to Vapi Dashboard → Assistants
2. Click your assistant → "Test Call"
3. Speak in Hebrew and verify the assistant responds correctly

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

#### UptimeRobot Setup

1. Go to [UptimeRobot.com](https://uptimerobot.com)
2. Add new monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://YOUR-DEPLOYED-URL.com/health`
   - **Interval**: 5 minutes

### Log Management

#### For VPS Deployment

```bash
# View service logs
sudo journalctl -u tts-server -f

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

### Performance Optimization

#### 1. Enable Gzip Compression (Nginx)

```nginx
# Add to your Nginx configuration
gzip on;
gzip_types text/plain application/json;
gzip_min_length 1000;
```

#### 2. Connection Pooling

The server already uses `httpx.AsyncClient` with connection pooling.

#### 3. Rate Limiting (Nginx)

```nginx
# Add to nginx.conf http block
http {
    limit_req_zone $binary_remote_addr zone=tts:10m rate=10r/m;
    
    server {
        location /synthesize {
            limit_req zone=tts burst=5 nodelay;
            # ... rest of config
        }
    }
}
```

---

## 🔧 Troubleshooting Deployment Issues

### Common Problems

#### 1. "Port already in use"

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 PID

# Or use different port in .env
SERVER_PORT=8080
```

#### 2. "Permission denied" on VPS

```bash
# Fix ownership
sudo chown -R ttsserver:ttsserver /home/ttsserver/vapi-hebrew-assistant

# Fix permissions
chmod +x /home/ttsserver/vapi-hebrew-assistant/start_server.py
```

#### 3. "SSL Certificate Error"

```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

#### 4. "502 Bad Gateway" (Nginx)

```bash
# Check if service is running
sudo systemctl status tts-server

# Check nginx configuration
sudo nginx -t

# Check logs
sudo journalctl -u tts-server -n 50
```

### Platform-Specific Issues

#### Railway
- **Build fails**: Check Python version in requirements.txt
- **App crashes**: Check environment variables are set correctly
- **Timeout**: Increase timeout in Railway settings

#### Render
- **Free tier limitations**: 750 hours/month, spins down after 15 minutes
- **Build time**: Can be slow, upgrade for faster builds
- **Memory limits**: 512MB on free tier

#### VPS
- **Out of memory**: Add swap space or upgrade server
- **Disk space**: Clean logs regularly
- **Network issues**: Check firewall and security groups

---

## 🚀 Production Checklist

### Pre-Launch

- [ ] All environment variables configured
- [ ] SSL certificate installed and working
- [ ] Health endpoint returns 200
- [ ] Both v3 and realtime modes tested
- [ ] Hebrew text synthesis tested
- [ ] Vapi assistant configured with correct URL
- [ ] Test call completed successfully

### Security

- [ ] API keys secured and not in code
- [ ] VAPI_SECRET is unique and strong
- [ ] HTTPS enforced everywhere
- [ ] Rate limiting enabled
- [ ] Server access restricted (SSH keys, etc.)

### Monitoring

- [ ] Health monitoring setup (UptimeRobot/Pingdom)
- [ ] Log aggregation configured
- [ ] Error alerting enabled
- [ ] Performance metrics tracking

### Documentation

- [ ] Team has access to deployment credentials
- [ ] Runbook created for common issues
- [ ] Emergency contact list prepared
- [ ] Backup/restore procedures documented

---

**🎉 Congratulations! Your Hebrew Assistant is now live and ready to take calls!**

For ongoing support, monitor your logs regularly and keep your dependencies updated.