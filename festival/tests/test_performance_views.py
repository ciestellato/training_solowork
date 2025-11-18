from unittest import skip

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, time, datetime, timedelta

from festival.models import Event, EventDay, Artist, Performance, Stage
from festival.views.performance_views import generate_time_slots

class PerformanceViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff_user = User.objects.create_user(username='admin', password='pass', is_staff=True)
        cls.event = Event.objects.create(
            name="Test Event",
            start_date=date(2025, 11, 18),
            end_date=date(2025, 11, 20),
            event_type="FES"
        )
        cls.artist = Artist.objects.create(name="YOASOBI", spotify_id="abc123")
        cls.event_day = EventDay.objects.create(event=cls.event, date="2025-11-18", venue="Test Venue")
        cls.performance = Performance.objects.create(event_day=cls.event_day, artist=cls.artist)
        cls.stage = Stage.objects.create(event=cls.event, name="Main", order=1)

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='pass')

    def test_register_event_day_get(self):
        url = reverse("festival:register_event_day") + f"?event_id={self.event.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "イベント")

    def test_register_event_day_post(self):
        url = reverse("festival:register_event_day") + f"?event_id={self.event.id}"
        data = {
            "event": self.event.id,
            "date": "2025-11-19",
            "venue": "New Venue",
            "artists": [self.artist.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(EventDay.objects.filter(event=self.event, date="2025-11-19").exists())

    def test_edit_event_day_get(self):
        url = reverse("festival:edit_event_day_performances", args=[self.event_day.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "出演者")

    def test_edit_event_day_post(self):
        url = reverse("festival:edit_event_day_performances", args=[self.event_day.id])
        data = {
            "event": self.event.id,
            "date": "2025-11-18",
            "venue": "Updated Venue",
            "artists": [self.artist.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.event_day.performance_set.count(), 1)

    def test_paste_schedule_register_post(self):
        url = reverse("festival:paste_schedule_register")
        raw_text = "2025-11-18 Zepp Tokyo\n2025-11-19 Zepp Osaka"
        data = {
            "artist": self.artist.id,
            "event_name": "Tour 2025",
            "raw_text": raw_text
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EventDay.objects.filter(event__name="Tour 2025").count(), 2)

    def test_register_timetable_get(self):
        url = reverse("festival:register_timetable") + f"?event_day={self.event_day.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "タイムテーブル")

    def test_register_timetable_post_valid(self):
        url = reverse("festival:register_timetable") + f"?event_day={self.event_day.id}"
        data = {
            "selected_artists": [self.artist.id],
            "selected_stage": self.stage.id,
            "save_times": "1",
            f"start_{self.artist.id}": "12:00",
            f"end_{self.artist.id}": "13:00"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        perf = Performance.objects.get(event_day=self.event_day, artist=self.artist)
        self.assertEqual(perf.start_time, time(12, 0))
        self.assertEqual(perf.end_time, time(13, 0))

    def test_register_timetable_post_invalid_time(self):
        url = reverse("festival:register_timetable") + f"?event_day={self.event_day.id}"
        data = {
            "selected_artists": [self.artist.id],
            "selected_stage": self.stage.id,
            "save_times": "1",
            f"start_{self.artist.id}": "14:00",
            f"end_{self.artist.id}": "13:00"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "開始時間は終了時間より前である必要があります")

    def test_timetable_view_get(self):
        self.performance.stage = self.stage
        self.performance.start_time = time(12, 0)
        self.performance.end_time = time(13, 0)
        self.performance.save()
        url = reverse("festival:timetable_view") + f"?event_day={self.event_day.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "タイムテーブル")

    def test_edit_performance_get(self):
        url = reverse("festival:edit_performance", args=[self.performance.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "タイムテーブル")

    def test_edit_performance_post_valid(self):
        url = reverse("festival:edit_performance", args=[self.performance.id])
        data = {
            "selected_stage": self.stage.id,
            "start_time": "12:00",
            "end_time": "13:00"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        perf = Performance.objects.get(id=self.performance.id)
        self.assertEqual(perf.start_time, time(12, 0))
        self.assertEqual(perf.end_time, time(13, 0))

    def test_edit_performance_post_invalid_time(self):
        url = reverse("festival:edit_performance", args=[self.performance.id])
        data = {
            "selected_stage": self.stage.id,
            "start_time": "14:00",
            "end_time": "13:00"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "開始時間は終了時間より前である必要があります")

    def test_generate_time_slots(self):
        slots = generate_time_slots(time(12, 0), time(13, 0), interval_minutes=15)
        self.assertEqual(len(slots), 4)
        self.assertEqual(slots[0], time(12, 0))
        self.assertEqual(slots[-1], time(12, 45))

class PerformanceViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.staff = User.objects.create_user(username="staffuser", password="pass", is_staff=True)

        # Event を追加
        self.event = Event.objects.create(
            name="Test Event",
            start_date=date(2025, 11, 18),
            end_date=date(2025, 11, 20),
            event_type="FES"
        )

        self.artist = Artist.objects.create(name="YOASOBI", spotify_id="abc123")
        self.stage = Stage.objects.create(
            event=self.event,  # ← ここが重要
            name="Main",
            color_code="#000000",
            order=1
        )

    def test_timetable_view_get(self):
        event_day = EventDay.objects.create(
            event=self.event,
            date="2025-11-18",
            venue="Test Venue"
        )
        performance = Performance.objects.create(
            artist=self.artist,
            stage=self.stage,
            event_day=event_day,
            start_time=time(12, 0),
            end_time=time(13, 0)
        )
        url = reverse("festival:timetable_view") + f"?event_day={event_day.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "タイムテーブル")
