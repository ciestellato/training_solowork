from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import timedelta

from .models import Artist, Event, EventDay, Performance
from .forms import EventDayPerformanceForm

from .spotify import save_artist_from_spotify  # Spotify API連携関数

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
    event_days = event.eventday_set.all().order_by('date')  # EventDayを取得

    # 各 EventDay に紐づく Performance をまとめる
    day_performances = []
    for day in event_days:
        performances = day.performance_set.select_related('artist').order_by('artist__name')
        day_performances.append((day, performances))

    return render(request, 'event_detail.html', {
        'event': event,
        'day_performances': day_performances
    })

def get_event_schedule_json(request):
    """イベント一覧をJSONで渡す"""
    message = ''
    events = Event.objects.all()
    event_data = {
        str(e.id): {
            'start': e.start_date.strftime('%Y-%m-%d'),
            'end': e.end_date.strftime('%Y-%m-%d')
        } for e in events
    }

    if request.method == 'POST':
        form = EventDayPerformanceForm(request.POST)
        if form.is_valid():
            event = form.cleaned_data['event']
            date = form.cleaned_data['date']
            venue = form.cleaned_data['venue']
            artists = form.cleaned_data['artists']

            event_day = EventDay.objects.create(event=event, date=date, venue=venue)

            for artist in artists:
                Performance.objects.create(event_day=event_day, artist=artist, is_confirmed=True)

            message = f"{event_day} に {artists.count()} 組の出演者を登録しました。"
            form = EventDayPerformanceForm()  # フォームをリセット
    else:
        form = EventDayPerformanceForm()

    return render(request, 'register_event_day.html', {
        'form': form,
        'message': message,
        'event_data_json': json.dumps(event_data, cls=DjangoJSONEncoder)
    })

def bulk_artist_register(request):
    """アーティストの一括登録処理"""
    from .forms import BulkArtistForm

    message = ''
    if request.method == 'POST':
        form = BulkArtistForm(request.POST)
        if form.is_valid():
            raw_names = form.cleaned_data['names']
            name_list = [name.strip() for name in raw_names.split(',') if name.strip()]
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
    else:
        form = BulkArtistForm()
    return render(request, 'bulk_artist_register.html', {'form': form, 'message': message})

@staff_member_required
def register_event_day_and_performances(request):
    """イベント日・会場・出演者登録"""
    message = ''
    event_id = request.GET.get('event_id')
    selected_event = get_object_or_404(Event, id=event_id) if event_id else None

    # 日付選択肢を生成
    date_choices = []
    event_data = {}
    if selected_event:
        start = selected_event.start_date
        end = selected_event.end_date
        current = start
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            date_choices.append((date_str, date_str))
            current += timedelta(days=1)

        event_data[str(selected_event.id)] = {
            'start': start.strftime('%Y-%m-%d'),
            'end': end.strftime('%Y-%m-%d')
        }

    # フォーム生成（POSTかGETかで分岐）
    if request.method == 'POST':
        post_data = request.POST.copy()
        if selected_event:
            post_data['event'] = selected_event.id  # hiddenで送ったeventを強制セット
        form = EventDayPerformanceForm(post_data)
    else:
        form = EventDayPerformanceForm(initial={'event': selected_event})

    # 日付選択肢をフォームに設定
    form.fields['date'].choices = date_choices

    # 登録処理
    if request.method == 'POST' and form.is_valid():
        event = form.cleaned_data['event']
        date = form.cleaned_data['date']
        venue = form.cleaned_data['venue']
        artists = form.cleaned_data['artists']

        event_day = EventDay.objects.create(event=event, date=date, venue=venue)
        for artist in artists:
            Performance.objects.create(event_day=event_day, artist=artist, is_confirmed=True)

        message = f"{event_day} に {artists.count()} 組の出演者を登録しました。"
        form = EventDayPerformanceForm(initial={'event': selected_event})
        form.fields['date'].choices = date_choices  # 再設定

    return render(request, 'register_event_day.html', {
        'form': form,
        'message': message,
        'event_data_json': json.dumps(event_data, cls=DjangoJSONEncoder),
        'selected_event_id': selected_event.id if selected_event else ''
    })