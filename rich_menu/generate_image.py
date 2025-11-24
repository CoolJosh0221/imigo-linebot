#!/usr/bin/env python3
"""
Generate a rich menu image for LINE bot
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def create_rich_menu_image():
    """Create a 2500x1686 rich menu image"""

    # Image dimensions
    WIDTH = 2500
    HEIGHT = 1686
    BUTTON_WIDTH = 625
    BUTTON_HEIGHT_1 = 421  # Rows 2
    BUTTON_HEIGHT_2 = 422  # Row 3

    # Create image
    img = Image.new('RGB', (WIDTH, HEIGHT), color='white')
    draw = ImageDraw.Draw(img)

    # Colors
    HEADER_BG = '#2E5C8A'
    HEADER_TEXT = 'white'

    # Button colors (matching categories)
    COLORS = {
        'healthcare': '#5CB85C',   # Green
        'labor': '#5BC0DE',        # Light blue
        'language': '#F0AD4E',     # Orange
        'emergency': '#D9534F',    # Red
        'government': '#5BC0DE',   # Light blue
        'daily': '#5CB85C',        # Green
        'translate': '#F0AD4E',    # Orange
        'clear': '#777777',        # Gray
    }

    # Draw header area (top section)
    draw.rectangle([(0, 0), (WIDTH, 843)], fill=HEADER_BG)

    # Try to use a font, fallback to default if not available
    try:
        title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 100)
        button_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 50)
        emoji_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 80)
    except:
        title_font = ImageFont.load_default()
        button_font = ImageFont.load_default()
        emoji_font = ImageFont.load_default()

    # Draw title
    title = "IMIGO HELPER"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_width) // 2
    draw.text((title_x, 350), title, fill=HEADER_TEXT, font=title_font)

    # Draw subtitle
    subtitle = "Tap a category for help"
    try:
        subtitle_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
    except:
        subtitle_font = ImageFont.load_default()
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (WIDTH - subtitle_width) // 2
    draw.text((subtitle_x, 500), subtitle, fill=HEADER_TEXT, font=subtitle_font)

    # Define buttons (x, y, label, color_key)
    buttons = [
        # Row 2 (y: 843-1264)
        (0, 843, 'Healthcare\n🏥', 'healthcare'),
        (625, 843, 'Labor\n💼', 'labor'),
        (1250, 843, 'Language\n🌐', 'language'),
        (1875, 843, 'Emergency\n🚨', 'emergency'),

        # Row 3 (y: 1264-1686)
        (0, 1264, 'Government\n🏛️', 'government'),
        (625, 1264, 'Daily Life\n🏠', 'daily'),
        (1250, 1264, 'Translate\n🔤', 'translate'),
        (1875, 1264, 'Clear Chat\n🗑️', 'clear'),
    ]

    # Draw buttons
    for x, y, label, color_key in buttons:
        # Determine height based on row
        height = BUTTON_HEIGHT_1 if y == 843 else BUTTON_HEIGHT_2

        # Draw button background
        draw.rectangle(
            [(x, y), (x + BUTTON_WIDTH, y + height)],
            fill=COLORS[color_key],
            outline='white',
            width=3
        )

        # Draw label (centered)
        lines = label.split('\n')
        total_height = len(lines) * 60
        start_y = y + (height - total_height) // 2

        for i, line in enumerate(lines):
            font = emoji_font if i == 1 else button_font
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = x + (BUTTON_WIDTH - text_width) // 2
            text_y = start_y + (i * 60)
            draw.text((text_x, text_y), line, fill='white', font=font)

    return img


def main():
    """Generate and save the rich menu image"""
    output_dir = Path(__file__).parent
    output_path = output_dir / 'menu_image.png'

    print("Generating rich menu image...")
    img = create_rich_menu_image()

    print(f"Saving to {output_path}...")
    img.save(output_path, 'PNG')

    print(f"✓ Rich menu image created: {output_path}")
    print(f"  Size: {img.size[0]}x{img.size[1]} pixels")
    print(f"  Format: PNG")

    return str(output_path)


if __name__ == '__main__':
    main()
