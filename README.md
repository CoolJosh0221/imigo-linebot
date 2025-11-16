# Indonesian Migrant Worker Assistant LINE Bot (MVP)

A minimal LINE chatbot for Indonesian migrant workers in Taiwan with AI conversation and group translation features.

## Features

### 🤖 AI-Powered Chat (Private Messages)
- **Conversational AI**: Powered by SEA-LION-7B, optimized for Southeast Asian languages
- **Multi-language Support**: Indonesian, Traditional Chinese, English
- **Context-aware Responses**: Maintains conversation history

### 🌐 Translation (Group Chats)
- **Automatic Translation**: Translate messages in LINE group chats
- **Multi-language**: Supports ID ↔️ ZH ↔️ EN translation
- **LLM-based**: Natural, context-aware translations

### 📱 Rich Menu Interface
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
- NVIDIA GPU (RTX 4090 recommended) for local LLM (or use OpenAI API)

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

```
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
- `language`: Preferred language (id/zh/en)
- `created_at`, `updated_at`: Timestamps

### Group Settings
- `group_id`: LINE group ID (primary key)
- `translate_enabled`: Translation enabled flag
- `target_language`: Target language for translation
- `enabled_by`: User who enabled translation
- `created_at`, `updated_at`: Timestamps

## Usage

### Private Chat (1-on-1)
User sends message → AI responds in their preferred language

### Group Chat (Translation)
1. Admin enables translation in group settings
2. User sends message in any language → Bot translates to target language

### Commands
- `/lang id` - Switch to Indonesian
- `/lang zh` - Switch to Traditional Chinese
- `/lang en` - Switch to English

## LLM Configuration

### SEA-LION-7B (Recommended for Production)
- **Model**: aisingapore/sealion7b-instruct
- **VRAM**: ~7-14GB (depending on quantization)
- **Languages**: Indonesian, Chinese, English, Vietnamese, Thai, Malay, Tagalog
- **License**: Apache 2.0

### OpenAI API (Alternative for Development)
```env
LLM_API_KEY=sk-your-openai-key
# Leave LLM_BASE_URL empty to use OpenAI
```

## Deployment

### Local GPU Server
1. Install NVIDIA drivers (525+) and CUDA 12.1+
2. Run: `docker-compose up -d`
3. Expose via Cloudflare Tunnel or ngrok

### Cloud Options
- AWS EC2 (g5.xlarge): $1.006/hour
- Google Cloud (n1-standard-4 + T4): ~$0.50/hour
- Vast.ai: $0.20-0.50/hour

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

## License

MIT License

## Acknowledgments

- AI Singapore for SEA-LION-7B model
- LINE Corporation for Messaging API
- FastAPI and vLLM communities
