import requests
from django.conf import settings
from festival.models import Artist
from festival.utils.text_utils import get_furigana

from spotipy.oauth2 import SpotifyOAuth

def get_app_token():
    """Spotify API用のアクセストークンを取得(アプリ用：読み取り専用)"""
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
    token = get_app_token()
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

def get_top_tracks(spotify_id, market='JP'):
    """
    指定されたSpotifyアーティストIDからトップトラック（代表曲）を取得する。
    各トラックに name, artist, spotify_url, uri を含めて返す。
    """
    token = get_app_token()
    if not token:
        return []

    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.spotify.com/v1/artists/{spotify_id}/top-tracks'
    params = {'market': market}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"トップトラック取得失敗: {response.status_code} - {response.text}")
        return []

    try:
        data = response.json()
        tracks = data.get('tracks', [])
        return [
            {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'spotify_url': track['external_urls']['spotify'],
                'uri': track['uri']
            }
            for track in tracks
        ]
    except ValueError:
        print("トップトラックのレスポンスがJSON形式ではありません")
        return []
    
def get_user_token(request):
    """Spotifyユーザー認証トークンを取得（Authorization Code Flow）"""

    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=settings.SPOTIFY_SCOPE,
        cache_path=f".cache-{request.session.session_key}"
    )

    # 認証コードがまだない場合 → 認証URLへリダイレクト
    if not request.GET.get("code"):
        auth_url = sp_oauth.get_authorize_url()
        return auth_url  # 呼び出し元で redirect する

    # 認証コードがある場合 → トークン取得
    code = request.GET.get("code")
    token_info = sp_oauth.get_access_token(code)

    # セッションに保存して再利用可能に
    request.session["spotify_token"] = token_info["access_token"]
    return token_info["access_token"]

def save_playlist_to_spotify(user_token, track_uris, playlist_name="Festival Forecast プレイリスト"):
    """Spotify上にプレイリストを作成し、楽曲を追加する"""
    print("🎧 Saving playlist to Spotify...")
    print("Track URIs:", track_uris)

    headers = {"Authorization": f"Bearer {user_token}"}

    # 1. ユーザー情報取得
    user_res = requests.get("https://api.spotify.com/v1/me", headers=headers)
    if user_res.status_code != 200:
        print(f"ユーザー情報取得失敗: {user_res.status_code} - {user_res.text}")
        return None

    user_id = user_res.json().get("id")
    if not user_id:
        print("ユーザーIDが取得できませんでした")
        return None

    # ユーザー情報取得ログ
    print("User info status:", user_res.status_code, user_res.text)

    # 2. プレイリスト作成
    create_res = requests.post(
        f"https://api.spotify.com/v1/users/{user_id}/playlists",
        headers=headers,
        json={
            "name": playlist_name,
            "description": "イベント出演アーティストの代表曲まとめ",
            "public": False
        }
    )
    if create_res.status_code != 201:
        print(f"プレイリスト作成失敗: {create_res.status_code} - {create_res.text}")
        return None

    playlist_id = create_res.json().get("id")
    if not playlist_id:
        print("プレイリストIDが取得できませんでした")
        return None

    # プレイリスト作成ログ
    print("Playlist create status:", create_res.status_code, create_res.text)

    # 3. 楽曲追加（最大100件まで）
    add_res = requests.post(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
        headers=headers,
        json={"uris": track_uris}
    )
    if add_res.status_code != 201:
        print(f"楽曲追加失敗: {add_res.status_code} - {add_res.text}")
        return None
    # 楽曲追加ログ
    print("Track add status:", add_res.status_code, add_res.text)

    # 4. プレイリストURLを返す
    return create_res.json().get("external_urls", {}).get("spotify")