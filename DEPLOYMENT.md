# Deployment Guide for IMIGO API

This guide explains how to deploy the IMIGO API to your domain `imigo.tw` with automatic SSL certificates.

## Prerequisites

- Docker and Docker Compose installed
- A domain name (imigo.tw) pointing to your server's public IP
- Ports 80 and 443 open on your firewall
- NVIDIA GPU with drivers installed (for vLLM)

## DNS Configuration

Before deploying, ensure your DNS records are configured:

```
A Record:     imigo.tw       -> YOUR_SERVER_IP
A Record:     www.imigo.tw   -> YOUR_SERVER_IP
A Record:     api.imigo.tw   -> YOUR_SERVER_IP
A Record:     traefik.imigo.tw -> YOUR_SERVER_IP (optional, for Traefik dashboard)
```

## Step 1: Configure SSL Email

Edit `traefik/traefik.yml` and replace the placeholder email with your actual email for Let's Encrypt:

```yaml
certificatesResolvers:
  letsencrypt:
    acme:
      email: YOUR_EMAIL@example.com  # REPLACE with your actual email
```

## Step 2: Set Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```bash
# LINE Bot Credentials
LINE_CHANNEL_SECRET=your_actual_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_actual_access_token

# Google Maps API (optional)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

## Step 3: Prepare SSL Storage

Create the directory for Let's Encrypt certificates:

```bash
mkdir -p letsencrypt
chmod 600 letsencrypt
```

## Step 4: Build and Deploy

Start the services with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- **Traefik** - Reverse proxy with automatic SSL
- **Backend** - FastAPI application
- **vLLM** - AI model server

## Step 5: Verify Deployment

### Check Container Status

```bash
docker-compose ps
```

All services should be "Up".

### Check Logs

```bash
# Backend logs
docker-compose logs -f backend

# Traefik logs
docker-compose logs -f traefik

# vLLM logs
docker-compose logs -f vllm
```

### Test SSL Certificate

Wait 1-2 minutes for Let's Encrypt to issue certificates, then visit:

```
https://imigo.tw/
https://api.imigo.tw/
```

You should see a valid SSL certificate.

## API Endpoints

Once deployed, your API will be available at:

### Main Endpoints

- **Root**: `https://imigo.tw/`
- **Health Check**: `https://imigo.tw/health`
- **API Documentation**: `https://imigo.tw/api/docs`
- **ReDoc**: `https://imigo.tw/api/redoc`

### API Routes

#### Chat API
- **POST** `/api/chat/message` - Send a message to the bot
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

### Chat with the Bot

```bash
curl -X POST https://imigo.tw/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Bagaimana cara mendapatkan visa kerja?",
    "language": "id"
  }'
```

### Translate Text

```bash
curl -X POST https://imigo.tw/api/translate/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_language": "id",
    "source_language": "en"
  }'
```

## Traefik Dashboard (Optional)

Access the Traefik dashboard at:

```
https://traefik.imigo.tw:8080/dashboard/
```

**Security Note**: In production, enable basic authentication for the dashboard by uncommenting and configuring the auth middleware in `docker-compose.yaml`.

## Troubleshooting

### SSL Certificate Not Working

1. Verify DNS is pointing to your server:
   ```bash
   dig imigo.tw
   ```

2. Check Traefik logs:
   ```bash
   docker-compose logs traefik
   ```

3. Ensure ports 80 and 443 are open:
   ```bash
   sudo ufw status
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

### Rate Limiting

If you hit rate limits, adjust the rate limit middleware in `traefik/dynamic.yml`:

```yaml
rateLimit:
  rateLimit:
    average: 200  # Increase from 100
    burst: 100    # Increase from 50
```

## Security Recommendations

1. **Enable Basic Auth for Traefik Dashboard**:
   ```bash
   # Generate password hash
   htpasswd -nb admin yourpassword

   # Add to docker-compose.yaml under traefik labels
   # - "traefik.http.middlewares.auth.basicauth.users=admin:$$apr1$$..."
   ```

2. **Restrict CORS Origins**: Edit `main.py`:
   ```python
   allow_origins=["https://imigo.tw", "https://www.imigo.tw"]
   ```

3. **Set Up Firewall**:
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

4. **Regular Updates**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

## Monitoring

### View Real-time Logs

```bash
docker-compose logs -f
```

### Check Resource Usage

```bash
docker stats
```

### SSL Certificate Renewal

Let's Encrypt certificates auto-renew. Traefik handles this automatically.

## Stopping the Service

```bash
docker-compose down
```

To remove all data including volumes:

```bash
docker-compose down -v
```

## Support

For issues, check:
1. Container logs: `docker-compose logs`
2. Traefik documentation: https://doc.traefik.io/traefik/
3. FastAPI documentation: https://fastapi.tiangolo.com/
