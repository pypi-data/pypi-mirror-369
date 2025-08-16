"""Tests for the arXiv command functionality."""

import os
import sys
from unittest.mock import MagicMock, mock_open, patch

from click.testing import CliRunner

from rxiv_maker.cli.commands.arxiv import arxiv


class TestArxivCommand:
    """Test the arXiv command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("rxiv_maker.cli.commands.arxiv.Path")
    def test_nonexistent_manuscript_directory(self, mock_path):
        """Test handling of nonexistent manuscript directory."""
        # Mock Path.exists() to return False
        mock_path.return_value.exists.return_value = False
        mock_path.return_value.name = "nonexistent"

        result = self.runner.invoke(arxiv, ["nonexistent"])

        assert result.exit_code == 1
        assert "❌ Error: Manuscript directory 'nonexistent' does not exist" in result.output
        assert "💡 Run 'rxiv init nonexistent' to create a new manuscript" in result.output

    @patch("rxiv_maker.cli.commands.arxiv.Path")
    @patch("rxiv_maker.cli.commands.arxiv.Progress")
    @patch("rxiv_maker.cli.commands.arxiv.BuildManager")
    def test_pdf_building_when_missing(self, mock_build_manager, mock_progress, mock_path):
        """Test PDF building when PDF doesn't exist."""

        # Mock different Path objects based on the path argument
        def path_side_effect(path_arg):
            path_mock = MagicMock()
            path_str = str(path_arg)

            if path_str == "test_manuscript":
                # Manuscript directory exists
                path_mock.exists.return_value = True
                path_mock.name = "test_manuscript"
            elif path_str.endswith("test_manuscript.pdf") or (path_str.endswith(".pdf") and "output" in path_str):
                # PDF file doesn't exist - this will trigger BuildManager call
                path_mock.exists.return_value = False
                path_mock.name = "test_manuscript.pdf"
            else:
                # Default mock for other Path calls (like directory paths)
                path_mock.exists.return_value = True
                path_mock.name = "test_manuscript"
            return path_mock

        mock_path.side_effect = path_side_effect

        # Mock BuildManager successful run
        mock_manager_instance = MagicMock()
        mock_manager_instance.run.return_value = True
        mock_build_manager.return_value = mock_manager_instance

        # Mock Progress context manager
        mock_progress_instance = MagicMock()
        mock_progress.return_value.__enter__ = MagicMock(return_value=mock_progress_instance)
        mock_progress.return_value.__exit__ = MagicMock(return_value=None)

        # Mock prepare_arxiv_main to avoid actual execution
        with patch("rxiv_maker.cli.commands.arxiv.prepare_arxiv_main"):
            result = self.runner.invoke(arxiv, ["test_manuscript", "--no-zip"], obj={"verbose": False})

        assert result.exit_code == 0
        mock_build_manager.assert_called_once()
        mock_manager_instance.run.assert_called_once()

    @patch("rxiv_maker.cli.commands.arxiv.Path")
    @patch("rxiv_maker.cli.commands.arxiv.Progress")
    @patch("rxiv_maker.cli.commands.arxiv.BuildManager")
    def test_build_manager_failure(self, mock_build_manager, mock_progress, mock_path):
        """Test handling of BuildManager failure."""

        # Mock different Path objects based on the path argument
        def path_side_effect(path_arg):
            path_mock = MagicMock()
            path_str = str(path_arg)

            if path_str == "test_manuscript":
                # Manuscript directory exists
                path_mock.exists.return_value = True
                path_mock.name = "test_manuscript"
            elif path_str.endswith("test_manuscript.pdf") or (path_str.endswith(".pdf") and "output" in path_str):
                # PDF file doesn't exist - this will trigger BuildManager call
                path_mock.exists.return_value = False
                path_mock.name = "test_manuscript.pdf"
            else:
                # Default mock for other Path calls (like directory paths)
                path_mock.exists.return_value = True
                path_mock.name = "test_manuscript"
            return path_mock

        mock_path.side_effect = path_side_effect

        # Mock BuildManager failure
        mock_manager_instance = MagicMock()
        mock_manager_instance.run.return_value = False
        mock_build_manager.return_value = mock_manager_instance

        # Mock Progress context manager
        mock_progress_instance = MagicMock()
        mock_progress.return_value.__enter__ = MagicMock(return_value=mock_progress_instance)
        mock_progress.return_value.__exit__ = MagicMock(return_value=None)

        result = self.runner.invoke(arxiv, ["test_manuscript"], obj={"verbose": False})

        assert result.exit_code == 1
        assert "❌ PDF build failed. Cannot prepare arXiv package." in result.output

    @patch("rxiv_maker.cli.commands.arxiv.Path")
    @patch("rxiv_maker.cli.commands.arxiv.Progress")
    @patch("rxiv_maker.cli.commands.arxiv.prepare_arxiv_main")
    def test_custom_options(self, mock_prepare, mock_progress, mock_path):
        """Test arXiv command with custom options."""

        # Mock different Path objects based on the path argument
        def path_side_effect(path_arg):
            path_mock = MagicMock()
            path_str = str(path_arg)

            if path_str == "test_manuscript":
                # Manuscript directory exists
                path_mock.exists.return_value = True
                path_mock.name = "test_manuscript"
            elif "custom_output" in path_str and ".pdf" in path_str:
                # PDF file exists (so BuildManager won't be called)
                path_mock.exists.return_value = True
                path_mock.name = "test_manuscript.pdf"
            else:
                # Default mock for other Path calls
                path_mock.exists.return_value = True
                path_mock.name = str(path_arg)
            return path_mock

        mock_path.side_effect = path_side_effect

        # Mock Progress context manager
        mock_progress_instance = MagicMock()
        mock_progress.return_value.__enter__ = MagicMock(return_value=mock_progress_instance)
        mock_progress.return_value.__exit__ = MagicMock(return_value=None)

        # Mock sys.argv manipulation
        original_argv = sys.argv.copy()

        # Mock prepare_arxiv_main to raise SystemExit(0) to trigger successful completion
        mock_prepare.side_effect = SystemExit(0)

        with patch("yaml.safe_load") as mock_yaml, patch("builtins.open", mock_open()):
            # Mock YAML config
            mock_yaml.return_value = {"date": "2024-01-01", "authors": [{"name": "Test Author"}]}

            result = self.runner.invoke(
                arxiv,
                [
                    "test_manuscript",
                    "--output-dir",
                    "custom_output",
                    "--arxiv-dir",
                    "custom_arxiv",
                    "--zip-filename",
                    "custom.zip",
                ],
                obj={"verbose": False},  # Provide proper context object
            )

        # Remove debug output
        assert result.exit_code == 0
        mock_prepare.assert_called_once()

        # Verify sys.argv was restored
        assert sys.argv == original_argv

    def test_environment_variable_manuscript_path(self):
        """Test using MANUSCRIPT_PATH environment variable."""
        with patch.dict(os.environ, {"MANUSCRIPT_PATH": "env_manuscript"}):
            with patch("rxiv_maker.cli.commands.arxiv.Path") as mock_path:
                mock_path.return_value.exists.return_value = False
                mock_path.return_value.name = "env_manuscript"

                result = self.runner.invoke(arxiv, [])

                assert result.exit_code == 1
                assert "env_manuscript" in result.output

    @patch("rxiv_maker.cli.commands.arxiv.Path")
    @patch("rxiv_maker.cli.commands.arxiv.Progress")
    @patch("rxiv_maker.cli.commands.arxiv.prepare_arxiv_main")
    def test_no_zip_option(self, mock_prepare, mock_progress, mock_path):
        """Test --no-zip option."""
        # Mock manuscript directory and PDF exist
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.name = "test_manuscript"

        # Mock Progress context manager
        mock_progress_instance = MagicMock()
        mock_progress.return_value.__enter__ = MagicMock(return_value=mock_progress_instance)
        mock_progress.return_value.__exit__ = MagicMock(return_value=None)

        result = self.runner.invoke(arxiv, ["test_manuscript", "--no-zip"])

        assert result.exit_code == 0
        mock_prepare.assert_called_once()

    @patch("rxiv_maker.cli.commands.arxiv.Path")
    @patch("rxiv_maker.cli.commands.arxiv.Progress")
    @patch("rxiv_maker.cli.commands.arxiv.prepare_arxiv_main")
    def test_pdf_copying_to_manuscript(self, mock_prepare, mock_progress, mock_path):
        """Test copying PDF to manuscript directory with proper naming."""

        # Mock different Path objects based on the path argument
        def path_side_effect(path_arg):
            path_mock = MagicMock()
            path_str = str(path_arg)

            if path_str == "test_manuscript":
                # Manuscript directory exists
                path_mock.exists.return_value = True
                path_mock.name = "test_manuscript"
            elif "output" in path_str and ".pdf" in path_str:
                # PDF file exists
                path_mock.exists.return_value = True
                path_mock.name = "test_manuscript.pdf"
            elif "00_CONFIG.yml" in path_str:
                # Config file exists
                path_mock.exists.return_value = True
            else:
                # Default mock for other Path calls
                path_mock.exists.return_value = True
                path_mock.name = str(path_arg)
            return path_mock

        mock_path.side_effect = path_side_effect

        # Mock Progress context manager
        mock_progress_instance = MagicMock()
        mock_progress.return_value.__enter__ = MagicMock(return_value=mock_progress_instance)
        mock_progress.return_value.__exit__ = MagicMock(return_value=None)

        # Mock prepare_arxiv_main to complete successfully without raising SystemExit
        mock_prepare.return_value = None

        with (
            patch("yaml.safe_load") as mock_yaml,
            patch("builtins.open", mock_open()),
            patch("shutil.copy2") as mock_copy,
        ):
            # Mock YAML config
            mock_yaml.return_value = {
                "date": "2024-01-15",
                "authors": [{"name": "John Doe"}],
            }

            result = self.runner.invoke(arxiv, ["test_manuscript"], obj={"verbose": False})

        assert result.exit_code == 0
        mock_copy.assert_called_once()

    @patch("rxiv_maker.cli.commands.arxiv.Path")
    @patch("rxiv_maker.cli.commands.arxiv.Progress")
    @patch("rxiv_maker.cli.commands.arxiv.prepare_arxiv_main")
    def test_keyboard_interrupt(self, mock_prepare, mock_progress, mock_path):
        """Test handling of KeyboardInterrupt."""
        # Mock manuscript directory and PDF exist
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.name = "test_manuscript"

        # Mock KeyboardInterrupt during prepare_arxiv_main
        mock_prepare.side_effect = KeyboardInterrupt()

        # Mock Progress context manager
        mock_progress_instance = MagicMock()
        mock_progress.return_value.__enter__ = MagicMock(return_value=mock_progress_instance)
        mock_progress.return_value.__exit__ = MagicMock(return_value=None)

        result = self.runner.invoke(arxiv, ["test_manuscript"])

        assert result.exit_code == 1
        assert "⏹️  arXiv preparation interrupted by user" in result.output

    @patch("rxiv_maker.cli.commands.arxiv.Path")
    @patch("rxiv_maker.cli.commands.arxiv.Progress")
    @patch("rxiv_maker.cli.commands.arxiv.prepare_arxiv_main")
    def test_regression_build_manager_method_call(self, mock_prepare, mock_progress, mock_path):
        """Regression test: Ensure BuildManager.run() is called, not build()."""

        # Mock different Path objects based on the path argument
        def path_side_effect(path_arg):
            path_mock = MagicMock()
            path_str = str(path_arg)

            if path_str == "test_manuscript":
                # Manuscript directory exists
                path_mock.exists.return_value = True
                path_mock.name = "test_manuscript"
            elif path_str.endswith("test_manuscript.pdf") or (path_str.endswith(".pdf") and "output" in path_str):
                # PDF file doesn't exist - this will trigger BuildManager call
                path_mock.exists.return_value = False
                path_mock.name = "test_manuscript.pdf"
            else:
                # Default mock for other Path calls (like directory paths)
                path_mock.exists.return_value = True
                path_mock.name = "test_manuscript"
            return path_mock

        mock_path.side_effect = path_side_effect

        # Mock Progress context manager
        mock_progress_instance = MagicMock()
        mock_progress.return_value.__enter__ = MagicMock(return_value=mock_progress_instance)
        mock_progress.return_value.__exit__ = MagicMock(return_value=None)

        with patch("rxiv_maker.cli.commands.arxiv.BuildManager") as mock_build_manager:
            mock_manager_instance = MagicMock()
            mock_manager_instance.run.return_value = True
            # Ensure 'build' method doesn't exist to catch regression
            del mock_manager_instance.build
            mock_build_manager.return_value = mock_manager_instance

            result = self.runner.invoke(arxiv, ["test_manuscript", "--no-zip"], obj={"verbose": False})

        assert result.exit_code == 0
        # Verify run() method was called, not build()
        mock_manager_instance.run.assert_called_once()

    @patch("rxiv_maker.cli.commands.arxiv.Path")
    @patch("rxiv_maker.cli.commands.arxiv.Progress")
    @patch("rxiv_maker.cli.commands.arxiv.prepare_arxiv_main")
    def test_create_zip_flag_regression(self, mock_prepare, mock_progress, mock_path):
        """Regression test: Ensure --create-zip flag is used, not --zip."""

        # Mock different Path objects based on the path argument
        def path_side_effect(path_arg):
            path_mock = MagicMock()
            path_str = str(path_arg)

            if path_str == "test_manuscript":
                # Manuscript directory exists
                path_mock.exists.return_value = True
                path_mock.name = "test_manuscript"
            elif "output" in path_str and ".pdf" in path_str:
                # PDF file exists (so BuildManager won't be called)
                path_mock.exists.return_value = True
                path_mock.name = "test_manuscript.pdf"
            else:
                # Default mock for other Path calls
                path_mock.exists.return_value = True
                path_mock.name = str(path_arg)
            return path_mock

        mock_path.side_effect = path_side_effect

        # Mock Progress context manager
        mock_progress_instance = MagicMock()
        mock_progress.return_value.__enter__ = MagicMock(return_value=mock_progress_instance)
        mock_progress.return_value.__exit__ = MagicMock(return_value=None)

        # Capture sys.argv to verify correct flag is used
        captured_argv = []

        def capture_argv(*args, **kwargs):
            captured_argv.extend(sys.argv)
            # Use SystemExit(0) to trigger successful completion
            raise SystemExit(0)

        mock_prepare.side_effect = capture_argv

        result = self.runner.invoke(arxiv, ["test_manuscript"], obj={"verbose": False})

        assert result.exit_code == 0
        # Verify --create-zip is in the arguments, not --zip
        assert "--create-zip" in captured_argv
        assert "--zip" not in captured_argv or captured_argv.count("--zip") <= captured_argv.count("--create-zip")
