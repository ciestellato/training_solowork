from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import timedelta, datetime

from .models import Artist, Event, EventDay, Performance
from .forms import EventDayPerformanceForm, ArtistSchedulePasteForm, EventForm, ArtistForm, ArtistBulkEditForm

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
    
    # 出演情報が入力されているイベント日程を取得（確定・未確定問わず）
    performances = Performance.objects.filter(artist=artist).select_related('event_day__event')

    return render(request, 'artist_detail.html', {
        'artist': artist,
        'performances': performances,
    })

@staff_member_required
def edit_artist_bulk(request):
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

def event_list(request):
    """イベントの一覧表示ページ"""
    events = Event.objects.all().order_by('start_date')
    return render(request, 'event_list.html', {'events': events})

def fes_event_list(request):
    """フェスイベント一覧ページ"""
    events = Event.objects.filter(event_type='FES').order_by('start_date')
    return render(request, 'event_list_fes.html', {'events': events})

def other_event_list(request):
    """フェス以外のイベント一覧ページ"""
    events = Event.objects.exclude(event_type='FES').order_by('start_date')
    return render(request, 'event_list_other.html', {'events': events})

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

@staff_member_required
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
def edit_artist(request, artist_id):
    """アーティスト情報編集ビュー"""
    artist = get_object_or_404(Artist, pk=artist_id)

    if request.method == 'POST':
        form = ArtistForm(request.POST, instance=artist)
        if form.is_valid():
            form.save()
            return redirect('festival:artist_detail', pk=artist.id)
    else:
        form = ArtistForm(instance=artist)

    return render(request, 'artist_form.html', {
        'form': form,
        'artist': artist,
        'mode': 'edit'
    })

@staff_member_required
def create_event(request):
    """イベント登録ビュー"""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('festival:fes_event_list')  # 遷移先はお好みで
    else:
        form = EventForm()
    return render(request, 'event_form.html', {'form': form, 'mode': 'create'})

def edit_event(request, event_id):
    """イベント編集ビュー"""
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('festival:event_detail', event.id)
    else:
        form = EventForm(instance=event)
    return render(request, 'event_form.html', {'form': form, 'mode': 'edit', 'event': event})

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

@staff_member_required
def edit_event_day_performances(request, event_day_id):
    """特定の EventDay に紐づく出演者を編集するビュー（管理者専用）"""

    # 対象の EventDay を取得（存在しない場合は 404）
    event_day = get_object_or_404(EventDay, pk=event_day_id)

    # EventDay に紐づくイベントを取得
    event = event_day.event

    # 現在登録されている出演者の ID を取得（初期値用）
    existing_artists = event_day.performance_set.values_list('artist_id', flat=True)

    # POST（フォーム送信）時の処理
    if request.method == 'POST':
        form = EventDayPerformanceForm(request.POST)

        # ✅ hiddenフィールドで送信された event ID を取得して Event オブジェクトに変換
        event_id = request.POST.get('event')
        if event_id:
            try:
                event = Event.objects.get(pk=event_id)
            except Event.DoesNotExist:
                form.add_error(None, "指定されたイベントが存在しません。")

        # 日付選択肢を1件だけ設定（この EventDay の日付）
        form.fields['date'].choices = [(event_day.date.strftime('%Y-%m-%d'), event_day.date.strftime('%Y-%m-%d'))]

        if form.is_valid():
            # 出演者情報を更新
            Performance.objects.filter(event_day=event_day).delete()
            for artist in form.cleaned_data['artists']:
                Performance.objects.create(event_day=event_day, artist=artist, is_confirmed=True)

            # 成功メッセージをセッションに保存してリダイレクト
            request.session['message'] = f"{event_day} の出演者を更新しました。"
            return redirect('festival:event_detail', pk=event.id)

    else:
        # GET（初期表示）時の処理
        date_str = event_day.date.strftime('%Y-%m-%d')
        date_choices = [(date_str, date_str)]

        # ✅ event は hiddenフィールドで送信されるため、initial に含める必要あり
        form = EventDayPerformanceForm(initial={
            'event': event.id,  # hiddenフィールド用にIDを渡す
            'date': date_str,
            'venue': event_day.venue,
            'artists': existing_artists
        })

        form.fields['date'].choices = date_choices

    # イベントの開催期間をJSON化してテンプレートに渡す
    event_data_json = json.dumps({
        str(event.id): {
            "start": event.start_date.strftime('%Y-%m-%d'),
            "end": event.end_date.strftime('%Y-%m-%d')
        }
    })

    return render(request, 'edit_event_day.html', {
        'form': form,
        'event_day': event_day,
        'event': event,
        'event_data_json': event_data_json,
        'selected_event_id': str(event.id)
    })

@staff_member_required
def paste_schedule_register(request):
    """ツアー日程登録ビュー"""
    message = ''
    artist_id = request.GET.get('artist_id')

    if request.method == 'POST':
        form = ArtistSchedulePasteForm(request.POST)
        if form.is_valid():
            artist = form.cleaned_data['artist']
            event_name = form.cleaned_data['event_name']
            raw_text = form.cleaned_data['raw_text']

            # イベント作成または取得
            event, _ = Event.objects.get_or_create(
                name=event_name,
                defaults={
                    'start_date': '',
                    'end_date': '',
                    'event_type': 'TOUR'
                }
            )

            count = 0
            for line in raw_text.splitlines():
                parts = line.strip().split(maxsplit=1)
                if len(parts) != 2:
                    continue
                date_str, venue = parts
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    event_day = EventDay.objects.create(event=event, date=date, venue=venue)
                    Performance.objects.create(event_day=event_day, artist=artist, is_confirmed=True)
                    count += 1
                except Exception:
                    continue  # 無効な行はスキップ

            message = f"{count} 件の出演日程を登録しました。"
            return redirect('festival:artist_detail', pk=form.cleaned_data['artist'].id)
    else:
        initial = {}
        if artist_id:
            initial['artist'] = artist_id
        form = ArtistSchedulePasteForm(initial=initial)

    return render(request, 'paste_schedule_register.html', {
        'form': form,
        'message': message,
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