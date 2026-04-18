import sys
import unittest
from unittest.mock import MagicMock

# Mock the flask module and its classes to avoid ImportError
# if flask is not installed in the environment
flask_mock = MagicMock()
sys.modules['flask'] = flask_mock

import app

from unittest.mock import mock_open, patch

class TestChargerRecettes(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    def test_charger_recettes_success(self, mock_json_load, mock_file):
        """Test charging recipes successfully from a valid JSON."""
        expected_recettes = [
            {"nom": "Recette 1", "portions": 2, "ingredients": []},
            {"nom": "Recette 2", "portions": 4, "ingredients": []}
        ]
        mock_json_load.return_value = {"recettes": expected_recettes}

        result = app.charger_recettes()

        self.assertEqual(result, expected_recettes)
        mock_file.assert_called_once_with(app.FICHIER_RECETTES, "r", encoding="utf-8")
        mock_json_load.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    def test_charger_recettes_missing_key(self, mock_json_load, mock_file):
        """Test behavior when the JSON does not contain the 'recettes' key."""
        mock_json_load.return_value = {"other_key": []}

        result = app.charger_recettes()

        self.assertEqual(result, [])
        mock_file.assert_called_once_with(app.FICHIER_RECETTES, "r", encoding="utf-8")
        mock_json_load.assert_called_once()

    @patch("builtins.open")
    def test_charger_recettes_file_not_found(self, mock_file):
        """Test behavior when the JSON file is not found."""
        mock_file.side_effect = FileNotFoundError

        with self.assertRaises(FileNotFoundError):
            app.charger_recettes()

        mock_file.assert_called_once_with(app.FICHIER_RECETTES, "r", encoding="utf-8")

if __name__ == '__main__':
    unittest.main()
