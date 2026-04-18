import unittest
from unittest.mock import patch
import io
import sys

# Import the module to test
from liste_courses import ajouter_recette

class TestListeCourses(unittest.TestCase):

    @patch('builtins.input', return_value='   ')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_ajouter_recette_nom_invalide(self, mock_stdout, mock_input):
        # We start with an initial list of recipes
        initial_recettes = [{'nom': 'Recette 1', 'portions': 2, 'ingredients': []}]

        # We call the function
        result = ajouter_recette(list(initial_recettes))

        # We check that the result is the same as the initial list, unmodified
        self.assertEqual(result, initial_recettes)

        # We verify that the proper error message was printed
        output = mock_stdout.getvalue()
        self.assertIn("Nom invalide, abandon.", output)

if __name__ == '__main__':
    unittest.main()
