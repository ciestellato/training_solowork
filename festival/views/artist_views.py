from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import localdate

from ..models import Artist, Performance, EventDay
from ..forms import ArtistForm, ArtistBulkEditForm, BulkArtistForm
from ..utils.spotify_utils import save_artist_from_spotify
from ..utils.text_utils import get_initial_group

def artist_list(request):
    """アーティスト一覧ページ（検索・頭文字絞り込み付き）"""
    query = request.GET.get('q')
    initial = request.GET.get('initial')

    all_artists = Artist.objects.exclude(furigana__isnull=True).exclude(furigana__exact='')
    artists = all_artists
    if query:
        artists = artists.filter(name__icontains=query)
    if initial:
        artists = artists.filter(furigana__startswith=initial)
    artists = artists.order_by('furigana')

    initials = sorted(set(get_initial_group(a.furigana) for a in all_artists if a.furigana))
    kana_order = ['あ', 'か', 'さ', 'た', 'な', 'は', 'ま', 'や', 'ら', 'わ']
    alpha_order = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    sorted_initials = [i for i in kana_order + alpha_order if i in initials]

    return render(request, 'artist_list.html', {
        'artists': artists,
        'query': query,
        'initial': initial,
        'initials': sorted_initials,
    })

def artist_detail(request, pk):
    """アーティスト詳細ページ"""
    artist = get_object_or_404(Artist, pk=pk)
    today = localdate()

    # 関連する出演情報を取得（イベント情報も含めて）
    performances = Performance.objects.filter(artist=artist).select_related('event_day__event', 'stage')

    # 今日以降のスケジュール（昇順）
    upcoming_performances = performances.filter(event_day__date__gte=today).order_by('event_day__date', 'start_time')

    # 昨日以前の出演履歴（降順）
    past_performances = performances.filter(event_day__date__lt=today).order_by('-event_day__date', '-start_time')

    return render(request, 'artist_detail.html', {
        'artist': artist,
        'upcoming_performances': upcoming_performances,
        'past_performances': past_performances,
    })

@staff_member_required
def edit_artist_bulk(request):
    """アーティスト一括編集ビュー"""
    artists = Artist.objects.all()
    for artist in artists:
        artist.initial_group = get_initial_group(artist.furigana or artist.name)
    artists = sorted(artists, key=lambda a: a.initial_group)

    form = ArtistBulkEditForm(request.POST or None, artists=artists)
    if request.method == 'POST' and form.is_valid():
        for artist in artists:
            artist.name = form.cleaned_data.get(f'name_{artist.id}', artist.name)
            artist.furigana = form.cleaned_data.get(f'furigana_{artist.id}', artist.furigana)
            artist.save()
        return redirect('festival:artist_list')

    return render(request, 'artist_bulk_edit.html', {
        'form': form,
        'artists': artists,
        'initials': sorted(set(a.initial_group for a in artists)),
    })

@staff_member_required
def bulk_artist_register(request):
    """Spotify APIを使ったアーティスト一括登録ビュー"""
    message = ''
    form = BulkArtistForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        raw_names = form.cleaned_data['names']
        name_list = [name.strip() for line in raw_names.splitlines() for name in line.split(',') if name.strip()]
        created = 0
        skipped = 0
        for name in name_list:
            if Artist.objects.filter(name__iexact=name).exists():
                skipped += 1
                continue
            result = save_artist_from_spotify(name)
            if result:
                created += 1
        message = f"{created} 件登録、{skipped} 件スキップしました。"

    return render(request, 'bulk_artist_register.html', {
        'form': form,
        'message': message
    })

@staff_member_required
def edit_artist(request, artist_id):
    """アーティスト個別編集ビュー"""
    artist = get_object_or_404(Artist, pk=artist_id)
    form = ArtistForm(request.POST or None, instance=artist)
    if form.is_valid():
        form.save()
        return redirect('festival:artist_detail', pk=artist.id)

    return render(request, 'artist_form.html', {
        'form': form,
        'artist': artist,
        'mode': 'edit'
    })