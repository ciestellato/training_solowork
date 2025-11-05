# Spotify APIモック
from unittest.mock import patch
from festival.spotify import search_artist

@patch("festival.spotify.requests.get")
def test_search_artist(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "artists": {
            "items": [{
                "name": "YOASOBI",
                "id": "123",
                "popularity": 85,
                "genres": ["j-pop"],
                "followers": {"total": 100000},
                "images": []
            }]
        }
    }
    result = search_artist("YOASOBI")
    assert result["name"] == "YOASOBI"