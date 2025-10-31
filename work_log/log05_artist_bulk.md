Djangoで「カンマ区切りのアーティスト名を一括登録」する機能は、**フォーム + バックエンド処理**で簡単に実装できます。以下のような流れで構築できますよ。

---

## 🧭 実装の流れ

### ✅ 1. フォーム作成（`forms.py`）

```python
from django import forms

class BulkArtistForm(forms.Form):
    names = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'YOASOBI, Aimer, King Gnu'}),
        label='アーティスト名（カンマ区切り）'
    )
```

---

### ✅ 2. ビュー作成（`views.py`）

```python
from django.shortcuts import render, redirect
from .forms import BulkArtistForm
from .models import Artist
from .spotify import save_artist_from_spotify  # Spotify API連携関数

def bulk_artist_register(request):
    message = ''
    if request.method == 'POST':
        form = BulkArtistForm(request.POST)
        if form.is_valid():
            raw_names = form.cleaned_data['names']
            name_list = [name.strip() for name in raw_names.split(',') if name.strip()]
            created = 0
            skipped = 0
            for name in name_list:
                if Artist.objects.filter(name__iexact=name).exists():
                    skipped += 1
                    continue
                result = save_artist_from_spotify(name)
                if result:
                    created += 1
            message = f"{created} 件登録、{skipped} 件スキップしました。"
    else:
        form = BulkArtistForm()
    return render(request, 'bulk_artist_register.html', {'form': form, 'message': message})
```

---

### ✅ 3. テンプレート作成（`bulk_artist_register.html`）

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>アーティスト一括登録</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-4">
    <h1>🎧 アーティスト一括登録</h1>

    {% if message %}
        <div class="alert alert-info">{{ message }}</div>
    {% endif %}

    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">登録する</button>
    </form>

    <a href="{% url 'artist_list' %}" class="btn btn-secondary mt-3">一覧に戻る</a>
</body>
</html>
```

---

### ✅ 4. ルーティング追加（`urls.py`）

```python
path('artists/bulk/', views.bulk_artist_register, name='bulk_artist_register'),
```

---

## ✨ 拡張アイデア

- 改行区切りにも対応（`,` だけでなく `\n` も分割対象に）
- 登録結果を一覧表示（成功・失敗・スキップ）
- CSVアップロード対応（`pandas` や `csv` モジュールで処理）

---

この機能があれば、**数十〜数百件のアーティストを一気に登録できる**ので、フェスやツアーの準備が格段に楽になります！  
実装してみて詰まったら、コードレビューやデバッグもお手伝いしますよ 💪
