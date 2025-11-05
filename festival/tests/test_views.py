# ビューテスト
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_artist_list_view(client):
    url = reverse("festival:artist_list")
    response = client.get(url)
    assert response.status_code == 200
    assert "アーティスト一覧" in response.content.decode()
    