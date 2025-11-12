import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from festival.models import EventDay, Performance, Artist
from festival.forms import PlaylistForm
from festival.utils.spotify_utils import get_top_tracks, save_playlist_to_spotify

from django.shortcuts import render
from festival.models import EventDay, Performance, Artist
from festival.forms import PlaylistForm
from festival.utils.spotify_utils import get_top_tracks

def create_playlist_view(request):
    """出演アーティストを選択してSpotifyプレイリストを生成するビュー"""

    selected_day_id = request.GET.get('event_day')
    selected_day = EventDay.objects.filter(id=selected_day_id).first()
    playlist = []
    track_uris = []

    # 出演アーティスト一覧（チェックボックス表示用）
    artists_qs = Artist.objects.filter(performance__event_day=selected_day).distinct() if selected_day else Artist.objects.none()

    if request.method == 'POST':
        form = PlaylistForm(request.POST, artists_queryset=artists_qs)
        if form.is_valid():
            selected_artists = form.cleaned_data['artists']
            for artist in selected_artists:
                tracks = get_top_tracks(artist.spotify_id)
                for track in tracks[:5]:  # 代表曲5曲使う
                    playlist.append({
                        'name': track['name'],
                        'artist': artist.name,
                        'spotify_url': track['spotify_url'],
                        'uri': track['uri']
                    })
                    track_uris.append(track['uri'])
    else:
        form = PlaylistForm(artists_queryset=artists_qs)

    # イベント日程一覧（セレクトボックス用）
    event_days = EventDay.objects.select_related('event').order_by('date')

    return render(request, 'playlist_create.html', {
        'form': form,
        'playlist': playlist,
        'track_uris': track_uris,
        'event_days': event_days,
        'selected_day_id': selected_day_id
    })

def save_playlist_to_spotify_view(request):
    """Spotifyにプレイリストを保存するビュー"""
    if request.method == 'POST':
        token = request.session.get("spotify_token")
        track_uris = request.POST.get("track_uris", "").split(",")

        if token and track_uris:
            playlist_url = save_playlist_to_spotify(token, track_uris)
            if playlist_url:
                messages.success(request, f"✅ Spotifyに保存しました！<br><a href='{playlist_url}' target='_blank'>プレイリストを開く</a>")
            else:
                messages.error(request, "❌ Spotifyへの保存に失敗しました")
        else:
            messages.error(request, "⚠️ Spotify認証が必要です")
            return redirect("festival:spotify_login")

    return redirect("festival:create_playlist")