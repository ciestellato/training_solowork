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

次はビューとテンプレートの構築に進みましょうか？それとも既存のデータをこの構造に移行する方法から始めますか？
