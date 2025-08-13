import logging
from unittest.mock import MagicMock, patch

from braze_mcp.utils.logging import get_logger


class TestGetLogger:
    """Test the get_logger function"""

    def test_get_logger_basic(self):
        """Test basic logger creation"""
        logger = get_logger("test_logger")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_get_logger_with_string_level(self):
        """Test logger creation with string log level"""
        with patch("braze_mcp.utils.logging.logging.basicConfig") as mock_basicConfig:
            with patch("braze_mcp.utils.logging.logging.getLogger") as mock_getLogger:
                mock_logger = MagicMock()
                mock_getLogger.return_value = mock_logger

                logger = get_logger("test_logger", "DEBUG")

                mock_basicConfig.assert_called_once_with(
                    level="DEBUG",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                )
                mock_getLogger.assert_called_once_with("test_logger")
                assert logger == mock_logger

    def test_get_logger_with_int_level(self):
        """Test logger creation with integer log level"""
        with patch("braze_mcp.utils.logging.logging.basicConfig") as mock_basicConfig:
            with patch("braze_mcp.utils.logging.logging.getLogger") as mock_getLogger:
                mock_logger = MagicMock()
                mock_getLogger.return_value = mock_logger

                logger = get_logger("test_logger", logging.ERROR)

                mock_basicConfig.assert_called_once_with(
                    level=logging.ERROR,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                )
                mock_getLogger.assert_called_once_with("test_logger")
                assert logger == mock_logger

    def test_get_logger_default_level(self):
        """Test logger creation with default INFO level"""
        with patch("braze_mcp.utils.logging.logging.basicConfig") as mock_basicConfig:
            with patch("braze_mcp.utils.logging.logging.getLogger") as mock_getLogger:
                mock_logger = MagicMock()
                mock_getLogger.return_value = mock_logger

                logger = get_logger("test_logger")

                mock_basicConfig.assert_called_once_with(
                    level="INFO",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                )
                mock_getLogger.assert_called_once_with("test_logger")
                assert logger == mock_logger
