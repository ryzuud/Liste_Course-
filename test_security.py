import os
import unittest
from unittest.mock import patch
from app import app

class TestSecurity(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    @patch('app.git_auto_push')
    def test_git_push_no_token(self, mock_push):
        if "GIT_PUSH_TOKEN" in os.environ:
            del os.environ["GIT_PUSH_TOKEN"]

        response = self.client.post('/api/git-push')
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"Configuration serveur manquante", response.data)

    @patch('app.git_auto_push')
    def test_git_push_missing_auth_header(self, mock_push):
        os.environ["GIT_PUSH_TOKEN"] = "mysecrettoken"

        response = self.client.post('/api/git-push')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Authentification requise", response.data)

    @patch('app.git_auto_push')
    def test_git_push_invalid_token(self, mock_push):
        os.environ["GIT_PUSH_TOKEN"] = "mysecrettoken"

        response = self.client.post('/api/git-push', headers={"Authorization": "Bearer wrongtoken"})
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Token invalide", response.data)

    @patch('app.git_auto_push')
    def test_git_push_valid_token(self, mock_push):
        os.environ["GIT_PUSH_TOKEN"] = "mysecrettoken"
        mock_push.return_value = {"success": True, "steps": ["test"]}

        response = self.client.post('/api/git-push', headers={"Authorization": "Bearer mysecrettoken"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"success", response.data)
        mock_push.assert_called_once()

if __name__ == '__main__':
    unittest.main()
