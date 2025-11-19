# Deployment Guide for IMIGO API

This guide explains how to deploy the IMIGO API using Pangolin Self-Host Community Edition for secure HTTPS access.

## Prerequisites

- Docker and Docker Compose installed
- NVIDIA GPU with drivers installed (for vLLM)
- A domain name (e.g., imigo.tw) pointing to your server (for custom domain)
- Ports 80 and 443 open on your firewall
- (Optional) Pangolin account for enhanced features

## What is Pangolin Self-Host Community Edition?

Pangolin Self-Host Community Edition is a free, open-source tunnel service that provides:
- **Automatic HTTPS** - No need to manage SSL certificates manually
- **Public URLs** - Expose your local services to the internet
- **Custom Domains** - Use your own domain (e.g., imigo.tw)
- **No Port Forwarding** - Works behind NAT (with custom domain setup)
- **Easy Setup** - Minimal DNS configuration required
- **Self-Hosted** - Run on your own infrastructure
- **Free Forever** - Community edition is completely free

## Step 1: DNS Configuration (For Custom Domain)

If you want to use your custom domain `imigo.tw`, configure DNS records:

```
A Record:     imigo.tw           -> YOUR_SERVER_PUBLIC_IP
A Record:     www.imigo.tw       -> YOUR_SERVER_PUBLIC_IP
A Record:     api.imigo.tw       -> YOUR_SERVER_PUBLIC_IP
```

**Note:** DNS propagation can take up to 48 hours, but typically completes within a few minutes.

To verify DNS is configured correctly:
```bash
dig imigo.tw
# Should return your server's public IP
```

## Step 2: Configure Pangolin Token (Optional)

Pangolin can run without a token for basic tunneling, or you can use a token for additional features:

**Without Token (Basic Mode):**
- Free random subdomain (if DOMAIN not set)
- Or use your custom domain (if DOMAIN is set and DNS configured)
- Automatic HTTPS
- No registration required
- Perfect for development and testing

**With Token (Enhanced Mode):**
1. Sign up at https://pangolin.com/ (optional)
2. Create a new tunnel token from your dashboard
3. Copy the token to use in `.env` file
4. Benefits: Analytics, persistent URLs, advanced features

## Step 3: Set Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```bash
# Pangolin Tunnel Token (OPTIONAL - leave empty for basic mode)
PANGOLIN_TOKEN=

# Domain Configuration
# Set your custom domain or leave empty for random subdomain
DOMAIN=imigo.tw

# LINE Bot Credentials
LINE_CHANNEL_SECRET=your_actual_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_actual_access_token

# Google Maps API (optional)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

**Important Notes:**
- Set `DOMAIN=imigo.tw` to use your custom domain (requires DNS configured)
- Leave `DOMAIN=` empty for a random pangolin subdomain
- `PANGOLIN_TOKEN` is optional - leave empty for basic mode (no account required)

## Step 4: Build and Deploy

Start the services with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- **Pangolin (Self-Host Community Edition)** - Secure tunnel service with automatic HTTPS
- **Backend** - FastAPI application
- **vLLM** - AI model server

## Step 5: Get Your Public URL

### If Using Custom Domain (DOMAIN=imigo.tw):

Your API will be accessible at:
```
https://imigo.tw/
```

Pangolin will automatically obtain and manage SSL certificates for your domain.

### If Using Random Subdomain (DOMAIN empty):

Check the Pangolin logs to find your public URL:

```bash
docker-compose logs pangolin
```

Look for a line like:
```
Tunnel established at: https://random-name-1234.pangolin.dev
```

This is your public HTTPS URL! The backend will be accessible at this URL.

## Step 6: Configure LINE Webhook

Update your LINE Bot webhook URL in the LINE Developers Console:

**If using custom domain:**
```
https://imigo.tw/webhook
```

**If using random subdomain:**
```
https://your-pangolin-url.pangolin.dev/webhook
```

Replace `your-pangolin-url.pangolin.dev` with the URL from the Pangolin logs.

## Step 7: Verify Deployment

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

Visit your URL in a browser or use curl:

**With custom domain:**
```bash
curl https://imigo.tw/health
```

**With random subdomain:**
```bash
curl https://your-pangolin-url.pangolin.dev/health
```

You should see a valid SSL certificate automatically!

## API Endpoints

Once deployed, your API will be available at your configured URL.

### Main Endpoints (using imigo.tw as example)

- **Root**: `https://imigo.tw/`
- **Health Check**: `https://imigo.tw/health`
- **API Documentation**: `https://imigo.tw/api/docs`
- **ReDoc**: `https://imigo.tw/api/redoc`

*Replace `imigo.tw` with your actual domain or Pangolin subdomain.*

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

### DNS Issues (Custom Domain)

1. Verify DNS is pointing to your server:
   ```bash
   dig imigo.tw
   # Should return your server's public IP
   ```

2. Check that ports 80 and 443 are open:
   ```bash
   sudo ufw status
   # Or check your cloud provider's firewall settings
   ```

3. Wait for DNS propagation (can take up to 48 hours, usually faster)

### LINE Webhook Issues

1. Ensure the webhook URL in LINE console matches your configured URL
2. Check that the `/webhook` endpoint is accessible:
   ```bash
   curl https://imigo.tw/webhook
   ```

## Advantages of Pangolin Self-Host Community Edition over Traefik

### Pangolin Benefits:
- ✅ **Minimal Configuration** - Simple DNS setup, automatic SSL certificates
- ✅ **Automatic HTTPS** - SSL certificates managed automatically (Let's Encrypt)
- ✅ **Custom Domains** - Use your own domain (e.g., imigo.tw) for free
- ✅ **Flexible Deployment** - Works with custom domains OR random subdomains
- ✅ **Free Forever** - Community edition has no costs
- ✅ **Self-Hosted** - Full control over your infrastructure
- ✅ **No Account Required** - Can run without registration (basic mode)
- ✅ **Easy Maintenance** - Automatic certificate renewal

### When to Use Traefik Instead:
- You require very advanced routing rules and middlewares
- You need multiple backend services with complex routing
- You want more granular control over every aspect of the proxy
- You need advanced features like circuit breakers, retries, etc.

## Monitoring

### View Real-time Logs

```bash
docker-compose logs -f
```

### Check Resource Usage

```bash
docker stats
```

### Pangolin Dashboard (If Using Token)

If you're using a Pangolin token, visit https://pangolin.com/dashboard to:
- View tunnel status
- See request analytics
- Manage tokens
- Configure custom domains (paid plans)

**Note:** Dashboard access requires a Pangolin account and token.

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

### Development Mode
**Without Custom Domain (DOMAIN empty):**
- Uses free Pangolin Self-Host Community Edition
- Random subdomain (e.g., random-1234.pangolin.dev)
- Perfect for testing and development
- No DNS configuration needed
- No account or token required
- Completely self-hosted and free

### Production Mode (Current Setup)
**With Custom Domain (DOMAIN=imigo.tw):**
- ✅ Uses free Pangolin Self-Host Community Edition
- ✅ Your own domain (e.g., imigo.tw, www.imigo.tw, api.imigo.tw)
- ✅ Automatic HTTPS with Let's Encrypt
- ✅ Professional appearance for users
- ✅ Persistent URL (doesn't change on restart)
- ✅ Simple DNS A record configuration
- ✅ No account or token required (basic mode)
- ✅ Completely self-hosted and free

### Enhanced Production (Optional)
**With Pangolin Token:**
- All production mode features, plus:
- Analytics dashboard
- Advanced monitoring
- Priority support

## Support

For issues, check:
1. Container logs: `docker-compose logs`
2. Pangolin documentation: https://pangolin.com/docs
3. FastAPI documentation: https://fastapi.tiangolo.com/
4. GitHub Issues: [Your Repository Issues URL]
