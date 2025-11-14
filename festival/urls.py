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
    edit_event_day_performances, edit_performance,
    paste_schedule_register, register_timetable, timetable_view
)
from .views.playlist_views import create_playlist_view, save_playlist_to_spotify_view
from .views.spotify_auth_views import spotify_login_view, spotify_callback_view
from .views.admin_views import admin_menu

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

    # プレイリスト関連
    path('playlist/create/', create_playlist_view, name='create_playlist'),
    path('playlist/save/', save_playlist_to_spotify_view, name='save_playlist_to_spotify'),

    # タイムテーブル関連
    path('timetable/register/', register_timetable, name='register_timetable'),
    path('timetable/view/', timetable_view, name='timetable_view'),
    path('timetable/edit/<int:performance_id>/', edit_performance, name='edit_performance'),

    # Spotify認証関連
    path('spotify/login/', spotify_login_view, name='spotify_login'),
    path('callback/', spotify_callback_view, name='spotify_callback'),

    # 管理者メニュー
    path('admin_menu/', admin_menu, name='admin_menu'),
]