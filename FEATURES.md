# IMIGO Features Guide

## Dynamic Language Switching

IMIGO supports multiple ways for users to change their preferred language at any time.

### Supported Languages

- **Indonesian** (`id`) - Bahasa Indonesia
- **Traditional Chinese** (`zh`) - 繁體中文
- **English** (`en`) - English
- **Vietnamese** (`vi`) - Tiếng Việt

### How to Switch Language

**Method 1: Text Command**
```
/lang id   # Switch to Indonesian
/lang zh   # Switch to Chinese
/lang en   # Switch to English
/lang vi   # Switch to Vietnamese
```

**Method 2: Quick Reply Buttons**
- Tap the "Language" button in the rich menu
- Bot shows language options with quick reply buttons
- Tap your preferred language

**Method 3: Postback Actions**
- Rich menu or flex messages can trigger language change
- Use postback data: `lang_id`, `lang_zh`, `lang_en`, or `lang_vi`

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

## Language-Specific Rich Menu Support

IMIGO features an advanced rich menu system that automatically adapts to each user's language preference. Every user sees a rich menu with buttons and text in their chosen language.

### How It Works

1. **Automatic Menu Creation**: On startup, the bot creates 4 separate rich menus (English, Indonesian, Chinese, Vietnamese)
2. **User Assignment**: Each user is automatically assigned the rich menu matching their language preference
3. **Dynamic Updates**: When a user changes their language, their rich menu updates immediately
4. **Persistent**: Rich menu preference persists across all chat sessions

### Rich Menu Categories

The rich menu includes 8 functional buttons organized in a 3x2 grid layout:

**Top Row (4 buttons):**
1. **Healthcare** - Medical information and health services
2. **Labor** - Work-related issues and labor rights
3. **Language** - Change language preferences
4. **Emergency** - Emergency contacts and hotlines

**Bottom Row (4 buttons):**
5. **Government** - Government services and documentation
6. **Daily Life** - Daily living assistance
7. **Translation** - Translation services
8. **Clear Chat** - Clear conversation history

### Technical Details

- **Image Dimensions**: 2500 x 1686 pixels
- **Layout**: 3 columns x 2 rows (with 8 tap areas)
- **Button Size**: Each button is approximately 625 x 421-422 pixels
- **Supported Formats**: PNG images with transparency support
- **Location**: Images stored in `rich_menu/menu_*.png`
  - `menu_en.png` - English menu
  - `menu_id.png` - Indonesian menu
  - `menu_vi.png` - Vietnamese menu
  - `menu_zh.png` - Chinese menu

### Rich Menu Management API

The bot automatically creates and manages language-specific rich menus. However, you can manually manage them using these API endpoints:

#### Setup Rich Menu

Create and activate rich menus (typically done automatically on startup):

```bash
curl -X POST http://localhost:8000/api/richmenu/setup \
  -H "Content-Type: application/json" \
  -d '{"set_as_default": false}'
```

Note: Setting `set_as_default: true` is not recommended with language-specific menus, as users should have individual menu assignments based on their language.

#### List All Rich Menus

Get all created rich menus with their language variants:

```bash
curl http://localhost:8000/api/richmenu/list
```

Response includes menu IDs, names, and configuration for each language.

#### Get Default Rich Menu

Check which rich menu is set as default (if any):

```bash
curl http://localhost:8000/api/richmenu/default
```

#### Link Rich Menu to User

Manually link a specific rich menu to a user (usually handled automatically):

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

Delete a specific rich menu:

```bash
curl -X DELETE http://localhost:8000/api/richmenu/richmenu-abc123
```

### Programmatic Access

The `RichMenuService` class provides methods for managing language-specific menus:

```python
from services.rich_menu_service import RichMenuService

# Create all language menus
language_menus = await rich_menu_service.create_language_rich_menus()

# Get menu ID for a specific language
menu_id = rich_menu_service.get_rich_menu_for_language("en")

# Set user's rich menu based on their language
await rich_menu_service.set_user_rich_menu(user_id, "zh")

# Cleanup all rich menus (useful for testing)
await rich_menu_service.cleanup_all_rich_menus()
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

1. **Update Configuration** - Add language code to `SUPPORTED_LANGUAGES` in `config.py`
2. **Add Translations** - Add message translations to `MESSAGES` dictionary in `config.py`
3. **Create Rich Menu Image** - Design and create `rich_menu/menu_[code].png` (2500 x 1686 pixels)
4. **Update Rich Menu Service** - Add language code to `supported_languages` list in `RichMenuService.create_language_rich_menus()`
5. **Add Language Name** - Update `language_names` dictionary with the localized menu name
6. **Update Language Detection** - Configure language detection service to recognize the new language

Example:

```python
# In config.py
SUPPORTED_LANGUAGES = {
    "id": "Bahasa Indonesia",
    "zh": "繁體中文",
    "en": "English",
    "vi": "Tiếng Việt",
    "th": "ภาษาไทย",  # New language
}

MESSAGES = {
    # ... existing languages ...
    "th": {
        "welcome": "ยินดีต้อนรับสู่ IMIGO!",
        "cleared": "ประวัติการสนทนาถูกลบแล้ว",
        "language_changed": "เปลี่ยนภาษาเป็นภาษาไทยแล้ว",
        "language_select": "เลือกภาษาของคุณ",
        "help": "วิธีใช้ IMIGO...",
    }
}

# In services/rich_menu_service.py
supported_languages = ["en", "id", "vi", "zh", "th"]  # Add new language
language_names = {
    "en": "English Menu",
    "id": "Menu Bahasa Indonesia",
    "vi": "Thực đơn Tiếng Việt",
    "zh": "繁體中文選單",
    "th": "เมนูภาษาไทย",  # Add localized name
}
```

After adding a new language, restart the application to create the new rich menu.

---

## Development

### Testing Language Switching

1. **First Contact**: Send a message to the bot to register as a new user
2. **Auto-Detection**: Bot detects your language and assigns appropriate rich menu
3. **Manual Switch**: Send `/lang zh` to switch to Chinese
4. **Confirmation**: Bot responds with confirmation in Chinese
5. **Rich Menu Update**: Your rich menu automatically changes to Chinese version
6. **Verify**: All subsequent responses and the rich menu will be in Chinese
7. **Switch Again**: Send `/lang id` to switch back to Indonesian

### Testing Rich Menu

1. **Automatic Setup**: Rich menus are created automatically when the bot starts

   To manually trigger setup:
   ```bash
   curl -X POST http://localhost:8000/api/richmenu/setup \
     -H "Content-Type: application/json" \
     -d '{"set_as_default": false}'
   ```

2. **Verify Creation**: Check that all language menus were created
   ```bash
   curl http://localhost:8000/api/richmenu/list
   ```

3. **Test in LINE App**:
   - Open LINE app and navigate to your bot chat
   - The rich menu should appear at the bottom of the chat
   - Menu should be in your preferred language
   - Tap buttons to test each category

4. **Test Language Switch**:
   - Tap the "Language" button in the rich menu
   - Select a different language
   - Observe the rich menu update to the new language

### Customizing Rich Menu

#### Configuration File

Edit `rich_menu/menu_config.json` to customize button behavior:

- Menu size and dimensions
- Button positions (`bounds` - x, y, width, height in pixels)
- Button actions (`postback` data)
- Chat bar text (shown when menu is collapsed)

Example button configuration:
```json
{
  "bounds": {
    "x": 0,
    "y": 843,
    "width": 625,
    "height": 421
  },
  "action": {
    "type": "postback",
    "data": "category_healthcare"
  }
}
```

#### Rich Menu Images

To customize the visual appearance:

1. Edit or create new images in `rich_menu/` directory
2. Ensure images are exactly 2500 x 1686 pixels
3. Use PNG format for best quality
4. Name files as `menu_[language_code].png`
5. Maintain consistent button layout across all language versions
6. Use the provided `draw.py` script to generate images programmatically

After making changes to images or configuration:
1. Delete existing rich menus (optional)
2. Restart the application to recreate menus with new content

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
