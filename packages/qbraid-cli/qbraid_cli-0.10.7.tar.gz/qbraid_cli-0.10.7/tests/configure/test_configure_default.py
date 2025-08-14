# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Unit tests for the default_action function in the configure app.

"""

import configparser
from unittest.mock import patch

from qbraid_cli.configure.actions import default_action


def test_default_action():
    """Test default_action method with mocked dependencies."""
    with (
        patch("qbraid_cli.configure.actions.load_config") as mock_load_config,
        patch("qbraid_cli.configure.actions.prompt_for_config") as mock_prompt,
        patch("qbraid_cli.configure.actions.handle_filesystem_operation") as mock_handle_fs,
        patch("qbraid_cli.configure.actions.Console") as mock_console,
    ):
        # Setup mock returns
        config = configparser.ConfigParser()
        config.add_section("default")
        mock_load_config.return_value = config

        # Setup prompt_for_config to return different values
        mock_prompt.side_effect = [
            "https://new.example.com",  # url
            "api-key-123",  # api-key
            "new-organization",  # organization
            "new-workspace",  # workspace
        ]

        # Create mock console
        mock_console_instance = mock_console.return_value

        # Call the function to test
        default_action()

        # Verify config load/save was called
        mock_load_config.assert_called_once()

        # Verify prompt_for_config was called 4 times
        assert mock_prompt.call_count == 4

        # Verify handle_filesystem_operation was called to save config
        mock_handle_fs.assert_called_once()

        # Verify console.print was called with success message
        mock_console_instance.print.assert_called_once_with(
            "\n[bold green]Configuration updated successfully."
        )
