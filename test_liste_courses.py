import unittest
from unittest.mock import patch
from datetime import datetime

import liste_courses

class TestListeCourses(unittest.TestCase):

    @patch('liste_courses.datetime')
    def test_generer_texte_export_vide(self, mock_datetime):
        # Mock datetime.now() to return a fixed date
        fixed_date = datetime(2023, 10, 27)
        mock_datetime.now.return_value = fixed_date

        liste = []
        selection = []

        resultat = liste_courses.generer_texte_export(liste, selection)

        attendu = (
            "🛒 LISTE DE COURSES\n"
            "📅 Semaine du 27/10/2023\n"
            "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📖 Recettes prévues :\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "\n"
            "📝 0 articles à acheter :\n"
            "\n"
            "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Bon shopping ! 🛍️"
        )

        self.assertEqual(resultat, attendu)

    @patch('liste_courses.datetime')
    def test_generer_texte_export_simple(self, mock_datetime):
        # Mock datetime.now() to return a fixed date
        fixed_date = datetime(2023, 10, 27)
        mock_datetime.now.return_value = fixed_date

        liste = [
            {"nom": "Pommes", "quantite": 5, "unite": "pcs"},
            {"nom": "Lait", "quantite": 1, "unite": "L"}
        ]
        selection = [
            {"nom": "Tarte aux pommes"},
            {"nom": "Crêpes"}
        ]

        resultat = liste_courses.generer_texte_export(liste, selection)

        attendu = (
            "🛒 LISTE DE COURSES\n"
            "📅 Semaine du 27/10/2023\n"
            "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📖 Recettes prévues :\n"
            "  • Tarte aux pommes\n"
            "  • Crêpes\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "\n"
            "📝 2 articles à acheter :\n"
            "\n"
            "☐ Pommes — 5 pcs\n"
            "☐ Lait — 1 L\n"
            "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Bon shopping ! 🛍️"
        )

        self.assertEqual(resultat, attendu)

if __name__ == '__main__':
    unittest.main()
