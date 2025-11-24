# Rich Menu Setup Guide

## Quick Setup

Rich menus need both a structure (JSON config) and an image. Here's how to set it up:

### Step 1: Create Rich Menu Image

**Requirements:**
- Size: **2500 x 1686 pixels**
- Format: PNG or JPEG
- Max file size: 1 MB

**Layout for our 8-button menu:**
```
Row 1 (y: 0-843):    [Top image area]
Row 2 (y: 843-1264): [🏥 Healthcare] [💼 Labor] [🌐 Language] [🚨 Emergency]
Row 3 (y: 1264-1686):[🏛️ Government] [🏠 Daily] [🔤 Translate] [🗑️ Clear]
```

Each button: **625 x 421 pixels**

### Step 2: Simple Template (Text-based)

You can create a simple rich menu using Python:

```python
from PIL import Image, ImageDraw, ImageFont

# Create blank image
img = Image.new('RGB', (2500, 1686), color='#4A90E2')
draw = ImageDraw.Draw(img)

# Add title area
draw.rectangle([(0, 0), (2500, 843)], fill='#2E5C8A')
draw.text((1250, 420), "IMIGO Helper", fill='white', anchor='mm', font=ImageFont.truetype('arial.ttf', 120))

# Draw buttons
buttons = [
    # Row 2
    (0, 843, '🏥\nHealth', '#5CB85C'),
    (625, 843, '💼\nWork', '#5BC0DE'),
    (1250, 843, '🌐\nLanguage', '#F0AD4E'),
    (1875, 843, '🚨\nEmergency', '#D9534F'),
    # Row 3
    (0, 1264, '🏛️\nGovt', '#5BC0DE'),
    (625, 1264, '🏠\nDaily', '#5CB85C'),
    (1250, 1264, '🔤\nTranslate', '#F0AD4E'),
    (1875, 1264, '🗑️\nClear', '#777'),
]

for x, y, text, color in buttons:
    draw.rectangle([(x, y), (x+625, y+422)], fill=color, outline='white', width=5)
    draw.text((x+312, y+211), text, fill='white', anchor='mm', font=ImageFont.truetype('arial.ttf', 60))

img.save('rich_menu/menu_image.png')
```

### Step 3: Upload via API

```bash
# Create rich menu and upload image
curl -X POST http://localhost:8000/api/richmenu/setup \
  -H "Content-Type: application/json" \
  -d '{
    "set_as_default": true,
    "image_path": "rich_menu/menu_image.png"
  }'
```

Or upload to existing menu:

```bash
curl -X POST http://localhost:8000/api/richmenu/upload-image \
  -H "Content-Type: application/json" \
  -d '{
    "rich_menu_id": "richmenu-xxx",
    "image_path": "rich_menu/menu_image.png"
  }'
```

### Step 4: Verify

Open LINE app → Your bot should show the rich menu at the bottom

---

## Using LINE Official Account Manager (Alternative)

1. Go to https://manager.line.biz/
2. Select your bot
3. Go to "Rich menus" → "Create"
4. Upload your 2500x1686 image
5. Draw clickable areas matching `menu_config.json` positions
6. Set actions for each area (use same postback data)
7. Set as default

---

## Troubleshooting

**Rich menu doesn't show:**
- Check if image was uploaded: `GET /api/richmenu/default`
- Verify default is set
- Try unlinking then relinking: `DELETE /api/richmenu/unlink/{user_id}`
- Restart LINE app

**Buttons don't work:**
- Check postback data matches `menu_config.json`
- View logs for postback events
- Verify action types are "postback"

**Image looks wrong:**
- Verify exact size: 2500x1686
- Check file format: PNG or JPEG only
- Max 1 MB file size
- Button positions must align with drawn areas

---

## Quick Test Without Image

You can test postback handling without an image:

```bash
# Just create the menu structure
curl -X POST http://localhost:8000/api/richmenu/setup \
  -H "Content-Type: application/json" \
  -d '{"set_as_default": true}'
```

Then trigger postback events from LINE Messaging API console or another test tool.

---

## Button Actions Reference

From `menu_config.json`:

```
Healthcare:  category_healthcare
Labor:       category_labor
Language:    category_language (shows quick reply buttons)
Emergency:   category_emergency
Government:  category_government
Daily Life:  category_daily
Translate:   category_translate
Clear Chat:  clear_chat
```

For language switching via postback: `lang_id`, `lang_zh`, `lang_en`
