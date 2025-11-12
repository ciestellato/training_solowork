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
        cache_path=f".cache-{request.session.session_key}"
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


def spotify_callback_view(request):
    """Spotify認証後のコールバック処理ビュー"""
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=settings.SPOTIFY_SCOPE,
        cache_path=f".cache-{request.session.session_key}"
    )

    code = request.GET.get("code")
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info.get("access_token")

    if access_token:
        request.session["spotify_token"] = access_token
        return redirect("festival:create_playlist")  # プレイリスト作成画面へ戻る
    else:
        return redirect("festival:error_page")  # エラー処理ビューへ（任意）