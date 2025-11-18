import unittest
from unittest.mock import patch
from django.test import RequestFactory
from festival.utils.spotify_utils import get_user_token

class MockSession(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_key = "test-session-key"

class TestGetUserToken(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("festival.utils.spotify_utils.SpotifyOAuth")
    def test_token_cached_and_valid(self, mock_oauth):
        request = self.factory.get("/")
        request.session = MockSession()

        mock_instance = mock_oauth.return_value
        mock_instance.get_cached_token.return_value = {"access_token": "cached_token"}
        mock_instance.is_token_expired.return_value = False

        token = get_user_token(request)
        self.assertEqual(token, "cached_token")
        self.assertEqual(request.session["spotify_token"], "cached_token")

    @patch("festival.utils.spotify_utils.SpotifyOAuth")
    def test_token_cached_and_expired(self, mock_oauth):
        request = self.factory.get("/")
        request.session = MockSession()

        mock_instance = mock_oauth.return_value
        mock_instance.get_cached_token.return_value = {
            "access_token": "expired",
            "refresh_token": "refresh"
        }
        mock_instance.is_token_expired.return_value = True
        mock_instance.refresh_access_token.return_value = {
            "access_token": "refreshed"
        }

        token = get_user_token(request)
        self.assertEqual(token, "refreshed")
        self.assertEqual(request.session["spotify_token"], "refreshed")

    @patch("festival.utils.spotify_utils.SpotifyOAuth")
    def test_no_token_no_code(self, mock_oauth):
        request = self.factory.get("/")
        request.session = MockSession()

        mock_instance = mock_oauth.return_value
        mock_instance.get_cached_token.return_value = None
        mock_instance.get_authorize_url.return_value = "https://spotify.com/auth"

        token = get_user_token(request)
        self.assertEqual(token, "https://spotify.com/auth")

    @patch("festival.utils.spotify_utils.SpotifyOAuth")
    def test_no_token_with_code(self, mock_oauth):
        request = self.factory.get("/", {"code": "abc123"})
        request.session = MockSession()

        mock_instance = mock_oauth.return_value
        mock_instance.get_cached_token.return_value = None
        mock_instance.get_access_token.return_value = {"access_token": "new_token"}

        token = get_user_token(request)
        self.assertEqual(token, "new_token")
        self.assertEqual(request.session["spotify_token"], "new_token")