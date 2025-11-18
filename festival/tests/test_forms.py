from django.test import TestCase
from festival.forms import (
    BulkArtistForm, ArtistForm, ArtistBulkEditForm,
    EventDayPerformanceForm, ArtistSchedulePasteForm,
    EventForm, PlaylistForm
)
from festival.models import Artist, Event

from datetime import date


class FormValidationTests(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(name="YOASOBI", spotify_id="abc123")
        self.event = Event.objects.create(
            name="Test Event",
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 3),
            event_type="FES"
        )

    def test_bulk_artist_form_valid(self):
        form = BulkArtistForm(data={"names": "YOASOBI, Aimer"})
        self.assertTrue(form.is_valid())

    def test_artist_form_valid(self):
        form = ArtistForm(data={
            "name": "Aimer",
            "furigana": "エメ",
            "popularity": 80,
            "genres": ["J-Pop"],
            "spotify_id": "xyz789"
        })
        self.assertTrue(form.is_valid())

    def test_artist_bulk_edit_form_fields(self):
        form = ArtistBulkEditForm(artists=[self.artist])
        self.assertIn(f"name_{self.artist.id}", form.fields)
        self.assertIn(f"furigana_{self.artist.id}", form.fields)

    def test_event_day_performance_form_missing_date(self):
        form = EventDayPerformanceForm(data={
            "event": self.event.id,
            "venue": "Test Venue",
            "artists": [self.artist.id]
        })
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_artist_schedule_paste_form_valid(self):
        form = ArtistSchedulePasteForm(data={
            "artist": self.artist.id,
            "event_name": "Tour 2025",
            "raw_text": "2025-11-10 Zepp Tokyo"
        })
        self.assertTrue(form.is_valid())

    def test_event_form_invalid_dates(self):
        form = EventForm(data={
            "name": "Invalid Event",
            "event_type": "FES",
            "start_date": "2025-11-10",
            "end_date": "2025-11-01",
            "description": "",
            "official_url": ""
        })
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_playlist_form_queryset(self):
        form = PlaylistForm(artists_queryset=Artist.objects.all())
        self.assertEqual(form.fields["artists"].queryset.count(), 1)