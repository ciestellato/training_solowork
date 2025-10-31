from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Artist(models.Model):
    name = models.CharField(max_length=255)
    popularity = models.IntegerField(null=True, blank=True)
    genres = models.JSONField(default=list, blank=True)
    spotify_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Performance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    performance_date = models.DateField()
    is_confirmed = models.BooleanField(default=False)

class RelatedArtist(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='base_artist')
    related_artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='similar_to')
    similarity_score = models.FloatField()

class ManualEntry(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)