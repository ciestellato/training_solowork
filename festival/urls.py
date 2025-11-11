from django.urls import path
from . import views

app_name = 'festival'

urlpatterns = [
    # トップページ
    path('', views.index, name='index'),

    # アーティスト一覧表示
    path('artists/', views.artist_list, name='artist_list'),
    # アーティスト詳細表示
    path('artist/<int:pk>/', views.artist_detail, name='artist_detail'),
    # アーティスト一括登録
    path('artists/bulk/', views.bulk_artist_register, name='bulk_artist_register'),

    # イベント一覧表示
    path('events/', views.event_list, name='event_list'),
    # イベント一覧表示（フェスのみ）
    path('events/fes/', views.fes_event_list, name='fes_event_list'),
    # イベント一覧表示（フェス以外）
    path('events/other/', views.other_event_list, name='other_event_list'),

    # イベント詳細表示
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    # イベント内容登録
    path('eventday/register/', views.register_event_day_and_performances, name='register_event_day'),
    # イベント詳細編集
    path('event_day/<int:event_day_id>/edit/', views.edit_event_day_performances, name='edit_event_day_performances'),
    
    # ツアー詳細登録
    path('tour/register/', views.paste_schedule_register, name='paste_schedule_register'),
]