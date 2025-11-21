from django.db import models

class Event(models.Model):
    """イベント全体のクラス"""
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
    official_url = models.URLField(blank=True, null=True, verbose_name='公式サイトURL')
    
    def __str__(self):
        return self.name

class Artist(models.Model):
    """アーティストクラス"""
    name = models.CharField(max_length=255)
    furigana = models.CharField(max_length=100, blank=True, null=True)
    popularity = models.IntegerField(null=True, blank=True)
    genres = models.JSONField(default=list, blank=True)
    spotify_id = models.CharField(max_length=100, unique=True)
    image_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['furigana']  # ふりがな順で並び替え

class EventDay(models.Model):
    """公演日・会場単位のクラス"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date = models.DateField()
    venue = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.event.name} - {self.date} @ {self.venue}"
    
    class Meta:
        unique_together = ('event', 'date', 'venue')

class Stage(models.Model):
    """イベント内のステージ情報"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    # 並び順を任意に指定
    order = models.PositiveIntegerField(default=0, help_text="タイムテーブル上の表示順")

    # カラーパレット選択（選択肢は管理画面でプルダウン表示）
    COLOR_CHOICES = [
        ("#4A90E2", "青系"),
        ("#E9184E", "ピンク系"),
        ("#38BD67", "緑系"),
        ("#F28C28", "オレンジ系"),
        ("#832C99", "紫系"),
        ("#A678C9", "ラベンダー系"),
        ("#A3C644", "ライム系"),
        ("#2CA6A4", "シアン系"),
        ("#D96C5F", "サーモン系"),
        ("#858585", "グレー系"),
    ]
    color_code = models.CharField(
        max_length=7,
        choices=COLOR_CHOICES,
        default="#e3f2fd",
        help_text="ステージカラー（タイムテーブル背景色）"
    )

    def __str__(self):
        return f"{self.event.name} - {self.name}"

    class Meta:
        ordering = ['order']  # 表示順を制御

class Performance(models.Model):
    """出演情報クラス（ステージ・出演時間付き）"""
    event_day = models.ForeignKey(EventDay, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.artist.name} @ {self.event_day} ({self.stage})"

    class Meta:
        unique_together = ('event_day', 'artist')
