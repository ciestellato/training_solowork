from django.shortcuts import render

def index(request):
    """ホームページ"""
    return render(request, 'index.html')

def error_page(request):
    """エラーページ"""
    return render(request, "error_page.html", {"message": "Spotify認証に失敗しました。"})