"""Tests for cleanup CLI command behavior."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from autowt.cli import main
from autowt.config import CleanupConfig, Config
from autowt.models import CleanupMode, Services


class TestCleanupCLI:
    """Tests for cleanup command CLI behavior."""

    def _create_mock_services(self):
        """Create a properly mocked Services object."""
        mock_services = Mock(spec=Services)
        mock_services.state = Mock()
        mock_services.git = Mock()
        mock_services.terminal = Mock()
        mock_services.process = Mock()

        # Mock git service methods to return empty lists to avoid iteration errors
        mock_services.git.find_repo_root.return_value = Path("/mock/repo")
        mock_services.git.fetch_branches.return_value = True
        mock_services.git.list_worktrees.return_value = []

        # Mock state service methods
        mock_config = Mock(spec=Config)
        mock_config.cleanup = Mock(spec=CleanupConfig)
        mock_config.cleanup.kill_processes = False
        mock_config.cleanup.default_mode = CleanupMode.INTERACTIVE
        mock_services.state.load_config.return_value = mock_config

        return mock_services

    def test_cleanup_defaults_to_interactive_in_tty(self):
        """Test that cleanup defaults to interactive mode when in a TTY."""
        runner = CliRunner()

        # Instead of mocking the whole cleanup function, just mock the CLI behavior
        # by checking that the correct CleanupCommand is created with interactive mode
        with (
            patch(
                "autowt.cli.create_services", return_value=self._create_mock_services()
            ),
            patch(
                "autowt.cli.is_interactive_terminal", return_value=True
            ),  # Simulate TTY
            patch("autowt.cli.cleanup_worktrees") as mock_cleanup,
        ):
            result = runner.invoke(main, ["cleanup"])

            if result.exit_code != 0:
                print(f"Exit code: {result.exit_code}")
                print(f"Output: {result.output}")
                print(f"Exception: {result.exception}")

            assert result.exit_code == 0
            mock_cleanup.assert_called_once()

            # Check that interactive mode was used
            cleanup_cmd = mock_cleanup.call_args[0][0]
            assert cleanup_cmd.mode == CleanupMode.INTERACTIVE

    def test_cleanup_requires_mode_in_non_tty(self):
        """Test that cleanup requires explicit mode when not in a TTY."""
        runner = CliRunner()

        with patch(
            "autowt.cli.is_interactive_terminal", return_value=False
        ):  # Simulate non-TTY
            result = runner.invoke(main, ["cleanup"])

            assert result.exit_code != 0
            assert "No TTY detected" in result.output
            assert "Please specify --mode explicitly" in result.output

    def test_cleanup_works_with_explicit_mode_in_non_tty(self):
        """Test that cleanup works when mode is explicitly specified in non-TTY."""
        runner = CliRunner()

        with (
            patch("autowt.cli.cleanup_worktrees") as mock_cleanup,
            patch(
                "autowt.cli.create_services", return_value=self._create_mock_services()
            ),
            patch(
                "autowt.cli.is_interactive_terminal", return_value=False
            ),  # Simulate non-TTY
        ):
            result = runner.invoke(main, ["cleanup", "--mode", "merged"])

            assert result.exit_code == 0
            mock_cleanup.assert_called_once()

            # Check that merged mode was used
            cleanup_cmd = mock_cleanup.call_args[0][0]
            assert cleanup_cmd.mode == CleanupMode.MERGED

    def test_cleanup_respects_explicit_mode_in_tty(self):
        """Test that explicit mode is respected even in TTY."""
        runner = CliRunner()

        with (
            patch("autowt.cli.cleanup_worktrees") as mock_cleanup,
            patch(
                "autowt.cli.create_services", return_value=self._create_mock_services()
            ),
            patch(
                "autowt.cli.is_interactive_terminal", return_value=True
            ),  # Simulate TTY
        ):
            result = runner.invoke(main, ["cleanup", "--mode", "all"])

            assert result.exit_code == 0
            mock_cleanup.assert_called_once()

            # Check that explicit mode was used (not interactive default)
            cleanup_cmd = mock_cleanup.call_args[0][0]
            assert cleanup_cmd.mode == CleanupMode.ALL

    @pytest.mark.parametrize("mode", ["all", "remoteless", "merged", "interactive"])
    def test_cleanup_accepts_all_valid_modes(self, mode):
        """Test that all valid cleanup modes are accepted."""
        runner = CliRunner()

        with (
            patch("autowt.cli.cleanup_worktrees") as mock_cleanup,
            patch(
                "autowt.cli.create_services", return_value=self._create_mock_services()
            ),
        ):
            result = runner.invoke(main, ["cleanup", "--mode", mode])

            assert result.exit_code == 0
            mock_cleanup.assert_called_once()

            # Check that the correct mode was used
            cleanup_cmd = mock_cleanup.call_args[0][0]
            assert cleanup_cmd.mode == CleanupMode(mode)

    def test_cleanup_passes_other_options_correctly(self):
        """Test that other cleanup options are passed through correctly."""
        runner = CliRunner()

        with (
            patch("autowt.cli.cleanup_worktrees") as mock_cleanup,
            patch(
                "autowt.cli.create_services", return_value=self._create_mock_services()
            ),
        ):
            result = runner.invoke(
                main,
                [
                    "cleanup",
                    "--mode",
                    "merged",
                    "--dry-run",
                    "--yes",
                    "--force",
                    "--kill",
                    "--debug",
                ],
            )

            assert result.exit_code == 0
            mock_cleanup.assert_called_once()

            # Check that all options were passed correctly
            cleanup_cmd = mock_cleanup.call_args[0][0]
            assert cleanup_cmd.mode == CleanupMode.MERGED
            assert cleanup_cmd.dry_run is True
            assert cleanup_cmd.auto_confirm is True
            assert cleanup_cmd.force is True
            assert cleanup_cmd.debug is True
            assert cleanup_cmd.kill_processes is True

    def test_cleanup_mutually_exclusive_kill_options(self):
        """Test that --kill and --no-kill options are mutually exclusive."""
        runner = CliRunner()

        result = runner.invoke(
            main, ["cleanup", "--mode", "merged", "--kill", "--no-kill"]
        )

        assert result.exit_code != 0
        assert "Cannot specify both --kill and --no-kill" in result.output

    def test_kill_processes_flag_handling(self):
        """Test that kill_processes flag is handled correctly based on CLI args and config."""
        runner = CliRunner()

        # Test --kill flag sets kill_processes=True
        with (
            patch("autowt.cli.cleanup_worktrees") as mock_cleanup,
            patch(
                "autowt.cli.create_services", return_value=self._create_mock_services()
            ),
            patch("autowt.cli.get_config") as mock_get_config,
        ):
            mock_config = Mock()
            mock_config.cleanup.kill_processes = False  # Config says don't kill
            mock_config.cleanup.default_mode = CleanupMode.INTERACTIVE
            mock_get_config.return_value = mock_config

            result = runner.invoke(main, ["cleanup", "--mode", "merged", "--kill"])

            assert result.exit_code == 0
            cleanup_cmd = mock_cleanup.call_args[0][0]
            assert cleanup_cmd.kill_processes is True  # --kill overrides config

        # Test --no-kill flag sets kill_processes=False
        with (
            patch("autowt.cli.cleanup_worktrees") as mock_cleanup,
            patch(
                "autowt.cli.create_services", return_value=self._create_mock_services()
            ),
            patch("autowt.cli.get_config") as mock_get_config,
        ):
            mock_config = Mock()
            mock_config.cleanup.kill_processes = True  # Config says kill
            mock_config.cleanup.default_mode = CleanupMode.INTERACTIVE
            mock_get_config.return_value = mock_config

            result = runner.invoke(main, ["cleanup", "--mode", "merged", "--no-kill"])

            assert result.exit_code == 0
            cleanup_cmd = mock_cleanup.call_args[0][0]
            assert cleanup_cmd.kill_processes is False  # --no-kill overrides config

        # Test no flags means kill_processes=None (allows prompting)
        with (
            patch("autowt.cli.cleanup_worktrees") as mock_cleanup,
            patch(
                "autowt.cli.create_services", return_value=self._create_mock_services()
            ),
            patch("autowt.cli.get_config") as mock_get_config,
        ):
            mock_config = Mock()
            mock_config.cleanup.kill_processes = True  # Config says kill
            mock_config.cleanup.default_mode = CleanupMode.INTERACTIVE
            mock_get_config.return_value = mock_config

            result = runner.invoke(main, ["cleanup", "--mode", "merged"])

            assert result.exit_code == 0
            cleanup_cmd = mock_cleanup.call_args[0][0]
            assert cleanup_cmd.kill_processes is None  # None allows prompting
