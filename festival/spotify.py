import requests

from conf.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from .models import Artist

def get_spotify_token():
    """トークン取得関数"""
    auth_url = "https://accounts.spotify.com/api/token"
    response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    })

    data = response.json()
    return data['access_token']

def search_artist(name):
    """アーティスト検索関数"""
    token = get_spotify_token()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    params = {
        'q': name,
        'type': 'artist',
        'limit': 1
    }
    response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
    data = response.json()

    if data['artists']['items']:
        artist = data['artists']['items'][0]
        return {
            'name': artist['name'],
            'spotify_id': artist['id'],
            'popularity': artist['popularity'],
            'genres': artist['genres']
        }
    return None


def save_artist_from_spotify(name):
    """Djangoモデルに保存"""
    artist_data = search_artist(name)
    if artist_data:
        artist, created = Artist.objects.get_or_create(
            spotify_id=artist_data['spotify_id'],
            defaults={
                'name': artist_data['name'],
                'popularity': artist_data['popularity'],
                'genres': artist_data['genres']
            }
        )
        return artist
    return None