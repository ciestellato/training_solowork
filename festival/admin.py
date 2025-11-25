from django.contrib import admin

from .models import Artist, Event, Performance, EventDay, Stage

# Register your models here.
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    # 一覧に表示する項目
    list_display = (
        'name', 'furigana',
        'image_url', 'twitter_url', 'official_url'
    )
    # 検索ボックスで検索可能な項目
    search_fields = ('name', 'furigana')
    # サイドバーにフィルターを追加
    list_filter = ('genres',)

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

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'order', 'color_code')
    list_filter = ('event',)
    ordering = ('event', 'order')
    fields = ('event', 'name', 'order', 'color_code')