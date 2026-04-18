import unittest
from liste_courses import parser_choix_recettes

class TestParser(unittest.TestCase):
    def test_valid(self):
        recettes = [{'nom': 'A'}, {'nom': 'B'}, {'nom': 'C'}]
        sel, inv = parser_choix_recettes("1, 3", recettes)
        self.assertEqual([r['nom'] for r in sel], ['A', 'C'])
        self.assertEqual(inv, [])

    def test_invalid_index(self):
        recettes = [{'nom': 'A'}]
        sel, inv = parser_choix_recettes("1, 99", recettes)
        self.assertEqual([r['nom'] for r in sel], ['A'])
        self.assertEqual(inv, [99])

    def test_value_error(self):
        with self.assertRaises(ValueError):
            parser_choix_recettes("1, a", [{'nom': 'A'}])

if __name__ == '__main__':
    unittest.main()
