# Deployment Guide for IMIGO API

This guide explains how to deploy the IMIGO API using Pangolin tunnel for secure HTTPS access.

## Prerequisites

- Docker and Docker Compose installed
- A Pangolin account and token (sign up at https://pangolin.com/)
- NVIDIA GPU with drivers installed (for vLLM)

## What is Pangolin?

Pangolin is a secure tunnel service that provides:
- **Automatic HTTPS** - No need to manage SSL certificates
- **Public URLs** - Expose your local services to the internet
- **No Port Forwarding** - Works behind firewalls and NAT
- **Easy Setup** - No DNS configuration required

## Step 1: Get Your Pangolin Token

1. Sign up at https://pangolin.com/
2. Create a new tunnel token from your dashboard
3. Copy the token for use in the next step

## Step 2: Set Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```bash
# Pangolin Tunnel Token
PANGOLIN_TOKEN=your_pangolin_token_here

# LINE Bot Credentials
LINE_CHANNEL_SECRET=your_actual_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_actual_access_token

# Google Maps API (optional)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

## Step 3: Build and Deploy

Start the services with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- **Pangolin** - Secure tunnel service with automatic HTTPS
- **Backend** - FastAPI application
- **vLLM** - AI model server

## Step 4: Get Your Public URL

After starting the services, check the Pangolin logs to find your public URL:

```bash
docker-compose logs pangolin
```

Look for a line like:
```
Tunnel established at: https://random-name-1234.pangolin.dev
```

This is your public HTTPS URL! The backend will be accessible at this URL.

## Step 5: Configure LINE Webhook

Update your LINE Bot webhook URL in the LINE Developers Console:

```
https://your-pangolin-url.pangolin.dev/webhook
```

Replace `your-pangolin-url.pangolin.dev` with the URL from the Pangolin logs.

## Step 6: Verify Deployment

### Check Container Status

```bash
docker-compose ps
```

All services should be "Up".

### Check Logs

```bash
# Backend logs
docker-compose logs -f backend

# Pangolin logs
docker-compose logs -f pangolin

# vLLM logs
docker-compose logs -f vllm
```

### Test Your API

Visit your Pangolin URL in a browser or use curl:

```bash
curl https://your-pangolin-url.pangolin.dev/health
```

You should see a valid SSL certificate automatically!

## API Endpoints

Once deployed, your API will be available at your Pangolin URL:

### Main Endpoints

- **Root**: `https://your-pangolin-url.pangolin.dev/`
- **Health Check**: `https://your-pangolin-url.pangolin.dev/health`
- **API Documentation**: `https://your-pangolin-url.pangolin.dev/api/docs`
- **ReDoc**: `https://your-pangolin-url.pangolin.dev/api/redoc`

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
curl -X POST https://your-pangolin-url.pangolin.dev/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Bagaimana cara mendapatkan visa kerja?",
    "language": "id"
  }'
```

### Translate Text

```bash
curl -X POST https://your-pangolin-url.pangolin.dev/api/translate/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_language": "id",
    "source_language": "en"
  }'
```

## Troubleshooting

### Pangolin Tunnel Not Connecting

1. Verify your token is correct in `.env`:
   ```bash
   cat .env | grep PANGOLIN_TOKEN
   ```

2. Check Pangolin logs for errors:
   ```bash
   docker-compose logs pangolin
   ```

3. Ensure the backend is running:
   ```bash
   docker-compose ps backend
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

### LINE Webhook Issues

1. Ensure the webhook URL in LINE console matches your Pangolin URL
2. Check that the `/webhook` endpoint is accessible:
   ```bash
   curl https://your-pangolin-url.pangolin.dev/webhook
   ```

## Advantages of Pangolin over Traefik

### Pangolin Benefits:
- ✅ **Zero Configuration** - No DNS, SSL certificates, or port forwarding needed
- ✅ **Automatic HTTPS** - SSL certificates managed automatically
- ✅ **Works Anywhere** - Behind NAT, firewalls, or on your laptop
- ✅ **Instant Setup** - Get a public URL in seconds
- ✅ **Built-in Security** - DDoS protection and rate limiting included

### When to Use Traefik Instead:
- You need custom domain names
- You require advanced routing rules
- You're running a production service with high traffic
- You need full control over SSL certificates

## Monitoring

### View Real-time Logs

```bash
docker-compose logs -f
```

### Check Resource Usage

```bash
docker stats
```

### Pangolin Dashboard

Visit https://pangolin.com/dashboard to:
- View tunnel status
- See request analytics
- Manage tokens
- Configure custom domains (paid plans)

## Stopping the Service

```bash
docker-compose down
```

To remove all data including volumes:

```bash
docker-compose down -v
```

## Production Considerations

### Custom Domains (Optional)

For production deployments, you may want to use a custom domain:

1. Upgrade to a Pangolin paid plan
2. Configure your custom domain in the Pangolin dashboard
3. Update the Pangolin service in `docker-compose.yaml`:
   ```yaml
   pangolin:
     image: pangolin/client:latest
     command:
       - "http"
       - "--url"
       - "http://backend:8000"
       - "--hostname"
       - "api.yourdomain.com"
   ```

### Security Recommendations

1. **Restrict CORS Origins**: Edit your FastAPI app to only allow specific origins:
   ```python
   allow_origins=["https://your-pangolin-url.pangolin.dev"]
   ```

2. **Add Rate Limiting**: Implement rate limiting in your FastAPI application

3. **Monitor Logs**: Regularly check logs for suspicious activity:
   ```bash
   docker-compose logs -f backend
   ```

4. **Regular Updates**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

## Development vs Production

### Development (Current Setup)
- Uses free Pangolin tunnel
- Random URL (changes on restart)
- Perfect for testing and development
- No DNS configuration needed

### Production (Recommended)
- Use Pangolin with custom domain
- Or migrate to Traefik/Nginx with dedicated server
- Set up proper monitoring
- Configure backups

## Support

For issues, check:
1. Container logs: `docker-compose logs`
2. Pangolin documentation: https://pangolin.com/docs
3. FastAPI documentation: https://fastapi.tiangolo.com/
4. GitHub Issues: [Your Repository Issues URL]
