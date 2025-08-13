"""
Tests for smart_gpu._logging module.
"""

import logging
import pytest

from smart_gpu._logging import get_logger


class TestLogging:
    """Test logging functionality."""
    
    def test_get_logger_default_name(self):
        """Test get_logger with default name."""
        logger = get_logger()
        assert logger.name == "smart_gpu"
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0
    
    def test_get_logger_custom_name(self):
        """Test get_logger with custom name."""
        logger = get_logger("test_logger")
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0
    
    def test_get_logger_same_name_returns_same_logger(self):
        """Test that get_logger returns the same logger for the same name."""
        logger1 = get_logger("test_same")
        logger2 = get_logger("test_same")
        assert logger1 is logger2
    
    def test_logger_has_handler(self):
        """Test that logger has a StreamHandler."""
        logger = get_logger("test_handler")
        handlers = logger.handlers
        assert len(handlers) > 0
        assert any(isinstance(h, logging.StreamHandler) for h in handlers)
    
    def test_logger_has_formatter(self):
        """Test that logger handler has a formatter."""
        logger = get_logger("test_formatter")
        handlers = logger.handlers
        assert len(handlers) > 0
        assert handlers[0].formatter is not None
    
    def test_logger_propagate_false(self):
        """Test that logger has propagate set to False."""
        logger = get_logger("test_propagate")
        assert logger.propagate is False


if __name__ == "__main__":
    pytest.main([__file__])
