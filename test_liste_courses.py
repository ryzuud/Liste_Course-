import unittest
from liste_courses import compiler_ingredients

class TestCompilerIngredients(unittest.TestCase):
    def test_compiler_ingredients_empty(self):
        self.assertEqual(compiler_ingredients([]), [])

    def test_compiler_ingredients_merge_identical(self):
        selection = [
            {"ingredients": [{"nom": "Lait", "quantite": 500, "unite": "ml"}]},
            {"ingredients": [{"nom": "Lait", "quantite": 250, "unite": "ml"}]},
        ]
        expected = [{"nom": "Lait", "quantite": 750, "unite": "ml"}]
        self.assertEqual(compiler_ingredients(selection), expected)

    def test_compiler_ingredients_mixed_casing_and_spacing(self):
        selection = [
            {"ingredients": [{"nom": " Tomate", "quantite": 2, "unite": " pièce"}]},
            {"ingredients": [{"nom": "tomate ", "quantite": 3, "unite": "Pièce "}]},
            {"ingredients": [{"nom": "TOMATE", "quantite": 1, "unite": "pièce"}]},
        ]
        # Should keep the first name encountered (" Tomate") and lower-case stripped unit ("pièce")
        expected = [{"nom": " Tomate", "quantite": 6, "unite": "pièce"}]
        self.assertEqual(compiler_ingredients(selection), expected)

    def test_compiler_ingredients_different_units(self):
        selection = [
            {"ingredients": [{"nom": "Farine", "quantite": 500, "unite": "g"}]},
            {"ingredients": [{"nom": "Farine", "quantite": 1, "unite": "kg"}]},
        ]
        expected = [
            {"nom": "Farine", "quantite": 500, "unite": "g"},
            {"nom": "Farine", "quantite": 1, "unite": "kg"},
        ]
        # Should be sorted by normal name (farine vs farine), then units
        result = compiler_ingredients(selection)
        self.assertEqual(len(result), 2)
        # Note: both will have the original name "Farine"
        # The keys used for sorting are ('farine', 'g') and ('farine', 'kg')
        self.assertEqual(result, expected)

    def test_compiler_ingredients_float_to_int(self):
        selection = [
            {"ingredients": [{"nom": "Eau", "quantite": 1.5, "unite": "L"}]},
            {"ingredients": [{"nom": "Eau", "quantite": 1.5, "unite": "L"}]},
            {"ingredients": [{"nom": "Sucre", "quantite": 1.2, "unite": "g"}]},
            {"ingredients": [{"nom": "Sucre", "quantite": 1.3, "unite": "g"}]},
        ]
        # Eau: 1.5 + 1.5 = 3.0 -> 3
        # Sucre: 1.2 + 1.3 = 2.5 -> 2.5
        expected = [
            {"nom": "Eau", "quantite": 3, "unite": "l"},
            {"nom": "Sucre", "quantite": 2.5, "unite": "g"},
        ]
        result = compiler_ingredients(selection)
        self.assertEqual(result, expected)

        # Explicit type checking
        eau_quantite = next(item["quantite"] for item in result if item["nom"] == "Eau")
        sucre_quantite = next(item["quantite"] for item in result if item["nom"] == "Sucre")
        self.assertIsInstance(eau_quantite, int)
        self.assertIsInstance(sucre_quantite, float)

if __name__ == '__main__':
    unittest.main()
