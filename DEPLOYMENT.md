# Deployment Guide for IMIGO API

Simple deployment guide for the IMIGO LINE Bot API with vLLM.

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

### Step 3: Verify Deployment

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
```

Test your API:

```bash
curl http://localhost:8000/health
```

## API Endpoints

Your API will be available at `http://localhost:8000`:

### Main Endpoints

- **Root**: `http://localhost:8000/`
- **Health Check**: `http://localhost:8000/health`
- **API Documentation**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

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
curl -X POST http://localhost:8000/api/translate/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_language": "id",
    "source_language": "en"
  }'
```

## LINE Bot Configuration

Update your LINE Bot webhook URL in the LINE Developers Console to point to your server:

```
http://your-server-ip:8000/webhook
```

**Note:** For production, you should use a reverse proxy (nginx, Caddy) with HTTPS.

## Troubleshooting

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

For production, consider:

1. **Reverse Proxy**: Use nginx or Caddy with HTTPS
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

2. **Firewall**: Only expose necessary ports
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

3. **Monitoring**: Add Prometheus + Grafana for metrics

4. **Backups**: Set up automated backups of `data/` directory

5. **Updates**:
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
- **API Documentation**: http://localhost:8000/api/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **vLLM Documentation**: https://docs.vllm.ai/
- **Container Status**: `docker-compose ps`
- **Logs**: `docker-compose logs`

## Features

✅ **Multi-Language Support** - Automatic language detection for 6 languages
✅ **AI-Powered Chat** - Powered by SEA-LION-7B via vLLM
✅ **LINE Bot Integration** - Ready for LINE Messaging API
✅ **Translation Service** - Built-in translation capabilities
✅ **Simple Deployment** - Just Docker Compose, no complex setup
✅ **API Documentation** - Interactive Swagger/ReDoc docs

Your IMIGO API is now ready to use at `http://localhost:8000`! 🎉
