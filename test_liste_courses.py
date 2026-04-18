import unittest
from unittest.mock import patch
import liste_courses

class TestSupprimerRecette(unittest.TestCase):
    def setUp(self):
        self.recettes = [
            {"nom": "Recette 1", "portions": 2, "ingredients": []},
            {"nom": "Recette 2", "portions": 4, "ingredients": []}
        ]

    @patch('builtins.input', return_value='99')
    @patch('liste_courses.sauvegarder_recettes')
    @patch('sys.stdout')
    def test_supprimer_recette_invalid_index(self, mock_stdout, mock_sauvegarder, mock_input):
        recettes_copy = list(self.recettes)
        result = liste_courses.supprimer_recette(recettes_copy)

        # Verify the list remains unchanged
        self.assertEqual(len(result), 2)
        self.assertEqual(result, self.recettes)
        # Verify sauvegarder_recettes was not called
        mock_sauvegarder.assert_not_called()

    @patch('builtins.input', return_value='abc')
    @patch('liste_courses.sauvegarder_recettes')
    @patch('sys.stdout')
    def test_supprimer_recette_invalid_type(self, mock_stdout, mock_sauvegarder, mock_input):
        recettes_copy = list(self.recettes)
        result = liste_courses.supprimer_recette(recettes_copy)

        # Verify the list remains unchanged
        self.assertEqual(len(result), 2)
        self.assertEqual(result, self.recettes)
        # Verify sauvegarder_recettes was not called
        mock_sauvegarder.assert_not_called()

if __name__ == '__main__':
    unittest.main()
