from django.shortcuts import render

def index(request):
    """ホームページ"""
    return render(request, 'index.html')