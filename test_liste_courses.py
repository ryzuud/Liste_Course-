import unittest
import subprocess
from unittest.mock import patch, MagicMock
from liste_courses import copier_presse_papiers

class TestListeCourses(unittest.TestCase):
    @patch("liste_courses.subprocess.Popen")
    def test_copier_presse_papiers_success(self, mock_popen):
        # Setup mock process
        mock_process = MagicMock()
        mock_process.returncode = 0

        # Popen returns context manager
        mock_popen.return_value.__enter__.return_value = mock_process

        result = copier_presse_papiers("test text")

        self.assertTrue(result)
        mock_popen.assert_called_once_with(
            ["clip.exe"],
            stdin=subprocess.PIPE,
            encoding="utf-16-le"
        )
        mock_process.communicate.assert_called_once_with(input="test text")

    @patch("liste_courses.subprocess.Popen")
    def test_copier_presse_papiers_failure_returncode(self, mock_popen):
        # Setup mock process with non-zero returncode
        mock_process = MagicMock()
        mock_process.returncode = 1

        mock_popen.return_value.__enter__.return_value = mock_process

        result = copier_presse_papiers("test text")

        self.assertFalse(result)
        mock_process.communicate.assert_called_once_with(input="test text")

    @patch("liste_courses.subprocess.Popen")
    def test_copier_presse_papiers_oserror(self, mock_popen):
        # Simulate OSError (e.g. clip.exe not found)
        mock_popen.side_effect = OSError("Command not found")

        result = copier_presse_papiers("test text")

        self.assertFalse(result)

    @patch("liste_courses.subprocess.Popen")
    def test_copier_presse_papiers_subprocess_error(self, mock_popen):
        # Simulate SubprocessError
        mock_popen.side_effect = subprocess.SubprocessError("Some subprocess error")

        result = copier_presse_papiers("test text")

        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
