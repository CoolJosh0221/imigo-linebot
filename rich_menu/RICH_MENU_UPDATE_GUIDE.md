# Rich Menu Update Guide

## Quick Start

**After updating `menu_config.json` or regenerating images:**

```bash
# 1. View current menus
python view_rich_menus.py

# 2. Update menus (cleanup old + create new)
python update_rich_menus.py

# 3. Verify changes
python view_rich_menus.py --details
```

**That's it!** Users will automatically get the new menus on their next interaction.

---

## How to Update Rich Menus with New Images and Configs

When you've generated new rich menu images (e.g., using `rich_menu/draw.py`) or updated the configuration, follow these steps to deploy them to your LINE bot.

---

## Method 1: Automatic Deployment (Recommended)

The app automatically creates/reuses language-specific rich menus on startup.

### Step 1: Prepare Your Files

Ensure you have these files in the `rich_menu/` directory:
```
rich_menu/
├── menu_config.json    # Button layout and actions
├── menu_en.png         # English menu image (2500x1686)
├── menu_id.png         # Indonesian menu image
├── menu_vi.png         # Vietnamese menu image
└── menu_zh.png         # Traditional Chinese menu image
```

### Step 2: Clean Up Old Menus (Optional but Recommended)

Create a cleanup script or use the API:

```python
# cleanup_rich_menus.py
import asyncio
from dependencies import get_rich_menu_service, initialize_services, cleanup_services

async def main():
    await initialize_services()
    rich_menu_service = await get_rich_menu_service()

    print("Deleting all existing rich menus...")
    success = await rich_menu_service.cleanup_all_rich_menus()

    if success:
        print("✓ All rich menus deleted successfully")
    else:
        print("✗ Failed to delete some menus")

    await cleanup_services()

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python cleanup_rich_menus.py
```

### Step 3: Restart the Application

The app will automatically create new rich menus on startup:

```bash
# Stop the app (Ctrl+C)
# Then restart:
uvicorn main:app --reload
```

Check logs for:
```
INFO: Rich menu created for en: richmenu-xxx with chatBarText: Tap for Help
INFO: Rich menu created for id: richmenu-yyy with chatBarText: Ketuk untuk Bantuan
INFO: Rich menu created for vi: richmenu-zzz with chatBarText: Nhấn để Trợ giúp
INFO: Rich menu created for zh: richmenu-www with chatBarText: 點擊尋求幫助
```

---

## Method 2: Manual Upload via Script

Create a deployment script:

```python
# deploy_rich_menus.py
import asyncio
from pathlib import Path
from dependencies import get_rich_menu_service, initialize_services, cleanup_services

async def deploy_language_menus():
    await initialize_services()
    rich_menu_service = await get_rich_menu_service()

    print("Creating language-specific rich menus...")
    menus = await rich_menu_service.create_language_rich_menus()

    print(f"\n✓ Created {len(menus)} rich menus:")
    for lang, menu_id in menus.items():
        print(f"  - {lang}: {menu_id}")

    await cleanup_services()

if __name__ == "__main__":
    asyncio.run(deploy_language_menus())
```

Run it:
```bash
python deploy_rich_menus.py
```

---

## Method 3: Using LINE Official Account Manager (Web Interface)

### Step 1: Access the Dashboard
1. Go to https://manager.line.biz/
2. Select your IMIGO bot account
3. Navigate to **Home** → **Rich menus**

### Step 2: Create New Rich Menu

For **each language** (en, id, vi, zh):

1. Click **"Create"** button
2. **Set Title:**
   - English: `English Menu`
   - Indonesian: `Menu Bahasa Indonesia`
   - Vietnamese: `Thực đơn Tiếng Việt`
   - Chinese: `繁體中文選單`

3. **Upload Image:**
   - Click "Upload image"
   - Select the corresponding file (e.g., `menu_en.png`)

4. **Define Tap Areas:**

   Create 6 tap areas matching your `menu_config.json`:

   | Area | Position (x, y, width, height) | Action Type | Data |
   |------|-------------------------------|-------------|------|
   | Healthcare | 0, 0, 833, 843 | Postback | category_healthcare |
   | Labor | 833, 0, 834, 843 | Postback | category_labor |
   | Language | 1667, 0, 833, 843 | Postback | category_language |
   | Emergency | 0, 843, 833, 843 | Postback | category_emergency |
   | Government | 833, 843, 834, 843 | Postback | category_government |
   | Translate | 1667, 843, 833, 843 | Postback | category_translate |

5. **Set Display Settings:**
   - Chat bar text (choose appropriate language):
     - `en`: "Tap for Help"
     - `id`: "Ketuk untuk Bantuan"
     - `vi`: "Nhấn để Trợ giúp"
     - `zh`: "點擊尋求幫助"

6. **Save** the rich menu

7. Note the Rich Menu ID (shown in the list view)

### Step 3: Link Menus to Users

You have two options:

**Option A: Set as Default (Simple but not language-specific)**
- Click the ⋮ menu next to one rich menu
- Select "Set as default"
- All users will see this menu

**Option B: Language-Specific Assignment (Recommended)**

Update your database with the new menu IDs:
```python
# update_menu_ids.py
import asyncio
from dependencies import get_rich_menu_service, initialize_services, cleanup_services

async def main():
    await initialize_services()
    rich_menu_service = await get_rich_menu_service()

    # Manually set the menu IDs you got from LINE Manager
    rich_menu_service.language_menus = {
        "en": "richmenu-abc123...",  # Copy from LINE Manager
        "id": "richmenu-def456...",
        "vi": "richmenu-ghi789...",
        "zh": "richmenu-jkl012...",
    }

    print("Menu IDs updated in service")
    # Users will get assigned menus when they next interact

    await cleanup_services()

asyncio.run(main())
```

---

## Updating Just the Images (No Config Changes)

If you only changed the images but kept the same button layout:

### Quick Update Script:
```python
# update_images_only.py
import asyncio
from pathlib import Path
from dependencies import get_rich_menu_service, initialize_services, cleanup_services

async def update_images():
    await initialize_services()
    rich_menu_service = await get_rich_menu_service()

    # Get existing menu IDs (assumes menus already created)
    menus = await rich_menu_service.get_rich_menu_list()

    language_map = {
        "English Menu": "en",
        "Menu Bahasa Indonesia": "id",
        "Thực đơn Tiếng Việt": "vi",
        "繁體中文選單": "zh",
    }

    for menu in menus:
        lang = language_map.get(menu.name)
        if lang:
            image_path = f"rich_menu/menu_{lang}.png"
            print(f"Uploading {image_path} to {menu.rich_menu_id}...")
            success = await rich_menu_service.upload_rich_menu_image(
                menu.rich_menu_id,
                image_path
            )
            print(f"  {'✓' if success else '✗'} {menu.name}")

    await cleanup_services()

asyncio.run(update_images())
```

Run it:
```bash
python update_images_only.py
```

---

## Updating the Config (Button Layout Changes)

If you changed `menu_config.json` (different button positions or actions):

### You MUST recreate the menus:

**Option 1: Use the Update Script (Recommended)**
```bash
# Full update: cleanup old menus + create new ones
python update_rich_menus.py

# Preview what will happen (dry run)
python update_rich_menus.py --dry-run

# Force recreation even if menus exist
python update_rich_menus.py --force
```

**Option 2: Restart the App**
```bash
# Clean up old menus first
python update_rich_menus.py --cleanup-only

# Then restart app (auto-creates with new config)
uvicorn main:app --reload
```

**Why?** LINE doesn't allow modifying button areas after creation. You must delete and recreate.

---

## Rich Menu Management Scripts

Three utility scripts are provided for easy management:

### 1. `view_rich_menus.py` - View Current Status

```bash
# Basic view
python view_rich_menus.py

# Show detailed area information
python view_rich_menus.py --details

# Export to JSON file
python view_rich_menus.py --export
```

**Output includes:**
- Total number of menus
- Default menu (if set)
- Language menu mappings
- Menu details (size, areas, chat bar text)

### 2. `update_rich_menus.py` - Update/Recreate Menus

```bash
# Full update (cleanup + create)
python update_rich_menus.py

# Preview changes without making them
python update_rich_menus.py --dry-run

# Only delete existing menus
python update_rich_menus.py --cleanup-only

# Only create new menus (keep existing)
python update_rich_menus.py --skip-cleanup

# Force recreation even if menus exist
python update_rich_menus.py --force
```

**What it does:**
1. Verifies all image files exist (menu_en.png, menu_id.png, etc.)
2. Deletes existing menus (if not skipped)
3. Creates new menus from config
4. Uploads images for each language
5. Reports success/failure for each step

### 3. `force_link_menu.py` - Link Menu to User

```bash
# Link specific user to a language menu
python force_link_menu.py U1234567890abcdef en

# Link another user to Indonesian menu
python force_link_menu.py U9876543210fedcba id

# Relink all users (requires database implementation)
python force_link_menu.py --all
```

**Use this when:**
- Testing with specific users
- Manually fixing user menu assignments
- User reports not seeing the correct menu

---

## Testing Your Changes

### 1. View Current Menu Status

```bash
python view_rich_menus.py
```

### 2. Test on Your LINE Account

- Open LINE app
- Go to your bot chat
- Look at the bottom - you should see the new menu
- Tap each button to verify actions work

### 3. Check Logs

Monitor the console for postback events:

```
INFO: Postback event: category_healthcare from user abc12345
```

---

## Troubleshooting

### ❌ Menu doesn't appear for users

**Solution 1: Restart the app** (forces menu recreation)

**Solution 2: Manually link menus:**
```python
# force_link_menu.py
import asyncio
from dependencies import get_rich_menu_service, get_database_service, initialize_services, cleanup_services

async def force_link(user_id, language):
    await initialize_services()
    rich_menu_service = await get_rich_menu_service()

    success = await rich_menu_service.set_user_rich_menu(user_id, language)
    print(f"{'✓' if success else '✗'} Linked {language} menu to user")

    await cleanup_services()

# Example usage:
# asyncio.run(force_link("U1234567890abcdef", "en"))
```

### ❌ "Image not found" errors

Check file paths:
```bash
ls -lh rich_menu/menu_*.png
```

Ensure files are exactly 2500x1686 pixels:
```bash
file rich_menu/menu_*.png
```

### ❌ Buttons trigger wrong actions

Verify `menu_config.json` matches your image layout. Use the `draw.py` script to regenerate images that match the config perfectly.

---

## Best Practices

1. **Always test locally first** before deploying to production
2. **Keep backup copies** of working menu images
3. **Version control** your `menu_config.json` and image generation scripts
4. **Document custom button positions** if you change the layout
5. **Clean up old menus** periodically to avoid hitting LINE's limit (1000 menus per channel)

---

## Quick Reference: File Locations

```
Project Structure:
├── rich_menu/
│   ├── menu_config.json      # Button layout and actions
│   ├── menu_en.png           # English menu (2500x1686)
│   ├── menu_id.png           # Indonesian menu
│   ├── menu_vi.png           # Vietnamese menu
│   ├── menu_zh.png           # Chinese menu
│   └── draw.py               # Script to generate menu images
├── services/
│   └── rich_menu_service.py  # Rich menu management logic
└── main.py                   # Auto-creates menus on startup
```

---

## Need Help?

1. Check the logs: `tail -f logs/app.log`
2. Review LINE Messaging API docs: https://developers.line.biz/en/docs/messaging-api/using-rich-menus/
3. Verify your images: https://www.linebot-designer.com/ (unofficial visualizer)
