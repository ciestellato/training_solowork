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
