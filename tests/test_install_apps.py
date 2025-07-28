import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import sys
import os

# Add the parent directory to the Python path to allow module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules import install_apps

class TestInstallApps(unittest.TestCase):

    def setUp(self):
        # Reset memory file content before each test
        self.mock_memory_data = {}
        self.mock_open_patcher = patch('builtins.open', new_callable=mock_open)
        self.mock_open = self.mock_open_patcher.start()
        self.mock_open.side_effect = lambda f, mode='r', **kwargs: self._mock_open_logic(f, mode, **kwargs)

    def tearDown(self):
        self.mock_open_patcher.stop()

    def _mock_open_logic(self, file_path, mode, **kwargs):
        if file_path == install_apps.MEMORY_FILE:
            if 'r' in mode:
                return mock_open(read_data=json.dumps(self.mock_memory_data)).return_value
            elif 'w' in mode:
                mock_file = mock_open().return_value
                mock_file.write.side_effect = lambda data: self._update_mock_memory_data(data)
                return mock_file
        return mock_open().return_value # Fallback for other files

    def _update_mock_memory_data(self, data):
        self.mock_memory_data = json.loads(data)

    @patch('platform.system', return_value='Windows')
    @patch('shutil.which', return_value=None)
    @patch('modules.install_apps._run_command') # Mock _run_command directly
    @patch('builtins.input', return_value='yes')
    def test_install_success_windows(self, mock_input, mock_run_command, mock_which, mock_platform):
        # First call to _run_command (for is_installed check) should return not found
        # Second call to _run_command (for install) should return success
        mock_run_command.side_effect = [
            MagicMock(success=False, stdout="", stderr="", exit_code=1), # is_installed check
            MagicMock(success=True, stdout="Successfully installed chrome", stderr="", exit_code=0) # install command
        ]
        response = install_apps.handle("install chrome")
        self.assertEqual(response, "Successfully installed 'chrome'.")
        # Assert that _run_command was called twice
        self.assertEqual(mock_run_command.call_count, 2)
        # Assert the second call was the install command
        mock_run_command.assert_called_with(
            ['winget', 'install', '--accept-package-agreements', '--accept-source-agreements', 'chrome']
        )

    @patch('platform.system', return_value='Windows')
    @patch('shutil.which', return_value=None)
    @patch('modules.install_apps.is_installed', return_value=False) # Mock is_installed directly
    @patch('modules.install_apps._run_command')
    @patch('builtins.input', return_value='yes')
    def test_install_failure_windows(self, mock_input, mock_run_command, mock_is_installed, mock_which, mock_platform):
        mock_run_command.return_value = MagicMock(success=False, stdout="", stderr="Installation failed", exit_code=1)
        response = install_apps.handle("install chrome")
        self.assertIn("Failed to install 'chrome'.", response)
        self.assertIn("Error: Installation failed", response)
        mock_run_command.assert_called_once_with(
            ['winget', 'install', '--accept-package-agreements', '--accept-source-agreements', 'chrome']
        )

    @patch('platform.system', return_value='Windows')
    @patch('shutil.which', return_value=None)
    @patch('modules.install_apps.is_installed', return_value=False) # Mock is_installed directly
    @patch('modules.install_apps._run_command') # Mock _run_command directly
    @patch('builtins.input', return_value='no')
    def test_install_user_cancel(self, mock_input, mock_run_command, mock_is_installed, mock_which, mock_platform):
        response = install_apps.handle("install chrome")
        self.assertEqual(response, "Installation of 'chrome' cancelled by user.")
        mock_run_command.assert_not_called() # _run_command should not be called for installation

    @patch('platform.system', return_value='Windows')
    @patch('shutil.which', return_value=None)
    @patch('modules.install_apps.is_installed', return_value=True) # Mock is_installed directly
    @patch('modules.install_apps._run_command') # Mock _run_command directly
    @patch('builtins.input', return_value='yes')
    def test_app_already_installed(self, mock_input, mock_run_command, mock_is_installed, mock_which, mock_platform):
        response = install_apps.handle("install chrome")
        self.assertEqual(response, "'chrome' is already installed.")
        mock_run_command.assert_not_called() # _run_command should not be called for installation

    @patch('platform.system', return_value='Windows')
    @patch('shutil.which', return_value=None)
    @patch('modules.install_apps._run_command')
    @patch('builtins.input', return_value='yes')
    def test_non_whitelisted_app(self, mock_input, mock_run_command, mock_which, mock_platform):
        response = install_apps.handle("install notepad")
        self.assertEqual(response, "'notepad' is not whitelisted for installation.")
        mock_run_command.assert_not_called()

    @patch('platform.system', return_value='UnknownOS')
    @patch('shutil.which', return_value=None)
    @patch('modules.install_apps._run_command')
    @patch('builtins.input', return_value='yes')
    def test_no_supported_package_manager(self, mock_input, mock_run_command, mock_which, mock_platform):
        response = install_apps.handle("install chrome")
        self.assertEqual(response, "No supported package manager found on this system.")
        mock_run_command.assert_not_called()

    @patch('platform.system', return_value='Darwin')
    @patch('shutil.which', return_value=None)
    @patch('modules.install_apps._run_command')
    @patch('builtins.input', return_value='yes')
    def test_install_success_macos(self, mock_input, mock_run_command, mock_which, mock_platform):
        mock_run_command.side_effect = [
            MagicMock(success=False, stdout="", stderr="", exit_code=1), # is_installed check
            MagicMock(success=True, stdout="successfully installed firefox", stderr="", exit_code=0) # install command
        ]
        response = install_apps.handle("install firefox")
        self.assertEqual(response, "Successfully installed 'firefox'.")
        self.assertEqual(mock_run_command.call_count, 2)
        mock_run_command.assert_called_with(
            ['brew', 'install', 'firefox']
        )

    @patch('platform.system', return_value='Linux')
    @patch('shutil.which', side_effect=lambda x: '/usr/bin/apt-get' if x == 'apt-get' else None)
    @patch('modules.install_apps._run_command')
    @patch('builtins.input', return_value='yes')
    def test_install_success_linux_apt(self, mock_input, mock_run_command, mock_which, mock_platform):
        mock_run_command.side_effect = [
            MagicMock(success=False, stdout="", stderr="", exit_code=1), # For dpkg -s (not installed)
            MagicMock(success=True, stdout="Setting up git", stderr="", exit_code=0) # For apt-get install
        ]
        response = install_apps.handle("install git")
        self.assertEqual(response, "Successfully installed 'git'.")
        self.assertEqual(mock_run_command.call_count, 2)
        mock_run_command.assert_called_with(
            ['sudo', 'apt-get', 'install', '-y', 'git']
        )

    @patch('platform.system', return_value='Linux')
    @patch('shutil.which', side_effect=lambda x: '/usr/bin/dnf' if x == 'dnf' else None)
    @patch('modules.install_apps._run_command')
    @patch('builtins.input', return_value='yes')
    def test_install_success_linux_dnf(self, mock_input, mock_run_command, mock_which, mock_platform):
        mock_run_command.side_effect = [
            MagicMock(success=False, stdout="", stderr="", exit_code=1), # For dnf list (not installed)
            MagicMock(success=True, stdout="Complete!", stderr="", exit_code=0) # For dnf install
        ]
        response = install_apps.handle("install git")
        self.assertEqual(response, "Successfully installed 'git'.")
        self.assertEqual(mock_run_command.call_count, 2)
        mock_run_command.assert_called_with(
            ['sudo', 'dnf', 'install', '-y', 'git']
        )

if __name__ == '__main__':
    unittest.main()