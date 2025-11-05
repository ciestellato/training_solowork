import pytest
from festival.forms import EventDayPerformanceForm, BulkArtistForm
from festival.models import Event, Artist, EventDay

@pytest.mark.django_db
def test_event_day_performance_form_valid():
    event = Event.objects.create(
        name="Test Fest",
        description="テストイベント",
        start_date="2025-12-01",
        end_date="2025-12-01",
        event_type="FES"
    )
    EventDay.objects.create(event=event, date="2025-12-01", venue="代々木公園")
    artist1 = Artist.objects.create(name="YOASOBI", spotify_id="abc123")
    artist2 = Artist.objects.create(name="Aimer", spotify_id="def456")

    form_data = {
        "event": event.id,
        "date": "2025-12-01",
        "venue": "代々木公園",
        "artists": [artist1.id, artist2.id],
    }

    form = EventDayPerformanceForm(data=form_data)
    form.fields["date"].choices = [("2025-12-01", "2025-12-01")]  # JSの代替

    assert form.is_valid()

def test_bulk_artist_form_valid():
    """正常系テスト"""
    form_data = {
        "names": "YOASOBI, Aimer, King Gnu"
    }
    form = BulkArtistForm(data=form_data)
    assert form.is_valid()
    assert form.cleaned_data["names"] == "YOASOBI, Aimer, King Gnu"

def test_bulk_artist_form_invalid_empty():
    """異常系テスト（空欄）"""
    form_data = {
        "names": ""
    }
    form = BulkArtistForm(data=form_data)
    assert not form.is_valid()
    assert "names" in form.errors