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

この構成で、イベントと出演者の関係がざっくりと見えるようになります！  
次はどこを詰めていきましょうか？出演予測、プレイリスト、画面デザインなども進められますよ。
