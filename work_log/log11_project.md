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

これで、プレイリスト作成機能のフォーム部分が完成です！次はテンプレートの調整や、Spotifyリンクの表示スタイルを整える段階に進めましょうか？
