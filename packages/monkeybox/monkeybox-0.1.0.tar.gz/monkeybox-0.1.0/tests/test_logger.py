"""Tests for the logger system."""

from unittest.mock import Mock, patch

from monkeybox.core.logger import MonkeyboxLogger, get_logger


def test_basic_logging():
    """Logger outputs formatted messages."""
    with patch("monkeybox.core.logger.logging.getLogger") as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger = MonkeyboxLogger("test_agent")
        logger.log_user_input("Hello world")

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "[bold blue]User:[/bold blue] Hello world" == call_args


def test_content_truncation():
    """Long content gets truncated with '...'."""
    with patch("monkeybox.core.logger.logging.getLogger") as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger = MonkeyboxLogger("test_agent")

        long_args = {"param": "a" * 60}
        logger.log_tool_call("test_tool", long_args, "call_123")

        call_args = mock_logger.info.call_args[0][0]
        assert "..." in call_args

        long_result = "x" * 150
        logger.log_tool_result(long_result)

        call_args = mock_logger.info.call_args[0][0]
        assert call_args.endswith("...")


def test_rich_formatting():
    """Rich markup preserved in output."""
    with patch("monkeybox.core.logger.logging.getLogger") as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger = MonkeyboxLogger("test_agent")

        logger.log_step(1, 5)
        call_args = mock_logger.info.call_args[0][0]
        assert "[bold white on blue]" in call_args
        assert " Step 1/5 " in call_args

        logger.log_error("Something went wrong")
        call_args = mock_logger.error.call_args[0][0]
        assert "[bold red]Error:[/bold red] Something went wrong" == call_args


def test_multiple_log_levels():
    with patch("monkeybox.core.logger.logging.getLogger") as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger = MonkeyboxLogger("test")

        logger.log_final_response("Final result")
        logger.log_max_steps_reached(10)
        logger.log_mcp_connect("test_server", "stdio")

        assert mock_logger.info.called
        assert mock_logger.error.called


def test_get_logger_function():
    """Test get_logger function without mocking."""

    named_logger = get_logger("test_name")
    assert "monkeybox.test_name" in named_logger.name

    default_logger = get_logger()
    assert "monkeybox" in default_logger.name
