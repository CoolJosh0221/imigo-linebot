# Deployment Guide for IMIGO API

This guide explains how to deploy the IMIGO API using Pangolin Self-Host Community Edition for secure HTTPS access without requiring a public IP address.

## What is Pangolin Self-Host?

Pangolin Self-Host is a free, open-source solution that allows you to expose your local services to the internet with:
- **Automatic HTTPS** - Free SSL certificates via Let's Encrypt
- **Works Without Public IP** - Uses WireGuard tunneling through Pangolin's infrastructure
- **Custom Domains** - Use your own domain (e.g., imigo.tw)
- **No Port Forwarding** - Works behind NAT, firewalls, and residential networks
- **Web Dashboard** - Manage your tunnels through a web interface
- **Completely Free** - Open-source and self-hosted

### How It Works

Pangolin consists of three components:
1. **Pangolin** - Dashboard and API server for managing tunnels
2. **Gerbil** - WireGuard tunnel client that connects to Pangolin's infrastructure
3. **Traefik** - Reverse proxy that handles SSL and routing

Your services connect through an encrypted WireGuard tunnel to Pangolin's servers, which then route traffic to your domain - no public IP required!

## Prerequisites

### Required:
- Docker and Docker Compose installed
- NVIDIA GPU with drivers installed (for vLLM)
- A domain name (e.g., imigo.tw)
- DNS access to configure A records

### Important Notes:
- ✅ **You do NOT need a public IP address**
- ✅ **You do NOT need to open ports 80/443 on your firewall**
- ✅ **Works behind NAT, firewalls, and residential networks**
- ⚠️ You DO need to configure DNS A records (Pangolin provides the IP)

## Step 1: DNS Configuration

Configure your domain's DNS A records to point to Pangolin's infrastructure:

```
A Record:     imigo.tw           -> [Will be provided by Pangolin dashboard]
A Record:     www.imigo.tw       -> [Will be provided by Pangolin dashboard]
A Record:     api.imigo.tw       -> [Will be provided by Pangolin dashboard]
```

**Note:** You'll get the actual IP address from the Pangolin dashboard after initial setup.

## Step 2: Set Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```bash
# Pangolin Self-Host Configuration
DOMAIN=imigo.tw
EMAIL=admin@imigo.tw

# LINE Bot Credentials
LINE_CHANNEL_SECRET=your_actual_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_actual_access_token

# Google Maps API (optional)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

## Step 3: Configure Pangolin

The configuration files are already created in the `config/` directory:

```
config/
├── config.yml                    # Pangolin main configuration
├── traefik/
│   ├── traefik_config.yml       # Traefik static configuration
│   └── dynamic_config.yml       # Traefik routing rules
├── db/                          # Database (auto-created)
├── letsencrypt/                 # SSL certificates (auto-created)
└── logs/                        # Log files (auto-created)
```

**Before deploying**, edit `config/config.yml` and update the security secrets:

```yaml
security:
  jwtSecret: "CHANGE_THIS_TO_A_RANDOM_STRING"
  sessionSecret: "CHANGE_THIS_TO_ANOTHER_RANDOM_STRING"
```

Generate random secrets with:
```bash
openssl rand -base64 32
```

## Step 4: Build and Deploy

Start all services with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- **Pangolin** - Dashboard and API (ports 3000, 3001, 3002)
- **Gerbil** - WireGuard tunnel (ports 51820/udp, 21820/udp, 80, 443)
- **Traefik** - Reverse proxy with automatic SSL
- **Backend** - Your FastAPI application
- **vLLM** - AI model server

## Step 5: Initial Setup

### Access the Pangolin Dashboard

Once the services are running, access the initial setup page:

```
https://imigo.tw/auth/initial-setup
```

**Note:** The first time you access this, you may get an SSL warning because the certificate isn't issued yet. This is normal - proceed anyway (the certificate will be automatically obtained).

### Complete Initial Setup

1. **Create Admin Account** - Set up your admin username and password
2. **Configure Tunnel** - The dashboard will show you the Pangolin server IP address
3. **Update DNS** - Add the provided IP to your domain's DNS A records
4. **Create Tunnel** - Configure a tunnel for your backend service

### Create a Tunnel for Your Backend

In the Pangolin dashboard:

1. Go to **Tunnels** → **Create New Tunnel**
2. Set the following:
   - **Name**: `imigo-backend`
   - **Type**: `HTTP`
   - **Backend URL**: `http://backend:8000`
   - **Domain**: `imigo.tw` (or `api.imigo.tw` for a subdomain)
3. Click **Create**

The tunnel should now route traffic from `https://imigo.tw` to your backend service!

## Step 6: Verify Deployment

### Check Container Status

```bash
docker-compose ps
```

All services should show "Up" status.

### Check Logs

```bash
# Pangolin logs
docker-compose logs -f pangolin

# Gerbil (tunnel) logs
docker-compose logs -f gerbil

# Traefik logs
docker-compose logs -f traefik

# Backend logs
docker-compose logs -f backend

# vLLM logs
docker-compose logs -f vllm
```

### Test Your API

Visit your domain in a browser or use curl:

```bash
curl https://imigo.tw/health
```

You should see a valid SSL certificate and your API response!

## Step 7: Configure LINE Webhook

Update your LINE Bot webhook URL in the LINE Developers Console:

```
https://imigo.tw/webhook
```

## API Endpoints

Once deployed, your API will be available at your domain:

### Main Endpoints

- **Root**: `https://imigo.tw/`
- **Health Check**: `https://imigo.tw/health`
- **API Documentation**: `https://imigo.tw/api/docs`
- **ReDoc**: `https://imigo.tw/api/redoc`
- **Pangolin Dashboard**: `https://imigo.tw/dashboard`

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

1. Check Gerbil logs for errors:
   ```bash
   docker-compose logs gerbil
   ```

2. Verify Pangolin is healthy:
   ```bash
   docker-compose ps pangolin
   ```

3. Ensure WireGuard ports are accessible (may require firewall configuration):
   ```bash
   sudo ufw allow 51820/udp
   sudo ufw allow 21820/udp
   ```

### SSL Certificate Issues

1. Check Traefik logs:
   ```bash
   docker-compose logs traefik
   ```

2. Verify DNS is pointing to the correct IP:
   ```bash
   dig imigo.tw
   # Should return the IP provided by Pangolin dashboard
   ```

3. Wait a few minutes for Let's Encrypt to issue certificates

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

1. Ensure the webhook URL in LINE console is correct:
   ```
   https://imigo.tw/webhook
   ```

2. Check that the `/webhook` endpoint is accessible:
   ```bash
   curl https://imigo.tw/webhook
   ```

3. Verify the tunnel is configured correctly in Pangolin dashboard

## Advantages of Pangolin Self-Host

### Key Benefits:
- ✅ **No Public IP Required** - Works behind NAT, firewalls, residential networks
- ✅ **Automatic HTTPS** - Free SSL certificates via Let's Encrypt
- ✅ **Custom Domains** - Use your own domain (imigo.tw)
- ✅ **Web Dashboard** - Manage tunnels through a friendly UI
- ✅ **WireGuard Tunneling** - Secure, fast, modern VPN technology
- ✅ **Free Forever** - Open-source and self-hosted
- ✅ **No Cloud Dependency** - All your data stays on your server
- ✅ **Professional Setup** - Production-ready with monitoring

### Comparison to Other Solutions:

**vs. Traefik Alone:**
- Pangolin: Works without public IP ✅
- Traefik: Requires public IP ❌

**vs. ngrok/CloudFlare Tunnel:**
- Pangolin: Self-hosted, full control ✅
- ngrok/CloudFlare: Cloud service, limited control ❌

**vs. VPS with Public IP:**
- Pangolin: Use your existing hardware ✅
- VPS: Monthly costs, data transfer limits ❌

## Monitoring

### Pangolin Dashboard

Access the dashboard at:
```
https://imigo.tw/dashboard
```

Features:
- Real-time tunnel status
- Traffic analytics
- SSL certificate status
- Service health monitoring

### View Real-time Logs

```bash
docker-compose logs -f
```

### Check Resource Usage

```bash
docker stats
```

## Security Recommendations

1. **Change Default Secrets**: Update `config/config.yml` with strong random secrets

2. **Restrict Dashboard Access**: Consider adding IP allowlisting in Traefik

3. **Monitor Logs**: Regularly check logs for suspicious activity:
   ```bash
   docker-compose logs -f pangolin
   ```

4. **Regular Updates**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

5. **Backup Configuration**:
   ```bash
   tar -czf pangolin-backup.tar.gz config/
   ```

## Stopping the Service

```bash
docker-compose down
```

To remove all data including volumes:

```bash
docker-compose down -v
```

**Warning:** This will delete your Pangolin database and SSL certificates!

## Production Deployment

### Current Setup is Production-Ready!

The Pangolin Self-Host setup is designed for production use:
- ✅ Automatic SSL certificate renewal
- ✅ Health checks and automatic restarts
- ✅ Persistent data in volumes
- ✅ Secure WireGuard tunneling
- ✅ Professional domain (imigo.tw)

### Optional Enhancements:

1. **Monitoring**: Add Prometheus + Grafana for metrics
2. **Backups**: Set up automated backups of config/ directory
3. **High Availability**: Run multiple Gerbil instances for redundancy
4. **CDN**: Add CloudFlare in front for DDoS protection and caching

## Support and Documentation

For more information:
1. **Pangolin Documentation**: https://docs.pangolin.net/
2. **Pangolin GitHub**: https://github.com/fosrl/pangolin
3. **Docker Logs**: `docker-compose logs`
4. **FastAPI Documentation**: https://fastapi.tiangolo.com/
5. **Container Status**: `docker-compose ps`

## Summary

You now have a fully functional, production-ready deployment of your IMIGO API that:
- ✅ Works without a public IP address
- ✅ Has automatic HTTPS with your custom domain (imigo.tw)
- ✅ Is completely self-hosted and free
- ✅ Includes a web dashboard for management
- ✅ Uses modern WireGuard tunneling technology

All accessible at `https://imigo.tw` with automatic SSL! 🎉
