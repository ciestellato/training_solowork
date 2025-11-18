from django.test import TestCase, RequestFactory
from django.urls import reverse
from unittest.mock import patch, MagicMock
from festival.views import spotify_auth_views


class SpotifyAuthViewsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("festival.views.spotify_auth_views.SpotifyOAuth")
    def test_spotify_login_redirect(self, mock_spotify_oauth):
        mock_instance = mock_spotify_oauth.return_value
        mock_instance.get_authorize_url.return_value = "https://accounts.spotify.com/authorize?mock"

        request = self.factory.get(reverse("festival:spotify_login"))
        response = spotify_auth_views.spotify_login_view(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn("spotify.com/authorize", response.url)

    @patch("festival.views.spotify_auth_views.SpotifyOAuth")
    def test_spotify_callback_success(self, mock_spotify_oauth):
        mock_instance = mock_spotify_oauth.return_value
        mock_instance.get_access_token.return_value = {
            "access_token": "mock_token",
            "refresh_token": "mock_refresh",
            "expires_in": 3600
        }

        request = self.factory.get(reverse("festival:spotify_callback"), {"code": "mock_code"})
        request.session = {}

        response = spotify_auth_views.spotify_callback_view(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("festival:create_playlist"))
        self.assertIn("spotify_token_info", request.session)

    @patch("festival.views.spotify_auth_views.SpotifyOAuth")
    def test_spotify_callback_failure(self, mock_spotify_oauth):
        mock_instance = mock_spotify_oauth.return_value
        mock_instance.get_access_token.return_value = None

        request = self.factory.get(reverse("festival:spotify_callback"), {"code": "invalid"})
        request.session = {}

        response = spotify_auth_views.spotify_callback_view(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("festival:error_page"))