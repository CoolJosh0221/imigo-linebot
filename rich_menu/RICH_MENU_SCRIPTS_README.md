# Rich Menu Management Scripts

Three powerful utility scripts for managing LINE rich menus.

## Scripts Overview

### 📊 `view_rich_menus.py` - Inspect Current Menus

View all rich menus and their status.

```bash
python view_rich_menus.py               # Basic view
python view_rich_menus.py --details     # Show clickable areas
python view_rich_menus.py --export      # Export to JSON
```

**Shows:**
- Total number of menus
- Default menu (if set)
- Language mappings (en, id, vi, zh)
- Menu sizes and areas
- Chat bar text for each language

---

### 🔄 `update_rich_menus.py` - Update/Recreate Menus

Deploy config changes and new images.

```bash
python update_rich_menus.py                # Full update
python update_rich_menus.py --dry-run      # Preview changes
python update_rich_menus.py --force        # Force recreation
python update_rich_menus.py --cleanup-only # Only delete
```

**Workflow:**
1. ✓ Verifies image files exist (menu_*.png)
2. ✓ Validates file sizes (<1MB)
3. ✓ Deletes old menus (optional)
4. ✓ Creates new menus from config
5. ✓ Uploads language-specific images
6. ✓ Reports detailed status

**Use when:**
- Changed `menu_config.json` button layout
- Generated new menu images
- Need to recreate menus from scratch

---

### 🔗 `force_link_menu.py` - Link Menu to User

Manually assign menus to specific users.

```bash
python force_link_menu.py U1234567890abcdef en  # Link English menu
python force_link_menu.py U9876543210fedcba id  # Link Indonesian menu
python force_link_menu.py --all                 # Relink all users
```

**Use when:**
- Testing with specific user IDs
- User reports seeing wrong menu
- Manually fixing menu assignments

---

## Common Workflows

### Scenario 1: Button Layout Changed

You modified `menu_config.json` (changed positions/actions):

```bash
# Step 1: View current status
python view_rich_menus.py

# Step 2: Update (will delete old and create new)
python update_rich_menus.py

# Step 3: Verify
python view_rich_menus.py --details
```

### Scenario 2: New Images Only

You regenerated images but kept same layout:

```bash
# Option A: Full update (safest)
python update_rich_menus.py

# Option B: Manual re-upload (if menus exist)
# Use the update_images_only.py script from the guide
```

### Scenario 3: First Time Setup

No menus exist yet:

```bash
# Create all language menus
python update_rich_menus.py

# Or let app create them on startup
uvicorn main:app --reload
```

### Scenario 4: Clean Slate

Start fresh by deleting everything:

```bash
# Delete all menus
python update_rich_menus.py --cleanup-only

# Then recreate
python update_rich_menus.py --skip-cleanup
```

---

## File Requirements

Before running `update_rich_menus.py`, ensure you have:

```
rich_menu/
├── menu_config.json  ✓ Button layout config
├── menu_en.png       ✓ 2500x1686, <1MB
├── menu_id.png       ✓ 2500x1686, <1MB
├── menu_vi.png       ✓ 2500x1686, <1MB
└── menu_zh.png       ✓ 2500x1686, <1MB
```

---

## Troubleshooting

### ❌ "Image file does not exist"

**Solution:** Check file paths and names:
```bash
ls -lh rich_menu/menu_*.png
```

### ❌ "No rich menu found for language"

**Solution:** Create menus first:
```bash
python update_rich_menus.py
```

### ❌ "Failed to link menu to user"

**Possible causes:**
- Invalid user ID format (must start with 'U')
- Menu doesn't exist for that language
- LINE API error

**Solution:**
```bash
# Verify menus exist
python view_rich_menus.py

# Recreate if needed
python update_rich_menus.py
```

### ⚠️ Script hangs or times out

**Solution:** Check your `.env` file has valid credentials:
```bash
LINE_CHANNEL_SECRET=...
LINE_CHANNEL_ACCESS_TOKEN=...
```

---

## Script Options Reference

### `view_rich_menus.py`

| Option | Description |
|--------|-------------|
| (none) | Basic menu list |
| `--details` | Show clickable areas |
| `--export` | Export to JSON file |

### `update_rich_menus.py`

| Option | Description |
|--------|-------------|
| (none) | Full update (cleanup + create) |
| `--dry-run` | Preview without changes |
| `--force` | Recreate even if exists |
| `--cleanup-only` | Only delete menus |
| `--skip-cleanup` | Only create menus |

### `force_link_menu.py`

| Usage | Description |
|-------|-------------|
| `<user_id> <lang>` | Link menu to user |
| `--all` | Relink all users |

---

## Integration with Main App

The main app (`main.py`) automatically:

1. **On Startup:** Creates language menus if they don't exist
2. **On Follow Event:** Shows welcome message with language selection
3. **On Language Change:** Updates user's rich menu
4. **On Message:** Ensures user has correct menu

**So typically you only need these scripts when:**
- Deploying config/image updates
- Troubleshooting menu issues
- Manual testing/debugging

---

## Advanced: Database Integration

To enable `force_link_menu.py --all`, implement in `DatabaseService`:

```python
async def get_all_users(self) -> List[Dict]:
    """Get all users with their language preferences"""
    # Example implementation
    async with self.get_session() as session:
        result = await session.execute(
            select(User.user_id, User.language)
        )
        return [{"user_id": row[0], "language": row[1]} for row in result]
```

Then uncomment the implementation in `force_link_menu.py`.

---

## Quick Reference

```bash
# View menus
python view_rich_menus.py

# Update menus
python update_rich_menus.py

# Link to user
python force_link_menu.py U1234567890abcdef en

# Full workflow
python view_rich_menus.py && \
python update_rich_menus.py && \
python view_rich_menus.py --details
```

For detailed information, see [RICH_MENU_UPDATE_GUIDE.md](RICH_MENU_UPDATE_GUIDE.md)
