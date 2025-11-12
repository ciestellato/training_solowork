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
    # 初期化
    selected_day_id = request.GET.get('event_day')
    selected_day = EventDay.objects.filter(id=selected_day_id).first()
    playlist = []
    track_uris = []
    track_count = 1
    can_save_to_spotify = True

    # 出演アーティスト一覧（チェックボックス表示用）
    artists_qs = Artist.objects.filter(performance__event_day=selected_day).distinct() if selected_day else Artist.objects.none()

    if request.method == 'POST':
        form = PlaylistForm(request.POST, artists_queryset=artists_qs)
        if form.is_valid():
            track_count = int(request.POST.get("track_count", 1))
            selected_artists = form.cleaned_data['artists']
            total_tracks = len(selected_artists) * track_count

            # Spotify保存制限チェック
            can_save_to_spotify = total_tracks <= 100

            for artist in selected_artists:
                tracks = get_top_tracks(artist.spotify_id)
                for track in tracks[:track_count]:
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

    event_day = EventDay.objects.select_related('event').filter(id=selected_day_id).first()
    event_name = event_day.event.name if event_day else "Festival"
    event_date = event_day.date.strftime("%Y%m%d") if event_day else "Unknown"

    playlist_name = f"{event_name} {event_date} 予習リスト"
    
    return render(request, 'playlist_create.html', {
        'form': form,
        'playlist': playlist,
        'track_uris': track_uris,
        'event_days': event_days,
        'selected_day_id': selected_day_id,
        'playlist_name': playlist_name,
        'selected_track_count': str(track_count),
        'can_save_to_spotify': can_save_to_spotify
    })

def save_playlist_to_spotify_view(request):
    """Spotifyにプレイリストを保存するビュー"""
    if request.method == 'POST':
        token = request.session.get("spotify_token")
        track_uris = request.POST.get("track_uris", "").split(",")
        playlist_name = request.POST.get("playlist_name", "フェス予習プレイリスト")

        if token and track_uris:
            playlist_url = save_playlist_to_spotify(token, track_uris, playlist_name)
            if playlist_url:
                messages.success(request, f"✅ Spotifyに保存しました！<br><a href='{playlist_url}' target='_blank'>プレイリストを開く</a>")
            else:
                messages.error(request, "❌ Spotifyへの保存に失敗しました")
        else:
            messages.error(request, "⚠️ Spotify認証が必要です")
            return redirect("festival:spotify_login")

    return redirect("festival:create_playlist")