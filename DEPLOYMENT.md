# Deployment Guide for IMIGO API

Simple deployment guide for the IMIGO LINE Bot API with vLLM and Bore tunnel for internet access.

## Prerequisites

- Docker and Docker Compose (or Podman) installed
- NVIDIA GPU with drivers installed (for vLLM)

## Quick Start

### Step 1: Set Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```bash
# Bot Configuration
DEFAULT_LANGUAGE=id

# LINE Bot Credentials
LINE_CHANNEL_SECRET=your_actual_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_actual_access_token

# Google Maps API (optional)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

### Step 2: Build and Deploy

Start all services with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- **Backend** - FastAPI application (port 8000)
- **vLLM** - AI model server (port 8001)
- **Bore** - Free tunnel to expose your API to the internet

### Step 3: Get Your Public URL

Check the Bore logs to find your public URL:

```bash
docker-compose logs bore
```

Look for a line like:
```
listening at bore.pub:xxxxx
```

Your API will be accessible at: `http://bore.pub:xxxxx`

**Note:** Bore uses HTTP (not HTTPS) by default. The port number changes on restart.

### Step 4: Verify Deployment

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

# Bore tunnel logs
docker-compose logs -f bore
```

Test your API locally:

```bash
curl http://localhost:8000/health
```

Test your API via internet:

```bash
# Replace xxxxx with your actual port from bore logs
curl http://bore.pub:xxxxx/health
```

## API Endpoints

Your API is available at two URLs:

**Locally:**
- `http://localhost:8000`

**Internet (via Bore):**
- `http://bore.pub:xxxxx` (check bore logs for exact port)

### Main Endpoints

- **Root**: `http://bore.pub:xxxxx/`
- **Health Check**: `http://bore.pub:xxxxx/health`
- **API Documentation**: `http://bore.pub:xxxxx/api/docs`
- **ReDoc**: `http://bore.pub:xxxxx/api/redoc`

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

**Via Bore (internet):**
```bash
curl -X POST http://bore.pub:xxxxx/api/chat/message \
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
curl -X POST http://bore.pub:xxxxx/api/translate/ \
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
http://bore.pub:xxxxx/webhook
```

**Important:**
- Replace `xxxxx` with your actual port from bore logs
- Get your port from: `docker-compose logs bore`
- Bore uses HTTP (not HTTPS)
- Port changes on restart (not persistent)

## Bore Features

### Characteristics
- ✅ Completely free
- ✅ No signup required
- ✅ Open source (Rust)
- ✅ Works behind firewalls/NAT
- ✅ Very lightweight and fast
- ⚠️ HTTP only (no automatic HTTPS)
- ⚠️ Port changes on restart
- ⚠️ Community-run bore.pub server

### Limitations
- No HTTPS (uses HTTP)
- Random port assignment
- Port changes every restart
- No web dashboard
- Less reliable than paid services

## Troubleshooting

### Bore Not Starting

1. Check bore logs:
   ```bash
   docker-compose logs bore
   ```

2. Verify backend is running:
   ```bash
   docker-compose ps backend
   ```

3. Restart bore:
   ```bash
   docker-compose restart bore
   ```

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

### LINE Webhook Issues

1. Ensure the webhook URL in LINE console matches your bore URL
2. Check that the `/webhook` endpoint is accessible:
   ```bash
   curl http://bore.pub:xxxxx/webhook
   ```

3. Verify the port from bore logs is correct

## Production Considerations

**Important:** Bore is best for development/testing. For production:

### Option 1: Get a VPS with Public IP
- Use nginx or Caddy with your domain
- Full HTTPS support
- Persistent URL
- More reliable

### Option 2: Paid Tunnel Service
- ngrok paid plan ($8/month)
- Persistent URLs and custom domains
- HTTPS included
- Better reliability

### Why Bore is Not Ideal for Production:
- ❌ HTTP only (no HTTPS) - security concern
- ❌ Port changes on restart - breaks LINE webhooks
- ❌ Community server (bore.pub) - no SLA
- ❌ No persistent URLs

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
- **API Documentation**: http://bore.pub:xxxxx/api/docs (replace xxxxx with your port)
- **Bore GitHub**: https://github.com/ekzhang/bore
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **vLLM Documentation**: https://docs.vllm.ai/
- **Container Status**: `docker-compose ps`
- **Logs**: `docker-compose logs`

## Features

✅ **Internet Access** - Exposed via Bore tunnel (free)
✅ **Multi-Language Support** - Automatic language detection for 6 languages
✅ **AI-Powered Chat** - Powered by SEA-LION-7B via vLLM
✅ **LINE Bot Integration** - Ready for LINE Messaging API
✅ **Translation Service** - Built-in translation capabilities
✅ **Simple Deployment** - Just Docker Compose + Bore
✅ **No Signup Required** - Bore is completely free and anonymous
✅ **No Firewall Config** - Bore tunnel works anywhere

Your IMIGO API is now accessible from anywhere via Bore! 🎉

**Get your public URL:** `docker-compose logs bore` and look for the port number
