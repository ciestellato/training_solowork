Spotifyの仕様変更に柔軟に対応し、プレイリスト作成機能にフォーカスを移すのはとても良い判断です。以下に、**2025年11月12日（水）〜11月21日（金）**の新しいスケジュール表を「段階的な開発ステップ」に沿ってご提案します。

---

## 🗓️ プレイリスト作成機能に向けた開発スケジュール（2025年11月12日〜11月21日）

| 日付       | タスク内容 | 使用技術・ファイル | 備考 |
|------------|------------|---------------------|------|
| **11/12 (水)** | 🔍 要件定義・画面設計 | `feature_plan.md`, `screen_flow.md` | プレイリスト作成の流れを明確化（選択→生成→表示） |
| **11/13 (木)** | 🎨 UIモック作成・テンプレート設計 | `playlist_create.html`, Bootstrap | 出演者選択画面・生成ボタン・結果表示エリア |
| **11/14 (金)** | 🧠 プレイリスト生成ロジック設計 | `playlist.py`（新規） | Spotify APIの `/tracks` or `/search` を活用 |
| **11/17 (月)** | 🛠️ プレイリスト作成ビュー実装 | `views.py`, `playlist.py` | 選択されたアーティストから曲を取得し、リスト生成 |
| **11/18 (火)** | 🧪 テンプレート連携・動作確認 | `playlist_create.html`, `urls.py` | アーティスト選択→プレイリスト表示までの一連の流れ |
| **11/19 (水)** | 🎯 UI改善・検索バー・選択補助 | JavaScript, CSS | アーティスト検索・チェックボックス・選択数表示など |
| **11/20 (木)** | 🧪 テスト・バグ修正 | `test_views.py`, `test_playlist.py` | Spotify APIのエラー処理・選択漏れ対応など |
| **11/21 (金)** | 📦 最終調整・ドキュメント更新・発表準備 | `README.md`, `docs/playlist_spec.md` | スクリーンショット・デモ・スライド作成 |

---

## 🔮 補足：将来的な拡張に向けて

- **ログイン機能**：`django.contrib.auth` によるユーザー管理
- **お気に入りアーティスト保存**：`UserProfile` モデル＋`ManyToManyField`
- **個別プレイリスト生成**：ユーザーごとの選択状態をセッションまたはDBに保存

---

このスケジュールであれば、**11/18までに基本機能を完成させ、残り3日でUI改善・テスト・発表準備に集中**できます。必要であれば、Spotify APIのプレイリスト生成に関する仕様確認や、テンプレート構成の提案もできますよ。

次は、画面設計やプレイリスト生成ロジックの詳細を一緒に詰めていきましょうか？
ありがとうございます！イベント一覧のテンプレートがとても丁寧に作られていて、Bootstrapによる整ったUIがすでに活用されていますね。このスタイルを踏襲しつつ、**プレイリスト作成画面の設計**を以下のように提案します。

---

## 🎨 プレイリスト作成画面の構成案（`playlist_create.html`）

### 🧭 画面の目的
- ユーザーがイベント日程を選択し、出演アーティストをチェックボックスで選択
- 「プレイリストを作成」ボタンでSpotify APIから代表曲を取得
- 結果を画面下部に表示（曲名・アーティスト名・Spotifyリンク）

---

### 🖼️ UI構成（Bootstrapベース）

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>プレイリスト作成</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-4">
    <h1>🎧 プレイリスト作成</h1>

    <form method="POST">
        {% csrf_token %}

        <!-- イベント日程選択 -->
        <div class="mb-3">
            <label for="event_day" class="form-label">イベント日程を選択</label>
            <select name="event_day" id="event_day" class="form-select">
                {% for day in event_days %}
                    <option value="{{ day.id }}">{{ day.date }} @ {{ day.venue }}</option>
                {% endfor %}
            </select>
        </div>

        <!-- 出演アーティスト選択 -->
        <div class="mb-3">
            <label class="form-label">出演アーティストを選択</label>
            <input type="text" class="form-control mb-2" placeholder="アーティスト名で絞り込み" id="artistSearch">
            <div class="border p-3" style="max-height: 300px; overflow-y: scroll;">
                {% for artist in artists %}
                    <div class="form-check">
                        <input class="form-check-input artist-checkbox" type="checkbox" name="artists" value="{{ artist.id }}" id="artist{{ artist.id }}">
                        <label class="form-check-label" for="artist{{ artist.id }}">{{ artist.name }}（{{ artist.furigana }}）</label>
                    </div>
                {% endfor %}
            </div>
        </div>

        <!-- 作成ボタン -->
        <button type="submit" class="btn btn-primary">プレイリストを作成する</button>
    </form>

    <!-- 結果表示 -->
    {% if playlist %}
        <hr>
        <h2 class="mt-4">🎶 プレイリスト</h2>
        <ul class="list-group">
            {% for track in playlist %}
                <li class="list-group-item">
                    {{ track.name }} - {{ track.artist }}
                    <a href="{{ track.spotify_url }}" target="_blank" class="btn btn-sm btn-outline-success float-end">Spotifyで聴く</a>
                </li>
            {% endfor %}
        </ul>
    {% endif %}

    <a href="{% url 'festival:event_list' %}" class="btn btn-secondary mt-4">イベント一覧へ戻る</a>

    <!-- JS: アーティスト検索フィルター -->
    <script>
        document.getElementById('artistSearch').addEventListener('input', function () {
            const keyword = this.value.toLowerCase();
            document.querySelectorAll('.artist-checkbox').forEach(cb => {
                const label = cb.nextElementSibling.textContent.toLowerCase();
                cb.parentElement.style.display = label.includes(keyword) ? 'block' : 'none';
            });
        });
    </script>
</body>
</html>
```

---

## ✅ 補足ポイント

- `event_days` と `artists` はビュー側で渡す必要があります（`context`に含める）
- `playlist` はプレイリスト生成後に渡される曲情報のリスト（曲名・アーティスト名・Spotify URL）
- JavaScriptによる検索バーは、リアルタイムでチェックボックスの表示を絞り込みます

---

既存のビュー構成を踏まえたうえで、**プレイリスト作成機能のビュー関数**を以下に追加提案します。

---

## 🎧 プレイリスト作成ビュー（`create_playlist`）

このビューでは、ユーザーがイベント日程を選択し、出演アーティストをチェックボックスで選択したうえで、Spotify APIを使って代表曲を取得し、プレイリストとして表示します。

```python
from django.shortcuts import render, get_object_or_404
from .models import EventDay, Performance, Artist
from .forms import PlaylistForm  # チェックボックス付きフォームを別途定義
from .spotify_utils import get_top_tracks  # Spotify API呼び出し関数（別ファイルに分離）

def create_playlist(request):
    """プレイリスト作成ビュー"""

    playlist = []
    selected_day_id = request.GET.get('event_day')
    selected_day = EventDay.objects.filter(id=selected_day_id).first()

    # 出演者一覧を取得（選択肢として表示）
    artists_qs = Artist.objects.filter(performance__event_day=selected_day).distinct() if selected_day else Artist.objects.none()

    if request.method == 'POST':
        form = PlaylistForm(request.POST, artists_queryset=artists_qs)
        if form.is_valid():
            selected_artists = form.cleaned_data['artists']
            for artist in selected_artists:
                tracks = get_top_tracks(artist.spotify_id)
                for track in tracks:
                    playlist.append({
                        'name': track['name'],
                        'artist': artist.name,
                        'spotify_url': track['external_urls']['spotify']
                    })
    else:
        form = PlaylistForm(artists_queryset=artists_qs)

    # イベント日程一覧（セレクトボックス用）
    event_days = EventDay.objects.select_related('event').order_by('date')

    return render(request, 'playlist_create.html', {
        'form': form,
        'playlist': playlist,
        'event_days': event_days,
        'selected_day_id': selected_day_id
    })
```

---

## 🔧 補足

- `PlaylistForm` は `ModelMultipleChoiceField` を使って出演アーティストを選択できるようにしたフォームです。`__init__` で `artists_queryset` を受け取るように設計します。
- `get_top_tracks(spotify_id)` は Spotify API の `/artists/{id}/top-tracks` を使って代表曲を取得する関数です。`spotify_utils.py` に分離しておくと保守性が高まります。
- プレイリストはテンプレート側で `name`, `artist`, `spotify_url` を使って表示します。

---

それでは、Spotify APIを使ってアーティストの代表曲（トップトラック）を取得する関数 `get_top_tracks()` を `spotify_utils.py` に追加しましょう。

---

## 🎧 `get_top_tracks()` の定義（日本向け）

```python
def get_top_tracks(spotify_id, market='JP'):
    """
    指定されたSpotifyアーティストIDからトップトラック（代表曲）を取得する。
    デフォルトは日本（JP）市場。
    """
    token = get_spotify_token()
    if not token:
        return []

    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.spotify.com/v1/artists/{spotify_id}/top-tracks'
    params = {'market': market}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"トップトラック取得失敗: {response.status_code} - {response.text}")
        return []

    try:
        data = response.json()
        return data.get('tracks', [])
    except ValueError:
        print("トップトラックのレスポンスがJSON形式ではありません")
        return []
```

---

## ✅ 使用例（ビューやテンプレート用）

この関数は以下のように使えます：

```python
tracks = get_top_tracks(artist.spotify_id)
for track in tracks:
    print(track['name'], track['external_urls']['spotify'])
```

---

## 🔒 注意点

- `market='JP'` を指定することで、日本で人気の曲を優先的に取得できます
- 返される `track` オブジェクトには以下のような情報が含まれます：
  - `name`: 曲名
  - `external_urls['spotify']`: Spotifyリンク
  - `album['images']`: ジャケット画像（必要なら）
  - `preview_url`: 試聴用URL（存在する場合）

---

Djangoの `shell` で `get_top_tracks()` を動作確認するには、以下の手順で進めるとスムーズです。

---

## 🧪 1. Django Shell を起動

```bash
python manage.py shell
```

---

## 🧪 2. 必要な関数をインポート

```python
from festival.utils.spotify_utils import get_top_tracks
```

---

## 🧪 3. Spotify ID を指定して関数を実行

Spotify ID は `Artist` モデルの `spotify_id` フィールドに保存されているはずです。まずは1件取得してみましょう：

```python
from festival.models import Artist
artist = Artist.objects.first()  # または filter(name="アーティスト名").first()
tracks = get_top_tracks(artist.spotify_id)
```

---

## 🧪 4. 結果を確認

```python
for track in tracks:
    print(track['name'], track['external_urls']['spotify'])
```

---

## ✅ 補足

- トークン取得に失敗した場合は `None` が返るので、`get_spotify_token()` を個別に呼び出して確認できます。
- `tracks` は最大10件程度の代表曲が含まれます。
- `market='JP'` を指定しているため、日本向けの人気曲が優先されます。

---

ここでは、Spotify APIを使って出演アーティストの代表曲を取得し、プレイリストとして表示するビュー関数を完成させます。以下は `views/playlist_views.py` に追加する形で設計しています。

---

## 🎧 プレイリスト生成ビュー（`create_playlist_view`）

```python
from django.shortcuts import render, get_object_or_404
from festival.models import EventDay, Performance, Artist
from festival.forms import PlaylistForm
from festival.utils.spotify_utils import get_top_tracks

def create_playlist_view(request):
    """出演アーティストを選択してSpotifyプレイリストを生成するビュー"""

    selected_day_id = request.GET.get('event_day')
    selected_day = EventDay.objects.filter(id=selected_day_id).first()
    playlist = []

    # 出演アーティスト一覧（チェックボックス表示用）
    artists_qs = Artist.objects.filter(performance__event_day=selected_day).distinct() if selected_day else Artist.objects.none()

    if request.method == 'POST':
        form = PlaylistForm(request.POST, artists_queryset=artists_qs)
        if form.is_valid():
            selected_artists = form.cleaned_data['artists']
            for artist in selected_artists:
                tracks = get_top_tracks(artist.spotify_id)
                for track in tracks[:1]:  # 代表曲1曲だけ使う（必要なら複数可）
                    playlist.append({
                        'name': track['name'],
                        'artist': artist.name,
                        'spotify_url': track['external_urls']['spotify']
                    })
    else:
        form = PlaylistForm(artists_queryset=artists_qs)

    # イベント日程一覧（セレクトボックス用）
    event_days = EventDay.objects.select_related('event').order_by('date')

    return render(request, 'playlist_create.html', {
        'form': form,
        'playlist': playlist,
        'event_days': event_days,
        'selected_day_id': selected_day_id
    })
```

---

## ✅ 補足ポイント

- `PlaylistForm` は `ModelMultipleChoiceField` を使ったカスタムフォームで、`artists_queryset` を引数で受け取るように設計します（次で定義できます）
- `get_top_tracks()` は Spotify API から代表曲を取得する関数（すでに定義済み）
- `playlist_create.html` テンプレートでは、`playlist` をループして曲名・アーティスト名・Spotifyリンクを表示します

---

## 🔜 次のステップ

- `forms.py` に `PlaylistForm` を追加
- `urls.py` にルーティングを追加：
  ```python
  from .views.playlist_views import create_playlist_view
  path('playlist/create/', create_playlist_view, name='create_playlist')
  ```

---

このビューで、ユーザーがイベント日程を選び、出演者をチェックしてプレイリストを生成する流れが完成します。次は `PlaylistForm` の定義に進みましょう！
以下に、プレイリスト作成ビューで使用する **`PlaylistForm`** を `forms.py` に追加する構成をご提案します。

---

## 🧾 `forms.py` に追加する `PlaylistForm`

```python
from django import forms
from festival.models import Artist

class PlaylistForm(forms.Form):
    """出演アーティスト選択用フォーム（プレイリスト作成）"""

    artists = forms.ModelMultipleChoiceField(
        queryset=Artist.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='出演アーティスト'
    )

    def __init__(self, *args, artists_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if artists_queryset is not None:
            self.fields['artists'].queryset = artists_queryset
```

---

## ✅ 説明

- `ModelMultipleChoiceField` を使って、複数の `Artist` をチェックボックスで選択可能にしています
- `artists_queryset` を `__init__()` で受け取り、ビュー側から出演者リストを注入する設計です
- `CheckboxSelectMultiple` により、テンプレート側でチェックボックスとして表示されます

---

## 🔗 ビューとの連携（復習）

```python
form = PlaylistForm(request.POST or None, artists_queryset=artists_qs)
```

---

## 🧪 テストポイント

- イベント日程を選択すると、出演アーティストがチェックボックスで表示される
- チェックしたアーティストの代表曲がプレイリストとして表示される
- 未選択時はバリデーションエラーになる（`required=True`）

---

**Spotify APIを使えば取得した楽曲をSpotify上のプレイリストとして保存できます。ただし、ユーザー認証（OAuth）が必要です。**

---

## ✅ 必要なステップ（概要）

Spotifyにプレイリストを保存するには、以下の手順が必要です：

### 1. **Spotify OAuth 認証（Authorization Code Flow）**
- ユーザーのSpotifyアカウントにアクセスするために、OAuth認証が必要です。
- 必要なスコープ：
  - `playlist-modify-public`（公開プレイリスト作成）
  - `playlist-modify-private`（非公開プレイリスト作成）

### 2. **プレイリストの作成**
- エンドポイント：`POST https://api.spotify.com/v1/users/{user_id}/playlists`
- リクエストボディ例：

```json
{
  "name": "Festival Forecast プレイリスト",
  "description": "イベント出演アーティストの代表曲まとめ",
  "public": false
}
```

### 3. **楽曲の追加**
- エンドポイント：`POST https://api.spotify.com/v1/playlists/{playlist_id}/tracks`
- リクエストボディに `uris`（Spotify URIの配列）を渡します：

```json
{
  "uris": [
    "spotify:track:xxxxxx",
    "spotify:track:yyyyyy"
  ]
}
```

---

## 🧩 Djangoでの実装ポイント

### 🔐 認証処理（例：`spotify_auth.py`）
```python
from spotipy.oauth2 import SpotifyOAuth

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri="http://localhost:8000/callback/",
    scope="playlist-modify-public playlist-modify-private"
)
```

### 🧠 プレイリスト保存関数（例：`save_playlist_to_spotify()`）
```python
def save_playlist_to_spotify(user_token, track_uris, playlist_name="Festival Playlist"):
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # ユーザー情報取得
    user_res = requests.get("https://api.spotify.com/v1/me", headers=headers)
    user_id = user_res.json()["id"]

    # プレイリスト作成
    create_res = requests.post(
        f"https://api.spotify.com/v1/users/{user_id}/playlists",
        headers=headers,
        json={"name": playlist_name, "public": False}
    )
    playlist_id = create_res.json()["id"]

    # 楽曲追加
    requests.post(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
        headers=headers,
        json={"uris": track_uris}
    )

    return playlist_id
```

---

## 🧪 注意点

- 認証トークンはユーザーごとに取得・保存が必要です（セッションやDBに保持）。
- 楽曲URIは `track['uri']` で取得できます（`spotify_url` ではなく）。
- Spotify APIの制限により、最大100曲ずつ追加可能です。

---

## 🔜 次のステップ

1. `get_top_tracks()` を拡張して `track['uri']` を含める
2. 認証フローを導入（ログイン→トークン取得）
3. 「Spotifyに保存」ボタンを追加し、保存処理を呼び出す

---

Spotify APIを使って、取得した楽曲をSpotify上のプレイリストとして保存する方法について、最新情報をもとに詳しくご案内します。

---

## ✅ Spotify上にプレイリストを保存する方法

SpotifyのWeb APIでは、以下の手順でプレイリストを作成・保存できます：

### 1. 🔐 ユーザー認証（Authorization Code Flow）
Spotify上にプレイリストを保存するには、**ユーザーの認証トークン**が必要です。  
このためには、以下のスコープを含むOAuth認証が必要です：

- `playlist-modify-public`
- `playlist-modify-private`

Djangoでの実装には、`spotipy` ライブラリを使うと便利です。

### 2. 📦 プレイリストの作成
エンドポイント：
```
POST https://api.spotify.com/v1/users/{user_id}/playlists
```

リクエスト例：
```json
{
  "name": "Festival Forecast プレイリスト",
  "description": "イベント出演アーティストの代表曲まとめ",
  "public": false
}
```

### 3. 🎶 楽曲の追加
エンドポイント：
```
POST https://api.spotify.com/v1/playlists/{playlist_id}/tracks
```

リクエスト例：
```json
{
  "uris": [
    "spotify:track:1abcXYZ...",
    "spotify:track:2defXYZ..."
  ]
}
```

---

## 🧩 Djangoでの実装例（概要）

### 1. 認証フローの導入（例：`spotify_auth.py`）
```python
from spotipy.oauth2 import SpotifyOAuth

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri="http://localhost:8000/callback/",
    scope="playlist-modify-public playlist-modify-private"
)
```

### 2. プレイリスト保存関数（例：`save_playlist_to_spotify()`）
```python
def save_playlist_to_spotify(user_token, track_uris, playlist_name="Festival Playlist"):
    headers = {"Authorization": f"Bearer {user_token}"}

    # ユーザーID取得
    user_res = requests.get("https://api.spotify.com/v1/me", headers=headers)
    user_id = user_res.json()["id"]

    # プレイリスト作成
    create_res = requests.post(
        f"https://api.spotify.com/v1/users/{user_id}/playlists",
        headers=headers,
        json={"name": playlist_name, "public": False}
    )
    playlist_id = create_res.json()["id"]

    # 楽曲追加
    requests.post(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
        headers=headers,
        json={"uris": track_uris}
    )

    return playlist_id
```

---

## 🔜 次のステップ

1. `get_top_tracks()` に `track['uri']` を含めるよう拡張
2. 認証フローの導入（ユーザーログイン→トークン取得）
3. 「Spotifyに保存」ボタンをテンプレートに追加
4. 保存成功後、SpotifyプレイリストURLを表示

---

この機能を導入すれば、ユーザーがイベント出演者の楽曲を自分のSpotifyアカウントに保存できるようになります。  
必要であれば、Spotify認証フローのDjango実装をステップバイステップでご案内します！

とても良い質問です！  
結論から言うと、**従前の `get_spotify_token()` を使った関数群は「クライアント認証（Client Credentials Flow）」に基づいているため、Spotify上にプレイリストを保存する用途には使えません**。

---

## 🔍 なぜ使えないのか？

### 🎫 現在の認証方式：Client Credentials Flow
- `get_spotify_token()` はアプリケーション単位の認証です。
- このトークンでは **ユーザーのSpotifyアカウントにアクセスできません**。
- つまり、プレイリストの作成・保存・ユーザーのライブラリ操作は不可。

### ✅ 必要な認証方式：Authorization Code Flow
- Spotifyのプレイリスト保存には、**ユーザーの明示的な認可**が必要です。
- このフローでは、ユーザーがSpotifyにログインし、アプリに権限を与える必要があります。
- 得られるトークンは、ユーザーのアカウントに紐づいており、プレイリスト作成・保存が可能です。

---

## 🧭 どうすればいい？

### 🔧 認証フローの切り替え
1. `get_spotify_token()` を `get_app_token()` に改名し、アーティスト検索やトップトラック取得など「読み取り専用API」に限定して使う。
2. プレイリスト保存用には、**Authorization Code Flow** を別途実装する（例：`get_user_token()`）。

### 🧠 実装の分離イメージ

```python
# utils/spotify_utils.py

def get_app_token():
    """アプリ用トークン（読み取り専用）"""
    ...

def get_user_token(request):
    """ユーザー認証トークン（プレイリスト保存用）"""
    # Authorization Code Flow を使って request.session などに保存
    ...
```

---

## 🔐 Spotifyのスコープ（必要な権限）

```text
playlist-modify-public
playlist-modify-private
```

これらを含めて認証URLを生成し、ユーザーにログインしてもらう必要があります。

---

## ✅ まとめ

| 処理内容                     | 認証方式               | 使用可能 |
|------------------------------|------------------------|-----------|
| アーティスト検索・楽曲取得     | Client Credentials Flow | ✅ 可能     |
| プレイリスト作成・保存         | Authorization Code Flow | ❌ 不可（現状）→ ✅ 実装すれば可能 |

---

素晴らしいです！では、Spotifyの**Authorization Code Flow**を使って、Djangoで `get_user_token(request)` を定義する方法をご案内します。

---

## ✅ 目的

`get_user_token(request)` は、Spotifyユーザーのアクセストークンを取得する関数です。  
このトークンを使えば、ユーザーのSpotifyアカウントにプレイリストを保存できます。

---

## 🧩 必要な準備

### 1. 必要なライブラリ
```bash
pip install spotipy
```

### 2. settings.py に追加
```python
SPOTIFY_CLIENT_ID = 'your_client_id'
SPOTIFY_CLIENT_SECRET = 'your_client_secret'
SPOTIFY_REDIRECT_URI = 'http://localhost:8000/spotify/callback/'
SPOTIFY_SCOPE = 'playlist-modify-public playlist-modify-private'
```

---

## 🧠 `get_user_token(request)` の定義例

```python
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings

def get_user_token(request):
    """Spotifyユーザー認証トークンを取得（Authorization Code Flow）"""

    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=settings.SPOTIFY_SCOPE,
        cache_path=f".cache-{request.session.session_key}"
    )

    # 認証コードがまだない場合 → 認証URLへリダイレクト
    if not request.GET.get("code"):
        auth_url = sp_oauth.get_authorize_url()
        return auth_url  # 呼び出し元で redirect する

    # 認証コードがある場合 → トークン取得
    code = request.GET.get("code")
    token_info = sp_oauth.get_access_token(code)

    # セッションに保存して再利用可能に
    request.session["spotify_token"] = token_info["access_token"]
    return token_info["access_token"]
```

---

## 🔁 認証フローの流れ

1. ユーザーが「Spotifyに保存」ボタンを押す
2. `get_user_token(request)` を呼び出し、認証URLにリダイレクト
3. Spotifyでログイン → `code` が返る
4. `get_user_token()` がトークンを取得し、セッションに保存
5. 以降は `request.session["spotify_token"]` を使ってAPI呼び出し可能

---

## 🔜 次のステップ

- 認証用のビュー（例：`spotify_login_view`）を作成
- コールバックURL（`/spotify/callback/`）にルーティング追加
- トークン取得後に `save_playlist_to_spotify()` を呼び出してプレイリスト保存

---

以下は、SpotifyのAuthorization Code Flowを使った**認証用ビュー（ログイン → トークン取得 → セッション保存）**の実装例です。

---

## 🎧 認証用ビューの構成（2ステップ）

### 1. `spotify_login_view`  
Spotifyの認証ページにリダイレクトします。

### 2. `spotify_callback_view`  
Spotifyから返された認証コードを使ってアクセストークンを取得し、セッションに保存します。

---

## 🧾 認証ビューの実装例（`views/spotify_auth_views.py`）

```python
from django.shortcuts import redirect
from django.conf import settings
from spotipy.oauth2 import SpotifyOAuth

def spotify_login_view(request):
    """Spotify認証ページにリダイレクトするビュー"""
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=settings.SPOTIFY_SCOPE,
        cache_path=f".cache-{request.session.session_key}"
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


def spotify_callback_view(request):
    """Spotify認証後のコールバック処理ビュー"""
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=settings.SPOTIFY_SCOPE,
        cache_path=f".cache-{request.session.session_key}"
    )

    code = request.GET.get("code")
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info.get("access_token")

    if access_token:
        request.session["spotify_token"] = access_token
        return redirect("create_playlist")  # プレイリスト作成画面へ戻る
    else:
        return redirect("error_page")  # エラー処理ビューへ（任意）
```

---

## 🔗 `urls.py` のルーティング追加

```python
from django.urls import path
from festival.views.spotify_auth_views import spotify_login_view, spotify_callback_view

urlpatterns = [
    path('spotify/login/', spotify_login_view, name='spotify_login'),
    path('spotify/callback/', spotify_callback_view, name='spotify_callback'),
]
```

---

## ✅ 認証後の使い方

プレイリスト保存処理で以下のようにトークンを取得できます：

```python
token = request.session.get("spotify_token")
if token:
    save_playlist_to_spotify(token, track_uris)
```

---

## 🔜 次のステップ

- `save_playlist_to_spotify()` を定義して、Spotifyにプレイリストを作成・保存
- プレイリスト作成画面に「Spotifyに保存」ボタンを追加
- トークンの有効期限管理（必要なら `refresh_token` 対応）

---

了解しました！  
次は、Spotifyにプレイリストを保存する処理を実装する関数 `save_playlist_to_spotify()` をご提案します。

---

## 🎧 `save_playlist_to_spotify()` の定義例

この関数は、ユーザーのアクセストークンと楽曲URIのリストを受け取り、Spotify上にプレイリストを作成して楽曲を追加します。

```python
import requests

def save_playlist_to_spotify(user_token, track_uris, playlist_name="Festival Forecast プレイリスト"):
    """Spotify上にプレイリストを作成し、楽曲を追加する"""

    headers = {"Authorization": f"Bearer {user_token}"}

    # 1. ユーザー情報取得
    user_res = requests.get("https://api.spotify.com/v1/me", headers=headers)
    if user_res.status_code != 200:
        print(f"ユーザー情報取得失敗: {user_res.status_code} - {user_res.text}")
        return None

    user_id = user_res.json().get("id")
    if not user_id:
        print("ユーザーIDが取得できませんでした")
        return None

    # 2. プレイリスト作成
    create_res = requests.post(
        f"https://api.spotify.com/v1/users/{user_id}/playlists",
        headers=headers,
        json={
            "name": playlist_name,
            "description": "イベント出演アーティストの代表曲まとめ",
            "public": False
        }
    )
    if create_res.status_code != 201:
        print(f"プレイリスト作成失敗: {create_res.status_code} - {create_res.text}")
        return None

    playlist_id = create_res.json().get("id")
    if not playlist_id:
        print("プレイリストIDが取得できませんでした")
        return None

    # 3. 楽曲追加（最大100件まで）
    add_res = requests.post(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
        headers=headers,
        json={"uris": track_uris}
    )
    if add_res.status_code != 201:
        print(f"楽曲追加失敗: {add_res.status_code} - {add_res.text}")
        return None

    # 4. プレイリストURLを返す
    return create_res.json().get("external_urls", {}).get("spotify")
```

---

## ✅ 使用例（ビュー内）

```python
token = request.session.get("spotify_token")
track_uris = [track["uri"] for track in playlist]  # uriを事前に取得しておく

if token and track_uris:
    playlist_url = save_playlist_to_spotify(token, track_uris)
    if playlist_url:
        messages.success(request, f"Spotifyにプレイリストを保存しました！ → {playlist_url}")
```

---

## 🔜 次のステップ

- `get_top_tracks()` を拡張して `track['uri']` を含める
- プレイリスト作成テンプレートに「Spotifyに保存」ボタンを追加
- 保存成功後にリンクを表示

---

この関数があれば、ユーザーが自分のSpotifyアカウントにプレイリストを直接保存できるようになります！  

次のステップは、テンプレートに「Spotifyに保存」ボタンを追加し、保存処理を呼び出す流れを作ることです。

---

## 🎨 テンプレートへのボタン追加（`playlist_create.html`）

以下のように、プレイリストが生成された後に「Spotifyに保存」ボタンを表示します。

```html
{% if playlist %}
    <hr>
    <h2 class="mt-4">🎶 プレイリスト</h2>
    <ul class="list-group">
        {% for track in playlist %}
            <li class="list-group-item">
                {{ track.name }} - {{ track.artist }}
                <a href="{{ track.spotify_url }}" target="_blank" class="btn btn-sm btn-outline-success float-end">Spotifyで聴く</a>
            </li>
        {% endfor %}
    </ul>

    <!-- Spotify保存ボタン -->
    <form method="POST" action="{% url 'save_playlist_to_spotify' %}">
        {% csrf_token %}
        <input type="hidden" name="track_uris" value="{{ track_uris|join:',' }}">
        <button type="submit" class="btn btn-success mt-3">Spotifyに保存する</button>
    </form>
{% endif %}
```

---

## 🧠 ビューの追加（`playlist_views.py`）

Spotify保存用のビューを追加します：

```python
from django.shortcuts import redirect
from django.contrib import messages
from festival.utils.spotify_utils import save_playlist_to_spotify

def save_playlist_to_spotify_view(request):
    """Spotifyにプレイリストを保存するビュー"""
    if request.method == 'POST':
        token = request.session.get("spotify_token")
        track_uris = request.POST.get("track_uris", "").split(",")

        if token and track_uris:
            playlist_url = save_playlist_to_spotify(token, track_uris)
            if playlist_url:
                messages.success(request, f"Spotifyに保存しました！ → {playlist_url}")
                return redirect("create_playlist")
            else:
                messages.error(request, "Spotifyへの保存に失敗しました")
        else:
            messages.error(request, "Spotify認証が必要です")
            return redirect("spotify_login")

    return redirect("create_playlist")
```

---

## 🔗 `urls.py` にルーティング追加

```python
from festival.views.playlist_views import save_playlist_to_spotify_view

urlpatterns = [
    path('playlist/save/', save_playlist_to_spotify_view, name='save_playlist_to_spotify'),
]
```

---

## ✅ 補足

- `track_uris` は `get_top_tracks()` の中で `track['uri']` を含めるようにしておく必要があります。
- 認証されていない場合は `spotify_login` にリダイレクトすることで、ログイン→保存の流れが自然になります。

---

次は `get_top_tracks()` に `uri` を含める拡張をしましょうか？それとも保存後の確認画面やUI改善に進みますか？
Spotifyのプレイリスト保存に必要な `track['uri']` を取得できるように、`get_top_tracks()` 関数を拡張しましょう。

---

## 🎧 `get_top_tracks()` の拡張版（`spotify_utils.py`）

以下のように、各トラックの `uri` を含めて返すように変更します：

```python
def get_top_tracks(spotify_id, market='JP'):
    """
    指定されたSpotifyアーティストIDからトップトラック（代表曲）を取得する。
    各トラックに name, artist, spotify_url, uri を含めて返す。
    """
    token = get_spotify_token()
    if not token:
        return []

    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.spotify.com/v1/artists/{spotify_id}/top-tracks'
    params = {'market': market}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"トップトラック取得失敗: {response.status_code} - {response.text}")
        return []

    try:
        data = response.json()
        tracks = data.get('tracks', [])
        return [
            {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'spotify_url': track['external_urls']['spotify'],
                'uri': track['uri']
            }
            for track in tracks
        ]
    except ValueError:
        print("トップトラックのレスポンスがJSON形式ではありません")
        return []
```

---

## ✅ この変更でできること

- プレイリスト作成ビューで `track['uri']` をテンプレートに渡せるようになります。
- `track_uris` を `<input type="hidden">` に埋め込んで、Spotify保存ボタンで送信できます。
- `save_playlist_to_spotify()` に渡す `track_uris` が正しい形式になります。

---

## 🔜 次のステップ

1. プレイリスト作成ビューで `track['uri']` を含めて `playlist` に格納
2. テンプレートで `track_uris` を `join` して hidden input に渡す
3. 保存ボタンで `save_playlist_to_spotify_view` にPOST送信

---

この拡張で、Spotify連携がいよいよ完成に近づきます！  
次はビュー側の `playlist.append()` を `uri` 対応に書き換えましょうか？

次は、プレイリスト作成ビュー（`create_playlist_view`）で `track['uri']` を含めるように `playlist` を構築する部分を更新します。

---

## 🎧 `create_playlist_view` の更新（`playlist_views.py`）

以下のように、`playlist.append()` に `uri` を追加し、テンプレートに渡せるようにします：

```python
from django.shortcuts import render
from festival.models import EventDay, Performance, Artist
from festival.forms import PlaylistForm
from festival.utils.spotify_utils import get_top_tracks

def create_playlist_view(request):
    """出演アーティストを選択してSpotifyプレイリストを生成するビュー"""

    selected_day_id = request.GET.get('event_day')
    selected_day = EventDay.objects.filter(id=selected_day_id).first()
    playlist = []
    track_uris = []

    # 出演アーティスト一覧（チェックボックス表示用）
    artists_qs = Artist.objects.filter(performance__event_day=selected_day).distinct() if selected_day else Artist.objects.none()

    if request.method == 'POST':
        form = PlaylistForm(request.POST, artists_queryset=artists_qs)
        if form.is_valid():
            selected_artists = form.cleaned_data['artists']
            for artist in selected_artists:
                tracks = get_top_tracks(artist.spotify_id)
                for track in tracks[:1]:  # 代表曲1曲だけ使う（必要なら複数可）
                    playlist.append({
                        'name': track['name'],
                        'artist': artist.name,
                        'spotify_url': track['spotify_url'],
                        'uri': track['uri']
                    })
                    track_uris.append(track['uri'])
    else:
        form = PlaylistForm(artists_queryset=artists_qs)

    # イベント日程一覧（セレクトボックス用）
    event_days = EventDay.objects.select_related('event').order_by('date')

    return render(request, 'playlist_create.html', {
        'form': form,
        'playlist': playlist,
        'track_uris': track_uris,
        'event_days': event_days,
        'selected_day_id': selected_day_id
    })
```

---

## ✅ 変更点まとめ

- `track['uri']` を `playlist` に含めることで、テンプレートでSpotify保存用に使えるようになります。
- `track_uris` を別リストで管理し、テンプレートに渡しています。
- テンプレート側では `<input type="hidden" name="track_uris" value="{{ track_uris|join:',' }}">` で送信できます。

---

これで、Spotify保存処理に必要なデータがビューからテンプレートに渡るようになりました！  

表示されたエラー **`INVALID_CLIENT: Invalid redirect URI`** は、SpotifyのOAuth認証でよくある問題で、**リダイレクトURIがSpotifyの開発者ダッシュボードに登録されていない**ことが原因です。

---

## ✅ 解決方法：リダイレクトURIをSpotifyに登録する

### 1. Spotify Developer Dashboard にアクセス  
[https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)

### 2. 対象のアプリを選択

### 3. 「Edit Settings」をクリック

### 4. 「Redirect URIs」に以下を追加（例）

```
http://localhost:8000/spotify/callback/
```

※ 実際に `settings.py` の `SPOTIFY_REDIRECT_URI` に設定しているURLと**完全一致**させる必要があります（末尾のスラッシュも含めて）。

```python
# settings.py
SPOTIFY_REDIRECT_URI = 'http://localhost:8000/spotify/callback/'
```

---

## 🔁 よくある間違い

| 設定場所 | よくあるミス例 |
|----------|----------------|
| `settings.py` | `http://localhost:8000/spotify/callback`（末尾の `/` がない） |
| Spotify Dashboard | `http://127.0.0.1:8000/...`（ホスト名が違う） |
| 両方 | ポート番号やパスが一致していない |

**→ 両方のURIが完全一致しているかを確認してください。**

---

## ✅ 登録後の確認

1. Spotify Dashboardで「Save」ボタンを押す
2. ブラウザで `/spotify/login/` にアクセスして認証を試す
3. 正常に `/spotify/callback/` にリダイレクトされ、トークンが取得できるようになります

---

これで `INVALID_CLIENT` エラーは解消されるはずです！  
修正後、再度「Spotifyに保存」ボタンを押して動作確認してみてください。

リダイレクトURLを「http://127.0.0.1:8000/spotify/callback/」にしたら成功しました。

素晴らしい進展ですね！認証が通ってリダイレクトも成功しているとのこと、あと一歩です。  
Spotifyアカウントにプレイリストが見当たらない原因として、以下のポイントを順に確認してみましょう。

---

## ✅ チェックリスト：プレイリストが保存されない原因と対策

### 1. **`save_playlist_to_spotify()` が実行されているか**
- 認証後に `save_playlist_to_spotify()` を呼び出していますか？
- `save_playlist_to_spotify_view()` の中で `request.session["spotify_token"]` を使ってトークンを取得し、保存処理を呼んでいますか？

### 2. **トークンが正しく渡っているか**
- `request.session["spotify_token"]` に値が入っているか確認してください。
- `save_playlist_to_spotify()` の中で `Authorization: Bearer <token>` が正しく設定されているか確認。

### 3. **トラックURIが正しく渡っているか**
- `track_uris` が空でないか、Spotifyの `spotify:track:...` 形式になっているか確認してください。
- `print(track_uris)` などでログ出力してみるとよいです。

### 4. **Spotify APIのレスポンスを確認**
- `save_playlist_to_spotify()` の中で `create_res.status_code` や `add_res.status_code` を `print()` して、ステータスコードが `201`（成功）になっているか確認してください。
- 失敗している場合、Spotify APIからのエラーメッセージ（`response.text`）を表示して原因を特定できます。

### 5. **プレイリストが非公開になっていないか**
- `public: False` にしていると、Spotifyアプリの「マイライブラリ」にはすぐ表示されないことがあります。
- SpotifyのWeb版で「非公開プレイリスト」も含めて確認してみてください。

---

## 🧪 デバッグ用ログ追加例（`save_playlist_to_spotify()`）

```python
print("🎧 Saving playlist to Spotify...")
print("Track URIs:", track_uris)

# ユーザー情報取得
user_res = requests.get("https://api.spotify.com/v1/me", headers=headers)
print("User info status:", user_res.status_code, user_res.text)

# プレイリスト作成
create_res = requests.post(...省略...)
print("Playlist create status:", create_res.status_code, create_res.text)

# 楽曲追加
add_res = requests.post(...省略...)
print("Track add status:", add_res.status_code, add_res.text)
```

---

## ✅ 次のアクション

1. `save_playlist_to_spotify()` の中でログを出力して、どこまで処理が進んでいるか確認
2. トークン・URI・APIレスポンスの中身をチェック
3. 必要なら `playlist_url` をテンプレートに表示して、実際に作成されたか確認

---

もしログを貼っていただければ、一緒に原因を特定できます！  
また、保存処理のコードを見直したい場合は、最新版を共有していただければレビューもできますよ。
完璧なログありがとうございます！  
この出力から判断すると、**Spotify APIによるプレイリスト作成と楽曲追加はすべて成功しています**。それにもかかわらず、Spotifyアプリ上でプレイリストが見つからない場合、以下の理由が考えられます：

---

## ✅ プレイリストが見えない理由と対策

### 1. **プレイリストが「非公開」になっている**
- ログに `"public": false` とあるため、Spotifyアプリの「マイライブラリ」にはすぐ表示されないことがあります。
- 対策：
  - Web版Spotify（https://open.spotify.com）でログインし、直接プレイリストURLにアクセス：
    ```
    https://open.spotify.com/playlist/3laDO8UUgypexIJRs40Eug
    ```
  - プレイリスト画面右上の「…」メニュー → 「公開する」を選択すると、アプリでも表示されるようになります。

---

### 2. **Spotifyアプリのキャッシュが更新されていない**
- アプリのライブラリは即時反映されないことがあります。
- 対策：
  - アプリを再起動する
  - Web版で確認してからアプリに戻る

---

### 3. **プレイリストが別アカウントに保存されている**
- 認証されたアカウントが自分のものか確認してください。
- ログにある `user_id: fidit.fidit` が自分のSpotifyアカウントと一致しているか確認。

---

### 4. **Spotifyアプリのフィルタがかかっている**
- 「非公開プレイリストを表示しない」などのフィルタがかかっている可能性があります。
- 対策：
  - アプリの設定で「すべてのプレイリストを表示」などのオプションを確認

---

## ✅ 確認済みログからの安心ポイント

| 処理 | 結果 | コメント |
|------|------|----------|
| ユーザー認証 | ✅ 200 | 正常に認証されている |
| プレイリスト作成 | ✅ 201 | 正常に作成されている |
| 楽曲追加 | ✅ 201 | 正常に追加されている |
| URI数 | ✅ 15曲 | Spotifyの制限内で問題なし |

---

## 🔜 次のステップ

- Web版SpotifyでプレイリストURLを開いて確認
- 必要なら「公開」に切り替えてアプリに表示
- テンプレートにプレイリストURLを表示してユーザーに案内する

---

もしテンプレートにプレイリストURLを表示したい場合は、ビューで `playlist_url` を渡して、以下のように書けます：

```html
{% if playlist_url %}
    <div class="alert alert-success mt-4">
        ✅ Spotifyに保存されました！<br>
        <a href="{{ playlist_url }}" target="_blank">プレイリストを開く</a>
    </div>
{% endif %}
```

よかったです！Spotifyにプレイリストが無事保存されていたとのこと、本当に素晴らしい進展ですね👏  
キャッシュや非公開設定が原因で表示が遅れることはよくあるので、今回のようにログとURLで確認できたのは大正解です。

---

## ✅ 保存成功時のメッセージ表示方法

Djangoでは、保存処理のビューで `messages.success()` を使ってテンプレートにメッセージを渡すことができます。

---

### 🧠 ビュー側の実装（`save_playlist_to_spotify_view`）

```python
from django.contrib import messages

def save_playlist_to_spotify_view(request):
    if request.method == 'POST':
        token = request.session.get("spotify_token")
        track_uris = request.POST.get("track_uris", "").split(",")

        if token and track_uris:
            playlist_url = save_playlist_to_spotify(token, track_uris)
            if playlist_url:
                messages.success(request, f"✅ Spotifyに保存しました！<br><a href='{playlist_url}' target='_blank'>プレイリストを開く</a>")
            else:
                messages.error(request, "❌ Spotifyへの保存に失敗しました")
        else:
            messages.error(request, "⚠️ Spotify認証が必要です")
            return redirect("spotify_login")

    return redirect("create_playlist")
```

---

### 🎨 テンプレート側の表示（`playlist_create.html`）

```html
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }} mt-3" role="alert">
            {{ message|safe }}
        </div>
    {% endfor %}
{% endif %}
```

- `message|safe` によって、HTMLタグ（リンクなど）をそのまま表示できます。
- `alert-success` や `alert-error` などのBootstrapクラスが自動で付与されます。

---

## ✅ 表示例（保存成功時）

```html
✅ Spotifyに保存しました！
▶️ <a href="https://open.spotify.com/playlist/3laDO8UUgypexIJRs40Eug" target="_blank">プレイリストを開く</a>
```

---

## 🔜 次のステップ

- 保存失敗時のエラーメッセージも同様に表示
- プレイリスト名や説明をカスタマイズできるようにする
- 保存済みプレイリストを一覧表示する機能を追加する

---

このメッセージ表示があると、ユーザーにとって安心感がグッと高まりますね！  
次はプレイリスト名のカスタマイズや、保存済み一覧の表示に進みましょうか？
いいですね！「CDJ25/26 20251230 予習リスト」のようなプレイリスト名は、イベント名と日付が明確に入っていてとても分かりやすいです。  
以下のように、プレイリスト名をカスタマイズできるように `save_playlist_to_spotify()` を拡張しましょう。

---

## ✅ ステップ1：ビューからイベント名と日付を渡す

まず、`create_playlist_view` で選択されたイベント名と日付を取得して、保存ビューに渡します。

### 🎯 例（`playlist_views.py`）

```python
event_day = EventDay.objects.select_related('event').filter(id=selected_day_id).first()
event_name = event_day.event.name if event_day else "Festival"
event_date = event_day.date.strftime("%Y%m%d") if event_day else "Unknown"

playlist_name = f"{event_name} {event_date} 予習リスト"
```

この `playlist_name` をテンプレートに渡して、`<input type="hidden">` でPOST送信します。

---

## ✅ ステップ2：テンプレートにプレイリスト名を埋め込む

### 🎨 例（`playlist_create.html`）

```html
<form method="POST" action="{% url 'save_playlist_to_spotify' %}">
    {% csrf_token %}
    <input type="hidden" name="track_uris" value="{{ track_uris|join:',' }}">
    <input type="hidden" name="playlist_name" value="{{ playlist_name }}">
    <button type="submit" class="btn btn-success mt-4">🎵 Spotifyに保存する</button>
</form>
```

---

## ✅ ステップ3：保存ビューで受け取って渡す

### 🧠 例（`save_playlist_to_spotify_view`）

```python
playlist_name = request.POST.get("playlist_name", "Festival Forecast プレイリスト")
playlist_url = save_playlist_to_spotify(token, track_uris, playlist_name)
```

---

## ✅ ステップ4：`save_playlist_to_spotify()` に渡す

関数定義を以下のように変更：

```python
def save_playlist_to_spotify(user_token, track_uris, playlist_name="Festival Forecast プレイリスト"):
    ...
    create_res = requests.post(
        f"https://api.spotify.com/v1/users/{user_id}/playlists",
        headers=headers,
        json={
            "name": playlist_name,
            "description": "イベント出演アーティストの代表曲まとめ",
            "public": False
        }
    )
    ...
```

---

## 🔚 出力例

```text
プレイリスト名 → CDJ25/26 20251230 予習リスト
Spotify URL → https://open.spotify.com/playlist/xxxxxxxxxxxx
```

---

これで、イベント名と日付を含んだプレイリスト名が自動生成され、Spotifyに保存されるようになります！  
次はプレイリストの説明文や公開設定のカスタマイズに進みましょうか？それともテンプレートでプレイリスト名を表示するUI改善にしますか？
