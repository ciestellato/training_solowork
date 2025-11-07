from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import timedelta

from .models import Artist, Event, EventDay, Performance
from .forms import EventDayPerformanceForm

from .spotify import save_artist_from_spotify  # Spotify API連携関数
from .utils import get_initial_group

# Create your views here.
def index(request):
    """ホームページ"""
    return render(request, 'index.html')

def artist_list(request):
    query = request.GET.get('q')
    initial = request.GET.get('initial')

    # 全アーティスト（initials生成用）
    all_artists = Artist.objects.exclude(furigana__isnull=True).exclude(furigana__exact='')

    # 表示対象アーティスト（絞り込み）
    artists = all_artists
    if query:
        artists = artists.filter(name__icontains=query)
    if initial:
        artists = artists.filter(furigana__startswith=initial)

    artists = artists.order_by('furigana')

    # initialsは全アーティストから生成（絞り込みに依存しない）
    def get_initial_group(char):
        import unicodedata, re
        char = unicodedata.normalize('NFKC', char)[0].lower()
        if re.match(r'[a-z]', char):
            return char.upper()
        kana_groups = {
            'あ': 'あ', 'い': 'あ', 'う': 'あ', 'え': 'あ', 'お': 'あ',
            'か': 'か', 'き': 'か', 'く': 'か', 'け': 'か', 'こ': 'か',
            'さ': 'さ', 'し': 'さ', 'す': 'さ', 'せ': 'さ', 'そ': 'さ',
            'た': 'た', 'ち': 'た', 'つ': 'た', 'て': 'た', 'と': 'た',
            'な': 'な', 'に': 'な', 'ぬ': 'な', 'ね': 'な', 'の': 'な',
            'は': 'は', 'ひ': 'は', 'ふ': 'は', 'へ': 'は', 'ほ': 'は',
            'ま': 'ま', 'み': 'ま', 'む': 'ま', 'め': 'ま', 'も': 'ま',
            'や': 'や', 'ゆ': 'や', 'よ': 'や',
            'ら': 'ら', 'り': 'ら', 'る': 'ら', 'れ': 'ら', 'ろ': 'ら',
            'わ': 'わ', 'を': 'わ', 'ん': 'わ',
        }
        return kana_groups.get(char, char)

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
        # 登録処理
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
        # フォーム初期表示（GET）
        form = EventDayPerformanceForm()

    return render(request, 'register_event_day.html', {
        'form': form,
        'message': message,
        'event_data_json': json.dumps(event_data, cls=DjangoJSONEncoder)
    })

def bulk_artist_register(request):
    """アーティストの一括登録処理（カンマ・改行対応）"""
    from .forms import BulkArtistForm

    message = ''
    if request.method == 'POST':
        form = BulkArtistForm(request.POST)
        if form.is_valid():
            raw_names = form.cleaned_data['names']

            # 改行とカンマの両方で分割 → 空白除去 → 空文字除外
            name_list = []
            for line in raw_names.splitlines():
                for name in line.split(','):
                    cleaned = name.strip()
                    if cleaned:
                        name_list.append(cleaned)

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

    return render(request, 'bulk_artist_register.html', {
        'form': form,
        'message': message
    })

@staff_member_required
def register_event_day_and_performances(request):
    """イベント日・会場・出演者登録ビュー"""

    # セッションから登録完了メッセージを取得（POST後のGETで表示）
    message = request.session.pop('message', '')

    # クエリパラメータから対象イベントを取得
    event_id = request.GET.get('event_id')
    selected_event = get_object_or_404(Event, id=event_id) if event_id else None

    # 日付選択肢とイベント情報JSONを生成
    date_choices = generate_event_date_choices(selected_event)
    event_data = {
        str(selected_event.id): {
            'start': selected_event.start_date.strftime('%Y-%m-%d'),
            'end': selected_event.end_date.strftime('%Y-%m-%d')
        }
    } if selected_event else {}

    # POST処理：フォーム送信された場合
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['event'] = selected_event.id  # hiddenで送ったeventを強制セット
        form = EventDayPerformanceForm(post_data)
        form.fields['date'].choices = date_choices  # 日付選択肢を設定

        if form.is_valid():
            # EventDay と Performance を登録
            event_day = EventDay.objects.create(
                event=form.cleaned_data['event'],
                date=form.cleaned_data['date'],
                venue=form.cleaned_data['venue']
            )
            for artist in form.cleaned_data['artists']:
                Performance.objects.create(event_day=event_day, artist=artist, is_confirmed=True)

            # 成功メッセージをセッションに保存してリダイレクト（PRG）
            request.session['message'] = f"{event_day} に {form.cleaned_data['artists'].count()} 組の出演者を登録しました。"
            return redirect(f"{request.path}?event_id={selected_event.id}")

    else:
        # GET処理：フォーム初期表示
        form = EventDayPerformanceForm(initial={'event': selected_event})
        form.fields['date'].choices = date_choices  # 日付選択肢を設定

    # 最終レンダリング（GET時またはPOST失敗時）
    return render(request, 'register_event_day.html', {
        'form': form,
        'message': message,
        'event_data_json': json.dumps(event_data, cls=DjangoJSONEncoder),
        'selected_event_id': selected_event.id if selected_event else ''
    })
    if not selected_event:
        return render(request, 'register_event_day.html', {
            'form': None,
            'message': 'イベントが指定されていません。',
            'event_data_json': '{}',
            'selected_event_id': ''
        })

def generate_event_date_choices(event):
    """イベントの開催期間から日付選択肢を生成"""
    if not event:
        return []  # イベントが未指定なら空リストを返す
    choices = []
    current = event.start_date
    while current <= event.end_date:
        date_str = current.strftime('%Y-%m-%d')
        choices.append((date_str, date_str))
        current += timedelta(days=1)
    return choices