from django.contrib import admin

from .models import Artist, Event, ManualEntry, Performance, RelatedArtist, EventDay

# Register your models here.
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'popularity', 'spotify_id')  # 一覧に表示する項目
    search_fields = ('name', 'genres')                   # 検索ボックスで検索可能な項目
    list_filter = ('popularity',)                        # サイドバーにフィルターを追加

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

@admin.register(RelatedArtist)
class RelatedArtistAdmin(admin.ModelAdmin):
    list_display = ('artist', 'related_artist', 'similarity_score')
    search_fields = ('artist__name', 'related_artist__name')

@admin.register(ManualEntry)
class ManualEntryAdmin(admin.ModelAdmin):
    list_display = ('event', 'artist', 'notes')
    search_fields = ('event__name', 'artist__name', 'notes')
