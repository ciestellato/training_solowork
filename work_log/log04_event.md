了解です！では、**フェス型イベントとライブツアー型イベントの両方に対応できるモデル構造**を、Djangoで実装する形で整理していきますね 🎸

---

## 🧱 モデル定義（拡張版）

以下の3層構造で設計します：

### 1. `Event`：イベント全体（フェス or ツアー）

```python
class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('FES', 'フェス'),
        ('TOUR', 'ツアー'),
        ('SOLO', '単独公演'),
        ('BATTLE', '対バン'),
        ('OTHER', 'その他'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES)
    
    def __str__(self):
        return self.name
```

---

### 2. `EventDay`：開催日・会場単位

```python
class EventDay(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date = models.DateField()
    venue = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.event.name} - {self.date} @ {self.venue}"
```

---

### 3. `Performance`：出演情報

```python
class Performance(models.Model):
    event_day = models.ForeignKey(EventDay, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.artist.name} @ {self.event_day}"
```

---

## 🛠️ 管理画面登録（`admin.py`）

```python
from django.contrib import admin
from .models import Event, EventDay, Performance

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'start_date', 'end_date')
    list_filter = ('event_type', 'start_date')
    search_fields = ('name',)

@admin.register(EventDay)
class EventDayAdmin(admin.ModelAdmin):
    list_display = ('event', 'date', 'venue')
    list_filter = ('date', 'venue')
    search_fields = ('event__name', 'venue')

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('event_day', 'artist', 'is_confirmed')
    list_filter = ('event_day__event', 'is_confirmed')
    search_fields = ('artist__name', 'event_day__event__name')
```

---

## ✅ マイグレーション

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## ✨ 次のステップ

- `Event` 一覧ページ → `EventDay` を日付順に表示
- `EventDay` 詳細ページ → 出演者一覧（`Performance`）を表示
- `Artist` 詳細ページ → 出演した `EventDay` と `Event` を表示

---

この設計なら、以下のようなケースにも対応できます：

- YOASOBIのツアー：複数都市・複数日 → `EventDay` で管理
- フェス：1日だけ出演するアーティスト → `Performance` に1日だけ紐づけ
- 出演確定前の仮登録 → `is_confirmed=False` で管理

---

「イベントに対して日程と出演者をまとめて登録する」機能は、**管理者向けの効率的な入力インターフェース**として非常に有用です。Djangoのフォームと管理者制限を組み合わせて、以下のように実装できます。

---

## 🧭 実装の流れ（管理者専用ビュー）

### ✅ 1. フォームの作成（`forms.py`）

```python
from django import forms
from .models import Event, EventDay, Artist, Performance

class EventDayPerformanceForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Event.objects.all(), label='イベント')
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='開催日')
    venue = forms.CharField(max_length=255, label='会場')
    artists = forms.ModelMultipleChoiceField(
        queryset=Artist.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='出演アーティスト'
    )
```

---

### ✅ 2. ビューの作成（`views.py`）

```python
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from .forms import EventDayPerformanceForm
from .models import EventDay, Performance

@staff_member_required
def register_event_day_and_performances(request):
    message = ''
    if request.method == 'POST':
        form = EventDayPerformanceForm(request.POST)
        if form.is_valid():
            event = form.cleaned_data['event']
            date = form.cleaned_data['date']
            venue = form.cleaned_data['venue']
            artists = form.cleaned_data['artists']

            # EventDayを作成
            event_day = EventDay.objects.create(event=event, date=date, venue=venue)

            # Performanceを作成（重複チェックは任意）
            for artist in artists:
                Performance.objects.create(event_day=event_day, artist=artist, is_confirmed=True)

            message = f"{event_day} に {artists.count()} 組の出演者を登録しました。"
            form = EventDayPerformanceForm()  # フォームをリセット
    else:
        form = EventDayPerformanceForm()

    return render(request, 'register_event_day.html', {'form': form, 'message': message})
```

---

### ✅ 3. テンプレート作成（`register_event_day.html`）

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>イベント日程と出演者登録</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-4">
    <h1>📅 イベント日程と出演者登録</h1>

    {% if message %}
        <div class="alert alert-success">{{ message }}</div>
    {% endif %}

    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">登録する</button>
    </form>

    <a href="{% url 'event_list' %}" class="btn btn-secondary mt-3">イベント一覧に戻る</a>
</body>
</html>
```

---

### ✅ 4. ルーティング追加（`urls.py`）

```python
path('eventday/register/', views.register_event_day_and_performances, name='register_event_day'),
```

---

## 🔐 管理者限定にするには？

- `@staff_member_required` デコレーターを使うことで、**ログイン済みかつ `is_staff=True` のユーザーのみアクセス可能**になります
- 管理画面と同じアカウントでログインしていればOK

---

## ✨ 拡張アイデア

- 出演確定フラグ（チェックボックスで個別に設定）
- 同じ日付・会場の重複チェック
- 登録済みの `EventDay` に対する出演者追加モード
- Ajaxで動的にアーティストを絞り込み（ジャンルや人気度で）

---

この機能があれば、**フェスやツアーの各日程に対して一括で出演者を登録できる**ので、運営効率が大幅にアップします！  
次は「登録済みの `EventDay` に対して出演者を追加・編集する画面」も作っていきましょうか？

# エラー発生：イベント詳細ページ表示エラー

このエラーの原因は、`Event` モデルに対して `performance_set` を参照しようとしている点にあります。  
しかし、現在のモデル構造では `Performance` は `EventDay` に紐づいているため、**`Event` から直接 `performance_set` を辿ることはできません**。

---

## 🔍 原因の整理

### モデル構造（現在）

```python
class Event(models.Model):
    ...

class EventDay(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ...

class Performance(models.Model):
    event_day = models.ForeignKey(EventDay, on_delete=models.CASCADE)
    ...
```

この構造では：

- `Event` → `EventDay` → `Performance` の順で辿る必要があります
- `event.performance_set` は存在しない（`eventday_set` は存在する）

---

## ✅ 修正方法（ビュー）

### `views.py` の `event_detail` ビューを以下のように修正：

```python
def event_detail(request, pk):
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
```

---

## ✅ 修正方法（テンプレート）

### `event_detail.html` の表示を以下のように変更：

```html
<h4>開催日程と出演者</h4>
{% for day, performances in day_performances %}
    <h5>{{ day.date }} @ {{ day.venue }}</h5>
    <ul class="list-group mb-3">
        {% for perf in performances %}
        <li class="list-group-item d-flex justify-content-between align-items-center">
            <div>
                <a href="{% url 'artist_detail' perf.artist.pk %}">{{ perf.artist.name }}</a>
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
{% empty %}
    <p>日程が登録されていません。</p>
{% endfor %}
```

---

## ✅ 補足

- `eventday_set` は Django が自動生成する逆参照名（ForeignKeyの `related_name` を指定していない場合）
- `performance_set` は `EventDay` に対する逆参照名なので、`Event` からは直接使えません

---

これで `Event` 詳細ページが正しく表示されるようになります！  
さらに `related_name` を使えばコードがもっと読みやすくなります。必要ならそのリファクタリングもお手伝いしますよ。
