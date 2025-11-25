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

    # 全アーティスト（ふりがなあり）
    all_artists = Artist.objects.exclude(furigana__isnull=True).exclude(furigana__exact='')

    artists = all_artists

    # 検索フィルタ
    if query:
        artists = artists.filter(name__icontains=query)

    artists = artists.order_by('furigana')

    # 頭文字フィルタ（Python側で最終的に絞り込み）
    if initial:
        artists = [a for a in artists if a.initial_group == initial]

    # 初期グループ一覧生成（全件ベース）
    kana_order = ['あ', 'か', 'さ', 'た', 'な', 'は', 'ま', 'や', 'ら', 'わ']
    alpha_order = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    initials = set(a.initial_group for a in all_artists if a.furigana)

    initials_kana = [i for i in kana_order if i in initials]
    initials_alpha = [i for i in alpha_order if i in initials]

    return render(request, 'artist_list.html', {
        'artists': artists,
        'query': query,
        'initial': initial,
        'initials_kana': initials_kana,
        'initials_alpha': initials_alpha,
    })

def artist_detail(request, pk):
    """アーティスト詳細ページ"""
    artist = get_object_or_404(Artist, pk=pk)
    today = localdate()

    performances = Performance.objects.filter(artist=artist).select_related(
        'event_day__event', 'stage'
    )

    upcoming_performances = performances.filter(
        event_day__date__gte=today
    ).order_by('event_day__date', 'start_time')

    past_performances = performances.filter(
        event_day__date__lt=today
    ).order_by('-event_day__date', '-start_time')

    return render(request, 'artist_detail.html', {
        'artist': artist,
        'upcoming_performances': upcoming_performances,
        'past_performances': past_performances,
    })

@staff_member_required
def edit_artist_bulk(request):
    """アーティスト一括編集ビュー"""
    artists = list(Artist.objects.all())
    artists.sort(key=lambda a: a.initial_group)

    form = ArtistBulkEditForm(request.POST or None, artists=artists)
    if request.method == 'POST' and form.is_valid():
        updated = []
        for artist in artists:
            artist.name = form.cleaned_data.get(f'name_{artist.id}', artist.name)
            artist.furigana = form.cleaned_data.get(f'furigana_{artist.id}', artist.furigana)
            updated.append(artist)
        Artist.objects.bulk_update(updated, ['name', 'furigana'])
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