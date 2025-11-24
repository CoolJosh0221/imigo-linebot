# IMIGO Features Guide

## Dynamic Language Switching

IMIGO supports multiple ways for users to change their preferred language at any time.

### Supported Languages

- **Indonesian** (`id`) - Bahasa Indonesia 🇮🇩
- **Traditional Chinese** (`zh`) - 繁體中文 🇹🇼
- **English** (`en`) - English 🇬🇧

### How to Switch Language

**Method 1: Text Command**
```
/lang id   # Switch to Indonesian
/lang zh   # Switch to Chinese
/lang en   # Switch to English
```

**Method 2: Quick Reply Buttons**
- Tap the "🌐 Language" button in the rich menu
- Bot shows language options with quick reply buttons
- Tap your preferred language

**Method 3: Postback Actions**
- Rich menu or flex messages can trigger language change
- Use postback data: `lang_id`, `lang_zh`, or `lang_en`

### Automatic Language Detection

When a new user first interacts with the bot, IMIGO automatically detects their language based on their initial message and sets it as their preferred language.

### Language Persistence

User language preferences are stored in the database and persist across sessions.

---

## Smart Intent Detection

IMIGO intelligently detects user intent to provide appropriate responses without always calling the AI.

### Supported Intents

1. **Commands** - `/lang`, `/help`, `/emergency`, `/clear`
2. **Greetings** - "hi", "hello", "你好", "halo"
3. **Thanks** - "thanks", "terima kasih", "謝謝"
4. **Goodbye** - "bye", "sampai jumpa", "再見"
5. **Emergency** - "emergency", "darurat", "緊急"
6. **Help Requests** - "help", "bantuan", "幫助"
7. **Queries** - General questions (sent to AI)

### How It Works

```
User: "Hello"
Bot: Quick response without AI call

User: "How do I apply for a work permit?"
Bot: Uses AI to provide detailed answer

User: "Emergency! I'm injured"
Bot: Shows emergency contacts immediately

User: "/help"
Bot: Shows help message
```

### Benefits

- **Faster responses** for simple interactions
- **Lower costs** by reducing AI calls
- **Better UX** with contextually appropriate replies
- **Emergency handling** prioritizes urgent situations

### Available Commands

- `/lang [id|zh|en]` - Change language
- `/help` - Show help message
- `/emergency` - Display emergency contacts
- `/clear` - Clear chat history

---

## Rich Menu Support

IMIGO includes a comprehensive rich menu (persistent menu at the bottom of LINE chat) for quick access to common features.

### Rich Menu Categories

The rich menu includes buttons for:

1. **Healthcare** (🏥) - Medical information and health services
2. **Labor** (💼) - Work-related issues and labor rights
3. **Language** (🌐) - Change language preferences
4. **Emergency** (🚨) - Emergency contacts and hotlines
5. **Government** (🏛️) - Government services and documentation
6. **Daily Life** (🏠) - Daily living assistance
7. **Translation** (🔤) - Translation services
8. **Clear Chat** (🗑️) - Clear conversation history

### Rich Menu Management API

#### Setup Rich Menu

Create and activate the rich menu:

```bash
curl -X POST http://localhost:8000/api/richmenu/setup \
  -H "Content-Type: application/json" \
  -d '{"set_as_default": true}'
```

#### List All Rich Menus

Get all created rich menus:

```bash
curl http://localhost:8000/api/richmenu/list
```

#### Get Default Rich Menu

Check which rich menu is set as default:

```bash
curl http://localhost:8000/api/richmenu/default
```

#### Link Rich Menu to User

Link a specific rich menu to a user:

```bash
curl -X POST http://localhost:8000/api/richmenu/link \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "U1234567890abcdef",
    "rich_menu_id": "richmenu-abc123"
  }'
```

#### Unlink Rich Menu from User

Remove rich menu from a user:

```bash
curl -X DELETE http://localhost:8000/api/richmenu/unlink/U1234567890abcdef
```

#### Delete Rich Menu

Delete a rich menu:

```bash
curl -X DELETE http://localhost:8000/api/richmenu/richmenu-abc123
```

---

## Configuration

### Environment Variables

All configuration is done through environment variables in `.env`:

```bash
# Language Configuration
DEFAULT_LANGUAGE=id  # Default language for the bot (id, zh, or en)

# LINE Configuration
LINE_CHANNEL_SECRET=your_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
```

### Adding New Languages

To add support for new languages:

1. Add language code to `SUPPORTED_LANGUAGES` in `config.py`
2. Add message translations to `MESSAGES` dictionary in `config.py`
3. Update language detection service to recognize the new language

Example:

```python
# In config.py
SUPPORTED_LANGUAGES = {
    "id": "Bahasa Indonesia",
    "zh": "繁體中文",
    "en": "English",
    "vi": "Tiếng Việt",  # New language
}

MESSAGES = {
    # ... existing languages ...
    "vi": {
        "welcome": "Chào mừng bạn đến với IMIGO!",
        "cleared": "Lịch sử trò chuyện đã được xóa.",
        # ... other messages ...
    }
}
```

---

## Development

### Testing Language Switching

1. Send a message to the bot to register as a user
2. Send `/lang zh` to switch to Chinese
3. Bot responds with confirmation in Chinese
4. All subsequent responses will be in Chinese
5. Send `/lang id` to switch back to Indonesian

### Testing Rich Menu

1. Use the API to set up the rich menu:
   ```bash
   curl -X POST http://localhost:8000/api/richmenu/setup \
     -H "Content-Type: application/json" \
     -d '{"set_as_default": true}'
   ```

2. Open LINE app and check the chat with your bot
3. The rich menu should appear at the bottom of the chat
4. Tap buttons to test each category

### Customizing Rich Menu

Edit `rich_menu/menu_config.json` to customize:

- Menu size and layout
- Button positions (`bounds`)
- Button actions (`postback` data)
- Chat bar text

After making changes, recreate the rich menu using the setup API.

---

## API Documentation

Full API documentation is available at:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

---

## Emergency Contacts (Taiwan)

These emergency contacts are always available through the bot:

- **Police**: 110
- **Fire/Ambulance**: 119
- **Foreign Worker Hotline**: 1955
- **Indonesia Representative Office**: +886-2-2356-5156
- **Labor Hotline**: 1955
- **Anti-Trafficking Hotline**: 113
