from PIL import Image, ImageDraw, ImageFont
import urllib.request
import os

TRANSLATIONS = {
    "en": {
        "buttons": {
            "health": "Health & Medical",
            "work": "Work & Employment",
            "language": "Switch Language",
            "emergency": "Emergency Help",
            "govt": "Government Services",
            "translate": "Translate Text",
        }
    },
    "zh": {
        "buttons": {
            "health": "健康與醫療",
            "work": "工作與就業",
            "language": "切換語言",
            "emergency": "緊急協助",
            "govt": "政府服務",
            "translate": "文字翻譯",
        }
    },
    "id": {
        "buttons": {
            "health": "Kesehatan & Medis",
            "work": "Pekerjaan & Kerja",
            "language": "Ganti Bahasa",
            "emergency": "Bantuan Darurat",
            "govt": "Layanan Pemerintah",
            "translate": "Terjemahkan Teks",
        }
    },
    "vi": {
        "buttons": {
            "health": "Sức Khỏe & Y Tế",
            "work": "Việc Làm & Lao Động",
            "language": "Đổi Ngôn Ngữ",
            "emergency": "Trợ Giúp Khẩn Cấp",
            "govt": "Dịch Vụ Chính Phủ",
            "translate": "Dịch Văn Bản",
        }
    },
}


def download_openmoji_icons():
    """Download colored OpenMoji icons"""
    os.makedirs("icons", exist_ok=True)

    # OpenMoji CDN - using 618x618 color PNGs
    base_url = (
        "https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/color/618x618/"
    )

    # OpenMoji hex codes for relevant emojis
    icons = {
        "health": "E090.png",
        "work": "1F4BC.png",
        "language": "1F4AC.png",
        "emergency": "1F6A8.png",
        "govt": "1F3DB.png",
        "translate": "1F310.png",
    }

    for key, filename in icons.items():
        filepath = f"icons/{key}.png"
        if not os.path.exists(filepath):
            url = f"{base_url}{filename}"
            print(f"Downloading {key} icon from OpenMoji...")
            try:
                urllib.request.urlretrieve(url, filepath)
                print(f"  ✓ Downloaded {key}")
            except Exception as e:
                print(f"  ✗ Could not download {key}: {e}")


def get_font(size, bold=False, language="en"):
    """Get appropriate font based on language"""
    if language == "zh":
        font_name = "NotoSansTC-Bold.ttf" if bold else "NotoSansTC-Regular.ttf"
    else:
        font_name = "NotoSans-Bold.ttf" if bold else "NotoSans-Regular.ttf"

    font_path = f"fonts/{font_name}"
    try:
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()


def generate_menu(language="en"):
    """Generate menu image in specified language"""
    trans = TRANSLATIONS.get(language, TRANSLATIONS["en"])

    # Dimensions - 3 columns x 2 rows
    WIDTH = 2500
    HEIGHT = 1686
    BUTTON_WIDTH = WIDTH // 3
    BUTTON_HEIGHT = HEIGHT // 2

    # Clean color palette
    COLORS = {
        "primary": "#0EA5E9",
        "secondary": "#0284C7",
        "bg": "#F0F9FF",
        "text_white": "#FFFFFF",
        "border": "#E0F2FE",
    }

    # Create image
    img = Image.new("RGB", (WIDTH, HEIGHT), color=COLORS["bg"])
    draw = ImageDraw.Draw(img)

    # Load font
    button_font = get_font(68, bold=True, language=language)

    # Button definitions
    button_keys = ["health", "work", "language", "emergency", "govt", "translate"]

    # Draw buttons
    for idx, key in enumerate(button_keys):
        row = idx // 3
        col = idx % 3
        x = col * BUTTON_WIDTH
        y = row * BUTTON_HEIGHT

        # Alternate colors
        color = COLORS["primary"] if idx % 2 == 0 else COLORS["secondary"]

        # Draw button background
        padding = 8
        draw.rectangle(
            [
                (x + padding, y + padding),
                (x + BUTTON_WIDTH - padding, y + BUTTON_HEIGHT - padding),
            ],
            fill=color,
            outline=COLORS["border"],
            width=4,
        )

        # Load and paste colored icon
        icon_path = f"icons/{key}.png"
        if os.path.exists(icon_path):
            try:
                icon = Image.open(icon_path).convert("RGBA")
                # Resize icon
                icon_size = 350
                icon = icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)

                # Calculate position (upper portion of button)
                icon_x = x + (BUTTON_WIDTH - icon_size) // 2
                icon_y = y + BUTTON_HEIGHT // 4 - icon_size // 4

                # Paste icon with transparency
                img.paste(icon, (icon_x, icon_y), icon)
            except Exception as e:
                print(f"Warning: Could not load icon {key}: {e}")

        # Draw text below icon
        text = trans["buttons"][key]
        bbox = draw.textbbox((0, 0), text, font=button_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = x + (BUTTON_WIDTH - text_width) // 2
        text_y = y + BUTTON_HEIGHT * 3 // 4 - text_height // 2

        draw.text((text_x, text_y), text, fill=COLORS["text_white"], font=button_font)

    return img


# Download OpenMoji icons
print("Downloading OpenMoji colored icons...\n")
download_openmoji_icons()

# Generate menus
print("\nGenerating modern multilingual menus...\n")
for lang_code, lang_name in [
    ("en", "English"),
    ("zh", "中文"),
    ("id", "Indonesian"),
    ("vi", "Vietnamese"),
]:
    print(f"Generating {lang_name} ({lang_code})...")
    menu_img = generate_menu(lang_code)
    menu_img.save(f"menu_{lang_code}.png")
    print(f"  ✓ Saved menu_{lang_code}.png\n")

print("✨ Done!")
