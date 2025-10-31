import requests

def get_artist_events_from_bandsintown(artist_name):
    """
    Bandsintown APIを使ってアーティストの出演予定イベントを取得
    """
    url = f"https://rest.bandsintown.com/artists/{artist_name}/events"
    params = {
        "app_id": "test_app"  # 任意の文字列でOK（公式が推奨）
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return []

    data = response.json()
    events = []

    for event in data:
        events.append({
            'name': event.get('title') or event.get('description'),
            'date': event['datetime'],
            'venue': event['venue']['name'],
            'location': f"{event['venue']['city']}, {event['venue']['country']}",
            'url': event['url']
        })

    return events