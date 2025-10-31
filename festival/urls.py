from django.urls import path
from . import views

app_name = 'festival'

urlpatterns = [
    path('', views.index, name='index'),  # トップページ
    # path('artists/', views.artist_list, name='artist_list'),  # アーティスト一覧（今後実装）
]