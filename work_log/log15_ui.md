# 配色変更

**「Blast the Music」カラーをベースに、ページ全体の配色を調整するには、staticフォルダに custom.css を作成して、主要色を反映させるのが最適です。**  
Bootstrapの構造を活かしつつ、以下のように色を割り当てることで、フェスらしい鮮やかで統一感のあるUIが実現できます。

---

## 🎨 カラーパレット（Blast the Music）

| 色名               | HEXコード   | 用途の提案 |
|--------------------|-------------|------------|
| Cadmium Violet     | `#832C99`   | ナビバー背景、ボタン |
| Medium Sea Green   | `#38BD67`   | 成功系メッセージ、チェック済み表示 |
| Champagne          | `#F6E2CB`   | 背景色、カード内背景 |
| Spanish Crimson    | `#E9184E`   | アクションボタン、リンクホバー |
| American Purple    | `#3F1E59`   | フッター、タイトル文字色 |

出典: 

---

## 🛠️ custom.css の例

```css
body {
    background-color: #F6E2CB; /* Champagne */
    color: #3F1E59; /* American Purple */
    font-family: 'Helvetica Neue', sans-serif;
}

.navbar {
    background-color: #832C99; /* Cadmium Violet */
}

.navbar-brand, .nav-link {
    color: #F6E2CB !important;
}

.nav-link:hover {
    color: #E9184E !important; /* Spanish Crimson */
}

.btn-primary {
    background-color: #E9184E;
    border-color: #E9184E;
}

.btn-primary:hover {
    background-color: #832C99;
    border-color: #832C99;
}

.card {
    background-color: #F6E2CB;
    border: none;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

footer {
    background-color: #3F1E59;
    color: #F6E2CB;
    padding: 10px;
    text-align: center;
}
```

---

## 📦 static フォルダに配置

1. `static/css/custom.css` を作成
2. `base.html` の `<head>` に以下を追加：

```html
{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/custom.css' %}">
{% endblock %}
```

---

## ✨ 補足アイデア

- ステージカラーを `Stage.color_code` に基づいてインラインスタイルで反映する場合、テンプレート内で `style="background-color: {{ stage.color_code }};"` を使うと柔軟です。
- Bootstrapの `btn`, `card`, `alert` などの構造を活かしつつ、色だけを上書きすることで、保守性と一貫性を両立できます。

---

このエラーの原因は明確で、テンプレート内で `{% static '...' %}` を使っているにもかかわらず、**`{% load static %}` をテンプレートの先頭で読み込んでいない**ことが原因です。

---

## ✅ 解決方法

テンプレートファイル（例：`base.html`）の冒頭に、以下の1行を追加してください：

```django
{% load static %}
```

### 修正後の例（`base.html`）

```html
{% load static %}
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}音楽フェスティバル管理{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    {% block extra_css %}
        <link rel="stylesheet" href="{% static 'css/color.css' %}">
    {% endblock %}
    <style>
        body {
            padding-top: 50px;
        }
    </style>
</head>
<body>
    ...
```

---

## 🔍 なぜ必要？

- `{% static %}` は Django のテンプレートタグで、静的ファイルのURLを解決するために使います。
- これを使うには、テンプレート内で `{% load static %}` を宣言して、テンプレートタグを有効にする必要があります。
- これを忘れると、Djangoは `{% static %}` を「知らないタグ」として扱い、`TemplateSyntaxError` を出します。

---

## ✅ 補足チェックポイント

- `color.css` のパスが `static/css/color.css` であることを再確認
- 開発環境であれば、`python manage.py runserver` で `STATICFILES_DIRS` の設定が効いているか確認
- ブラウザのキャッシュをクリアして、CSSの変更が反映されているか確認

---

これでエラーは解消されるはずです！  
もし他のテンプレートでも `{% static %}` を使っている場合は、それぞれのテンプレートにも `{% load static %}` を忘れずに追加してくださいね。

# アーティスト詳細ページ

アーティスト詳細ページで「今日以降のスケジュール」と「過去の出演履歴」を分けて表示し、それぞれを日付順（未来は昇順、過去は降順）に並べるには、`artist_detail` ビューを以下のように修正できます。

---

## ✅ 修正後の `artist_detail` ビュー

```python
from datetime import date
from django.utils.timezone import localdate

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
```

---

## 🧾 テンプレート側の表示例（`artist_detail.html`）

```django
<h1>{{ artist.name }}</h1>

{% if upcoming_performances %}
    <h2 class="mt-4">🎤 今後の出演予定</h2>
    <ul class="list-group mb-4">
        {% for perf in upcoming_performances %}
            <li class="list-group-item">
                {{ perf.event_day.date }} @ {{ perf.event_day.venue }}<br>
                {{ perf.stage.name }} / {{ perf.start_time|time:"H:i" }} - {{ perf.end_time|time:"H:i" }}<br>
                <a href="{% url 'festival:event_detail' perf.event_day.event.id %}">{{ perf.event_day.event.name }}</a>
            </li>
        {% endfor %}
    </ul>
{% else %}
    <p>今後の出演予定はありません。</p>
{% endif %}

{% if past_performances %}
    <h2 class="mt-4">📜 過去の出演履歴</h2>
    <ul class="list-group">
        {% for perf in past_performances %}
            <li class="list-group-item">
                {{ perf.event_day.date }} @ {{ perf.event_day.venue }}<br>
                {{ perf.stage.name }} / {{ perf.start_time|time:"H:i" }} - {{ perf.end_time|time:"H:i" }}<br>
                <a href="{% url 'festival:event_detail' perf.event_day.event.id %}">{{ perf.event_day.event.name }}</a>
            </li>
        {% endfor %}
    </ul>
{% else %}
    <p>過去の出演履歴はありません。</p>
{% endif %}
```

---

## 💡補足ポイント

- `localdate()` を使うことで、タイムゾーンに対応した「今日」の日付を取得できます。
- `event_day__date` を基準にフィルタリングしているため、`EventDay` モデルに `date` フィールドがある前提です。
- 並び順は `upcoming` は昇順、`past` は降順にして、ユーザーが直感的に把握しやすくしています。

# イベントの過去と未来のページ分け

フェスイベント一覧を「今後のイベント（upcoming）」と「過去のイベント（history）」でページ分割するには、以下の3ステップで対応できます。

---

## ✅ 1. ビュー関数の分割（`event_views.py`）

```python
from datetime import date
from django.shortcuts import render
from ..models import Event

def event_list_upcoming(request):
    """今後のフェスイベント一覧"""
    today = date.today()
    events = Event.objects.filter(end_date__gte=today).order_by('start_date')
    return render(request, 'event_list_upcoming.html', {
        'events': events,
        'mode': 'upcoming',
    })

def event_list_history(request):
    """過去のフェスイベント一覧"""
    today = date.today()
    events = Event.objects.filter(end_date__lt=today).order_by('-start_date')
    return render(request, 'event_list_history.html', {
        'events': events,
        'mode': 'history',
    })
```

---

## ✅ 2. URL設定（`festival/urls.py`）

```python
from django.urls import path
from .views import event_views

urlpatterns = [
    path('events/upcoming/', event_views.event_list_upcoming, name='fes_event_upcoming'),
    path('events/history/', event_views.event_list_history, name='fes_event_history'),
]
```

---

## ✅ 3. テンプレートの共通化（`event_list_base.html`）

```django
{% extends 'base.html' %}
{% load static %}

{% block extra_css %}
    <link rel="stylesheet" href="{% static 'css/color.css' %}">
{% endblock %}

{% block title %}
    {% if mode == 'upcoming' %}今後のフェスイベント一覧{% else %}過去のフェスイベント一覧{% endif %}
{% endblock %}

{% block content %}
<h1>
    {% if mode == 'upcoming' %}🎪 今後のフェスイベント一覧{% else %}📜 過去のフェスイベント一覧{% endif %}
    {% if request.user.is_staff %}
        <a href="{% url 'festival:create_event' %}" class="btn btn-primary mt-3">📅 イベント登録</a>
    {% endif %}
</h1>

<div class="mb-3">
    <a href="{% url 'festival:fes_event_upcoming' %}" class="btn {% if mode == 'upcoming' %}btn-secondary{% else %}btn-outline-secondary{% endif %}">今後のイベント</a>
    <a href="{% url 'festival:fes_event_history' %}" class="btn {% if mode == 'history' %}btn-secondary{% else %}btn-outline-secondary{% endif %}">過去のイベント</a>
</div>

{% if events %}
    <ul class="list-group">
        {% for event in events %}
            <li class="list-group-item">
                <a href="{% url 'festival:event_detail' event.id %}">{{ event.name }}</a>
                <span class="text-muted">（{{ event.start_date }}〜{{ event.end_date }}）</span>
                {% if request.user.is_staff %}
                    <a href="{% url 'festival:edit_event' event.id %}" class="btn btn-outline-secondary btn-sm ms-2">編集</a>
                {% endif %}
            </li>
        {% endfor %}
    </ul>
{% else %}
    <p class="text-muted">該当するイベントはありません。</p>
{% endif %}

<a href="{% url 'festival:index' %}" class="btn btn-primary mt-3">トップへ戻る</a>
{% endblock %}
```

そして `event_list_upcoming.html` / `event_list_history.html` は以下のように共通テンプレートを継承：

```django
{% include 'event_list_base.html' %}
```

---

この構成により、今後のイベントと過去のイベントを明確に分けて表示でき、ユーザーも管理者も使いやすくなります。必要なら、フィルタや検索機能も追加できますよ！
