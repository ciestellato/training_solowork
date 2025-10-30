from django.contrib import admin

from .models import Artist, Event, ManualEntry, Performance, RelatedArtist

# Register your models here.
admin.site.register(Artist)
admin.site.register(Event)
admin.site.register(ManualEntry)
admin.site.register(Performance)
admin.site.register(RelatedArtist)
