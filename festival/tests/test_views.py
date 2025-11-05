# ビューテスト
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

from festival.models import Event, EventDay, Performance, Artist

# アーティスト一覧
@pytest.mark.django_db
def test_artist_list_view(client):
    url = reverse("festival:artist_list")
    response = client.get(url)
    assert response.status_code == 200
    assert "アーティスト一覧" in response.content.decode()

# アーティスト一覧
@pytest.mark.django_db
def test_artist_list_view_with_query(client):
    Artist.objects.create(name="YOASOBI", spotify_id="abc123")
    Artist.objects.create(name="Aimer", spotify_id="def456")

    url = reverse("festival:artist_list") + "?q=YOA"
    response = client.get(url)
    assert response.status_code == 200
    assert "YOASOBI" in response.content.decode()
    assert "Aimer" not in response.content.decode()

# アーティスト詳細
@pytest.mark.django_db
def test_artist_detail_view(client):
    artist = Artist.objects.create(name="King Gnu", spotify_id="xyz789")
    url = reverse("festival:artist_detail", args=[artist.id])
    response = client.get(url)
    assert response.status_code == 200
    assert "King Gnu" in response.content.decode()

# index ====================================================
def test_index_view(client):
    url = reverse("festival:index")
    response = client.get(url)
    assert response.status_code == 200
    assert "text/html" in response["Content-Type"]

# イベント一覧
@pytest.mark.django_db
def test_event_list_view(client):
    Event.objects.create(
        name="Test Fest",
        description="説明",
        start_date="2025-12-01",
        end_date="2025-12-02",
        event_type="FES"
    )
    url = reverse("festival:event_list")
    response = client.get(url)
    assert response.status_code == 200
    assert "Test Fest" in response.content.decode()

# イベント詳細
@pytest.mark.django_db
def test_event_detail_view(client):
    event = Event.objects.create(
        name="Winter Sonic",
        description="冬フェス",
        start_date="2025-12-10",
        end_date="2025-12-10",
        event_type="FES"
    )
    day = EventDay.objects.create(event=event, date="2025-12-10", venue="幕張メッセ")
    artist = Artist.objects.create(name="Aimer", spotify_id="def456")
    Performance.objects.create(event_day=day, artist=artist, is_confirmed=True)

    url = reverse("festival:event_detail", args=[event.id])
    response = client.get(url)
    assert response.status_code == 200
    assert "Aimer" in response.content.decode()

# bulk_artist_register のPOSTテスト
@patch("festival.views.save_artist_from_spotify")
@pytest.mark.django_db
def test_bulk_artist_register_post(mock_save, client):
    def mock_save_artist(name):
        return Artist.objects.create(name=name, spotify_id="64tJ2EAv1R6UaZqc4iOCyj")

    mock_save.side_effect = mock_save_artist

    url = reverse("festival:bulk_artist_register")
    data = {"names": "YOASOBI"}
    response = client.post(url, data)

    print(response.content.decode())  # デバッグ用

    assert response.status_code == 200
    assert Artist.objects.filter(name="YOASOBI").exists()
    assert "1 件登録" in response.content.decode()

# register_event_day_and_performances のPOSTテスト
@pytest.mark.django_db
def test_register_event_day_post(client):
    event = Event.objects.create(
        name="Test Fest",
        description="テスト",
        start_date="2025-12-01",
        end_date="2025-12-01",
        event_type="FES"
    )
    artist = Artist.objects.create(name="Aimer", spotify_id="def456")

    url = reverse("festival:register_event_day")
    data = {
        "event": event.id,
        "date": "2025-12-01",
        "venue": "幕張メッセ",
        "artists": [artist.id],
    }

    # 日付選択肢をフォームに設定するためにGETで一度取得
    client.get(url + f"?event_id={event.id}")

    response = client.post(url + f"?event_id={event.id}", data)
    assert response.status_code == 200
    assert "1 組の出演者を登録しました" in response.content.decode()

@pytest.mark.django_db
def test_register_event_day_post(client):
    # スタッフユーザー作成とログイン
    user = User.objects.create_user(username="admin", password="password", is_staff=True)
    client.login(username="admin", password="password")

    event = Event.objects.create(
        name="Test Fest",
        description="テスト",
        start_date="2025-12-01",
        end_date="2025-12-01",
        event_type="FES"
    )
    artist = Artist.objects.create(name="Aimer", spotify_id="def456")

    url = reverse("festival:register_event_day")
    data = {
        "event": event.id,
        "date": "2025-12-01",
        "venue": "幕張メッセ",
        "artists": [artist.id],
    }

    client.get(url + f"?event_id={event.id}")
    response = client.post(url + f"?event_id={event.id}", data)

    assert response.status_code == 200
    assert "1 組の出演者を登録しました" in response.content.decode()