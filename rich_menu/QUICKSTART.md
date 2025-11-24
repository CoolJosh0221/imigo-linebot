# Rich Menu Quick Start

## Setup Rich Menu in 2 Steps

### Step 1: Generate Image

```bash
cd rich_menu
python3 generate_image.py
```

This creates `menu_image.png` (2500x1686 pixels) with all 8 buttons.

### Step 2: Upload to LINE

```bash
python3 setup_rich_menu.py setup
```

This will:
1. ✓ Create rich menu structure
2. ✓ Upload the image
3. ✓ Set as default for all users

**Done!** Open LINE app and check your bot - the menu should appear at the bottom.

---

## Commands

```bash
# Setup rich menu (with image)
python3 setup_rich_menu.py setup

# List all rich menus
python3 setup_rich_menu.py list

# Delete all rich menus
python3 setup_rich_menu.py delete
```

---

## Requirements

Install Pillow for image generation:

```bash
pip install Pillow
```

Or using uv:

```bash
uv pip install Pillow
```

---

## Troubleshooting

**Rich menu doesn't appear:**
1. Restart LINE app
2. Send a message to the bot
3. Wait 5-10 seconds
4. Check if default is set: `python3 setup_rich_menu.py list`

**Image upload fails:**
- Check image size: must be exactly 2500x1686 pixels
- Check file size: must be under 1 MB
- Check format: PNG or JPEG only

**Script fails:**
- Make sure `.env` has `LINE_CHANNEL_ACCESS_TOKEN`
- Check you have Pillow installed
- Run from project root directory

---

## Button Layout

```
┌─────────────────────────────────────────────┐
│                                             │
│              IMIGO HELPER                   │
│         Tap a category for help             │
│                                             │
├───────────┬───────────┬───────────┬─────────┤
│ Healthcare│  Labor    │ Language  │Emergency│
│    🏥     │    💼     │    🌐     │   🚨    │
├───────────┼───────────┼───────────┼─────────┤
│Government │Daily Life │ Translate │  Clear  │
│    🏛️     │    🏠     │    🔤     │   🗑️    │
└───────────┴───────────┴───────────┴─────────┘
```

---

## Customize Image

Edit `generate_image.py`:

```python
# Change colors
COLORS = {
    'healthcare': '#5CB85C',   # Your color
    'labor': '#5BC0DE',        # Your color
    # ...
}

# Change title
title = "YOUR BOT NAME"

# Change button labels
buttons = [
    (0, 843, 'Your Label\n🏥', 'healthcare'),
    # ...
]
```

Then regenerate:

```bash
python3 generate_image.py
python3 setup_rich_menu.py setup
```

---

## Alternative: Use LINE Manager

Instead of scripts, you can use LINE Official Account Manager:

1. Go to https://manager.line.biz/
2. Select your bot
3. Go to "Rich menus" → "Create"
4. Upload your generated image
5. Draw clickable areas (match coordinates from `menu_config.json`)
6. Set postback actions (use same data as config)
7. Publish and set as default

This gives you a visual editor but requires manual setup.
