from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.dateparse import parse_time
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q

from ..models import Event, EventDay, Performance, Stage, Artist
from ..forms import EventDayPerformanceForm, ArtistSchedulePasteForm

import json
from datetime import datetime, timedelta

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

    # 最終レンダリング    
    if not selected_event:
        return render(request, 'register_event_day.html', {
            'form': None,
            'message': 'イベントが指定されていません。',
            'event_data_json': '{}',
            'selected_event_id': ''
        })
    else:
        return render(request, 'register_event_day.html', {
            'form': form,
            'message': message,
            'event_data_json': json.dumps(event_data, cls=DjangoJSONEncoder),
            'selected_event_id': selected_event.id if selected_event else ''
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

def register_timetable(request):
    """タイムテーブル登録"""
    event_day_id = request.GET.get('event_day')
    event_day = get_object_or_404(EventDay, id=event_day_id) if event_day_id else None
    stages = Stage.objects.filter(event=event_day.event) if event_day else []
    form_errors = []
    selected_artist_ids = []
    selected_stage_id = None

    # 出演時間未登録のアーティストのみ表示
    artists = Artist.objects.filter(
        performance__event_day=event_day
    ).filter(
        Q(performance__start_time__isnull=True) | Q(performance__end_time__isnull=True)
    ).distinct() if event_day else []

    if request.method == 'POST':
        selected_artist_ids = request.POST.getlist('selected_artists')
        selected_stage_id = request.POST.get('selected_stage')
        new_stage_name = request.POST.get('new_stage_name')

        # ステージ選択または新規作成
        if new_stage_name:
            stage = Stage.objects.create(event=event_day.event, name=new_stage_name)
        elif selected_stage_id:
            stage = Stage.objects.filter(id=selected_stage_id).first()
        else:
            stage = None

        if 'save_times' in request.POST:
            for artist_id in selected_artist_ids:
                start = request.POST.get(f'start_{artist_id}')
                end = request.POST.get(f'end_{artist_id}')

                # バリデーション
                if start and end and parse_time(start) >= parse_time(end):
                    artist = Artist.objects.filter(id=artist_id).first()
                    form_errors.append(f"{artist.name} の開始時間は終了時間より前である必要があります。")
                    continue

                # Performance取得または作成
                perf, _ = Performance.objects.get_or_create(
                    event_day=event_day,
                    artist_id=artist_id
                )

                perf.stage = stage
                perf.start_time = parse_time(start) if start else None
                perf.end_time = parse_time(end) if end else None
                perf.save()

            if not form_errors:
                messages.success(request, "タイムテーブルを保存しました！")
                return redirect(request.path + f"?event_day={event_day_id}")

    context = {
        'event_days': EventDay.objects.order_by('date'),
        'selected_day_id': event_day_id,
        'event_day': event_day,
        'stages': stages,
        'artists': artists,
        'selected_artist_ids': selected_artist_ids,
        'selected_stage_id': selected_stage_id,
        'form_errors': form_errors,
    }
    return render(request, 'timetable_register.html', context)

def timetable_view(request):
    """タイムテーブル表示機能"""
    event_day_id = request.GET.get('event_day')
    event_day = None
    stages = []

    if event_day_id:
        event_day = get_object_or_404(EventDay, id=event_day_id)
        stages = Stage.objects.filter(event=event_day.event)

    context = {
        'event_days': EventDay.objects.order_by('date'),
        'selected_day_id': event_day_id,
        'event_day': event_day,
        'stages': stages,
    }
    return render(request, 'timetable_view.html', context)

def edit_performance(request, performance_id):
    """タイムテーブル修正ビュー"""
    perf = get_object_or_404(Performance, id=performance_id)
    stages = Stage.objects.filter(event=perf.event_day.event)

    if request.method == 'POST':
        selected_stage_id = request.POST.get('selected_stage')
        start = request.POST.get('start_time')
        end = request.POST.get('end_time')

        if start and end and parse_time(start) >= parse_time(end):
            messages.error(request, "開始時間は終了時間より前である必要があります。")
        else:
            perf.stage_id = selected_stage_id
            perf.start_time = parse_time(start) if start else None
            perf.end_time = parse_time(end) if end else None
            perf.save()
            messages.success(request, "タイムテーブルを更新しました！")
            return redirect('festival:timetable_view')  # 表示画面に戻る

    context = {
        'performance': perf,
        'stages': stages,
    }
    return render(request, 'edit_performance.html', context)