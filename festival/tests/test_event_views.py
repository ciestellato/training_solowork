from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from festival.models import Event, EventDay, Artist, Performance
from datetime import date


class EventViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.client.login(username="admin", password="pass")

        self.event_upcoming = Event.objects.create(
            name="Future Fest",
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 2),
            event_type="FES"
        )
        self.event_past = Event.objects.create(
            name="Past Fest",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 2),
            event_type="FES"
        )
        self.event_other = Event.objects.create(
            name="Solo Live",
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 1),
            event_type="SOLO"
        )

    def test_event_list_upcoming(self):
        response = self.client.get(reverse("festival:fes_event_upcoming"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Future Fest")
        self.assertNotContains(response, "Past Fest")

    def test_event_list_history(self):
        response = self.client.get(reverse("festival:fes_event_history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Past Fest")
        self.assertNotContains(response, "Future Fest")

    def test_fes_event_list(self):
        response = self.client.get(reverse("festival:fes_event_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Future Fest")
        self.assertContains(response, "Past Fest")
        self.assertNotContains(response, "Solo Live")

    def test_other_event_list(self):
        response = self.client.get(reverse("festival:other_event_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Solo Live")
        self.assertNotContains(response, "Future Fest")

    def test_event_detail_view(self):
        event_day = EventDay.objects.create(event=self.event_upcoming, date="2025-12-01", venue="Tokyo")
        artist = Artist.objects.create(name="YOASOBI", spotify_id="abc123")
        Performance.objects.create(event_day=event_day, artist=artist)

        response = self.client.get(reverse("festival:event_detail", args=[self.event_upcoming.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "YOASOBI")
        self.assertContains(response, "Tokyo")

    def test_create_event_post(self):
        data = {
            "name": "New Event",
            "event_type": "FES",
            "start_date": "2025-12-10",
            "end_date": "2025-12-11",
            "description": "",
            "official_url": ""
        }
        response = self.client.post(reverse("festival:create_event"), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(name="New Event").exists())

    def test_edit_event_post(self):
        data = {
            "name": "Updated Fest",
            "event_type": "FES",
            "start_date": "2025-12-01",
            "end_date": "2025-12-02",
            "description": "Updated",
            "official_url": ""
        }
        response = self.client.post(reverse("festival:edit_event", args=[self.event_upcoming.id]), data)
        self.assertEqual(response.status_code, 302)
        self.event_upcoming.refresh_from_db()
        self.assertEqual(self.event_upcoming.name, "Updated Fest")