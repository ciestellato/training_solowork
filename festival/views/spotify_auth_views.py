from django.shortcuts import redirect
from django.conf import settings
from spotipy.oauth2 import SpotifyOAuth

def spotify_login_view(request):
    """Spotify認証ページにリダイレクトするビュー"""
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=settings.SPOTIFY_SCOPE,
        cache_path=None
    )
    auth_url = sp_oauth.get_authorize_url()
    print("Spotify認証URL:", auth_url)
    return redirect(auth_url)

def spotify_callback_view(request):
    """Spotify認証後のコールバック処理ビュー"""
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=settings.SPOTIFY_SCOPE,
        cache_path=None  # セッションベースで管理するためキャッシュ無効化
    )

    code = request.GET.get("code")
    token_info = sp_oauth.get_access_token(code)

    if token_info and token_info.get("access_token"):
        request.session["spotify_token_info"] = token_info  # トークン情報を丸ごと保存
        return redirect("festival:create_playlist")
    else:
        return redirect("festival:error_page")