import unittest
from unittest.mock import patch, MagicMock
import requests
from django.test import RequestFactory
from festival.utils import spotify_utils


class TestSpotifyUtils(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    # get_app_token
    @patch("festival.utils.spotify_utils.requests.post")
    def test_get_app_token_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "token"}
        self.assertEqual(spotify_utils.get_app_token(), "token")

    @patch("festival.utils.spotify_utils.requests.post")
    def test_get_app_token_http_error(self, mock_post):
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Bad Request"
        self.assertIsNone(spotify_utils.get_app_token())

    @patch("festival.utils.spotify_utils.requests.post")
    def test_get_app_token_json_error(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.side_effect = ValueError()
        self.assertIsNone(spotify_utils.get_app_token())

    @patch("festival.utils.spotify_utils.requests.post")
    def test_get_app_token_exception(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("Error")
        self.assertIsNone(spotify_utils.get_app_token())

    # search_artist
    @patch("festival.utils.spotify_utils.get_app_token", return_value=None)
    def test_search_artist_token_none(self, _):
        self.assertIsNone(spotify_utils.search_artist("YOASOBI"))

    @patch("festival.utils.spotify_utils.get_app_token", return_value="token")
    @patch("festival.utils.spotify_utils.requests.get")
    def test_search_artist_request_exception(self, mock_get, _):
        mock_get.side_effect = requests.exceptions.RequestException("Timeout")
        self.assertIsNone(spotify_utils.search_artist("YOASOBI"))

    @patch("festival.utils.spotify_utils.get_app_token", return_value="token")
    @patch("festival.utils.spotify_utils.requests.get")
    def test_search_artist_http_error(self, mock_get, _):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.side_effect = Exception("Should not be called")
        mock_get.return_value = mock_response
        self.assertIsNone(spotify_utils.search_artist("YOASOBI"))

    @patch("festival.utils.spotify_utils.get_app_token", return_value="token")
    @patch("festival.utils.spotify_utils.requests.get")
    def test_search_artist_json_error(self, mock_get, _):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.side_effect = ValueError()
        self.assertIsNone(spotify_utils.search_artist("YOASOBI"))

    @patch("festival.utils.spotify_utils.get_app_token", return_value="token")
    @patch("festival.utils.spotify_utils.requests.get")
    def test_search_artist_not_found(self, mock_get, _):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"artists": {"items": []}}
        self.assertIsNone(spotify_utils.search_artist("Unknown"))

    @patch("festival.utils.spotify_utils.get_app_token", return_value="token")
    @patch("festival.utils.spotify_utils.requests.get")
    @patch("festival.utils.spotify_utils.get_furigana", return_value="よあそび")
    def test_search_artist_success(self, mock_furigana, mock_get, _):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "artists": {
                "items": [{
                    "name": "YOASOBI",
                    "id": "abc123",
                    "popularity": 90,
                    "genres": ["j-pop"]
                }]
            }
        }
        result = spotify_utils.search_artist("YOASOBI")
        self.assertEqual(result["name"], "YOASOBI")
        self.assertEqual(result["furigana"], "よあそび")

    # save_artist_from_spotify
    @patch("festival.utils.spotify_utils.search_artist", return_value=None)
    def test_save_artist_none(self, _):
        self.assertIsNone(spotify_utils.save_artist_from_spotify("YOASOBI"))

    @patch("festival.utils.spotify_utils.search_artist")
    @patch("festival.utils.spotify_utils.Artist.objects.get_or_create")
    def test_save_artist_success(self, mock_get_or_create, mock_search):
        mock_search.return_value = {
            "name": "YOASOBI",
            "furigana": "よあそび",
            "spotify_id": "abc123",
            "popularity": 90,
            "genres": ["j-pop"]
        }
        mock_get_or_create.return_value = ("artist_obj", True)
        self.assertEqual(spotify_utils.save_artist_from_spotify("YOASOBI"), "artist_obj")

    # get_top_tracks
    @patch("festival.utils.spotify_utils.get_app_token", return_value=None)
    def test_get_top_tracks_token_none(self, _):
        self.assertEqual(spotify_utils.get_top_tracks("abc123"), [])

    @patch("festival.utils.spotify_utils.get_app_token", return_value="token")
    @patch("festival.utils.spotify_utils.requests.get")
    def test_get_top_tracks_exception(self, mock_get, _):
        mock_get.side_effect = requests.exceptions.RequestException("Error")
        self.assertEqual(spotify_utils.get_top_tracks("abc123"), [])

    @patch("festival.utils.spotify_utils.get_app_token", return_value="token")
    @patch("festival.utils.spotify_utils.requests.get")
    def test_get_top_tracks_json_error(self, mock_get, _):
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.side_effect = ValueError()
        self.assertEqual(spotify_utils.get_top_tracks("abc123"), [])

    @patch("festival.utils.spotify_utils.get_app_token", return_value="token")
    @patch("festival.utils.spotify_utils.requests.get")
    def test_get_top_tracks_success(self, mock_get, _):
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json.return_value = {
            "tracks": [{
                "name": "Track A",
                "artists": [{"name": "YOASOBI"}],
                "external_urls": {"spotify": "http://spotify.com/trackA"},
                "uri": "spotify:track:abc"
            }]
        }
        result = spotify_utils.get_top_tracks("abc123")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Track A")

    # save_playlist_to_spotify
    @patch("festival.utils.spotify_utils.requests.get")
    def test_save_playlist_user_error(self, mock_get):
        mock_get.return_value.status_code = 401
        mock_get.return_value.text = "Unauthorized"
        self.assertIsNone(spotify_utils.save_playlist_to_spotify("token", ["uri"]))

    @patch("festival.utils.spotify_utils.requests.get")
    def test_save_playlist_user_id_missing(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}
        self.assertIsNone(spotify_utils.save_playlist_to_spotify("token", ["uri"]))

    @patch("festival.utils.spotify_utils.requests.get")
    @patch("festival.utils.spotify_utils.requests.post")
    def test_save_playlist_create_error(self, mock_post, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": "user123"}
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Bad Request"
        self.assertIsNone(spotify_utils.save_playlist_to_spotify("token", ["uri"]))

    @patch("festival.utils.spotify_utils.requests.get")
    @patch("festival.utils.spotify_utils.requests.post")
    def test_save_playlist_id_missing(self, mock_post, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": "user123"}
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {}
        self.assertIsNone(spotify_utils.save_playlist_to_spotify("token", ["uri"]))

    @patch("festival.utils.spotify_utils.requests.get")
    @patch("festival.utils.spotify_utils.requests.post")
    def test_save_playlist_add_error(self, mock_post, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": "user123"}

        create_mock = MagicMock()
        create_mock.status_code = 201
        create_mock.json.return_value = {
            "id": "playlist123",
            "external_urls": {"spotify": "http://spotify.com/playlist123"}
        }

        add_mock = MagicMock()
        add_mock.status_code = 400
        add_mock.text = "Bad Request"

        mock_post.side_effect = [create_mock, add_mock]

        result = spotify_utils.save_playlist_to_spotify("token", ["spotify:track:abc"])
        self.assertIsNone(result)

    @patch("festival.utils.spotify_utils.requests.get")
    @patch("festival.utils.spotify_utils.requests.post")
    def test_save_playlist_success(self, mock_post, mock_get):
        # ユーザー情報取得
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": "user123"}

        # プレイリスト作成
        create_mock = MagicMock()
        create_mock.status_code = 201
        create_mock.json.return_value = {
            "id": "playlist123",
            "external_urls": {"spotify": "http://spotify.com/playlist123"}
        }

        # 楽曲追加
        add_mock = MagicMock()
        add_mock.status_code = 201

        mock_post.side_effect = [create_mock, add_mock]

        result = spotify_utils.save_playlist_to_spotify("token", ["spotify:track:abc"])
        self.assertEqual(result, "http://spotify.com/playlist123")