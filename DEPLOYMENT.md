# Deployment Guide for IMIGO API

Simple deployment guide for the IMIGO LINE Bot API with vLLM and ngrok tunnel for internet access.

## Prerequisites

- Docker and Docker Compose (or Podman) installed
- NVIDIA GPU with drivers installed (for vLLM)
- ngrok account (free) - Sign up at https://ngrok.com/

## Quick Start

### Step 1: Get ngrok Auth Token

1. Sign up at https://dashboard.ngrok.com/signup (free account)
2. Go to https://dashboard.ngrok.com/get-started/your-authtoken
3. Copy your authtoken

### Step 2: Set Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```bash
# Bot Configuration
DEFAULT_LANGUAGE=id

# ngrok Auth Token (required for internet access)
NGROK_AUTHTOKEN=your_ngrok_authtoken_here

# LINE Bot Credentials
LINE_CHANNEL_SECRET=your_actual_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_actual_access_token

# Google Maps API (optional)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

### Step 3: Build and Deploy

Start all services with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- **Backend** - FastAPI application (port 8000)
- **vLLM** - AI model server (port 8001)
- **ngrok** - Secure tunnel to expose your API to the internet with HTTPS

### Step 4: Get Your Public URL

Once ngrok starts, get your public HTTPS URL:

**Option 1: Check ngrok logs**
```bash
docker-compose logs ngrok
```

Look for a line like:
```
Forwarding https://abc-123-xyz.ngrok-free.app -> http://backend:8000
```

**Option 2: Visit ngrok web interface**
```
http://localhost:4040
```

The ngrok dashboard will show your public URL and all requests.

### Step 5: Verify Deployment

Check container status:

```bash
docker-compose ps
```

All services should show "Up" status.

Check logs:

```bash
# Backend logs
docker-compose logs -f backend

# vLLM logs
docker-compose logs -f vllm

# ngrok tunnel logs
docker-compose logs -f ngrok
```

Test your API locally:

```bash
curl http://localhost:8000/health
```

Test your API via internet:

```bash
curl https://your-ngrok-url.ngrok-free.app/health
```

## API Endpoints

Your API is available at two URLs:

**Locally:**
- `http://localhost:8000`

**Internet (via ngrok):**
- `https://your-ngrok-url.ngrok-free.app` (check ngrok logs or dashboard for exact URL)

### Main Endpoints

- **Root**: `https://your-ngrok-url.ngrok-free.app/`
- **Health Check**: `https://your-ngrok-url.ngrok-free.app/health`
- **API Documentation**: `https://your-ngrok-url.ngrok-free.app/api/docs`
- **ReDoc**: `https://your-ngrok-url.ngrok-free.app/api/redoc`
- **ngrok Dashboard**: `http://localhost:4040`

### API Routes

#### Chat API (with Auto Language Detection)
- **POST** `/api/chat/message` - Send a message to the bot
  - Set `language: "auto"` (default) for automatic language detection
  - Supports: Indonesian, English, Chinese, Vietnamese, Thai, Filipino
- **POST** `/api/chat/clear` - Clear conversation history
- **GET** `/api/chat/history/{user_id}` - Get conversation history

#### Translation API
- **POST** `/api/translate/` - Translate text
- **GET** `/api/translate/languages` - Get supported languages

#### System API
- **GET** `/api/system/health` - Health check
- **GET** `/api/system/info` - System information
- **GET** `/api/system/stats` - Service statistics

### LINE Webhook
- **POST** `/webhook` - LINE Bot webhook endpoint

## Example API Usage

### Chat with the Bot (Auto Language Detection)

**Via ngrok (internet):**
```bash
curl -X POST https://your-ngrok-url.ngrok-free.app/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Bagaimana cara mendapatkan visa kerja?"
  }'
```

**Local testing:**
```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Bagaimana cara mendapatkan visa kerja?"
  }'
```

The system will automatically detect that the message is in Indonesian and respond accordingly.

### Translate Text

```bash
curl -X POST https://your-ngrok-url.ngrok-free.app/api/translate/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_language": "id",
    "source_language": "en"
  }'
```

## LINE Bot Configuration

Update your LINE Bot webhook URL in the LINE Developers Console:

```
https://your-ngrok-url.ngrok-free.app/webhook
```

**Important:**
- Replace `your-ngrok-url.ngrok-free.app` with your actual ngrok URL
- Get your ngrok URL from: `docker-compose logs ngrok` or `http://localhost:4040`
- ngrok provides automatic HTTPS - no manual SSL setup needed!
- Free ngrok URLs change on restart; for persistent URLs, upgrade to ngrok paid plan

## ngrok Features

### Free Plan
- ✅ Automatic HTTPS
- ✅ Random subdomain (e.g., `abc-123.ngrok-free.app`)
- ✅ Works behind firewalls/NAT
- ✅ Web dashboard at `http://localhost:4040`
- ⚠️ URL changes on restart

### Paid Plan Benefits
- 🔒 Reserved domains (persistent URL)
- 🔒 Custom domains (your own domain)
- 🔒 More bandwidth
- 🔒 More simultaneous tunnels

### ngrok Dashboard

Visit `http://localhost:4040` to see:
- Your current public URL
- Real-time request logs
- Request/response details
- Traffic statistics

## Troubleshooting

### ngrok Not Starting

1. Check if authtoken is set correctly:
   ```bash
   cat .env | grep NGROK_AUTHTOKEN
   ```

2. Check ngrok logs:
   ```bash
   docker-compose logs ngrok
   ```

3. Verify ngrok account at https://dashboard.ngrok.com/

### Backend Not Responding

1. Check if vLLM is running:
   ```bash
   docker-compose logs vllm
   ```

2. Verify backend can connect to vLLM:
   ```bash
   docker-compose exec backend curl http://vllm:8001/v1/models
   ```

3. Check backend logs for errors:
   ```bash
   docker-compose logs backend
   ```

### vLLM Issues

1. Verify GPU is available:
   ```bash
   nvidia-smi
   ```

2. Check vLLM logs:
   ```bash
   docker-compose logs vllm
   ```

3. Ensure model files exist:
   ```bash
   ls -la models/sealion-model/
   ```

## Production Deployment

### Option 1: ngrok Paid Plan (Easiest)
- Upgrade to ngrok paid plan for reserved/custom domains
- No server configuration needed
- Automatic HTTPS, DDoS protection, load balancing
- Perfect for small-to-medium traffic

### Option 2: Traditional VPS Setup
If you have a server with public IP:

1. **Skip ngrok**: Remove ngrok service from docker-compose.yaml

2. **Reverse Proxy**: Use nginx or Caddy with HTTPS
   ```nginx
   server {
       listen 443 ssl;
       server_name api.yourdomain.com;

       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Firewall**: Only expose necessary ports
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

4. **Monitoring**: Add Prometheus + Grafana for metrics

5. **Backups**: Set up automated backups of `data/` directory

6. **Updates**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

## Stopping the Service

```bash
docker-compose down
```

To remove all data including volumes:

```bash
docker-compose down -v
```

## Support and Documentation

For more information:
- **API Documentation**: https://your-ngrok-url.ngrok-free.app/api/docs
- **ngrok Dashboard**: http://localhost:4040
- **ngrok Documentation**: https://ngrok.com/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **vLLM Documentation**: https://docs.vllm.ai/
- **Container Status**: `docker-compose ps`
- **Logs**: `docker-compose logs`

## Features

✅ **Internet Access** - Exposed via ngrok with automatic HTTPS
✅ **Multi-Language Support** - Automatic language detection for 6 languages
✅ **AI-Powered Chat** - Powered by SEA-LION-7B via vLLM
✅ **LINE Bot Integration** - Ready for LINE Messaging API
✅ **Translation Service** - Built-in translation capabilities
✅ **Simple Deployment** - Just Docker Compose + ngrok
✅ **API Documentation** - Interactive Swagger/ReDoc docs
✅ **No Firewall Config** - ngrok tunnel works anywhere
✅ **Automatic HTTPS** - Free SSL certificates via ngrok

Your IMIGO API is now accessible from anywhere at your ngrok URL! 🎉

**Get your public URL:** `docker-compose logs ngrok` or visit `http://localhost:4040`
