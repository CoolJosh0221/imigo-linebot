# Indonesian Migrant Worker Assistant LINE Bot (MVP)

A minimal LINE chatbot for Indonesian migrant workers in Taiwan with AI conversation and group translation features.

## Features

### 🤖 AI-Powered Assistance

- **Conversational AI**: Powered by SEA-LION-7B, optimized for Southeast Asian languages
- **Multi-language Support**: Indonesian, Traditional Chinese, English
- **Context-aware Responses**: Maintains conversation history

### 📍 Location Services

- **Find Nearby Places**: Indonesian restaurants, hospitals, mosques
- **Google Maps Integration**: Directions and distance calculations
- **Location Sharing**: Send location to get relevant nearby recommendations

### 🌐 Translation

- **Group Chat Translation**: Automatic translation in group chats
- **Multi-language**: Supports ID → ZH → EN translation
- **Context-aware**: Uses LLM for natural translations

### 🚨 Emergency & Resources

- **Emergency Contacts**: Quick access to police, ambulance, labor hotline
- **Embassy Information**: Indonesian embassy contact details
- **Healthcare Guidance**: Find nearby hospitals and medical facilities

### 📱 Rich Menu Interface

- Healthcare
- Labor Rights
- Language Settings
- Emergency Contacts
- Language Settings
- Clear Chat History

## Technology Stack

- **Backend**: FastAPI 0.116.1 (Python 3.11+)
- **LLM**: SEA-LION-7B-Instruct via vLLM
- **Database**: SQLAlchemy + aiosqlite (SQLite)
- **LINE SDK**: line-bot-sdk 3.19.0
- **Containerization**: Docker/Podman

## Prerequisites

### Required

- Python 3.11+
- LINE Messaging API credentials
- NVIDIA GPU (RTX 4090 recommended) for local LLM
- 24GB+ VRAM for SEA-LION-7B

### Optional

- Google Maps API key (for location services)
- Docker/Podman for containerized deployment

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd imigo-linebot
```

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env with your credentials
nano .env
```

Required environment variables:
```env
LINE_CHANNEL_SECRET=your_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
DEFAULT_LANGUAGE=id
```

### 3. Install Dependencies

#### Using uv (recommended)
```bash
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

uv pip install -r pyproject.toml
```

#### Using pip
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn line-bot-sdk aiosqlite sqlalchemy openai pyyaml attrs python-dotenv
```

### 4. Run the Bot

#### Development (Local)
```bash
# Terminal 1: Start vLLM server
python -m vllm.entrypoints.openai.api_server \
  --model aisingapore/sealion7b-instruct \
  --dtype auto \
  --port 8001

# Terminal 2: Start FastAPI backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Expose via ngrok (for LINE webhook)
ngrok http 8000
```

#### Production (Docker)
```bash
docker-compose up -d
```

#### Production (Podman)
```bash
podman-compose up -d
```

### 5. Configure LINE Webhook

1. Go to [LINE Developers Console](https://developers.line.biz/console/)
2. Select your Messaging API channel
3. Set Webhook URL to: `https://your-domain.com/webhook` or `https://xxx.ngrok.io/webhook`
4. Enable webhook
5. Disable auto-reply and greeting messages

## Project Structure

```text
imigo-linebot/
├── main.py                 # FastAPI application & webhook handler
├── config.py               # Configuration management
├── pyproject.toml          # Project dependencies
├── Dockerfile              # Backend container
├── Dockerfile.llm          # vLLM server container
├── docker-compose.yaml     # Docker orchestration
├── .env.example            # Environment template
├── database/
│   ├── models.py           # SQLAlchemy models
│   └── database.py         # Database service
├── services/
│   ├── ai_service.py       # LLM conversation service
│   └── translation_service.py  # Translation service
└── config/
    ├── indonesia.yaml      # Indonesian bot config
    ├── chinese.yaml        # Chinese bot config
    └── english.yaml        # English bot config
```

## API Endpoints

- `GET /` - Bot status and configuration
- `GET /health` - Health check
- `POST /webhook` - LINE webhook endpoint

## Database Schema

### Conversations

- `id`: Unique conversation ID
- `user_id`: LINE user ID
- `role`: "user" or "assistant"
- `content`: Message content
- `created_at`: Timestamp

### User Preferences

- `user_id`: LINE user ID (primary key)
- `language`: Preferred language (id/zh/en/etc.)
- `created_at`: Account creation time
- `updated_at`: Last update time

### Group Settings
- `group_id`: LINE group ID (primary key)
- `translate_enabled`: Translation enabled flag
- `target_language`: Target language for translation
- `enabled_by`: User who enabled translation
- `created_at`, `updated_at`: Timestamps

- `group_id`: LINE group ID (primary key)
- `translate_enabled`: Translation enabled flag
- `target_language`: Target language for translation
- `enabled_by`: User who enabled translation
- `created_at`: Setting creation time
- `updated_at`: Last update time

## Configuration

### Language Files

Each language has a YAML config file in `config/`:

```yaml
bot:
  name: "Bot Name"
  language: id
  country: indonesia

messages:
  welcome: "Welcome message..."
  help: "Help message..."
  # ... more messages

emergency:
  police: "110"
  ambulance: "119"
  # ... more contacts

quick_replies:
  - label: "🏥 Health"
    text: "I need health assistance"
  # ... more quick replies
```

### Switching Languages

Users can change their language preference:

- Via rich menu → Language
- Send: `/lang id` (Indonesian), `/lang zh` (Chinese), `/lang en` (English)

## Google Maps Integration

### Private Chat (1-on-1)
User sends message → AI responds in their preferred language

1. Places API (Nearby Search)
2. Geocoding API
3. Directions API

### Setup

1. Create Google Cloud Project
2. Enable Maps Platform APIs
3. Create API key
4. Add restrictions:
      - HTTP referrers (for security)
      - API restrictions (only enable needed APIs)
5. Add to `.env`: `Maps_API_KEY=your_key`

### Free Tier

- $200 free credit per month
- Places API: $17 per 1000 requests
- Geocoding/Directions: $5 per 1000 requests
- Sufficient for MVP scale

## LLM Configuration

### SEA-LION-7B (Recommended)

- **Model**: aisingapore/sealion7b-instruct
- **VRAM**: \~7-14GB (depending on quantization)
- **Languages**: Indonesian, Chinese, English, Vietnamese, Thai, Malay, Tagalog
- **License**: Apache 2.0

### Alternative: OpenAI API

### OpenAI API (Alternative for Development)
```env
LLM_API_KEY=sk-your-openai-key
# Leave LLM_BASE_URL empty to use OpenAI
```

## Deployment

### Local GPU Server

1. Install NVIDIA drivers (525+)
2. Install CUDA 12.1+
3. Run docker-compose or podman-compose
4. Expose via Cloudflare Tunnel or ngrok

### Cloud Options

- AWS EC2 (g5.xlarge): $1.006/hour
- Google Cloud (n1-standard-4 + T4): \~$0.50/hour
- Vast.ai: $0.20-0.50/hour

### Tunneling Services

#### Ngrok (Development)

```bash
ngrok http 8000
# Use the HTTPS URL for LINE webhook
```

#### Cloudflare Tunnel (Production)

```bash
cloudflared tunnel create migrant-bot
cloudflared tunnel run migrant-bot
```

## Monitoring

### Logs

```bash
# Docker
docker-compose logs -f backend
docker-compose logs -f llm

# Podman
podman-compose logs -f backend
```

### GPU Monitoring

```bash
watch -n 1 nvidia-smi
```

### Metrics to Track

- Message volume per hour
- LLM response time (P50, P95, P99)
- Google Maps API usage
- Error rates
- User language distribution

## Development

### Running Tests
```bash
uv pip install -r pyproject.toml --extra dev
pytest
```

### Code Formatting
```bash
black .
ruff check .
```

## Troubleshooting

### vLLM Server Issues

- **Out of memory**: Reduce `--max-model-len` or use quantization
- **Slow loading**: Model downloads on first run (15-30 minutes)
- **GPU not detected**: Check `nvidia-smi` and CUDA installation

### LINE Webhook Issues

- **Invalid signature**: Check `LINE_CHANNEL_SECRET` is correct
- **403 Forbidden**: Ensure webhook URL is HTTPS
- **No response**: Check FastAPI logs and server connectivity

### Google Maps Issues

- **API key error**: Enable required APIs in Google Cloud Console
- **Quota exceeded**: Check usage in Google Cloud Console
- **No results**: Verify coordinates and search parameters

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit pull request

## License

MIT License

## Support

For issues and questions:

- GitHub Issues: [repository-url]/issues

## Acknowledgments

- AI Singapore for SEA-LION-7B model
- LINE Corporation for Messaging API
- Google for Maps Platform APIs
- FastAPI and vLLM communities
