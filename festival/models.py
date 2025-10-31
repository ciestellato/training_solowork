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
    
    def __str__(self):
        return self.name

class Artist(models.Model):
    name = models.CharField(max_length=255)
    popularity = models.IntegerField(null=True, blank=True)
    genres = models.JSONField(default=list, blank=True)
    spotify_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class EventDay(models.Model):
    """公演日・会場単位のクラス"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date = models.DateField()
    venue = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.event.name} - {self.date} @ {self.venue}"

class Performance(models.Model):
    """出演情報クラス"""
    event_day = models.ForeignKey(EventDay, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.artist.name} @ {self.event_day}"

class RelatedArtist(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='base_artist')
    related_artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='similar_to')
    similarity_score = models.FloatField()

class ManualEntry(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)