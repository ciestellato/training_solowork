from django.shortcuts import render, get_object_or_404

from .models import Artist, Event, Performance

# Create your views here.
def index(request):
    """ホームページ"""
    return render(request, 'index.html')

def artist_list(request):
    """アーティストの一覧表示ページ"""
    query = request.GET.get('q')  # 検索語を取得
    if query:
        artists = Artist.objects.filter(name__icontains=query).order_by('name')
    else:
        artists = Artist.objects.all().order_by('name')
    return render(request, 'artist_list.html', {'artists': artists, 'query': query})

def artist_detail(request, pk):
    """アーティストの詳細ページ"""
    artist = get_object_or_404(Artist, pk=pk)
    return render(request, 'artist_detail.html', {'artist': artist})

def event_list(request):
    """イベントの一覧表示ページ"""
    events = Event.objects.all().order_by('start_date')
    return render(request, 'event_list.html', {'events': events})

def event_detail(request, pk):
    """イベント詳細ページ"""
    event = get_object_or_404(Event, pk=pk)
    performances = event.performance_set.select_related('artist').order_by('performance_date')
    return render(request, 'event_detail.html', {
        'event': event,
        'performances': performances
    })