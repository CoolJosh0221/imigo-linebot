import asyncio
import argparse
import logging
from pathlib import Path
from typing import Dict, List

from config import load_config
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


class RichMenuUpdater:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.rich_menu_service = None
        self.db_service = None

    async def initialize(self):
        """Initialize services"""
        load_config()
        await initialize_services()
        self.rich_menu_service = await get_rich_menu_service()
        self.db_service = await get_database_service()
        logger.info("Services initialized")

    async def cleanup(self):
        """Cleanup services"""
        await cleanup_services()
        logger.info("Services cleaned up")

    async def get_existing_menus(self) -> Dict[str, str]:
        """Get existing rich menus"""
        menus = await self.rich_menu_service.get_rich_menu_list()

        existing = {}
        for menu in menus:
            logger.info(f"Found existing menu: {menu.name} (ID: {menu.rich_menu_id})")
            existing[menu.name] = menu.rich_menu_id

        return existing

    async def delete_all_menus(self) -> bool:
        """Delete all existing rich menus"""
        if self.dry_run:
            logger.info("[DRY RUN] Would delete all existing rich menus")
            return True

        logger.info("=" * 60)
        logger.info("STEP 1: Deleting all existing rich menus")
        logger.info("=" * 60)

        menus = await self.rich_menu_service.get_rich_menu_list()

        if not menus:
            logger.info("No existing menus to delete")
            return True

        logger.info(f"Found {len(menus)} menu(s) to delete")

        success_count = 0
        for menu in menus:
            try:
                await self.rich_menu_service.delete_rich_menu(menu.rich_menu_id)
                logger.info(f"✓ Deleted: {menu.name} ({menu.rich_menu_id})")
                success_count += 1
            except Exception as e:
                logger.error(f"✗ Failed to delete {menu.name}: {e}")

        self.rich_menu_service.language_menus.clear()

        logger.info(f"Deleted {success_count}/{len(menus)} menus successfully\n")
        return success_count == len(menus)

    async def verify_image_files(self) -> Dict[str, Path]:
        """Verify all required image files exist"""
        logger.info("=" * 60)
        logger.info("Verifying image files")
        logger.info("=" * 60)

        rich_menu_dir = Path(__file__).parent / "rich_menu"
        languages = self.rich_menu_service.SUPPORTED_LANGUAGES

        image_files = {}
        missing_files = []

        for lang in languages:
            image_path = rich_menu_dir / f"menu_{lang}.png"

            if image_path.exists():
                # Check file size
                size_mb = image_path.stat().st_size / (1024 * 1024)
                logger.info(f"✓ Found {image_path.name} ({size_mb:.2f} MB)")

                if size_mb > 1.0:
                    logger.warning(f"  ⚠ Warning: File size exceeds 1 MB LINE limit")

                image_files[lang] = image_path
            else:
                logger.error(f"✗ Missing: {image_path.name}")
                missing_files.append(image_path.name)

        if missing_files:
            logger.error(f"\nMissing {len(missing_files)} image file(s):")
            for f in missing_files:
                logger.error(f"  - {f}")
            return {}

        logger.info(f"\n✓ All {len(image_files)} image files verified\n")
        return image_files

    async def create_language_menus(self) -> Dict[str, str]:
        """Create rich menus for all languages"""
        if self.dry_run:
            logger.info("[DRY RUN] Would create language-specific rich menus")
            return {}

        logger.info("=" * 60)
        logger.info("STEP 2: Creating language-specific rich menus")
        logger.info("=" * 60)

        menus = await self.rich_menu_service.create_language_rich_menus()

        if not menus:
            logger.error("Failed to create any rich menus")
            return {}

        logger.info(f"\n✓ Successfully created {len(menus)} rich menu(s):")
        for lang, menu_id in menus.items():
            logger.info(f"  - {lang}: {menu_id}")

        return menus

    async def get_users_by_language(self) -> Dict[str, List[str]]:
        """Get all users grouped by their language preference"""
        logger.info("=" * 60)
        logger.info("STEP 3: Getting user language preferences")
        logger.info("=" * 60)

        # This is a placeholder - you'll need to implement this in your DatabaseService
        # For now, we'll return an empty dict
        logger.info("Note: User relinking will happen automatically when users next interact")
        logger.info("      Or manually link specific users using the force_link_menu.py script\n")

        return {}

    async def update_all(self, skip_cleanup: bool = False, cleanup_only: bool = False, force: bool = False):
        """Complete update workflow"""
        try:
            await self.initialize()

            # Check existing menus
            existing = await self.get_existing_menus()

            if existing and not force and not skip_cleanup and not cleanup_only:
                logger.warning("\n⚠ Existing menus found!")
                logger.warning("Use --force to recreate them, or --skip-cleanup to keep existing ones")
                return False

            # Verify images first
            image_files = await self.verify_image_files()
            if not image_files and not cleanup_only:
                logger.error("Cannot proceed without required image files")
                return False

            # Step 1: Cleanup
            if not skip_cleanup:
                success = await self.delete_all_menus()
                if not success:
                    logger.error("Cleanup failed, aborting")
                    return False

            if cleanup_only:
                logger.info("✓ Cleanup complete (cleanup-only mode)")
                return True

            # Step 2: Create new menus
            menus = await self.create_language_menus()
            if not menus:
                logger.error("Failed to create menus")
                return False

            # Step 3: User relinking info
            await self.get_users_by_language()

            logger.info("=" * 60)
            logger.info("✓ UPDATE COMPLETE")
            logger.info("=" * 60)
            logger.info(f"Created {len(menus)} language-specific rich menus")
            logger.info("\nNext steps:")
            logger.info("1. Test the menus in LINE app")
            logger.info("2. Existing users will get new menus on next interaction")
            logger.info("3. New users will get welcome message with language selection")
            logger.info("\nTo manually link a user to a menu:")
            logger.info("  python force_link_menu.py <user_id> <language>")

            return True

        except Exception as e:
            logger.error(f"Update failed: {e}", exc_info=True)
            return False
        finally:
            await self.cleanup()


async def main():
    parser = argparse.ArgumentParser(
        description="Update LINE bot rich menus with new config/images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full update (cleanup + recreate)
  python update_rich_menus.py

  # Only cleanup old menus
  python update_rich_menus.py --cleanup-only

  # Only create new menus (keep existing)
  python update_rich_menus.py --skip-cleanup

  # Force recreation even if menus exist
  python update_rich_menus.py --force

  # Dry run (show what would happen)
  python update_rich_menus.py --dry-run
        """
    )

    parser.add_argument(
        '--cleanup-only',
        action='store_true',
        help='Only delete existing menus without creating new ones'
    )
    parser.add_argument(
        '--skip-cleanup',
        action='store_true',
        help='Skip cleanup and only create new menus'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force recreation even if menus already exist'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    if args.cleanup_only and args.skip_cleanup:
        logger.error("Cannot use --cleanup-only and --skip-cleanup together")
        return

    if args.dry_run:
        logger.info("=" * 60)
        logger.info("DRY RUN MODE - No changes will be made")
        logger.info("=" * 60 + "\n")

    updater = RichMenuUpdater(dry_run=args.dry_run)

    success = await updater.update_all(
        skip_cleanup=args.skip_cleanup,
        cleanup_only=args.cleanup_only,
        force=args.force
    )

    if success:
        logger.info("\n✓ Script completed successfully")
    else:
        logger.error("\n✗ Script completed with errors")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
