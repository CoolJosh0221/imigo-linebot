import asyncio
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

from config import load_config
from dependencies import (
    get_rich_menu_service,
    initialize_services,
    cleanup_services,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


async def view_menus(show_details: bool = False, export: bool = False):
    """View all rich menus"""
    try:
        load_config()
        await initialize_services()
        rich_menu_service = await get_rich_menu_service()

        logger.info("=" * 70)
        logger.info("RICH MENU STATUS")
        logger.info("=" * 70)

        # Get all menus
        menus = await rich_menu_service.get_rich_menu_list()

        if not menus:
            logger.info("\n⚠ No rich menus found")
            logger.info("\nTo create menus, run:")
            logger.info("  python update_rich_menus.py")
            return

        logger.info(f"\nTotal Menus: {len(menus)}")

        # Get default menu
        default_menu_id = await rich_menu_service.get_default_rich_menu_id()
        if default_menu_id:
            logger.info(f"Default Menu: {default_menu_id}")
        else:
            logger.info("Default Menu: Not set")

        # Show language mappings
        logger.info("\n" + "-" * 70)
        logger.info("LANGUAGE-SPECIFIC MENUS")
        logger.info("-" * 70)

        if rich_menu_service.language_menus:
            for lang, menu_id in rich_menu_service.language_menus.items():
                lang_name = rich_menu_service.LANGUAGE_NAMES.get(lang, lang.upper())
                logger.info(f"  {lang:3s} ({lang_name:25s}): {menu_id}")
        else:
            logger.info("  (Language menus not loaded in service)")
            logger.info("  (App loads them on startup)")

        # List all menus
        logger.info("\n" + "-" * 70)
        logger.info("ALL MENUS")
        logger.info("-" * 70)

        export_data = []

        for i, menu in enumerate(menus, 1):
            is_default = menu.rich_menu_id == default_menu_id

            logger.info(f"\n{i}. {menu.name}")
            logger.info(f"   ID: {menu.rich_menu_id}")
            logger.info(f"   Chat Bar Text: {menu.chat_bar_text}")
            logger.info(f"   Selected: {menu.selected}")
            logger.info(f"   Default: {'Yes ⭐' if is_default else 'No'}")
            logger.info(f"   Size: {menu.size.width}x{menu.size.height}")
            logger.info(f"   Areas: {len(menu.areas)} clickable region(s)")

            if show_details:
                logger.info(f"\n   Clickable Areas:")
                for j, area in enumerate(menu.areas, 1):
                    bounds = area.bounds
                    action = area.action

                    logger.info(f"     {j}. Position: ({bounds.x}, {bounds.y}, {bounds.width}, {bounds.height})")

                    if hasattr(action, 'data'):
                        logger.info(f"        Action: postback → {action.data}")
                        if hasattr(action, 'display_text') and action.display_text:
                            logger.info(f"        Display: {action.display_text}")
                    elif hasattr(action, 'uri'):
                        logger.info(f"        Action: uri → {action.uri}")
                    elif hasattr(action, 'text'):
                        logger.info(f"        Action: message → {action.text}")

            if export:
                export_data.append({
                    'name': menu.name,
                    'id': menu.rich_menu_id,
                    'chat_bar_text': menu.chat_bar_text,
                    'selected': menu.selected,
                    'is_default': is_default,
                    'size': {
                        'width': menu.size.width,
                        'height': menu.size.height
                    },
                    'areas_count': len(menu.areas)
                })

        # Export to file if requested
        if export:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = Path(f"rich_menu_export_{timestamp}.json")

            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'exported_at': datetime.now().isoformat(),
                    'total_menus': len(menus),
                    'default_menu_id': default_menu_id,
                    'menus': export_data
                }, f, indent=2, ensure_ascii=False)

            logger.info(f"\n✓ Exported to: {export_file}")

        logger.info("\n" + "=" * 70)

        # Show quick actions
        logger.info("\nQUICK ACTIONS:")
        logger.info("  View details: python view_rich_menus.py --details")
        logger.info("  Export JSON:  python view_rich_menus.py --export")
        logger.info("  Update menus: python update_rich_menus.py")
        logger.info("  Link to user: python force_link_menu.py <user_id> <lang>")

    except Exception as e:
        logger.error(f"\nError: {e}", exc_info=True)
    finally:
        await cleanup_services()


async def main():
    parser = argparse.ArgumentParser(
        description="View rich menu status and details",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic view
  python view_rich_menus.py

  # Show detailed area information
  python view_rich_menus.py --details

  # Export to JSON file
  python view_rich_menus.py --export

  # Both details and export
  python view_rich_menus.py --details --export
        """
    )

    parser.add_argument(
        '--details',
        action='store_true',
        help='Show detailed information for each menu'
    )
    parser.add_argument(
        '--export',
        action='store_true',
        help='Export menu information to JSON file'
    )

    args = parser.parse_args()

    await view_menus(show_details=args.details, export=args.export)


if __name__ == "__main__":
    asyncio.run(main())
