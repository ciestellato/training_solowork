from django.urls import path
from .views.base_views import index
from .views.artist_views import (
    artist_list, artist_detail,
    bulk_artist_register, edit_artist,
    edit_artist_bulk
)
from .views.event_views import (
    event_list, fes_event_list, other_event_list,
    event_detail, create_event, edit_event
)
from .views.performance_views import (
    register_event_day_and_performances,
    edit_event_day_performances,
    paste_schedule_register
)

app_name = 'festival'

urlpatterns = [
    # トップページ
    path('', index, name='index'),

    # アーティスト関連
    path('artists/', artist_list, name='artist_list'),
    path('artist/<int:pk>/', artist_detail, name='artist_detail'),
    path('artists/bulk/', bulk_artist_register, name='bulk_artist_register'),
    path('artist/edit/<int:artist_id>/', edit_artist, name='edit_artist'),
    path('artist/bulk_edit/', edit_artist_bulk, name='edit_artist_bulk'),

    # イベント関連
    path('events/', event_list, name='event_list'),
    path('events/fes/', fes_event_list, name='fes_event_list'),
    path('events/other/', other_event_list, name='other_event_list'),
    path('event/<int:pk>/', event_detail, name='event_detail'),
    path('events/create/', create_event, name='create_event'),
    path('events/edit/<int:event_id>/', edit_event, name='edit_event'),

    # 出演者・日程関連
    path('eventday/register/', register_event_day_and_performances, name='register_event_day'),
    path('event_day/<int:event_day_id>/edit/', edit_event_day_performances, name='edit_event_day_performances'),
    path('tour/register/', paste_schedule_register, name='paste_schedule_register'),
]