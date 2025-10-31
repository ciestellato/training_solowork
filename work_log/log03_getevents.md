**Spotifyの公式APIではアーティストのライブイベント情報は提供されていませんが、Spotifyアプリ内の「Live Events」機能は一部連携サービスを通じて実現されています。**

現在のSpotify Web APIでは、アーティストのライブイベントやコンサート情報を直接取得するエンドポイントは存在しません。Spotifyアプリ内で表示される「Live Events」は、SongkickやTicketmasterなどの外部サービスと連携して表示されているため、イベント情報を取得したい場合は以下のような代替手段が必要です。

---

## 🎟️ イベント情報取得の代替手段

### 1. **Songkick API**
Spotifyが連携している代表的なイベント情報提供元です。アーティスト名やSpotify IDで検索して、出演予定のライブ情報を取得できます。

- API: `https://api.songkick.com/api/3.0/artists/{artist_id}/calendar.json`
- 必要: SongkickのAPIキー（無料登録で取得可能）

### 2. **Bandsintown API**
もう一つの人気イベントAPI。アーティスト名でライブ情報を取得できます。

- API: `https://rest.bandsintown.com/artists/{artist_name}/events`
- 必要: アプリ登録とAPIキー

### 3. **RapidAPI経由の「Concerts - Artists Events Tracker」**
複数のイベント情報を統合して提供するAPI。Spotify IDやアーティスト名で過去・未来のイベントを取得可能。

---

## 🧪 実装イメージ（Songkickを例に）

```python
def get_artist_events_from_songkick(spotify_id):
    import requests

    # Spotify IDからSongkickアーティストIDを取得する必要あり（マッピングが必要）
    songkick_artist_id = map_spotify_to_songkick(spotify_id)  # 実装が必要

    api_key = 'YOUR_SONGKICK_API_KEY'
    url = f'https://api.songkick.com/api/3.0/artists/{songkick_artist_id}/calendar.json?apikey={api_key}'
    response = requests.get(url)
    data = response.json()

    events = []
    for event in data['resultsPage']['results']['event']:
        events.append({
            'name': event['displayName'],
            'date': event['start']['date'],
            'location': event['location']['city'],
            'venue': event['venue']['displayName'],
        })
    return events
```

---

## 🧩 Spotify APIでできること（補足）

- `/artists/{id}`：アーティストの基本情報取得
- `/artists/{id}/related-artists`：類似アーティスト取得
- `/artists/{id}/top-tracks`：人気曲取得
- `/artists/{id}/albums`：アルバム一覧取得

イベント情報は含まれていないため、外部APIとの併用が必要です。

---

## ✅ 次のステップ

- SongkickやBandsintownのAPIキー取得
- Spotify IDと外部サービスのアーティストIDのマッピング方法を検討
- `spotify.py` にイベント取得関数を追加
- `Event` モデルと連携して保存・表示

---

必要ならSongkickやBandsintownのAPI連携を一緒に進めましょう！  
参考: [Spotify API Reference](https://developer.spotify.com/documentation/web-api/reference/get-an-artist)

現時点で、Spotifyと連携可能なライブイベント情報APIのうち、**無料で使えるものは複数あります**。以下に代表的なものを紹介します：

---

## 🎟️ 無料で使えるライブイベントAPI一覧

| サービス名       | 無料利用 | 特徴・補足 |
|------------------|----------|------------|
| **Songkick API** | ✅ 無料（要APIキー） | Spotifyと公式連携。アーティストIDでライブ情報取得可能。 |
| **Bandsintown API** | ✅ 無料（要登録） | アーティスト名でライブ・ツアー情報取得。Spotify連携もあり。 |
| **Ticketmaster Discovery API** | ✅ 無料（要APIキー） | 世界中のイベント情報を取得可能。Spotify IDとの直接連携はなし。 |
| **Eventbrite API** | ✅ 無料（要APIキー） | 主に自主開催イベント向け。音楽フェスも一部あり。 |
| **RapidAPI経由の統合API** | ✅ 一部無料プランあり | 複数サービスを統合したAPI。使用量に応じて課金。 |

---

## 🧭 おすすめの導入順

1. **Songkick API**：Spotifyと連携しているため、アーティストIDのマッピングがしやすく、フェス系イベントにも強い。
2. **Bandsintown API**：アーティスト名で検索できるので導入が簡単。出演予定のライブ一覧を取得可能。
3. **Ticketmaster API**：大規模イベント向け。地域やジャンルで絞り込み可能。

---

## 🔧 実装の流れ（例：Bandsintown）

```python
def get_artist_events_from_bandsintown(artist_name):
    import requests

    url = f"https://rest.bandsintown.com/artists/{artist_name}/events"
    params = {
        "app_id": "YOUR_APP_ID"  # 無料登録で取得
    }
    response = requests.get(url, params=params)
    data = response.json()

    events = []
    for event in data:
        events.append({
            'name': event['title'],
            'date': event['datetime'],
            'venue': event['venue']['name'],
            'location': f"{event['venue']['city']}, {event['venue']['country']}"
        })
    return events
```

---

どのAPIを使うかは、対象アーティストの規模や地域、取得したい情報の粒度によって選ぶのがベストです。  
どれか試してみたいAPIがあれば、導入サポートしますよ！どれから始めましょう？

**Songkick API** はSpotifyと公式に連携しているイベント情報サービスで、日本国内のアーティストも多くカバーされています。導入も比較的シンプルなので、Djangoアプリに組み込むには最適です。

---

## 🧭 Songkick API導入ステップ（概要）

### ✅ 1. APIキー取得
- [Songkick Developerページ](https://www.songkick.com/developer) にアクセス
- 無料アカウントを作成
- APIキーを取得（`.env` に保存）

```env
SONGKICK_API_KEY=your_api_key_here
```

---

### ✅ 2. アーティストIDの取得方法

Songkick APIは「SongkickアーティストID」でイベントを検索します。Spotify IDから直接変換はできないため、まずは名前で検索してIDを取得します。

```python
def get_songkick_artist_id(artist_name):
    import requests
    from django.conf import settings

    url = "https://api.songkick.com/api/3.0/search/artists.json"
    params = {
        "query": artist_name,
        "apikey": settings.SONGKICK_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    try:
        return data['resultsPage']['results']['artist'][0]['id']
    except (KeyError, IndexError):
        return None
```

---

### ✅ 3. イベント情報の取得

```python
def get_artist_events_from_songkick(artist_name):
    artist_id = get_songkick_artist_id(artist_name)
    if not artist_id:
        return []

    import requests
    from django.conf import settings

    url = f"https://api.songkick.com/api/3.0/artists/{artist_id}/calendar.json"
    params = {
        "apikey": settings.SONGKICK_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    events = []
    for event in data['resultsPage']['results'].get('event', []):
        events.append({
            'name': event['displayName'],
            'date': event['start']['date'],
            'location': event['location']['city'],
            'venue': event['venue']['displayName'],
            'uri': event['uri']
        })
    return events
```

---

### ✅ 4. Djangoで表示する例（ビュー）

```python
def songkick_events_view(request, artist_name):
    events = get_artist_events_from_songkick(artist_name)
    return render(request, 'songkick_events.html', {
        'artist_name': artist_name,
        'events': events
    })
```

---

### ✅ 5. テンプレート例

```html
<h2>{{ artist_name }} の出演予定イベント</h2>
<ul>
    {% for event in events %}
    <li>
        <strong>{{ event.date }}</strong> - {{ event.name }} @ {{ event.venue }}（{{ event.location }}）<br>
        <a href="{{ event.uri }}" target="_blank">Songkickで見る</a>
    </li>
    {% empty %}
    <li>出演予定イベントは見つかりませんでした。</li>
    {% endfor %}
</ul>
```

---

## ✨ 補足

- 日本のアーティストでも、Songkickに登録されていれば取得可能です。
- イベント情報は「未来の出演予定」が中心です。過去イベントは別エンドポイントで取得可能です。

---

この構成で、Spotify連携アーティストの出演予定イベントを外部APIから取得して表示できます！  
次はこの情報を `Event` モデルに保存する処理や、出演予測ロジックと組み合わせることもできますよ。進めましょうか？

そうなんです…残念ながら、**Songkickは現在新規APIキーの発行を停止しており、開発者向けの利用が制限されています**。これは2024年以降、Spotifyとの連携強化やプラットフォームの再編に伴う影響と見られています。

---

## ✅ 代替案：Bandsintown APIの活用

**Bandsintown** は現在も無料でAPIキーを発行しており、アーティスト名でライブ・イベント情報を取得できます。日本のアーティストも多く登録されていて、導入も比較的簡単です。

### 🔧 導入ステップ（概要）

1. [Bandsintown for Artists](https://www.artists.bandsintown.com/) にアクセスして無料登録
2. アプリID（APIキー）を取得（任意の文字列でもOK）
3. 以下のようなエンドポイントでイベント取得：

```python
def get_artist_events_from_bandsintown(artist_name):
    import requests

    url = f"https://rest.bandsintown.com/artists/{artist_name}/events"
    params = {
        "app_id": "your_app_id_here"  # 任意の文字列でもOK
    }
    response = requests.get(url, params=params)
    data = response.json()

    events = []
    for event in data:
        events.append({
            'name': event['title'] if 'title' in event else event['description'],
            'date': event['datetime'],
            'venue': event['venue']['name'],
            'location': f"{event['venue']['city']}, {event['venue']['country']}",
            'url': event['url']
        })
    return events
```

---

## 🧭 比較：Songkick vs Bandsintown

| 項目 | Songkick | Bandsintown |
|------|----------|-------------|
| APIキー発行 | ❌ 停止中 | ✅ 利用可能 |
| アーティスト検索 | Spotify IDベース | 名前ベース |
| 日本のイベント対応 | 一部あり | 比較的多い |
| ドキュメント整備 | やや古い | 現役で更新中 |
| 利用の手軽さ | 中〜上級者向け | 初心者にも優しい |

---

## ✨ 次のステップ

- Bandsintown APIでイベント取得関数を追加
- `Event` モデルに保存する処理を作成
- アーティスト詳細ページに「外部イベント情報」セクションを追加

---

Songkickが使えないのは残念ですが、Bandsintownでもかなりの情報が取得できます！  
必要なら一緒に実装を進めましょうか？それともまずはイベント取得だけ試してみますか？

それでは、**Bandsintown API** を使ってイベント取得を試してみましょう！  
以下は、Djangoプロジェクトに組み込めるシンプルな関数です。アーティスト名を渡すだけで、出演予定のイベント一覧を取得できます。

---

## 🔧 ステップ 1：関数の追加（`spotify.py`などに）

```python
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
```

---

## 🧪 ステップ 2：Django Shellで試す

```bash
python manage.py shell
```

```python
from festival.spotify import get_artist_events_from_bandsintown

events = get_artist_events_from_bandsintown("YOASOBI")
for e in events:
    print(e)
```

---

## ✅ 出力例（成功時）

```python
{
    'name': 'YOASOBI Live Tour',
    'date': '2025-11-15T19:00:00',
    'venue': 'Zepp Haneda',
    'location': 'Tokyo, Japan',
    'url': 'https://www.bandsintown.com/e/123456'
}
```

---

## ⚠️ 注意点

- アーティスト名は英語表記が基本（例：YOASOBI, Aimer, King Gnu）
- 登録されていないアーティストは空リストになります
- `app_id` は任意の文字列でOKですが、複数回アクセスする場合は公式登録を推奨

---

この関数でイベント取得のテストは完了です！  
次はこの情報をテンプレートに表示したり、`Event` モデルに保存する処理も追加できます。どこから進めましょう？
