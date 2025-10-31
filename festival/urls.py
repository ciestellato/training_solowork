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

    # イベント一覧
    path('events/', views.event_list, name='event_list'),
]