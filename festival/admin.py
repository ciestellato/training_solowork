from django.contrib import admin

from .models import Artist, Event, ManualEntry, Performance, RelatedArtist

# Register your models here.
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'popularity', 'spotify_id')  # 一覧に表示する項目
    search_fields = ('name', 'genres')                   # 検索ボックスで検索可能な項目
    list_filter = ('popularity',)                        # サイドバーにフィルターを追加

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'start_date', 'end_date')
    search_fields = ('name', 'location')
    list_filter = ('start_date',)

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'artist', 'performance_date', 'is_confirmed')
    list_filter = ('is_confirmed', 'performance_date')
    search_fields = ('event__name', 'artist__name')

@admin.register(RelatedArtist)
class RelatedArtistAdmin(admin.ModelAdmin):
    list_display = ('artist', 'related_artist', 'similarity_score')
    search_fields = ('artist__name', 'related_artist__name')

@admin.register(ManualEntry)
class ManualEntryAdmin(admin.ModelAdmin):
    list_display = ('event', 'artist', 'notes')
    search_fields = ('event__name', 'artist__name', 'notes')
