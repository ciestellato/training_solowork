# モデルテスト
import pytest
from festival.models import Artist

@pytest.mark.django_db
def test_artist_str():
    artist = Artist.objects.create(name="YOASOBI")
    assert str(artist) == "YOASOBI"