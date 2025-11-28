"""Tests for rich menu service"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from services.rich_menu_service import RichMenuService
from exceptions import RichMenuError, ValidationError


class TestRichMenuService:
    """Test RichMenuService class"""

    @pytest.fixture
    def mock_line_api(self):
        """Create a mock LINE API"""
        return AsyncMock()

    @pytest.fixture
    def mock_blob_api(self):
        """Create a mock LINE Blob API"""
        return AsyncMock()

    @pytest.fixture
    def rich_menu_service(self, mock_line_api, mock_blob_api):
        """Create a rich menu service with mock API"""
        return RichMenuService(mock_line_api, mock_blob_api)

    def test_initialization(self, rich_menu_service):
        """Test service initialization"""
        assert rich_menu_service.line_api is not None
        assert rich_menu_service.config_path.exists()
        assert rich_menu_service.language_menus == {}

    def test_validate_image_path_success(self, rich_menu_service, project_root):
        """Test successful image path validation"""
        # Create a test image path
        test_image = project_root / "rich_menu" / "menu_en.png"

        if test_image.exists():
            validated = rich_menu_service._validate_image_path(str(test_image))
            assert validated == test_image.resolve()

    def test_validate_image_path_not_exists(self, rich_menu_service):
        """Test validation fails for non-existent path"""
        with pytest.raises(ValueError, match="does not exist"):
            rich_menu_service._validate_image_path("/nonexistent/path.png")

    def test_validate_image_path_traversal(self, rich_menu_service):
        """Test path traversal protection"""
        with pytest.raises(ValueError, match="must be within"):
            rich_menu_service._validate_image_path("/etc/passwd")

    def test_validate_image_path_invalid_extension(self, rich_menu_service, tmp_path, monkeypatch):
        """Test validation fails for invalid file extension"""
        # Create a temporary directory structure mimicking rich_menu_dir
        mock_rich_menu_dir = tmp_path / "rich_menu"
        mock_rich_menu_dir.mkdir()

        # Mock rich_menu_service.rich_menu_dir to point to our mock directory
        monkeypatch.setattr(rich_menu_service, 'rich_menu_dir', mock_rich_menu_dir)

        # Create a temporary file with invalid extension INSIDE the mock rich_menu_dir
        test_file = mock_rich_menu_dir / "test.txt"
        test_file.write_text("test")

        with pytest.raises(ValueError, match="Invalid image format"):
            rich_menu_service._validate_image_path(str(test_file))

    def test_get_rich_menu_for_language(self, rich_menu_service):
        """Test getting rich menu for a language"""
        rich_menu_service.language_menus = {"en": "menu_123", "id": "menu_456"}

        assert rich_menu_service.get_rich_menu_for_language("en") == "menu_123"
        assert rich_menu_service.get_rich_menu_for_language("id") == "menu_456"
        assert rich_menu_service.get_rich_menu_for_language("zh") is None

    @pytest.mark.asyncio
    async def test_link_rich_menu_to_user(self, rich_menu_service, mock_line_api):
        """Test linking rich menu to user"""
        user_id = "test_user_123"
        rich_menu_id = "richmenu_456"

        mock_line_api.link_rich_menu_id_to_user = AsyncMock(return_value=None)

        result = await rich_menu_service.link_rich_menu_to_user(user_id, rich_menu_id)

        assert result is True
        mock_line_api.link_rich_menu_id_to_user.assert_called_once_with(
            user_id, rich_menu_id
        )

    @pytest.mark.asyncio
    async def test_link_rich_menu_error(self, rich_menu_service, mock_line_api):
        """Test error handling when linking rich menu fails"""
        user_id = "test_user_123"
        rich_menu_id = "richmenu_456"

        mock_line_api.link_rich_menu_id_to_user = AsyncMock(
            side_effect=Exception("API Error")
        )

        result = await rich_menu_service.link_rich_menu_to_user(user_id, rich_menu_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_unlink_rich_menu_from_user(self, rich_menu_service, mock_line_api):
        """Test unlinking rich menu from user"""
        user_id = "test_user_123"

        mock_line_api.unlink_rich_menu_id_from_user = AsyncMock(return_value=None)

        result = await rich_menu_service.unlink_rich_menu_from_user(user_id)

        assert result is True
        mock_line_api.unlink_rich_menu_id_from_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_set_user_rich_menu_success(self, rich_menu_service, mock_line_api):
        """Test setting user rich menu successfully"""
        user_id = "test_user_123"
        language = "en"

        rich_menu_service.language_menus = {"en": "menu_123"}
        mock_line_api.link_rich_menu_id_to_user = AsyncMock(return_value=None)

        result = await rich_menu_service.set_user_rich_menu(user_id, language)

        assert result is True

    @pytest.mark.asyncio
    async def test_set_user_rich_menu_no_menu(self, rich_menu_service):
        """Test setting user rich menu when no menu exists for language"""
        user_id = "test_user_123"
        language = "fr"  # Not in language_menus

        result = await rich_menu_service.set_user_rich_menu(user_id, language)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_rich_menu_list(self, rich_menu_service, mock_line_api):
        """Test getting rich menu list"""
        mock_response = MagicMock()
        mock_response.richmenus = [
            MagicMock(rich_menu_id="menu_1", name="Menu 1"),
            MagicMock(rich_menu_id="menu_2", name="Menu 2"),
        ]
        mock_line_api.get_rich_menu_list = AsyncMock(return_value=mock_response)

        menus = await rich_menu_service.get_rich_menu_list()

        assert len(menus) == 2
        assert menus[0].rich_menu_id == "menu_1"
        assert menus[1].rich_menu_id == "menu_2"

    @pytest.mark.asyncio
    async def test_delete_rich_menu(self, rich_menu_service, mock_line_api):
        """Test deleting a rich menu"""
        rich_menu_id = "menu_123"

        mock_line_api.delete_rich_menu = AsyncMock(return_value=None)

        result = await rich_menu_service.delete_rich_menu(rich_menu_id)

        assert result is True
        mock_line_api.delete_rich_menu.assert_called_once_with(rich_menu_id)

    @pytest.mark.asyncio
    async def test_upload_rich_menu_image_success(self, rich_menu_service, mock_blob_api, tmp_path, monkeypatch):
        """Test successful image upload for rich menu"""
        rich_menu_id = "test_rich_menu_id"
        
        # Mock rich_menu_service.rich_menu_dir to point to tmp_path
        monkeypatch.setattr(rich_menu_service, 'rich_menu_dir', tmp_path)
        
        image_path = tmp_path / "test_image.png"
        image_path.write_bytes(b"test_image_content")

        mock_blob_api.set_rich_menu_image = AsyncMock(return_value=None)

        result = await rich_menu_service.upload_rich_menu_image(rich_menu_id, str(image_path))

        assert result is True
        mock_blob_api.set_rich_menu_image.assert_called_once()
        args, kwargs = mock_blob_api.set_rich_menu_image.call_args
        assert kwargs["rich_menu_id"] == rich_menu_id
        assert kwargs["body"] == b"test_image_content"
        assert kwargs["_headers"]["Content-Type"] == "image/png"

    @pytest.mark.asyncio
    async def test_upload_rich_menu_image_failure(self, rich_menu_service, mock_blob_api, tmp_path, monkeypatch):
        """Test image upload failure for rich menu"""
        rich_menu_id = "test_rich_menu_id"
        
        # Mock rich_menu_service.rich_menu_dir to point to tmp_path
        monkeypatch.setattr(rich_menu_service, 'rich_menu_dir', tmp_path)
        
        image_path = tmp_path / "test_image.png"
        image_path.write_bytes(b"test_image_content")

        mock_blob_api.set_rich_menu_image = AsyncMock(side_effect=Exception("Upload error"))

        result = await rich_menu_service.upload_rich_menu_image(rich_menu_id, str(image_path))

        assert result is False
        mock_blob_api.set_rich_menu_image.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_rich_menu_for_language_success(self, rich_menu_service, mock_line_api, project_root):
        """Test successful creation of rich menu for a specific language"""
        language = "en"
        menu_name = "English Menu"
        mock_rich_menu_id = "richmenu-test-en"

        # Mock the create_rich_menu response
        mock_response = MagicMock()
        mock_response.rich_menu_id = mock_rich_menu_id
        mock_line_api.create_rich_menu.return_value = mock_response

        # Ensure the config file exists for the test
        rich_menu_service.config_path = project_root / "rich_menu" / "menu_config.json"
        assert rich_menu_service.config_path.exists()

        result_id = await rich_menu_service.create_rich_menu_for_language(language, menu_name)

        assert result_id == mock_rich_menu_id
        mock_line_api.create_rich_menu.assert_called_once()
        args, kwargs = mock_line_api.create_rich_menu.call_args
        assert args[0].name == menu_name
        
    @pytest.mark.asyncio
    async def test_create_language_rich_menus_success(self, rich_menu_service, mock_line_api, mock_blob_api, project_root, tmp_path):
        """Test successful creation of rich menus for all languages"""
        # Create dummy image files for the test
        rich_menu_service.rich_menu_dir = tmp_path
        (tmp_path / "menu_en.png").write_bytes(b"en_img")
        (tmp_path / "menu_id.png").write_bytes(b"id_img")
        (tmp_path / "menu_vi.png").write_bytes(b"vi_img")
        (tmp_path / "menu_zh.png").write_bytes(b"zh_img")

        # Mock existing menus to be empty initially
        mock_line_api.get_rich_menu_list.return_value = MagicMock(richmenus=[])

        # Mock create_rich_menu to return distinct rich_menu_ids
        mock_line_api.create_rich_menu.side_effect = [
            MagicMock(rich_menu_id="richmenu-en"),
            MagicMock(rich_menu_id="richmenu-id"),
            MagicMock(rich_menu_id="richmenu-vi"),
            MagicMock(rich_menu_id="richmenu-zh"),
        ]

        # Mock set_rich_menu_image to always succeed
        mock_blob_api.set_rich_menu_image.return_value = None

        # Ensure the config file exists for the test
        rich_menu_service.config_path = project_root / "rich_menu" / "menu_config.json"
        assert rich_menu_service.config_path.exists()

        result_menus = await rich_menu_service.create_language_rich_menus()

        assert len(result_menus) == 4
        assert result_menus["en"] == "richmenu-en"
        assert result_menus["id"] == "richmenu-id"
        assert result_menus["vi"] == "richmenu-vi"
        assert result_menus["zh"] == "richmenu-zh"

        assert mock_line_api.create_rich_menu.call_count == 4
        assert mock_blob_api.set_rich_menu_image.call_count == 4
        

