from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from festival.models import Artist, Event, EventDay, Performance
from datetime import date


class ArtistViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.artist = Artist.objects.create(name="YOASOBI", furigana="よあそび", spotify_id="abc123")
        self.event = Event.objects.create(
            name="Test Fes",
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 2),
            event_type="FES"
        )
        self.event_day = EventDay.objects.create(event=self.event, date="2025-11-01", venue="Tokyo")
        self.performance = Performance.objects.create(event_day=self.event_day, artist=self.artist)

    def test_artist_list_view(self):
        response = self.client.get(reverse("festival:artist_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "YOASOBI")

    def test_artist_list_search(self):
        response = self.client.get(reverse("festival:artist_list") + "?q=YOA")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "YOASOBI")

    def test_artist_detail_view(self):
        response = self.client.get(reverse("festival:artist_detail", args=[self.artist.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "YOASOBI")

    def test_edit_artist_bulk_get(self):
        self.client.force_login(self._create_staff_user())
        response = self.client.get(reverse("festival:edit_artist_bulk"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "YOASOBI")

    def test_edit_artist_bulk_post(self):
        self.client.force_login(self._create_staff_user())
        data = {
            f"name_{self.artist.id}": "YOASOBI",
            f"furigana_{self.artist.id}": "よあそび"
        }
        response = self.client.post(reverse("festival:edit_artist_bulk"), data)
        self.assertEqual(response.status_code, 302)

    @patch("festival.views.artist_views.save_artist_from_spotify")
    def test_bulk_artist_register_post(self, mock_save):
        self.client.force_login(self._create_staff_user())
        mock_save.return_value = True
        data = {"names": "Aimer, YOASOBI"}
        response = self.client.post(reverse("festival:bulk_artist_register"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "件登録")

    def test_edit_artist_get(self):
        self.client.force_login(self._create_staff_user())
        response = self.client.get(reverse("festival:edit_artist", args=[self.artist.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "YOASOBI")

    def test_edit_artist_post(self):
        self.client.force_login(self._create_staff_user())
        data = {
            "name": "YOASOBI",
            "furigana": "よあそび",
            "spotify_id": "abc123"
        }
        response = self.client.post(reverse("festival:edit_artist", args=[self.artist.id]), data)
        self.assertEqual(response.status_code, 302)

    def _create_staff_user(self):
        from django.contrib.auth.models import User
        return User.objects.create_user(username="admin", password="pass", is_staff=True)