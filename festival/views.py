from django.shortcuts import render

from .models import Artist

# Create your views here.
def index(request):
    """ホームページ"""
    return render(request, 'index.html')

def artist_list(request):
    """アーティストの一覧表示ページ"""
    artists = Artist.objects.all().order_by('name')  # 名前順で取得
    return render(request, 'artist_list.html', {'artists': artists})