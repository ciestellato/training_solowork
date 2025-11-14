# タイムテーブル表示画面を改良しよう！

現在の`stage`ごとの縦並び表示を、**時間軸を縦軸、ステージを横軸にしたグリッド形式のタイムテーブル**に変更することで、出演時間の重なりやバッティングが一目で分かるようになります。

以下に、**グリッド型タイムテーブル表示**への改良案を提示します。

---

## 🧩 改良方針：時間×ステージのグリッド表示

### ✅ 目的
- ステージごとの出演時間を横並びに表示
- 時間を縦軸にして、同時刻にどのステージで誰が出演しているかを可視化
- 時間の粒度は15分単位などで調整可能

---

## 🧱 実装ステップ概要

### 1. **ビュー側（Python）での準備**
- 指定された`event_day`に属する`Performance`をすべて取得
- 出演時間の最小・最大をもとに時間スロットを生成（例：10:00〜22:00を15分刻み）

```python
from datetime import datetime, timedelta

def generate_time_slots(start, end, interval_minutes=15):
    slots = []
    current = start
    while current < end:
        slots.append(current)
        current += timedelta(minutes=interval_minutes)
    return slots
```

- 各ステージ・時間スロットに該当する`Performance`をマッピングしてテンプレートに渡す

---

### 2. **テンプレート（HTML）での表示ロジック**

以下は、時間×ステージのグリッド表示の基本構造です：

```html
<table class="table table-bordered timetable-grid">
    <thead>
        <tr>
            <th>時間</th>
            {% for stage in stages %}
                <th>{{ stage.name }}</th>
            {% endfor %}
        </tr>
    </thead>
    <tbody>
        {% for time in time_slots %}
            <tr>
                <td>{{ time|time:"H:i" }}</td>
                {% for stage in stages %}
                    <td>
                        {% for perf in performances_by_stage_and_time|get_item:stage.id|get_item:time %}
                            {{ perf.artist.name }}<br>
                            <small>{{ perf.start_time|time:"H:i" }} - {{ perf.end_time|time:"H:i" }}</small>
                            {% if request.user.is_staff %}
                                <a href="{% url 'festival:edit_performance' perf.id %}" class="btn btn-sm btn-outline-primary">編集</a>
                            {% endif %}
                        {% endfor %}
                    </td>
                {% endfor %}
            </tr>
        {% endfor %}
    </tbody>
</table>
```

> 💡 `performances_by_stage_and_time` は `{stage_id: {time_slot: [Performance, ...]}}` のようなネスト辞書をビューで構築しておくと便利です。

---

### 3. **スタイル調整（CSS）**
- `.timetable-grid td` に `min-height` を設定して見やすく
- `.table-fixed` や `overflow-x: auto` で横スクロール対応もおすすめ

---

## 🧪 補足：テンプレートフィルター `get_item`

辞書のネストアクセス用に以下のようなカスタムテンプレートフィルターを追加すると便利です：

```python
# festival/templatetags/custom_filters.py
from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
```

テンプレートで `{% load custom_filters %}` を忘れずに。

---

## ✅ まとめ

この改良により、以下のようなUXが実現できます：

- 同時間帯の出演者が横並びで比較できる
- ステージごとの空き時間やバッティングが視覚的に把握できる
- 管理者にとってもスケジュール調整がしやすくなる


タイムテーブルの見出しは表示されるが、出演者名などのデータが表示されないということですね。これはテンプレート側のループ処理か、ビューで渡しているデータ構造に原因がある可能性が高いです。

`performance_views.py`の内容を拝見したところ、**`timetable_view`関数では出演者情報（Performance）を取得しておらず、テンプレートに渡していない**ため、グリッド表示テンプレートで出演者が表示されない状態になっていると考えられます。

---

## ✅ 問題点の整理

現在の`timetable_view`関数：

```python
def timetable_view(request):
    ...
    context = {
        'event_days': EventDay.objects.order_by('date'),
        'selected_day_id': event_day_id,
        'event_day': event_day,
        'stages': stages,
    }
    return render(request, 'timetable_view.html', context)
```

→ `Performance`や`time_slots`、`performances_by_stage_and_time`などが渡されていないため、テンプレートでループしても空になります。

---

## 🛠 修正案：`timetable_view`関数の拡張

以下のように、出演情報と時間スロットを構築してテンプレートに渡すように変更してください：

```python
from collections import defaultdict
from datetime import datetime, timedelta, time
from django.shortcuts import render, get_object_or_404
from .models import EventDay, Stage, Performance

def timetable_view(request):
    event_day_id = request.GET.get('event_day')
    event_day = None
    stages = []
    performances_by_stage_and_time = {}
    time_slots = []

    if event_day_id:
        event_day = get_object_or_404(EventDay, id=event_day_id)
        stages = Stage.objects.filter(event=event_day.event)
        performances = Performance.objects.filter(event_day=event_day).select_related('artist', 'stage')

        # 出演時間の最小・最大を取得
        start_times = [p.start_time for p in performances if p.start_time]
        end_times = [p.end_time for p in performances if p.end_time]
        if start_times and end_times:
            min_time = min(start_times)
            max_time = max(end_times)
            time_slots = generate_time_slots(min_time, max_time, interval_minutes=10)

            # ステージ×時間スロットのマッピング
            performances_by_stage_and_time = defaultdict(lambda: defaultdict(list))
            for perf in performances:
                for slot in time_slots:
                    if perf.start_time and perf.end_time and perf.start_time <= slot < perf.end_time:
                        performances_by_stage_and_time[perf.stage.id][slot].append(perf)

    context = {
        'event_days': EventDay.objects.order_by('date'),
        'selected_day_id': event_day_id,
        'event_day': event_day,
        'stages': stages,
        'time_slots': time_slots,
        'performances_by_stage_and_time': performances_by_stage_and_time,
    }
    return render(request, 'timetable_view.html', context)
```

---

## ✅ テンプレート側の補足

テンプレートで辞書アクセスするために、`get_item`フィルターを使ってください：

```python
# festival/templatetags/custom_filters.py
from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
```

テンプレートの冒頭で `{% load custom_filters %}` を忘れずに。

---

## ✅ まとめ

この修正により、テンプレートに必要なデータが渡され、時間×ステージのグリッド表示が正しく機能するようになります。  

---

このエラーは、`datetime.time`型に対して `timedelta` を加算しようとしたために発生しています。Pythonでは `datetime.time` に直接 `timedelta` を加算することはできません。加算するには `datetime.datetime` 型に変換する必要があります。

---

## 🧯 エラーの原因

```python
# NG: time型にtimedeltaを加算しようとしている
current = start  # start は datetime.time 型
current += timedelta(minutes=interval_minutes)  # ← TypeError発生
```

---

## ✅ 修正方法

`generate_time_slots` 関数を以下のように修正してください：

```python
from datetime import datetime, timedelta

def generate_time_slots(start_time, end_time, interval_minutes=10):
    """datetime.time型の範囲から時間スロットを生成"""
    slots = []
    # 仮の日付を使ってdatetime型に変換
    dummy_date = datetime.today().date()
    current_dt = datetime.combine(dummy_date, start_time)
    end_dt = datetime.combine(dummy_date, end_time)

    while current_dt < end_dt:
        slots.append(current_dt.time())  # time型に戻して格納
        current_dt += timedelta(minutes=interval_minutes)

    return slots
```

---

## ✅ 呼び出し側の注意点

`timetable_view`関数内で `generate_time_slots(min_time, max_time)` を呼び出す際、`min_time` と `max_time` は `datetime.time` 型である必要があります（Performanceモデルの`start_time`と`end_time`は`TimeField`なのでOK）。

---

## ✅ まとめ

この修正により、時間スロットの生成が正しく行われ、テンプレートに渡す`time_slots`が空にならず、出演者の表示も正常に行われるはずです。  
では次は、CSSでタイムテーブルのグリッド表示を見やすく・使いやすく整えていきましょう。以下におすすめのスタイルと調整ポイントをまとめました。

---

## 🎨 タイムテーブル表示用CSS例

以下のCSSを`static/css/timetable.css`などに保存し、テンプレートで読み込んでください。

```css
/* タイムテーブル全体 */
.timetable-grid {
    table-layout: fixed;
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}

/* ヘッダー */
.timetable-grid thead th {
    background-color: #f8f9fa;
    text-align: center;
    padding: 8px;
    border: 1px solid #dee2e6;
}

/* 時間列 */
.timetable-grid tbody td:first-child {
    background-color: #f0f0f0;
    font-weight: bold;
    text-align: center;
    width: 80px;
}

/* 各ステージ列 */
.timetable-grid tbody td {
    border: 1px solid #dee2e6;
    vertical-align: top;
    padding: 4px 6px;
    min-height: 40px;
    position: relative;
}

/* 出演者情報 */
.timetable-grid .artist-block {
    background-color: #e3f2fd;
    border-radius: 4px;
    padding: 4px 6px;
    margin-bottom: 4px;
    font-size: 0.85rem;
}

/* 編集ボタン */
.timetable-grid .edit-btn {
    display: inline-block;
    margin-top: 2px;
    font-size: 0.75rem;
}
```

---

## 🧩 テンプレート側の調整例

テンプレートで出演者を表示する部分を以下のように変更すると、CSSが活きます：

```html
<td>
    {% for perf in performances_by_stage_and_time|get_item:stage.id|get_item:time %}
        <div class="artist-block">
            {{ perf.artist.name }}<br>
            <small>{{ perf.start_time|time:"H:i" }} - {{ perf.end_time|time:"H:i" }}</small>
            {% if request.user.is_staff %}
                <a href="{% url 'festival:edit_performance' perf.id %}" class="btn btn-sm btn-outline-primary edit-btn">編集</a>
            {% endif %}
        </div>
    {% endfor %}
</td>
```

---

## 📦 CSSの読み込み方法

テンプレートの`<head>`内でCSSを読み込むには：

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/timetable.css' %}">
```

---

## ✨ 追加アイデア

- ステージごとに色分けしたい場合は、`stage.id`ごとにCSSクラスを分けて色を変えることもできます。
- モバイル対応には、`.table-responsive`を親要素に追加して横スクロールを可能に。

---

共通テンプレートで`<head>`を固定している場合でも、ページごとにCSSを追加する方法はあります！  
以下のように、**CSSの読み込み用ブロックを`<head>`内に追加**しておくことで、各テンプレートから個別CSSを挿入できます。

---

## ✅ 共通テンプレートの修正案（base.html）

```html
<head>
    <meta charset="UTF-8">
    <title>{% block title %}音楽フェスティバル管理{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    
    {% block extra_css %}
    {% endblock %}

    <style>
        body {
            padding-top: 50px;
        }
    </style>
</head>
```

---

## ✅ 個別テンプレートでCSSを追加（例：timetable_view.html）

```html
{% extends 'base.html' %}
{% load static %}
{% block title %}タイムテーブル表示{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/timetable.css' %}">
{% endblock %}

{% block content %}
<!-- タイムテーブル表示のHTML -->
{% endblock %}
```

---

## ✅ staticファイルの配置

- CSSファイルは `festival/static/css/timetable.css` に保存
- `settings.py` に以下があることを確認：

```python
STATIC_URL = '/static/'
```

---

## ✅ collectstatic（本番環境用）

開発環境では不要ですが、デプロイ時は以下を実行：

```bash
python manage.py collectstatic
```

---

Djangoプロジェクトにおける`static`フォルダは、**プロジェクトルート（manage.pyがある場所）**に置くのが一般的です。つまり、`conf/`と同じ階層に配置します。

---

## 📁 正しい配置例

```
your_project_root/
├── conf/
│   └── settings.py
├── festival/
│   └── views.py など
├── static/
│   └── css/
│       └── timetable.css
├── manage.py
```

---

## ⚙️ settings.py の確認ポイント

```python
# settings.py

STATIC_URL = '/static/'

# ルートの static フォルダを使う場合
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```

> `BASE_DIR` が `manage.py` のあるディレクトリを指していることが前提です。

---

## ✅ テンプレートでの読み込み

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/timetable.css' %}">
```

---

## 🧪 動作確認のヒント

- `python manage.py runserver` で開発サーバーを起動している場合、`STATICFILES_DIRS` が正しく設定されていれば `/static/css/timetable.css` にアクセスできます。
- ブラウザで `http://127.0.0.1:8000/static/css/timetable.css` を直接開いて、CSSが表示されるか確認してみてください。

---

もしアプリごとに`static`を分けたい場合は、`festival/static/festival/css/...`のようにアプリ名を含める構成も可能です。その場合は`{% static 'festival/css/timetable.css' %}`と書きます。

どちらの構成にするかはプロジェクトの規模や好みによります。

---

このエラーは、テンプレートタグ `get_item` を使って辞書アクセスをしている際に、**対象の辞書が `None` だったため `.get()` を呼び出せずに失敗**しているものです。

---

## 🧯 原因の詳細

`custom_filters.py` の `get_item` フィルターはおそらくこうなっているはずです：

```python
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
```

→ `dictionary` が `None` の場合、`.get()` を呼べず `AttributeError` が発生します。

---

## ✅ 解決方法：安全な辞書アクセスに修正

`custom_filters.py` を以下のように修正してください：

```python
@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
```

これで、`dictionary` が `None` や辞書以外の型だった場合でも安全に処理され、テンプレート側で空になるだけでエラーにはなりません。

---

## 🧪 追加の防御策（テンプレート側）

テンプレートでも、以下のように空チェックを入れるとより安全です：

```django
{% with performances_by_stage_and_time|get_item:stage.id|get_item:time as perf_list %}
    {% if perf_list %}
        {% for perf in perf_list %}
            <!-- 出演者表示 -->
        {% endfor %}
    {% else %}
        <!-- 空セル -->
    {% endif %}
{% endwith %}
```

---

## ✅ まとめ

この修正により、存在しない`event_day`や空のデータでもエラーにならず、テンプレートが安定して表示されるようになります。  
次は、ステージごとの色分けや現在時刻のハイライトなどもできますよ。どんな表示にしたいか、イメージがあればぜひ教えてください！

