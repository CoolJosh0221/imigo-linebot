import asyncio
import argparse
import logging
import sys

from dependencies import (
    get_rich_menu_service,
    get_database_service,
    initialize_services,
    cleanup_services,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def link_user_menu(user_id: str, language: str) -> bool:
    """Link a rich menu to a specific user"""
    try:
        await initialize_services()
        rich_menu_service = await get_rich_menu_service()
        db_service = await get_database_service()

        # Verify language is supported
        if language not in rich_menu_service.SUPPORTED_LANGUAGES:
            logger.error(f"Language '{language}' not supported")
            logger.info(f"Supported languages: {', '.join(rich_menu_service.SUPPORTED_LANGUAGES)}")
            return False

        # Get the rich menu ID for this language
        rich_menu_id = rich_menu_service.get_rich_menu_for_language(language)

        if not rich_menu_id:
            logger.error(f"No rich menu found for language '{language}'")
            logger.info("Please run 'python update_rich_menus.py' first to create menus")
            return False

        # Update user's language preference in database
        await db_service.set_user_language(user_id, language)
        logger.info(f"Updated user language preference to '{language}'")

        # Link the rich menu
        success = await rich_menu_service.link_rich_menu_to_user(user_id, rich_menu_id)

        if success:
            logger.info(f"✓ Successfully linked {language} menu ({rich_menu_id}) to user {user_id[:8]}...")
            return True
        else:
            logger.error(f"✗ Failed to link menu to user")
            return False

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return False
    finally:
        await cleanup_services()


async def relink_all_users() -> bool:
    """Relink all users in the database to their language-specific menus"""
    try:
        await initialize_services()
        rich_menu_service = await get_rich_menu_service()
        db_service = await get_database_service()

        logger.info("=" * 60)
        logger.info("Relinking all users to their language-specific menus")
        logger.info("=" * 60)

        # Note: This requires implementing a method to get all users from the database
        # For now, we'll log a message about this
        logger.warning("This feature requires implementing 'get_all_users()' in DatabaseService")
        logger.info("\nAlternative approach:")
        logger.info("Users will automatically get the correct menu when they:")
        logger.info("  - Send a message to the bot")
        logger.info("  - Change their language preference")
        logger.info("  - Follow the bot (new users)")

        # If you have a method to get all users, uncomment and implement:
        """
        users = await db_service.get_all_users()
        logger.info(f"Found {len(users)} users to relink")

        success_count = 0
        for user in users:
            user_id = user['user_id']
            language = user['language']

            if not language:
                logger.warning(f"Skipping user {user_id[:8]}... (no language set)")
                continue

            rich_menu_id = rich_menu_service.get_rich_menu_for_language(language)
            if not rich_menu_id:
                logger.warning(f"No menu for language '{language}', skipping user")
                continue

            success = await rich_menu_service.link_rich_menu_to_user(user_id, rich_menu_id)
            if success:
                success_count += 1
                logger.info(f"✓ Linked {language} menu to user {user_id[:8]}...")
            else:
                logger.error(f"✗ Failed to link menu to user {user_id[:8]}...")

        logger.info(f"\n✓ Relinked {success_count}/{len(users)} users successfully")
        """

        return True

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return False
    finally:
        await cleanup_services()


async def main():
    parser = argparse.ArgumentParser(
        description="Force link rich menu to user(s)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Link English menu to specific user
  python force_link_menu.py U1234567890abcdef en

  # Link Indonesian menu to user
  python force_link_menu.py U9876543210fedcba id

  # Relink all users (requires database implementation)
  python force_link_menu.py --all

Supported languages: en, id, vi, zh
        """
    )

    parser.add_argument(
        'user_id',
        nargs='?',
        help='LINE user ID (starts with U)'
    )
    parser.add_argument(
        'language',
        nargs='?',
        help='Language code (en, id, vi, zh)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Relink all users in database'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.all:
        success = await relink_all_users()
    elif args.user_id and args.language:
        if not args.user_id.startswith('U'):
            logger.error("Invalid user ID format (should start with 'U')")
            sys.exit(1)

        success = await link_user_menu(args.user_id, args.language)
    else:
        parser.print_help()
        sys.exit(1)

    if success:
        logger.info("\n✓ Operation completed successfully")
    else:
        logger.error("\n✗ Operation failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
