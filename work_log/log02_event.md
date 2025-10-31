ありがとうございます、非常に理にかなった設計です！🎸  
フェスが複数日開催される一方で、アーティストの出演は1日のみという構造は、現実の音楽フェスの運営にぴったりですね。

このモデル定義をもとに、ざっくりとイベントと出演情報を表示する画面を作っていきましょう。

---

## 🧭 今回の目標

- イベント一覧ページを作成（開催日・場所・概要）
- 各イベントに紐づく出演者一覧を表示（出演日・確定状況）
- 管理画面で登録・編集できるようにする

---

## 🔧 1. 管理画面登録（`admin.py`）

```python
from django.contrib import admin
from .models import Event, Performance

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'location')
    search_fields = ('name', 'location')
    list_filter = ('start_date',)

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'artist', 'performance_date', 'is_confirmed')
    list_filter = ('event', 'performance_date', 'is_confirmed')
    search_fields = ('artist__name', 'event__name')
```

---

## 🗂️ 2. ルーティング追加（`urls.py`）

```python
path('events/', views.event_list, name='event_list'),
```

---

## 🧱 3. ビュー作成（`views.py`）

```python
from .models import Event

def event_list(request):
    events = Event.objects.all().order_by('start_date')
    return render(request, 'event_list.html', {'events': events})
```

---

## 🖼️ 4. テンプレート作成（`event_list.html`）

```html
<!-- festival/templates/event_list.html -->

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>イベント一覧</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-4">
    <h1>🎪 イベント一覧</h1>

    {% for event in events %}
    <div class="card mb-4">
        <div class="card-header">
            <strong>{{ event.name }}</strong>（{{ event.start_date }}〜{{ event.end_date }} / {{ event.location }}）
        </div>
        <div class="card-body">
            <p>{{ event.description|linebreaks }}</p>
            <h5>出演者一覧</h5>
            <ul class="list-group">
                {% for perf in event.performance_set.all %}
                <li class="list-group-item">
                    {{ perf.performance_date }}：{{ perf.artist.name }}
                    {% if perf.is_confirmed %}
                        <span class="badge bg-success">確定</span>
                    {% else %}
                        <span class="badge bg-warning text-dark">未確定</span>
                    {% endif %}
                </li>
                {% empty %}
                <li class="list-group-item text-muted">出演者未登録</li>
                {% endfor %}
            </ul>
        </div>
    </div>
    {% empty %}
    <p>イベントが登録されていません。</p>
    {% endfor %}

    <a href="{% url 'index' %}" class="btn btn-secondary">トップへ戻る</a>
</body>
</html>
```

---

## ✅ 5. マイグレーション（必要なら）

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## ✨ 次のステップ候補

- イベント詳細ページ（出演者＋Spotifyリンク）
- アーティスト詳細ページに出演イベント一覧を追加
- 出演予測ロジック（類似アーティスト × 過去出演 ×ジャンル）

---

イベント詳細ページでは、イベントの基本情報（名前・開催期間・場所・説明）に加えて、出演者一覧（出演日・確定状況）を表示する構成にしましょう。

---

## 🧭 今回の目標

- `/event/<int:pk>/` でイベント詳細ページを表示
- イベント情報と出演者一覧を表示
- 一覧ページからリンクで遷移できるようにする

---

## 🔧 1. `urls.py` にルート追加

```python
# festival/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('artists/', views.artist_list, name='artist_list'),
    path('events/', views.event_list, name='event_list'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),  # ← 追加
]
```

---

## 🧱 2. `views.py` に詳細ビュー追加

```python
# festival/views.py

from django.shortcuts import render, get_object_or_404
from .models import Event

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    performances = event.performance_set.select_related('artist').order_by('performance_date')
    return render(request, 'event_detail.html', {
        'event': event,
        'performances': performances
    })
```

---

## 🖼️ 3. `event_detail.html` を作成

```html
<!-- festival/templates/event_detail.html -->

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>{{ event.name }} の詳細</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-4">
    <h1>{{ event.name }} の詳細</h1>

    <div class="mb-3">
        <p><strong>開催期間:</strong> {{ event.start_date }} 〜 {{ event.end_date }}</p>
        <p><strong>場所:</strong> {{ event.location }}</p>
        <p><strong>説明:</strong><br>{{ event.description|linebreaks }}</p>
    </div>

    <h4>出演者一覧</h4>
    <ul class="list-group mb-4">
        {% for perf in performances %}
        <li class="list-group-item d-flex justify-content-between align-items-center">
            <div>
                {{ perf.performance_date }}：<a href="{% url 'artist_detail' perf.artist.pk %}">{{ perf.artist.name }}</a>
            </div>
            {% if perf.is_confirmed %}
                <span class="badge bg-success">確定</span>
            {% else %}
                <span class="badge bg-warning text-dark">未確定</span>
            {% endif %}
        </li>
        {% empty %}
        <li class="list-group-item text-muted">出演者未登録</li>
        {% endfor %}
    </ul>

    <a href="{% url 'event_list' %}" class="btn btn-secondary">イベント一覧に戻る</a>
</body>
</html>
```

---

## 🔗 4. 一覧ページからリンク追加（任意）

```html
<!-- event_list.html のイベント名をリンクに変更 -->

<div class="card-header">
    <strong><a href="{% url 'event_detail' event.pk %}">{{ event.name }}</a></strong>
    （{{ event.start_date }}〜{{ event.end_date }} / {{ event.location }}）
</div>
```

---

## ✅ 5. 動作確認

- `/event/1/` のようなURLで詳細ページが表示されるか確認
- 出演者一覧が正しく表示されるか確認
- 一覧ページからリンクで遷移できるか確認

---

このページができれば、イベントごとの出演者情報をしっかり把握できるようになります！  
次はアーティスト詳細ページに出演イベント一覧を追加するのもおすすめです。進めましょうか？
