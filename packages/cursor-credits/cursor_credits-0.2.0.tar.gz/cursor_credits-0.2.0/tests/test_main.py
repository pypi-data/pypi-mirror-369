"""Tests for the main module and core functionality."""

import pytest
from unittest.mock import patch
from cursor_credits import hello
from cursor_credits.main import main

def test_hello() -> None:
    """Test the hello function includes the project name."""
    assert "cursor_credits" in hello()

def test_main_output_with_auth(capsys: pytest.CaptureFixture[str]) -> None:
    """Test the output of the main function when authentication is successful."""
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0  # Should exit with success code
    captured = capsys.readouterr()
    # Should show successful authentication and usage data
    assert ("User ID:" in captured.out or "Email:" in captured.out)
    assert "Fast:" in captured.out
    assert "Slow:" in captured.out
    assert captured.err == ""

def test_main_output_no_auth(capsys: pytest.CaptureFixture[str]) -> None:
    """Test the output of the main function when no authentication is found."""
    # Mock get_cursor_paths to return None (no paths found)
    with patch('cursor_credits.paths.get_cursor_paths') as mock_paths:
        mock_paths.return_value = None
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1  # Should exit with error code
        captured = capsys.readouterr()
        # Should show error message when no authentication is found
        assert "Could not find Cursor authentication token" in captured.out
        assert captured.err == ""
