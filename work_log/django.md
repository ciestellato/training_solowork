それでは、**仮DB設計をDjangoのモデルクラスに落とし込む準備**に入りましょう。

---

## 🧭 ステップバイステップ：Djangoモデル設計の準備

### ✅ 1. アプリの作成（まだなら）
まずはDjangoプロジェクト内にアプリを作成します：

```bash
python manage.py startapp festival
```

### ✅ 2. `models.py` にエンティティを定義する準備
先ほどのER図に基づいて、以下のようなモデルクラスを設計します。

---

## 🧱 Djangoモデル設計（準備用コード）

```python
from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Artist(models.Model):
    name = models.CharField(max_length=255)
    popularity = models.IntegerField(null=True, blank=True)
    genres = models.CharField(max_length=255, blank=True)
    spotify_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Performance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    performance_date = models.DateField()
    is_confirmed = models.BooleanField(default=False)

class RelatedArtist(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='base_artist')
    related_artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='similar_to')
    similarity_score = models.FloatField()

class ManualEntry(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
```

---

### ✅ 3. モデル設計のポイント

- **外部キー**：`ForeignKey` を使ってリレーションを表現
- **自己参照**：`RelatedArtist` で `Artist` を2回参照（`related_name` を使って区別）
- **文字列表示**：`__str__()` を定義して管理画面で見やすく
- **バリデーション**：`blank=True` や `null=True` で柔軟性を確保

---

### ✅ 4. 次にやること

1. `models.py` に上記を記述
2. `python manage.py makemigrations` → モデルの変更をマイグレーションに変換
3. `python manage.py migrate` → 実際にDBに反映
4. `admin.py` にモデルを登録して管理画面で確認

---

このあと、管理画面やデータ取り込み機能（Spotify API）に進むとスムーズです。必要なら、管理画面のカスタマイズやAPI連携のサンプルコードもお手伝いできますよ！どこから進めましょうか？
