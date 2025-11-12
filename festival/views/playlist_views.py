from django.shortcuts import render, get_object_or_404
from festival.models import EventDay, Performance, Artist
from festival.forms import PlaylistForm
from festival.utils.spotify_utils import get_top_tracks

def create_playlist_view(request):
    """出演アーティストを選択してSpotifyプレイリストを生成するビュー"""

    selected_day_id = request.GET.get('event_day')
    selected_day = EventDay.objects.filter(id=selected_day_id).first()
    playlist = []

    # 出演アーティスト一覧（チェックボックス表示用）
    artists_qs = Artist.objects.filter(performance__event_day=selected_day).distinct() if selected_day else Artist.objects.none()

    if request.method == 'POST':
        form = PlaylistForm(request.POST, artists_queryset=artists_qs)
        if form.is_valid():
            selected_artists = form.cleaned_data['artists']
            for artist in selected_artists:
                tracks = get_top_tracks(artist.spotify_id)
                for track in tracks[:1]:  # 代表曲1曲だけ使う（必要なら複数可）
                    playlist.append({
                        'name': track['name'],
                        'artist': artist.name,
                        'spotify_url': track['external_urls']['spotify']
                    })
    else:
        form = PlaylistForm(artists_queryset=artists_qs)

    # イベント日程一覧（セレクトボックス用）
    event_days = EventDay.objects.select_related('event').order_by('date')

    return render(request, 'playlist_create.html', {
        'form': form,
        'playlist': playlist,
        'event_days': event_days,
        'selected_day_id': selected_day_id
    })