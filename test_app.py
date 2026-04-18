import unittest
from unittest.mock import patch
import app

class TestApp(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()

    @patch('app.charger_recettes')
    @patch('app.sauvegarder_recettes')
    def test_api_delete_recette_invalid_index(self, mock_save, mock_load):
        # Mock charger_recettes to return a list with 1 item
        mock_load.return_value = [{"nom": "Recette 1", "portions": 2, "ingredients": []}]

        # Test out of bounds index (e.g. 5)
        response = self.client.delete('/api/recettes/5')

        # Expect 400 Bad Request
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"success": False, "error": "Index invalide"})

        # Mock save should not be called since index is invalid
        mock_save.assert_not_called()

if __name__ == '__main__':
    unittest.main()
