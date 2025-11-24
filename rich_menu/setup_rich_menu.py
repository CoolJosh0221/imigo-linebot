#!/usr/bin/env python3
"""
Setup rich menu for IMIGO LINE bot
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from linebot.v3.messaging import AsyncApiClient, AsyncMessagingApi, Configuration
from services.rich_menu_service import RichMenuService
from dotenv import load_dotenv


async def setup_rich_menu():
    """Setup rich menu with image"""
    # Load environment variables
    load_dotenv()

    line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    if not line_token:
        print("❌ ERROR: LINE_CHANNEL_ACCESS_TOKEN not found in .env")
        return False

    # Initialize LINE API
    config = Configuration(access_token=line_token)
    async with AsyncApiClient(config) as client:
        line_api = AsyncMessagingApi(client)
        service = RichMenuService(line_api)

        print("📋 Creating rich menu...")
        rich_menu_id = await service.create_rich_menu()

        if not rich_menu_id:
            print("❌ Failed to create rich menu")
            return False

        print(f"✓ Rich menu created: {rich_menu_id}")

        # Check if image exists
        image_path = Path(__file__).parent / 'menu_image.png'
        if not image_path.exists():
            print(f"\n⚠️  Image not found: {image_path}")
            print("Generating image...")

            # Import and run generator
            from generate_image import create_rich_menu_image
            img = create_rich_menu_image()
            img.save(image_path, 'PNG')
            print(f"✓ Image generated: {image_path}")

        # Upload image
        print(f"\n📤 Uploading image...")
        success = await service.upload_rich_menu_image(rich_menu_id, str(image_path))

        if not success:
            print("❌ Failed to upload image")
            return False

        print("✓ Image uploaded")

        # Set as default
        print(f"\n⚙️  Setting as default rich menu...")
        success = await service.set_default_rich_menu(rich_menu_id)

        if not success:
            print("❌ Failed to set as default")
            return False

        print("✓ Set as default")

        print(f"\n{'='*60}")
        print(f"✅ SUCCESS! Rich menu is now active")
        print(f"{'='*60}")
        print(f"\nRich Menu ID: {rich_menu_id}")
        print(f"\n📱 Open your LINE app and check the bot chat")
        print(f"   The rich menu should appear at the bottom!")
        print(f"\n💡 If you don't see it:")
        print(f"   1. Restart LINE app")
        print(f"   2. Send any message to the bot")
        print(f"   3. Wait a few seconds")

        return True


async def list_rich_menus():
    """List all rich menus"""
    load_dotenv()

    line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    if not line_token:
        print("❌ ERROR: LINE_CHANNEL_ACCESS_TOKEN not found")
        return

    config = Configuration(access_token=line_token)
    async with AsyncApiClient(config) as client:
        line_api = AsyncMessagingApi(client)
        service = RichMenuService(line_api)

        print("\n📋 Listing all rich menus...")
        menus = await service.get_rich_menu_list()

        if not menus:
            print("No rich menus found")
            return

        print(f"\nFound {len(menus)} rich menu(s):")
        for i, menu in enumerate(menus, 1):
            print(f"\n{i}. {menu.name}")
            print(f"   ID: {menu.rich_menu_id}")
            print(f"   Chat Bar Text: {menu.chat_bar_text}")
            print(f"   Selected: {menu.selected}")

        # Check default
        default_id = await service.get_default_rich_menu_id()
        if default_id:
            print(f"\n✓ Default rich menu: {default_id}")
        else:
            print(f"\n⚠️  No default rich menu set")


async def delete_all_rich_menus():
    """Delete all rich menus"""
    load_dotenv()

    line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    if not line_token:
        print("❌ ERROR: LINE_CHANNEL_ACCESS_TOKEN not found")
        return

    config = Configuration(access_token=line_token)
    async with AsyncApiClient(config) as client:
        line_api = AsyncMessagingApi(client)
        service = RichMenuService(line_api)

        print("\n🗑️  Deleting all rich menus...")
        menus = await service.get_rich_menu_list()

        if not menus:
            print("No rich menus to delete")
            return

        for menu in menus:
            print(f"Deleting: {menu.rich_menu_id}...")
            await service.delete_rich_menu(menu.rich_menu_id)

        print(f"✓ Deleted {len(menus)} rich menu(s)")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='IMIGO Rich Menu Setup')
    parser.add_argument('action', choices=['setup', 'list', 'delete'],
                       help='Action to perform')

    args = parser.parse_args()

    if args.action == 'setup':
        asyncio.run(setup_rich_menu())
    elif args.action == 'list':
        asyncio.run(list_rich_menus())
    elif args.action == 'delete':
        confirm = input("⚠️  Delete ALL rich menus? (yes/no): ")
        if confirm.lower() == 'yes':
            asyncio.run(delete_all_rich_menus())
        else:
            print("Cancelled")


if __name__ == '__main__':
    main()
