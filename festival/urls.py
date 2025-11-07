from django.urls import path
from . import views

app_name = 'festival'

urlpatterns = [
    # トップページ
    path('', views.index, name='index'),

    # アーティスト一覧
    path('artists/', views.artist_list, name='artist_list'),
    # アーティスト詳細
    path('artist/<int:pk>/', views.artist_detail, name='artist_detail'),
    # アーティスト一括登録
    path('artists/bulk/', views.bulk_artist_register, name='bulk_artist_register'),

    # イベント一覧
    path('events/', views.event_list, name='event_list'),
    # イベント詳細
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    # イベント内容登録
    path('eventday/register/', views.register_event_day_and_performances, name='register_event_day'),
    
    # ツアー詳細登録
    path('tour/register/', views.paste_schedule_register, name='paste_schedule_register'),
]