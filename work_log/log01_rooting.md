# Djangoアプリのルーティング

## 🔧 1. `conf/urls.py` の編集

まずはプロジェクト全体のルート設定です。`festival` アプリのURLを読み込むようにします。

```python
# conf/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('festival.urls')),  # festivalアプリのルーティングを読み込む
]
```

---

## 📁 2. `festival/urls.py` の作成

アプリ側のルーティングファイルを新規作成します。トップページや一覧ページなど、今後の画面に対応するURLをここに定義していきます。

```python
# festival/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # トップページ
    path('artists/', views.artist_list, name='artist_list'),  # アーティスト一覧（今後実装）
]
```

---

## 🖼️ 3. `views.py` にトップページ用ビューを追加

まずはトップページ用の簡単なビュー関数を用意しましょう。

```python
# festival/views.py

from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
```

---

## 🧱 4. テンプレートファイルの作成

`festival/templates/index.html` を作成して、トップページの表示を確認します。

```html
<!-- festival/templates/index.html -->

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>音楽フェスティバル管理</title>
</head>
<body>
    <h1>🎶 音楽フェスティバル管理アプリへようこそ！</h1>
    <p>出演アーティスト情報を管理・予測できます。</p>
</body>
</html>
```

---

## ✅ 5. 動作確認

以下のコマンドで開発サーバーを起動し、`http://localhost:8000/` にアクセスしてトップページが表示されるか確認しましょう。

```bash
python manage.py runserver
```

---

では、次のステップとして「アーティスト一覧表示」機能のルーティングと画面連携を進めましょう。

---

## 🧭 今回の目標

- アーティスト一覧ページのルーティングとビュー作成
- `Artist` モデルのデータをテンプレートに表示
- Bootstrapで簡単な見た目調整（任意）

---

## 🔧 1. `festival/urls.py` に一覧ページを追加

```python
# festival/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('artists/', views.artist_list, name='artist_list'),  # 一覧ページ
]
```

---

## 🧱 2. `views.py` に一覧表示用ビューを追加

```python
# festival/views.py

from django.shortcuts import render
from .models import Artist

def index(request):
    return render(request, 'index.html')

def artist_list(request):
    artists = Artist.objects.all().order_by('name')  # 名前順で取得
    return render(request, 'artist_list.html', {'artists': artists})
```

---

## 🖼️ 3. テンプレートファイル `artist_list.html` を作成

```html
<!-- festival/templates/artist_list.html -->

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>出演アーティスト一覧</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-4">
    <h1>🎤 出演アーティスト一覧</h1>
    <table class="table table-striped">
        <thead>
            <tr>
                <th>名前</th>
                <th>Spotify ID</th>
                <th>ジャンル</th>
                <th>人気度</th>
            </tr>
        </thead>
        <tbody>
            {% for artist in artists %}
            <tr>
                <td>{{ artist.name }}</td>
                <td>{{ artist.spotify_id }}</td>
                <td>{{ artist.genres|join:", " }}</td>
                <td>{{ artist.popularity }}</td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="4">登録されたアーティストがまだありません。</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <a href="{% url 'index' %}" class="btn btn-secondary">トップへ戻る</a>
</body>
</html>
```

※ `genres` がリスト型の場合は `join` フィルターで表示できます。

---

## ✅ 4. 動作確認

- 管理画面または `save_artist_from_spotify()` で登録済みのアーティストが一覧表示されるか確認
- Bootstrapが読み込まれているか確認（テーブルの装飾）

---

# 表示の不具合

アーティスト一覧表示には成功したが、ジャンルの表示が意図した通りになっていなかった。

ジャンルが `"anime, j-pop, j-rock"` のような文字列ではなく、`['a', 'n', 'i', 'm', 'e', ',', ' ', 'j', '-', 'p', 'o', 'p', ',', ' ', 'j', '-', 'r', 'o', 'c', 'k']` のように1文字ずつ分割されてしまっている状態ですね。

これは、ジャンル情報が文字列ではなく「文字のリスト」として保存されているため、テンプレートで `join` を使ったときに1文字ずつ処理されてしまっているのが原因です。

---

## ✅ 解決方法

### 1. モデルの `genres` フィールドを確認

まず、`Artist` モデルの `genres` フィールドがどう定義されているか確認しましょう。おそらく `CharField` ではなく `TextField` で、Spotify APIから取得したジャンルリストをそのまま保存していると思われます。

```python
# 例: models.py
class Artist(models.Model):
    name = models.CharField(max_length=255)
    spotify_id = models.CharField(max_length=255)
    genres = models.JSONField(default=list)  # ← こうなっている場合はOK
    popularity = models.IntegerField()
```

### 2. テンプレート側の修正

ジャンルがリスト型（例：`["anime", "j-pop", "j-rock"]`）であれば、テンプレートでは以下のように `join` フィルターを使って表示できます：

```html
<td>{{ artist.genres|join:", " }}</td>
```

しかし、もしジャンルが文字列型（例：`"anime, j-pop, j-rock"`）として保存されている場合は、`join` を使うと1文字ずつ分割されてしまいます。

その場合はテンプレートをこう修正してください：

```html
<td>{{ artist.genres }}</td>
```

---

## 🔍 どちらの形式か確認する方法

Django Shellで確認できます：

```bash
python manage.py shell
```

```python
from festival.models import Artist
a = Artist.objects.first()
print(a.genres)
print(type(a.genres))
```

- `list` 型 → `join` フィルターを使う
- `str` 型 → そのまま表示する

---

## 💡 おすすめ：JSONFieldで保存する

Spotify APIからジャンルを取得する際に、`genres` をリスト型のまま `JSONField` に保存するのが一番扱いやすいです。すでにそうしている場合はテンプレートの `join` だけでOKです。

---

## 原因特定：保存時に文字列に変換されていた

```
def search_artist(name):
    import requests
    from .auth import get_token  # トークン取得関数

    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": name,
        "type": "artist",
        "limit": 1
    }
    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    data = response.json()

    if data['artists']['items']:
        artist = data['artists']['items'][0]
        return {
            'name': artist['name'],
            'spotify_id': artist['id'],
            'popularity': artist['popularity'],
            'genres': artist['genres']  # ← joinせずそのままリスト型で返す
        }
    return None
```

---

## 🪄 次のステップ案

- 検索機能（`GET` パラメータで名前フィルター）
- 詳細ページ（`artist/<int:pk>/`）
- 類似アーティスト表示（`RelatedArtist` モデルとの連携）

---

アーティスト一覧ページに「名前で検索できる機能」を追加していきましょう🔍  
Djangoの `GET` パラメータを使って、シンプルで使いやすい検索フォームを実装します。

---

## 🧭 今回の目標

- アーティスト一覧ページに検索フォームを追加
- 名前に部分一致するアーティストだけを表示
- 検索語を保持したまま表示

---

## 🔧 1. `views.py` の修正

```python
# festival/views.py

from django.shortcuts import render
from .models import Artist

def artist_list(request):
    query = request.GET.get('q')  # 検索語を取得
    if query:
        artists = Artist.objects.filter(name__icontains=query).order_by('name')
    else:
        artists = Artist.objects.all().order_by('name')
    return render(request, 'artist_list.html', {'artists': artists, 'query': query})
```

---

## 🖼️ 2. `artist_list.html` に検索フォームを追加

```html
<!-- festival/templates/artist_list.html -->

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>出演アーティスト一覧</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-4">
    <h1>🎤 出演アーティスト一覧</h1>

    <!-- 検索フォーム -->
    <form method="get" class="mb-3">
        <div class="input-group">
            <input type="text" name="q" class="form-control" placeholder="アーティスト名で検索" value="{{ query }}">
            <button type="submit" class="btn btn-primary">検索</button>
        </div>
    </form>

    <!-- 一覧表示 -->
    <table class="table table-striped">
        <thead>
            <tr>
                <th>名前</th>
                <th>Spotify ID</th>
                <th>ジャンル</th>
                <th>人気度</th>
            </tr>
        </thead>
        <tbody>
            {% for artist in artists %}
            <tr>
                <td>{{ artist.name }}</td>
                <td>{{ artist.spotify_id }}</td>
                <td>{{ artist.genres|join:", " }}</td>
                <td>{{ artist.popularity }}</td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="4">該当するアーティストが見つかりませんでした。</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <a href="{% url 'index' %}" class="btn btn-secondary">トップへ戻る</a>
</body>
</html>
```

---

## ✅ 3. 動作確認

- `/artists/` にアクセスして一覧が表示されるか確認
- 検索フォームに「YOASOBI」などを入力して、部分一致で絞り込みされるか確認
- 検索語がフォームに残っているか確認

---

## ✨ 拡張アイデア

- ジャンルや人気度でも絞り込み（複数条件検索）
- 検索結果の件数表示
- 検索語のハイライト表示（`{{ artist.name|highlight:query }}` のようなカスタムフィルター）

---

では、アーティストの詳細ページを作成して、個別の情報（名前・ジャンル・人気度など）を表示できるようにしましょう。

---

## 🧭 今回の目標

- 詳細ページへのルーティング追加（`artist/<int:pk>/`）
- `DetailView` または関数ベースビューで個別表示
- テンプレートで情報を整えて表示

---

## 🔧 1. `urls.py` に詳細ページルートを追加

```python
# festival/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('artists/', views.artist_list, name='artist_list'),
    path('artist/<int:pk>/', views.artist_detail, name='artist_detail'),  # ← 追加
]
```

---

## 🧱 2. `views.py` に詳細ビューを追加

```python
# festival/views.py

from django.shortcuts import render, get_object_or_404
from .models import Artist

def artist_detail(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    return render(request, 'artist_detail.html', {'artist': artist})
```

---

## 🖼️ 3. `artist_detail.html` を作成

```html
<!-- festival/templates/artist_detail.html -->

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>{{ artist.name }} の詳細</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-4">
    <h1>{{ artist.name }} の詳細</h1>

    <ul class="list-group mb-3">
        <li class="list-group-item"><strong>Spotify ID:</strong> {{ artist.spotify_id }}</li>
        <li class="list-group-item"><strong>ジャンル:</strong> {{ artist.genres|join:", " }}</li>
        <li class="list-group-item"><strong>人気度:</strong> {{ artist.popularity }}</li>
    </ul>

    <a href="{% url 'artist_list' %}" class="btn btn-secondary">一覧に戻る</a>
</body>
</html>
```

---

## 🧩 4. 一覧ページからリンクを追加（任意）

```html
<!-- artist_list.html の名前列をリンクに変更 -->

<td>
    <a href="{% url 'artist_detail' artist.pk %}">{{ artist.name }}</a>
</td>
```

---

## ✅ 5. 動作確認

- `/artist/1/` のようなURLで詳細ページが表示されるか確認
- 一覧ページからリンクで遷移できるか確認
- ジャンルが正しく表示されるか確認

---

## ✨ 拡張アイデア

- Spotifyのアーティストページへのリンク追加（`https://open.spotify.com/artist/{{ artist.spotify_id }}`）
- 類似アーティストの表示（`RelatedArtist` モデルと連携）
- プレイリストや出演履歴の表示

---
