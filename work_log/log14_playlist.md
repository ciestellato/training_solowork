「イベント日程ページなどから直接プレイリスト作成に遷移」できるようにするには、**URLパラメータで `event_day` を渡すリンクを設置**し、ビュー側でそれを受け取るようにすればOKです。

---

## ✅ 1. リンクの設置（テンプレート側）

例えば `timetable_view.html` の下部などに以下のリンクを追加：

```django
<a href="{% url 'festival:create_playlist' %}?event_day={{ day.id }}" class="btn btn-success mt-3">
    🎧 この日程のプレイリストを作成
</a>
```

→ `event_day.id` をURLパラメータとして渡すことで、プレイリスト作成画面に遷移したときにその日程が選択された状態になります。

---

## ✅ 2. ビュー側の修正（`create_playlist_view`）

現在のコードはすでに `request.GET.get('event_day')` を使っているので、**URLパラメータで渡された `event_day` を受け取る準備はできています**。  
そのため、ビューの修正は不要です。

ただし、テンプレート側で「イベント日程のセレクトボックス」が不要になる場合は、以下のように表示を制御できます：

```django
{% if selected_day_id %}
    <p class="fw-bold">対象日程：{{ event_day.date }} @ {{ event_day.venue }}</p>
{% else %}
    <!-- セレクトボックス表示 -->
    <form method="GET" class="mb-4">
        ...
    </form>
{% endif %}
```

---

## ✅ 3. URL設定（`urls.py`）

すでに `create_playlist_view` が `festival:create_playlist` に紐づいているなら、変更不要です。

```python
path("playlist/create/", views.create_playlist_view, name="create_playlist"),
```

---

## ✅ まとめ

| 項目 | 対応内容 |
|------|----------|
| 遷移方法 | 公演日ページから `?event_day=ID` を付けたリンクで遷移 |
| ビュー側 | 既存の `request.GET.get('event_day')` を活用 |
| テンプレート | セレクトボックスを省略し、日程情報を表示するように調整可能 |

---

Spotify Dashboardで `http://localhost:8000/` が登録できないという制約がある場合、**SpotifyのOAuth認証をローカル環境でテストするには別の方法が必要**です。

---

## ✅ 解決策：Spotifyが許可するリダイレクトURIを使う

Spotifyはローカル開発用に以下のような**特定のリダイレクトURI**を許可しています：

### ✅ 使えるリダイレクトURIの例

- `http://127.0.0.1:8888/callback`
- `http://localhost:8888/callback`

これらはSpotifyが公式に許可している開発用URIです。  
**重要：Djangoのポートを `8888` に変更する必要があります。**

---

## 🔧 手順

### 1. `settings.py` を修正：

```python
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'
```

### 2. Spotify Developer Dashboard に登録：

- 「Redirect URIs」に `http://127.0.0.1:8888/callback` を追加して保存

### 3. Djangoをポート `8888` で起動：

```bash
python manage.py runserver 8888
```

### 4. `urls.py` に対応するルートを設定：

```python
path('callback/', spotify_callback_view, name='spotify_callback')
```

※ `/spotify/callback/` ではなく `/callback/` に変更することで、URIと一致させます。

---

## ✅ これでできること

- Spotifyが許可する `127.0.0.1:8888/callback` を使って認証が通る
- ローカル環境でもOAuth認証が可能になる
- 認証後にトークンを取得してプレイリスト保存まで進められる

---

## 💡 補足

Spotifyはセキュリティ上、**任意のポート・任意のホスト名では許可していません**。  
そのため、開発時は `127.0.0.1:8888` や `localhost:8888` を使うのが最も確実です。

---

以下に、Spotifyプレイリスト作成機能のためのビュー関数とテンプレートを、最新の要件に合わせて整理した完全版としてご提供します。

---

## 🎯 ビュー関数：`create_playlist_view` & `save_playlist_to_spotify_view`

```python
# views/playlist_views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.http import urlencode

from festival.models import EventDay, Artist
from festival.forms import PlaylistForm
from festival.utils.spotify_utils import get_top_tracks, save_playlist_to_spotify

def create_playlist_view(request):
    """出演アーティストを選択してSpotifyプレイリストを生成するビュー"""

    # イベント日程IDの取得（GETまたはPOST）
    selected_day_id = request.GET.get('event_day') or request.POST.get('event_day')
    event_day = get_object_or_404(EventDay.objects.select_related('event'), id=selected_day_id)

    # プレイリスト初期化
    playlist = []
    track_uris = []
    track_count = 1
    can_save_to_spotify = True

    # 出演アーティスト一覧（チェックボックス表示用）
    artists_qs = Artist.objects.filter(performance__event_day=event_day).distinct()

    # フォーム処理
    if request.method == 'POST':
        form = PlaylistForm(request.POST, artists_queryset=artists_qs)
        if form.is_valid():
            track_count = int(request.POST.get("track_count", 1))
            selected_artists = form.cleaned_data['artists']
            total_tracks = len(selected_artists) * track_count

            # Spotify保存制限チェック（最大100曲）
            can_save_to_spotify = total_tracks <= 100

            # トラック取得とプレイリスト構築
            for artist in selected_artists:
                tracks = get_top_tracks(artist.spotify_id)
                for track in tracks[:track_count]:
                    playlist.append({
                        'name': track['name'],
                        'artist': artist.name,
                        'spotify_url': track['spotify_url'],
                        'uri': track['uri']
                    })
                    track_uris.append(track['uri'])
    else:
        form = PlaylistForm(artists_queryset=artists_qs)

    # プレイリスト名の生成
    event_name = event_day.event.name
    event_date = event_day.date.strftime("%Y%m%d")
    playlist_name = f"{event_name} {event_date} 予習リスト"

    # テンプレート描画
    return render(request, 'playlist_create.html', {
        'form': form,
        'playlist': playlist,
        'track_uris': track_uris,
        'selected_day_id': selected_day_id,
        'playlist_name': playlist_name,
        'selected_track_count': str(track_count),
        'can_save_to_spotify': can_save_to_spotify
    })


def save_playlist_to_spotify_view(request):
    """Spotifyにプレイリストを保存するビュー"""
    if request.method == 'POST':
        token = request.session.get("spotify_token")
        track_uris = request.POST.get("track_uris", "").split(",")
        playlist_name = request.POST.get("playlist_name", "フェス予習プレイリスト")
        selected_day_id = request.POST.get("event_day")

        if token and track_uris:
            playlist_url = save_playlist_to_spotify(token, track_uris, playlist_name)
            if playlist_url:
                messages.success(request, f"✅ Spotifyに保存しました！<br><a href='{playlist_url}' target='_blank'>プレイリストを開く</a>")
            else:
                messages.error(request, "❌ Spotifyへの保存に失敗しました")
        else:
            messages.error(request, "⚠️ Spotify認証が必要です")
            return redirect("festival:spotify_login")

        # 保存後に元のイベント日程に戻る
        base_url = reverse("festival:create_playlist")
        query_string = urlencode({"event_day": selected_day_id})
        return redirect(f"{base_url}?{query_string}")

    return redirect("festival:create_playlist")
```

---

## 🎨 テンプレート：`playlist_create.html`

```django
{% extends 'base.html' %}

{% block title %}プレイリスト作成{% endblock %}

{% block content %}
<h1>🎧 プレイリスト作成</h1>

{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }} mt-3" role="alert">
            {{ message|safe }}
        </div>
    {% endfor %}
{% endif %}

<!-- イベント情報表示 -->
<div class="mb-4">
    <p><strong>イベント:</strong> {{ playlist_name }}</p>
    <input type="hidden" name="event_day" value="{{ selected_day_id }}">
</div>

{% if form %}
<form method="POST">
    {% csrf_token %}
    <input type="hidden" name="event_day" value="{{ selected_day_id }}">
    <input type="hidden" name="playlist_name" value="{{ playlist_name }}">

    {% if form.errors %}
        <div class="alert alert-danger">
            <strong>エラーがあります：</strong>
            <ul>
                {% for field in form %}
                    {% for error in field.errors %}
                        <li>{{ error }}</li>
                    {% endfor %}
                {% endfor %}
            </ul>
        </div>
    {% endif %}

    <div class="mb-3">
        <label class="form-label">出演アーティストを選択</label>
        <input type="text" class="form-control mb-2" placeholder="アーティスト名で絞り込み" id="artistSearch">
        <div class="border p-3" style="max-height: 300px; overflow-y: scroll;">
            {{ form.artists }}
        </div>
    </div>

    <div class="mb-3">
        <label for="track_count">1組あたりの保存曲数:</label>
        <select id="track_count" name="track_count" class="form-select w-auto">
            {% for i in "123456789" %}
                <option value="{{ i }}" {% if i == selected_track_count %}selected{% endif %}>{{ i }}</option>
            {% endfor %}
        </select>
    </div>

    <button type="submit" class="btn btn-primary">プレイリストを作成する</button>
</form>
{% endif %}

{% if playlist %}
    <hr>
    <h2 class="mt-4">🎶 プレイリスト（{{ track_uris|length }}曲）</h2>

    {% if not can_save_to_spotify %}
        <div class="alert alert-warning">
            ⚠️ Spotifyの保存上限（100曲）を超えています。<br>
            保存曲数または選択アーティスト数を減らしてください。
        </div>
    {% else %}
        <ul class="list-group">
            {% for track in playlist %}
                <li class="list-group-item">
                    {{ track.name }} - {{ track.artist }}
                    <a href="{{ track.spotify_url }}" target="_blank" class="btn btn-sm btn-outline-success float-end">Spotifyで聴く</a>
                </li>
            {% endfor %}
        </ul>

        <form method="POST" action="{% url 'festival:save_playlist_to_spotify' %}">
            {% csrf_token %}
            <input type="hidden" name="track_uris" value="{{ track_uris|join:',' }}">
            <input type="hidden" name="playlist_name" value="{{ playlist_name }}">
            <input type="hidden" name="event_day" value="{{ selected_day_id }}">
            <button type="submit" class="btn btn-success mt-4">🎵 Spotifyに保存する</button>
        </form>
    {% endif %}
{% endif %}

<a href="{% url 'festival:fes_event_list' %}" class="btn btn-secondary mt-4">イベント一覧へ戻る</a>

<script>
    document.getElementById('artistSearch').addEventListener('input', function () {
        const keyword = this.value.toLowerCase();
        document.querySelectorAll('.form-check').forEach(cb => {
            const label = cb.textContent.toLowerCase();
            cb.style.display = label.includes(keyword) ? 'block' : 'none';
        });
    });
</script>
{% endblock %}
```

---

ありがとうございます。このエラーは非常に明確です：

---

## ❌ エラーの原因

> **No EventDay matches the given query.**

つまり、`create_playlist_view` にアクセスしたときに `event_day` パラメータが渡されておらず、ビュー内で `get_object_or_404(EventDay, id=None)` を実行してしまい、404エラーになっています。

---

## ✅ 解決方法

### ① `create_playlist_view` に `event_day` パラメータが必須であることを明示し、渡されていない場合はエラーメッセージを表示するようにします。

#### 🔧 修正案（ビュー関数の冒頭）

```python
def create_playlist_view(request):
    selected_day_id = request.GET.get('event_day') or request.POST.get('event_day')
    if not selected_day_id:
        messages.error(request, "⚠️ イベント日程が指定されていません。イベント詳細ページからプレイリスト作成に進んでください。")
        return redirect("festival:fes_event_list")  # または index に戻す
```

これにより、`event_day` が指定されていない場合は、ユーザーをイベント一覧に戻し、エラーを表示できます。

---

### ② 「Spotifyに保存する」ボタンを押した後のリダイレクト先に `event_day` を含める

すでに以下のように修正済みであればOKです：

```python
base_url = reverse("festival:create_playlist")
query_string = urlencode({"event_day": selected_day_id})
return redirect(f"{base_url}?{query_string}")
```

---

### ③ イベント詳細ページからプレイリスト作成画面へ遷移するリンクに `event_day` を含める

```html
<a href="{% url 'festival:create_playlist' %}?event_day={{ event_day.id }}" class="btn btn-primary">
    このイベントでプレイリストを作成
</a>
```

---

## ✅ まとめ

| 修正箇所 | 内容 |
|----------|------|
| ビュー関数 | `event_day` が未指定ならリダイレクト＋警告 |
| リダイレクト | `save_playlist_to_spotify_view` から `event_day` を含めて戻す |
| テンプレート | イベント詳細から `event_day` を含めて遷移するリンクを設置 |

---

この修正で、404エラーは確実に防げます。  
うまくいったら、次は「プレイリスト履歴」や「Spotify連携状態の表示」なども強化できますよ！
