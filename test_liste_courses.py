import unittest
from unittest.mock import patch, mock_open
import json

import liste_courses

class TestListeCourses(unittest.TestCase):

    @patch('liste_courses.FICHIER_RECETTES', 'dummy_path.json')
    @patch('builtins.open', new_callable=mock_open, read_data='{"recettes": [{"nom": "Recette1"}]}')
    def test_charger_recettes_success(self, mock_file):
        result = liste_courses.charger_recettes()
        self.assertEqual(result, [{"nom": "Recette1"}])
        mock_file.assert_called_once_with('dummy_path.json', 'r', encoding='utf-8')

    @patch('liste_courses.FICHIER_RECETTES', 'dummy_path.json')
    @patch('sys.exit')
    @patch('builtins.open')
    @patch('builtins.print')
    def test_charger_recettes_file_not_found(self, mock_print, mock_file, mock_exit):
        mock_file.side_effect = FileNotFoundError()

        liste_courses.charger_recettes()

        mock_exit.assert_called_once_with(1)
        mock_print.assert_called_once()
        self.assertIn("introuvable", mock_print.call_args[0][0])

    @patch('liste_courses.FICHIER_RECETTES', 'dummy_path.json')
    @patch('sys.exit')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('builtins.print')
    def test_charger_recettes_json_decode_error(self, mock_print, mock_file, mock_exit):
        liste_courses.charger_recettes()

        mock_exit.assert_called_once_with(1)
        mock_print.assert_called_once()
        self.assertIn("Erreur de lecture JSON", mock_print.call_args[0][0])

if __name__ == '__main__':
    unittest.main()
