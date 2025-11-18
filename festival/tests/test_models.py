from django.test import TestCase
from datetime import date, time
from festival.models import Event, Artist, EventDay, Stage, Performance
from django.db.utils import IntegrityError


class ModelTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            name="Test Fes",
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 2),
            event_type="FES"
        )
        self.artist = Artist.objects.create(name="YOASOBI", spotify_id="abc123")
        self.event_day = EventDay.objects.create(event=self.event, date="2025-11-01", venue="Tokyo")
        self.stage = Stage.objects.create(event=self.event, name="Main", order=1)
        self.performance = Performance.objects.create(
            event_day=self.event_day,
            artist=self.artist,
            stage=self.stage,
            start_time=time(12, 0),
            end_time=time(13, 0)
        )

    def test_event_str(self):
        self.assertEqual(str(self.event), "Test Fes")

    def test_artist_str(self):
        self.assertEqual(str(self.artist), "YOASOBI")

    def test_event_day_str(self):
        expected = "Test Fes - 2025-11-01 @ Tokyo"
        self.assertEqual(str(self.event_day), expected)

    def test_stage_str(self):
        self.assertEqual(str(self.stage), "Test Fes - Main")

    def test_performance_str(self):
        self.assertIn("YOASOBI", str(self.performance))
        self.assertIn("Test Fes", str(self.performance))

    def test_artist_ordering(self):
        Artist.objects.create(name="Aimer", spotify_id="xyz789", furigana="あいまー")
        Artist.objects.create(name="King Gnu", spotify_id="def456", furigana="きんぐぬー")
        furigana_list = [a.furigana for a in Artist.objects.all() if a.furigana is not None]
        self.assertEqual(furigana_list, sorted(furigana_list))

    def test_event_day_unique_together(self):
        with self.assertRaises(IntegrityError):
            EventDay.objects.create(event=self.event, date="2025-11-01", venue="Tokyo")

    def test_performance_unique_together(self):
        with self.assertRaises(IntegrityError):
            Performance.objects.create(event_day=self.event_day, artist=self.artist)