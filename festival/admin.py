from django.contrib import admin

from .models import Artist, Event, Performance, EventDay

# Register your models here.
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'furigana', 'popularity', 'spotify_id')  # 一覧に表示する項目
    search_fields = ('name', 'genres')                   # 検索ボックスで検索可能な項目
    list_filter = ('genres',)                        # サイドバーにフィルターを追加

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
    list_display = ('event_day', 'artist')
    list_filter = ('event_day__event', 'artist')
    search_fields = ('artist__name', 'event_day__event__name')
