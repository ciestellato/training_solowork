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

この方法で、Spotify認証の壁を突破できるはずです。  
うまくいったら、次はトークンの保存・履歴表示・Spotify連携状態のUIなどにも進めましょう！
