import requests
from django.conf import settings
from festival.models import Artist
from festival.utils.text_utils import get_furigana

def get_spotify_token():
    """Spotify API用のアクセストークンを取得"""
    auth_url = "https://accounts.spotify.com/api/token"
    response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'client_secret': settings.SPOTIFY_CLIENT_SECRET,
    })

    if response.status_code != 200:
        print(f"Token取得失敗: {response.status_code} - {response.text}")
        return None

    try:
        return response.json()['access_token']
    except ValueError:
        print("TokenレスポンスがJSON形式ではありません")
        return None

def search_artist(name):
    """Spotify APIでアーティストを検索し、必要な情報を抽出"""
    token = get_spotify_token()
    if not token:
        return None

    headers = {'Authorization': f'Bearer {token}'}
    params = {'q': name, 'type': 'artist', 'limit': 1}
    response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)

    if response.status_code != 200:
        print(f"検索失敗: {response.status_code} - {response.text}")
        return None

    try:
        data = response.json()
    except ValueError:
        print("検索結果がJSON形式ではありません")
        return None

    items = data.get('artists', {}).get('items', [])
    if not items:
        print(f"アーティストが見つかりません: {name}")
        return None

    artist = items[0]
    return {
        'name': artist['name'],
        'furigana': get_furigana(name),
        'spotify_id': artist['id'],
        'popularity': artist.get('popularity', 0),
        'genres': artist.get('genres', [])
    }

def save_artist_from_spotify(name):
    """取得したアーティスト情報をDjangoモデルに保存"""
    artist_data = search_artist(name)
    if artist_data:
        artist, _ = Artist.objects.get_or_create(
            spotify_id=artist_data['spotify_id'],
            defaults={
                'name': artist_data['name'],
                'furigana': artist_data['furigana'],
                'popularity': artist_data['popularity'],
                'genres': artist_data['genres']
            }
        )
        return artist
    return None