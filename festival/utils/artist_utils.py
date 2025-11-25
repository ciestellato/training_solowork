from festival.models import Artist
from festival.utils.spotify_utils import fetch_artist_image

def update_missing_artist_images():
    """image_urlが空のアーティストにSpotify画像を登録"""
    artists = Artist.objects.filter(image_url__isnull=True) | Artist.objects.filter(image_url__exact='')
    for artist in artists:
        if not artist.spotify_id:
            continue
        image_url = fetch_artist_image(artist.spotify_id)
        if image_url:
            artist.image_url = image_url
            artist.save()
            print(f"✅ {artist.name} の画像を更新しました: {image_url}")
        else:
            print(f"⚠️ {artist.name} の画像が見つかりませんでした")
