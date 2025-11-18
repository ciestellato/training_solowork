import time
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from festival.models import EventDay, Event, Artist, Performance, Stage
from unittest.mock import patch

class TestPlaylistViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.event = Event.objects.create(
            name="Test Fes",
            start_date=date(2025, 11, 18),
            end_date=date(2025, 11, 18),
            event_type="FES"
        )
        self.event_day = EventDay.objects.create(
            event=self.event,
            date="2025-11-18",
            venue="Test Venue"
        )
        self.stage = Stage.objects.create(
            event=self.event,
            name="Main",
            order=1,
            color_code="#FF0000"
        )
        self.artist = Artist.objects.create(name="YOASOBI", spotify_id="123")
        Performance.objects.create(
            event_day=self.event_day,
            stage=self.stage,
            artist=self.artist,
            start_time="12:00"
        )

    def test_create_playlist_view_get(self):
        url = reverse("festival:create_playlist") + f"?event_day={self.event_day.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "予習リスト")

    @patch("festival.views.playlist_views.get_top_tracks", return_value=[
        {"name": "Track A", "artist": "YOASOBI", "spotify_url": "http://spotify.com/trackA", "uri": "spotify:track:abc"}
    ])
    def test_create_playlist_view_post(self, mock_tracks):
        url = reverse("festival:create_playlist")
        data = {
            "event_day": self.event_day.id,
            "artists": [self.artist.id],
            "track_count": 1
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Track A", response.content.decode())

    @patch("festival.views.playlist_views.save_playlist_to_spotify", return_value="http://spotify.com/playlist123")
    def test_save_playlist_success(self, mock_save):
        session = self.client.session
        session["spotify_token_info"] = {
            "access_token": "dummy_token",
            "refresh_token": "dummy_refresh",
            "expires_at": int(time.time()) + 3600
        }
        session.save()

        url = reverse("festival:save_playlist_to_spotify")
        data = {
            "track_uris": "spotify:track:abc",
            "playlist_name": "Test Playlist",
            "event_day": self.event_day.id
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse("festival:create_playlist") + f"?event_day={self.event_day.id}")