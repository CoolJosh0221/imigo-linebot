# IMIGO - Indonesian Migrant Worker Assistant

IMIGO is an AI-powered LINE bot and API designed to assist Indonesian migrant workers in Taiwan. The bot provides multilingual support, intelligent conversation handling, and quick access to essential services through language-specific rich menus.

## Key Features

- **Multilingual Support**: English, Indonesian, Traditional Chinese, and Vietnamese
- **Language-Specific Rich Menus**: Each user sees a rich menu in their preferred language
- **AI-Powered Conversations**: Context-aware responses using Llama-SEA-LION model
- **Smart Intent Detection**: Fast responses for common queries without AI calls
- **Real-time Translation**: Built-in translation services
- **Emergency Information**: Quick access to Taiwan emergency contacts
- **Persistent User Preferences**: Language preferences stored across sessions

## Supported Languages

| Language | Code | Display Name |
|----------|------|--------------|
| English | `en` | English |
| Indonesian | `id` | Bahasa Indonesia |
| Traditional Chinese | `zh` | 繁體中文 |
| Vietnamese | `vi` | Tiếng Việt |

## Language-Specific Rich Menus

IMIGO automatically creates and manages rich menus for each supported language. When users set or change their language preference, the bot automatically updates their rich menu to display content in the appropriate language.

### Features

- **Automatic Menu Creation**: On startup, the bot creates 4 language-specific rich menus
- **Dynamic User Assignment**: Users receive the rich menu matching their language preference
- **Seamless Updates**: When users change language, their rich menu updates automatically
- **8 Quick Access Buttons**:
  - Healthcare Information
  - Labor Rights & Work Issues
  - Language Settings
  - Emergency Contacts
  - Government Services
  - Daily Life Assistance
  - Translation Services
  - Clear Chat History

### Rich Menu Layout

All rich menus use a 3x2 button grid layout:
- **Dimensions**: 2500 x 1686 pixels
- **6 Main Categories**: Equally divided across the menu area
- **2 Bottom Buttons**: Translation and Clear Chat
- **Language-Specific Images**: Located in `rich_menu/menu_*.png`

## Quick Start

### Prerequisites

- Python 3.11+
- LINE Messaging API account
- OpenAI API key (for AI features)
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/CoolJosh0221/imigo-linebot.git
cd imigo-linebot
```

2. Install dependencies using uv:
```bash
uv pip install -r pyproject.toml
```

3. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Initialize the database:
```bash
python -c "from database.database import DatabaseService; import asyncio; asyncio.run(DatabaseService().init_db())"
```

5. Run the application:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
docker-compose up -d
```

Or with Podman:
```bash
podman-compose up -d
```

## Environment Variables

Key configuration options in `.env`:

```bash
# LINE Configuration
LINE_CHANNEL_SECRET=your_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# Bot Configuration
BOT_NAME=IMIGO
DEFAULT_LANGUAGE=id
COUNTRY=taiwan

# Database
DATABASE_URL=sqlite+aiosqlite:///./database.db
```

## API Endpoints

### Health Check
```bash
GET /
GET /health
```

### Chat API
```bash
POST /api/chat
```

### Translation API
```bash
POST /api/translate
```

### Rich Menu Management
```bash
GET  /api/richmenu/list
GET  /api/richmenu/default
POST /api/richmenu/setup
POST /api/richmenu/link
DELETE /api/richmenu/unlink/{user_id}
DELETE /api/richmenu/{rich_menu_id}
```

### System API
```bash
GET /api/system/config
```

Full API documentation available at:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## Usage

### Changing Language

Users can change their language preference in multiple ways:

**Text Command:**
```
/lang en   # Switch to English
/lang id   # Switch to Indonesian
/lang zh   # Switch to Chinese
/lang vi   # Switch to Vietnamese
```

**Rich Menu Button:**
- Tap the "Language" button in the rich menu
- Select preferred language from quick reply buttons

**Automatic Detection:**
- New users have their language automatically detected from their first message

### Available Commands

- `/lang [code]` - Change language preference
- `/help` - Display help information
- `/emergency` - Show emergency contacts
- `/clear` - Clear conversation history

## Architecture

```
imigo-linebot/
├── api/              # FastAPI route handlers
│   └── routes/       # API endpoint definitions
├── config/           # Configuration files
├── database/         # Database models and service
├── rich_menu/        # Rich menu images and configuration
├── services/         # Business logic services
│   ├── ai_service.py
│   ├── translation_service.py
│   ├── language_detection.py
│   └── rich_menu_service.py
├── main.py           # Application entry point
└── config.py         # Configuration management
```

## Rich Menu Setup

The bot automatically creates language-specific rich menus on startup. To manually manage rich menus:

### Create All Language Menus
```bash
curl -X POST http://localhost:8000/api/richmenu/setup \
  -H "Content-Type: application/json" \
  -d '{"set_as_default": true}'
```

### List All Rich Menus
```bash
curl http://localhost:8000/api/richmenu/list
```

### Link Menu to User
```bash
curl -X POST http://localhost:8000/api/richmenu/link \
  -H "Content-Type: application/json" \
  -d '{"user_id": "U1234...", "rich_menu_id": "richmenu-..."}'
```

## Development

### Project Structure

- **Services Layer**: Handles business logic (AI, translation, language detection, rich menu)
- **API Layer**: RESTful endpoints for external integrations
- **Database Layer**: User preferences and conversation history
- **Webhook Handler**: Processes LINE messaging events

### Adding New Languages

1. Add language code to `config.py`:
```python
SUPPORTED_LANGUAGES = {
    # ... existing languages ...
    "new": "Language Name",
}
```

2. Add translations to `MESSAGES` dict in `config.py`

3. Create rich menu image: `rich_menu/menu_new.png`

4. Update `RichMenuService.create_language_rich_menus()` to include new language

### Testing

Run the test suite:
```bash
python test.py
```

## Emergency Contacts (Taiwan)

- Police: 110
- Fire/Ambulance: 119
- Foreign Worker Hotline: 1955
- Indonesia Representative Office: +886-2-2356-5156
- Labor Hotline: 1955
- Anti-Trafficking Hotline: 113

## Documentation

- [FEATURES.md](FEATURES.md) - Detailed feature documentation
- [API.md](API.md) - Complete API reference
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please open an issue on GitHub.

## Acknowledgments

- Built with FastAPI and LINE Messaging API
- AI powered by OpenAI and Llama-SEA-LION
- Translation services by OpenAI
- Designed for Indonesian migrant workers in Taiwan
