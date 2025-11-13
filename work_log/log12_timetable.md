# タイムテーブル機能を実装する

タイムテーブル機能を実装するには、**ステージ情報**と**出演時間帯（開始・終了）**をモデルに組み込むことで、柔軟かつ現実的なスケジュール管理が可能になります。以下に、既存モデルを拡張する形での設計案を提案します。

---

## 🧱 モデル拡張案：ステージと出演時間の追加

### 1. `Stage` モデルの新規追加

```python
class Stage(models.Model):
    """イベント内のステージ情報"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.event.name} - {self.name}"
```

- 単一ステージの場合でも1件だけ登録すればOK。
- 複数ステージがあるイベントにも対応可能。

---

### 2. `Performance` モデルの拡張

```python
class Performance(models.Model):
    """出演情報クラス（ステージ・時間帯付き）"""
    event_day = models.ForeignKey(EventDay, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.artist.name} @ {self.event_day} ({self.stage})"
```

- `stage` は `null=True` にしておくことで、ステージ未定の出演も許容。
- `start_time` / `end_time` により、タイムテーブル表示が可能になります。

---

## 🗂️ タイムテーブル表示の例（テンプレート）

```html
{% for stage in stages %}
  <h3>{{ stage.name }}</h3>
  <ul>
    {% for perf in stage.performance_set.all|dictsort:"start_time" %}
      <li>{{ perf.start_time }} - {{ perf.end_time }} : {{ perf.artist.name }}</li>
    {% endfor %}
  </ul>
{% endfor %}
```

- ステージごとに出演者を時間順で表示。
- `dictsort:"start_time"` により、開始時間順に並び替え。

---

## ✅ 今後の拡張可能性

- タイムテーブルを**PDFや画像で出力**する機能
- **ステージ別のジャンル傾向**や**混雑予測**などの分析
- **ユーザーのお気に入りアーティストの出演時間通知**

---

`playlist_create.html` をベースに `timetable_register.html` を作成するのは非常に良いアプローチです！  
ただし、目的が「プレイリスト作成」から「タイムテーブル登録」に変わるため、以下のような変更が必要になります。

---

## ✅ `timetable_register.html` のフルテンプレート例

```html
{% extends 'base.html' %}

{% block title %}タイムテーブル登録{% endblock %}

{% block content %}
<h1>📅 タイムテーブル登録</h1>

{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }} mt-3" role="alert">
            {{ message|safe }}
        </div>
    {% endfor %}
{% endif %}

<!-- イベント日程選択（GET） -->
<form method="GET" class="mb-4">
    <label for="event_day" class="form-label">イベント日程を選択</label>
    <div class="input-group">
        <select name="event_day" id="event_day" class="form-select">
            {% for day in event_days %}
                <option value="{{ day.id }}" {% if day.id|stringformat:"s" == selected_day_id %}selected{% endif %}>
                    {{ day.date }} @ {{ day.venue }}
                </option>
            {% endfor %}
        </select>
        <button type="submit" class="btn btn-outline-primary">出演者を表示</button>
    </div>
</form>

{% if performances %}
<!-- タイムテーブル入力フォーム（POST） -->
<form method="POST">
    {% csrf_token %}
    {% if form_errors %}
        <div class="alert alert-danger">
            <strong>エラーがあります：</strong>
            <ul>
                {% for error in form_errors %}
                    <li>{{ error }}</li>
                {% endfor %}
            </ul>
        </div>
    {% endif %}

    {% for perf in performances %}
        <div class="border p-3 mb-3">
            <h5>{{ perf.artist.name }}</h5>

            <div class="row">
                <div class="col-md-4">
                    <label>ステージ</label>
                    <select name="stage_{{ perf.id }}" class="form-select">
                        {% for stage in stages %}
                            <option value="{{ stage.id }}" {% if perf.stage and perf.stage.id == stage.id %}selected{% endif %}>
                                {{ stage.name }}
                            </option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-4">
                    <label>開始時間</label>
                    <input type="time" name="start_{{ perf.id }}" value="{{ perf.start_time|default_if_none:'' }}" class="form-control">
                </div>
                <div class="col-md-4">
                    <label>終了時間</label>
                    <input type="time" name="end_{{ perf.id }}" value="{{ perf.end_time|default_if_none:'' }}" class="form-control">
                </div>
            </div>
        </div>
    {% endfor %}

    <button type="submit" class="btn btn-success mt-3">タイムテーブルを保存する</button>
</form>
{% endif %}

<a href="{% url 'festival:event_list' %}" class="btn btn-secondary mt-4">イベント一覧へ戻る</a>
{% endblock %}
```

---

## 🧠 補足ポイント

- `performances` は `Performance` オブジェクトのリストで、選択された `EventDay` に紐づくもの。
- `stages` はその `Event` に紐づく `Stage` のリスト。
- `stage_{{ perf.id }}`, `start_{{ perf.id }}`, `end_{{ perf.id }}` のように、IDベースでフォームを構成することで、ビュー側で更新処理がしやすくなります。
- `form_errors` はビューでバリデーションエラーをまとめて渡すと便利です。

---

では、`timetable_register.html` に対応するビューと保存処理の実装を、以下のように段階的に整理してご紹介します。

---

## 🧭 ビューの構成方針

このビューは以下の2つの処理を持ちます：

1. **GETリクエスト**：イベント日程を選択 → 出演者一覧と既存のタイムテーブル情報を表示
2. **POSTリクエスト**：ステージ・開始時間・終了時間の入力 → `Performance` モデルに保存

---

## 🧠 ビュー実装例（`views/performance_views.py`）

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from festival.models import EventDay, Performance, Stage
from django.utils.dateparse import parse_time

def register_timetable(request):
    event_day_id = request.GET.get('event_day')
    event_day = None
    performances = []
    stages = []
    form_errors = []

    if event_day_id:
        event_day = get_object_or_404(EventDay, id=event_day_id)
        performances = Performance.objects.filter(event_day=event_day).select_related('artist', 'stage')
        stages = Stage.objects.filter(event=event_day.event)

    if request.method == 'POST' and event_day:
        for perf in performances:
            stage_id = request.POST.get(f'stage_{perf.id}')
            start_time = request.POST.get(f'start_{perf.id}')
            end_time = request.POST.get(f'end_{perf.id}')

            # バリデーション
            if start_time and end_time and parse_time(start_time) >= parse_time(end_time):
                form_errors.append(f"{perf.artist.name} の開始時間は終了時間より前である必要があります。")
                continue

            # 保存処理
            perf.stage_id = stage_id if stage_id else None
            perf.start_time = parse_time(start_time) if start_time else None
            perf.end_time = parse_time(end_time) if end_time else None
            perf.save()

        if not form_errors:
            messages.success(request, "タイムテーブルを保存しました！")
            return redirect(request.path + f"?event_day={event_day_id}")

    context = {
        'event_days': EventDay.objects.order_by('date'),
        'selected_day_id': event_day_id,
        'event_day': event_day,
        'performances': performances,
        'stages': stages,
        'form_errors': form_errors,
    }
    return render(request, 'timetable_register.html', context)
```

---

## 🛣️ URL設定（`festival/urls.py`）

```python
from festival.views import performance_views

urlpatterns = [
    ...
    path('timetable/register/', performance_views.register_timetable, name='register_timetable'),
]
```

---

## ✅ 補足ポイント

- `parse_time()` を使って `HH:MM` 形式の文字列を `datetime.time` に変換しています。
- `stage_id` が空の場合は `None` を代入して未設定を許容。
- バリデーションエラーがある場合は `form_errors` に追加してテンプレートに表示。

---

タイムテーブル表示画面は、ユーザーにとってイベントの全体像を把握するうえで非常に重要です。以下に、**ビュー・テンプレート・URL設定**を含めた実装例を体系的にご紹介します。

---

## 🧭 タイムテーブル表示画面の構成

### 機能概要
- イベント日程を選択
- ステージごとに出演者を時間順に表示
- 開始・終了時間、アーティスト名、ステージ名を明示

---

## 🧠 ビュー実装（`views/performance_views.py`）

```python
from django.shortcuts import render, get_object_or_404
from festival.models import EventDay, Performance, Stage

def timetable_view(request):
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
```

---

## 🗂️ URL設定（`festival/urls.py`）

```python
from festival.views import performance_views

urlpatterns = [
    ...
    path('timetable/view/', performance_views.timetable_view, name='timetable_view'),
]
```

---

## 🎨 テンプレート例（`timetable_view.html`）

```html
{% extends 'base.html' %}

{% block title %}タイムテーブル表示{% endblock %}

{% block content %}
<h1>🎪 タイムテーブル表示</h1>

<!-- イベント日程選択 -->
<form method="GET" class="mb-4">
    <label for="event_day" class="form-label">イベント日程を選択</label>
    <div class="input-group">
        <select name="event_day" id="event_day" class="form-select">
            {% for day in event_days %}
                <option value="{{ day.id }}" {% if day.id|stringformat:"s" == selected_day_id %}selected{% endif %}>
                    {{ day.date }} @ {{ day.venue }}
                </option>
            {% endfor %}
        </select>
        <button type="submit" class="btn btn-outline-primary">表示</button>
    </div>
</form>

{% if event_day %}
    <h2 class="mt-4">{{ event_day.date }} @ {{ event_day.venue }}</h2>

    {% for stage in stages %}
        <div class="mt-5">
            <h4>🎤 {{ stage.name }}</h4>
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>時間</th>
                        <th>アーティスト</th>
                    </tr>
                </thead>
                <tbody>
                    {% for perf in stage.performance_set.all|dictsort:"start_time" %}
                        <tr>
                            <td>
                                {% if perf.start_time and perf.end_time %}
                                    {{ perf.start_time|time:"H:i" }} - {{ perf.end_time|time:"H:i" }}
                                {% else %}
                                    未定
                                {% endif %}
                            </td>
                            <td>{{ perf.artist.name }}</td>
                        </tr>
                    {% empty %}
                        <tr><td colspan="2">出演者未登録</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% endfor %}
{% endif %}

<a href="{% url 'festival:event_list' %}" class="btn btn-secondary mt-4">イベント一覧へ戻る</a>
{% endblock %}
```

---

## ✅ 補足ポイント

- `dictsort:"start_time"` により、開始時間順に並び替え。
- 時間未定の出演者も「未定」として表示。
- ステージが1つしかない場合でも、同じテンプレートで対応可能。

---

「イベント日程を選択 → 出演者をチェックボックスで選択 → ステージを1つ選択 → 選択された出演者に対して開始・終了時間を入力」という流れに沿って、ビューとテンプレートを再設計しましょう。

---

## 🧭 入力フローの再設計

### ステップ1：イベント日程選択（GET）
- `EventDay` を選択 → 出演候補者一覧を表示

### ステップ2：出演者選択 + ステージ選択（POST）
- チェックボックスで出演者を選択
- ステージを1つ選択
- 選択された出演者に対して、開始・終了時間を入力するフォームを表示

### ステップ3：時間入力 + 保存（POST）
- 入力された時間を `Performance` モデルに保存

---

## 🧠 ビュー構成（2段階POST）

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from festival.models import EventDay, Performance, Stage, Artist
from django.utils.dateparse import parse_time

def register_timetable(request):
    event_day_id = request.GET.get('event_day')
    event_day = get_object_or_404(EventDay, id=event_day_id) if event_day_id else None
    stages = Stage.objects.filter(event=event_day.event) if event_day else []
    artists = Artist.objects.filter(performance__event_day=event_day).distinct() if event_day else []
    selected_artist_ids = request.POST.getlist('selected_artists')
    selected_stage_id = request.POST.get('selected_stage')
    form_errors = []

    if request.method == 'POST' and 'save_times' in request.POST:
        # 保存処理
        for artist_id in selected_artist_ids:
            start = request.POST.get(f'start_{artist_id}')
            end = request.POST.get(f'end_{artist_id}')
            perf = Performance.objects.filter(event_day=event_day, artist_id=artist_id).first()
            if not perf:
                continue

            if start and end and parse_time(start) >= parse_time(end):
                form_errors.append(f"{perf.artist.name} の開始時間は終了時間より前である必要があります。")
                continue

            perf.stage_id = selected_stage_id
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
```

---

## 🎨 テンプレート構成（`timetable_register.html`）

### ステージ選択＋出演者チェック（初期POST）

```html
<form method="POST">
    {% csrf_token %}
    <label class="form-label">ステージを選択</label>
    <select name="selected_stage" class="form-select mb-3">
        {% for stage in stages %}
            <option value="{{ stage.id }}" {% if stage.id|stringformat:"s" == selected_stage_id %}selected{% endif %}>{{ stage.name }}</option>
        {% endfor %}
    </select>

    <label class="form-label">出演アーティストを選択</label>
    <div class="border p-3 mb-3" style="max-height: 300px; overflow-y: scroll;">
        {% for artist in artists %}
            <div class="form-check">
                <input class="form-check-input" type="checkbox" name="selected_artists" value="{{ artist.id }}"
                       id="artist_{{ artist.id }}" {% if artist.id|stringformat:"s" in selected_artist_ids %}checked{% endif %}>
                <label class="form-check-label" for="artist_{{ artist.id }}">{{ artist.name }}</label>
            </div>
        {% endfor %}
    </div>

    <button type="submit" name="prepare_times" class="btn btn-primary">時間入力へ進む</button>
</form>
```

### 時間入力フォーム（2回目のPOST）

```html
{% if selected_artist_ids %}
<form method="POST">
    {% csrf_token %}
    <input type="hidden" name="selected_stage" value="{{ selected_stage_id }}">
    {% for artist_id in selected_artist_ids %}
        {% with artist=artists|get_by_id:artist_id %}
        <div class="border p-3 mb-3">
            <h5>{{ artist.name }}</h5>
            <div class="row">
                <div class="col-md-6">
                    <label>開始時間</label>
                    <input type="time" name="start_{{ artist.id }}" class="form-control">
                </div>
                <div class="col-md-6">
                    <label>終了時間</label>
                    <input type="time" name="end_{{ artist.id }}" class="form-control">
                </div>
            </div>
        </div>
        {% endwith %}
    {% endfor %}
    <button type="submit" name="save_times" class="btn btn-success mt-3">タイムテーブルを保存する</button>
</form>
{% endif %}
```

---

## 🧩 カスタムテンプレートフィルター（`get_by_id`）

DjangoテンプレートではリストからIDで取得できないため、以下のようなフィルターを追加すると便利です：

```python
# festival/templatetags/custom_filters.py
from django import template
register = template.Library()

@register.filter
def get_by_id(queryset, id):
    return queryset.filter(id=id).first()
```

```python
# settings.py に 'festival.templatetags' を追加
```

---

以下は、あなたの希望に沿った **タイムテーブル登録画面（timetable_register.html）** のフルテンプレートです。  
このテンプレートは以下の流れに対応しています：

1. イベント日程を選択（GET）
2. 出演者をチェックボックスで選択し、ステージを1つ選択（POST）
3. 選択された出演者に対して、開始・終了時間を入力（POST）

---

## 🎨 `timetable_register.html`（フルテンプレート）

```html
{% extends 'base.html' %}

{% block title %}タイムテーブル登録{% endblock %}

{% block content %}
<h1>📅 タイムテーブル登録</h1>

{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }} mt-3" role="alert">
            {{ message|safe }}
        </div>
    {% endfor %}
{% endif %}

<!-- イベント日程選択 -->
<form method="GET" class="mb-4">
    <label for="event_day" class="form-label">イベント日程を選択</label>
    <div class="input-group">
        <select name="event_day" id="event_day" class="form-select">
            {% for day in event_days %}
                <option value="{{ day.id }}" {% if day.id|stringformat:"s" == selected_day_id %}selected{% endif %}>
                    {{ day.date }} @ {{ day.venue }}
                </option>
            {% endfor %}
        </select>
        <button type="submit" class="btn btn-outline-primary">表示</button>
    </div>
</form>

{% if event_day %}
    <!-- ステージ選択 + 出演者チェック -->
    <form method="POST" class="mb-5">
        {% csrf_token %}
        <label class="form-label">ステージを選択</label>
        <select name="selected_stage" class="form-select mb-3">
            {% for stage in stages %}
                <option value="{{ stage.id }}" {% if stage.id|stringformat:"s" == selected_stage_id %}selected{% endif %}>
                    {{ stage.name }}
                </option>
            {% endfor %}
        </select>

        <label class="form-label">出演アーティストを選択</label>
        <input type="text" class="form-control mb-2" placeholder="アーティスト名で絞り込み" id="artistSearch">
        <div class="border p-3 mb-3" style="max-height: 300px; overflow-y: scroll;">
            {% for artist in artists %}
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" name="selected_artists" value="{{ artist.id }}"
                           id="artist_{{ artist.id }}" {% if artist.id|stringformat:"s" in selected_artist_ids %}checked{% endif %}>
                    <label class="form-check-label" for="artist_{{ artist.id }}">{{ artist.name }}</label>
                </div>
            {% endfor %}
        </div>

        <button type="submit" name="prepare_times" class="btn btn-primary">時間入力へ進む</button>
    </form>

    <!-- 時間入力フォーム -->
    {% if selected_artist_ids %}
        <form method="POST">
            {% csrf_token %}
            <input type="hidden" name="selected_stage" value="{{ selected_stage_id }}">
            {% for artist_id in selected_artist_ids %}
                {% with artist=artists|get_by_id:artist_id %}
                <div class="border p-3 mb-3">
                    <h5>{{ artist.name }}</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <label>開始時間</label>
                            <input type="time" name="start_{{ artist.id }}" class="form-control">
                        </div>
                        <div class="col-md-6">
                            <label>終了時間</label>
                            <input type="time" name="end_{{ artist.id }}" class="form-control">
                        </div>
                    </div>
                </div>
                {% endwith %}
            {% endfor %}
            <button type="submit" name="save_times" class="btn btn-success mt-3">タイムテーブルを保存する</button>
        </form>
    {% endif %}

    {% if form_errors %}
        <div class="alert alert-danger mt-4">
            <strong>エラーがあります：</strong>
            <ul>
                {% for error in form_errors %}
                    <li>{{ error }}</li>
                {% endfor %}
            </ul>
        </div>
    {% endif %}
{% endif %}

<a href="{% url 'festival:event_list' %}" class="btn btn-secondary mt-4">イベント一覧へ戻る</a>

<script>
    document.getElementById('artistSearch').addEventListener('input', function () {
        const keyword = this.value.toLowerCase();
        document.querySelectorAll('.form-check').forEach(cb => {
            const label = cb.textContent.toLowerCase();
            cb.style.display = label.includes(keyword) ? 'block' : 'none';
        });
    });
</script>
{% endblock %}
```

---

## 🔧 補足

- `get_by_id` フィルターはカスタムテンプレートタグとして定義する必要があります（前回の回答参照）。
- `selected_artist_ids` や `selected_stage_id` はビューから渡す必要があります。
- `prepare_times` と `save_times` でPOSTの分岐を制御しています。

---

`festival.templatetags` を `settings.py` に直接追加する必要は **ありません**。Djangoでは、**カスタムテンプレートタグ**を使うために `INSTALLED_APPS` にアプリ名（この場合は `festival`）が登録されていれば十分です。

---

## ✅ 正しい手順：カスタムテンプレートタグの使い方

### 1. `templatetags` ディレクトリを作成

アプリフォルダ（例：`festival/`）の中に `templatetags/` フォルダを作ります：

```
festival/
├── templatetags/
│   ├── __init__.py
│   └── custom_filters.py
```

- `__init__.py` は空でOK（Pythonパッケージとして認識させるため）
- `custom_filters.py` にフィルターを定義します

### 2. フィルター定義例（`custom_filters.py`）

```python
from django import template
register = template.Library()

@register.filter
def get_by_id(queryset, id):
    return queryset.filter(id=id).first()
```

### 3. テンプレートで読み込む

テンプレートの先頭で以下を記述します：

```django
{% load custom_filters %}
```

これで `get_by_id` フィルターが使えるようになります。

---

## ✅ `settings.py` の確認ポイント

以下のように `INSTALLED_APPS` に `festival` が含まれていればOKです：

```python
INSTALLED_APPS = [
    ...
    'festival',
    ...
]
```

---

## ❌ 不要なこと

- `festival.templatetags` を `INSTALLED_APPS` に追加する必要はありません
- `settings.py` に特別な文言を追加する必要はありません

---

## 🎤 ステージ入力についての設計方針

現在のビューでは、ステージは「既存のステージから選択する」前提になっています。つまり、**事前にステージが登録されていることが前提**です。

ですが、現実の運用では：

- ステージがまだ登録されていないこともある
- イベントごとにステージ名が異なる
- 管理者がその場でステージを追加したい

というケースが多いため、**「該当ステージがなければ新規入力できる」**ようにするのが理想的です。

---

## ✅ ステージ選択＋新規入力のUI提案（テンプレート）

```html
<label class="form-label">ステージを選択または新規入力</label>
<div class="row mb-3">
    <div class="col-md-6">
        <select name="selected_stage" class="form-select">
            <option value="">（未選択）</option>
            {% for stage in stages %}
                <option value="{{ stage.id }}" {% if stage.id|stringformat:"s" == selected_stage_id %}selected{% endif %}>
                    {{ stage.name }}
                </option>
            {% endfor %}
        </select>
    </div>
    <div class="col-md-6">
        <input type="text" name="new_stage_name" class="form-control" placeholder="新しいステージ名を入力">
    </div>
</div>
```

---

## 🧠 ビュー側の処理（`register_timetable`）

```python
# ステージ選択または新規作成
selected_stage_id = request.POST.get('selected_stage')
new_stage_name = request.POST.get('new_stage_name')

if new_stage_name:
    # 新規ステージ作成
    stage = Stage.objects.create(event=event_day.event, name=new_stage_name)
elif selected_stage_id:
    stage = Stage.objects.filter(id=selected_stage_id).first()
else:
    stage = None
```

その後、`stage` を `Performance` に紐づけて保存すればOKです。

---

## ✅ UX的な工夫

- 新規ステージ名が入力されていれば、選択されたステージは無視して新規作成を優先
- 両方空なら「ステージ未設定」として保存（または警告）

---

タイムテーブル表示画面でイベント名だけが表示され、ステージや出演者が表示されない場合、主に以下の原因が考えられます。

---

## ✅ 原因チェックリスト

### 1. **Performanceに`start_time`と`end_time`が未登録**
- タイムテーブル表示テンプレートでは、通常 `stage.performance_set.all|dictsort:"start_time"` のように時間順で並べています。
- もし `start_time` が `None` のままだと、テンプレートで何も表示されない可能性があります。

### 2. **Performanceに`stage`が未設定**
- タイムテーブル表示はステージ単位でループしているため、`stage` が `null` の `Performance` は表示されません。

### 3. **Stageがイベントに紐づいていない**
- `Stage.objects.filter(event=event_day.event)` でステージを取得している場合、イベントに紐づくステージが存在しないと表示されません。

---

## 🧪 確認方法（Djangoシェル）

```bash
python manage.py shell
```

```python
from festival.models import EventDay, Performance

event_day = EventDay.objects.get(id=1)  # ← 適切なIDに変更
Performance.objects.filter(event_day=event_day).values('artist__name', 'stage__name', 'start_time', 'end_time')
```

これで、対象イベント日の出演者・ステージ・時間が登録されているか確認できます。

---

## ✅ 解決策

### 1. タイムテーブル登録画面で `stage`, `start_time`, `end_time` が保存されているか再確認
- `perf.stage = stage` の代入が正しく行われているか
- `perf.save()` が呼ばれているか

### 2. 表示テンプレートに「未登録の場合の案内」を追加

```django
{% if stages %}
  {% for stage in stages %}
    ...
  {% endfor %}
{% else %}
  <p>このイベントにはステージ情報が登録されていません。</p>
{% endif %}
```

---

## ✅ テスト用ダミーデータ登録（管理画面でもOK）

- `Stage` をイベントに紐づけて1件登録
- `Performance` に `stage`, `start_time`, `end_time` を手動で登録
- 表示画面で反映されるか確認

---

もし必要なら、表示テンプレートのコードを一緒に見ながら調整もできますよ！  
また、登録済みのタイムテーブル一覧を管理者向けに表示する機能も追加できます。
