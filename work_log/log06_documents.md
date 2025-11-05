# ドキュメント類の作成

## README.mdの作成

現時点での成果をCopilotへ伝えて、READMEを作成した

## requirements.txtの作成

`requirements.txt` を自動生成したい場合は、以下のコマンドが便利です：

```bash
pip freeze > requirements.txt
```

これで現在の環境にインストールされているパッケージ一覧を保存できます。  
他にもセットアップスクリプトや依存管理を整えたい場合は、`pip-tools` や `Poetry` の導入も検討できますよ！

以下のように `requirements.txt` を整えておくと、他の開発者やチームメンバーが環境構築しやすくなります ✅

---

## 📦 整理済み `requirements.txt`

```txt
# Webフレームワーク
Django==5.2.7
asgiref==3.10.0
sqlparse==0.5.3
tzdata==2025.2

# API連携・通信
requests==2.32.5
urllib3==2.5.0
certifi==2025.10.5
charset-normalizer==3.4.4
idna==3.11

# 環境変数管理
python-dotenv==1.2.1
```

---

## 💡 補足

- 上記は `pip freeze` による自動生成結果を整理したものです。コメントを加えることで、依存関係の目的が明確になります。
- 今後、Bootstrapやテストツール（`pytest`, `django-debug-toolbar` など）を導入する場合は、ここに追記していくと良いです。
- `requirements.txt` を更新したら、GitHubにコミットしておくと環境の再現性が保てます。

---

ドキュメント整備はプロジェクトの理解・引き継ぎ・外部共有にとって非常に重要です。以下のように、整備すべきドキュメントを目的別に整理しました ✍️

---

## 📚 ドキュメント整備ガイド

### 1. `README.md`（✅ 完了済み）
- プロジェクト概要、技術構成、セットアップ手順、機能説明などを網羅
- 今後は英語版やスクリーンショットの追加も検討可能

---

### 2. `.env.example`
目的：環境変数のテンプレートを共有  
内容例：

```env
# Spotify API credentials
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here

# Django secret key
DJANGO_SECRET_KEY=your_django_secret_key_here

# その他必要な環境変数があれば追加
```

---

### 3. `docs/` フォルダの新設
目的：設計資料や仕様書を整理  
おすすめファイル：

| ファイル名 | 内容 |
|------------|------|
| `ER_diagram.png` | モデル設計のER図（Event, Artist, Performanceなど） |
| `screen_flow.md` | 画面遷移図・ページ構成の説明 |
| `api_spec.md` | Spotify API連携の仕様と使用エンドポイント |
| `feature_plan.md` | 実装予定の機能一覧と優先度 |
| `dev_notes.md` | 開発中のメモや注意点（例：バリデーションの仕様） |

---

### 4. `CONTRIBUTING.md`（任意）
目的：外部コラボレーター向けの開発ルール  
内容例：
- ブランチ運用ルール（例：`main`, `dev`, `feature/*`）
- コミットメッセージの書き方
- Issue・Pull Requestのテンプレート

---

### 5. `CHANGELOG.md`（任意）
目的：バージョンごとの変更履歴を記録  
内容例：

```md
## [0.1.0] - 2025-11-05
### Added
- アーティスト一覧・詳細ページ
- Spotify API連携による一括登録機能
- イベント登録フォーム（JSによる日付選択）

### Changed
- 管理画面の表示項目をカスタマイズ
```

---

## ✅ 次のアクション提案

1. `.env.example` を作成して `.env` を除外する `.gitignore` を確認
2. `docs/` フォルダを作成して ER図や画面構成を追加
3. `feature_plan.md` に今後の機能アイデアを整理
4. 必要に応じて `CONTRIBUTING.md` や `CHANGELOG.md` を追加

---

## screen_flow.mdの作成

[screen_flow.md](../docs/screen_flow.md)

## api_spec.mdの作成

[api_spec.md](../docs/api_spec.md)

## feature_plan.mdの作成

[feature_plan.md](../docs/feature_plan.md)

# テスト体制の構築

## 🧪 Djangoプロジェクトのテスト体制構築ガイド

### 1. **テスト方針の決定**
目的別にテスト対象を整理しましょう：

| テスト対象 | 内容 |
|------------|------|
| モデル | フィールド定義、バリデーション、関連性 |
| ビュー | レスポンスのステータスコード、テンプレートのレンダリング |
| フォーム | 入力バリデーション、保存処理 |
| API連携 | Spotify APIのレスポンス、エラーハンドリング（モック化） |

---

### 2. **テスト環境の準備**

#### ✅ 必要パッケージのインストール

```bash
pip install pytest pytest-django
```

#### ✅ `pytest` の初期設定

プロジェクトルートに `pytest.ini` を作成：

```ini
[pytest]
DJANGO_SETTINGS_MODULE = conf.settings
python_files = tests.py test_*.py *_tests.py
```

---

### 3. **テストディレクトリの構成例**

```
festival/
├── tests/
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_forms.py
│   └── test_spotify.py
```

---

### 4. **テストコードの例**

#### ✅ モデルテスト（`test_models.py`）

```python
import pytest
from festival.models import Artist

@pytest.mark.django_db
def test_artist_str():
    artist = Artist.objects.create(name="YOASOBI")
    assert str(artist) == "YOASOBI"
```

#### ✅ ビューテスト（`test_views.py`）

```python
from django.urls import reverse

def test_artist_list_view(client):
    url = reverse("artist_list")
    response = client.get(url)
    assert response.status_code == 200
    assert "アーティスト一覧" in response.content.decode()
```

#### ✅ Spotify APIモック（`test_spotify.py`）

```python
from unittest.mock import patch
from festival.spotify import search_artist

@patch("festival.spotify.requests.get")
def test_search_artist(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "artists": {"items": [{"name": "YOASOBI", "id": "123"}]}
    }
    result = search_artist("YOASOBI")
    assert result["name"] == "YOASOBI"
```

---

### 5. **テスト実行コマンド**

```bash
pytest
```

---

## 📌 次のステップ

- [ ] `tests/` ディレクトリを作成して基本テストを追加  
- [ ] Spotify API連携部分をモック化してテスト可能にする  
- [ ] CIツール（GitHub Actionsなど）で自動テストを導入（任意）

---

## 実行結果

```
short test summary info =================================================== 
FAILED festival/tests/test_spotify.py::test_search_artist - KeyError: 'popularity'
FAILED festival/tests/test_views.py::test_artist_list_view - django.urls.exceptions.NoReverseMatch: Reverse for 'artist_list' not found. 'artist_list' is not a valid view function or p...
================================================= 2 failed, 1 passed in 1.31s 
```

以下にそれぞれの原因と対処法をまとめました ✅

---

## ❌ 1. `test_spotify.py` のエラー  
**エラー内容**：`KeyError: 'popularity'`  
**原因**：モックのレスポンスに `'popularity'` キーが含まれていないため、テスト対象の関数がそのキーを参照した際にエラーが発生。

### ✅ 修正方法

モックのレスポンスに `'popularity'` を含めましょう：

```python
mock_get.return_value.json.return_value = {
    "artists": {
        "items": [{
            "name": "YOASOBI",
            "id": "123",
            "popularity": 85,  # ← 追加
            "genres": ["j-pop"],
            "followers": {"total": 100000},
            "images": []
        }]
    }
}
```

---

~~~
## ❌ 2. `test_views.py` のエラー  
**エラー内容**：`NoReverseMatch: Reverse for 'artist_list' not found.`  
**原因**：`reverse("artist_list")` に対応するURLパターンが `urls.py` に定義されていない、または名前が一致していない。

### ✅ 修正方法

`conf/urls.py` または `festival/urls.py` に以下のようなURLパターンを追加・確認してください：

```python
from django.urls import path
from festival.views import ArtistListView

urlpatterns = [
    path("artists/", ArtistListView.as_view(), name="artist_list"),
]
```

または、関数ベースビューの場合：

```python
from festival.views import artist_list_view

urlpatterns = [
    path("artists/", artist_list_view, name="artist_list"),
]
```

---

## ✅ テスト再実行

修正後に再度テストを実行して確認しましょう：

```bash
pytest
```
~~~

---

テストで発生していたエラー：

> `NoReverseMatch: Reverse for 'artist_list' not found.`

この原因は、**`reverse("artist_list")` を使っているが、`app_name = 'festival'` が定義されているため、名前空間付きで参照する必要がある**という点にあります。

---

## ✅ 修正方法（テスト側）

テストコードで `reverse()` を使うときは、**名前空間を含めて指定**しましょう：

```python
from django.urls import reverse

def test_artist_list_view(client):
    url = reverse("festival:artist_list")  # ← 名前空間を追加
    response = client.get(url)
    assert response.status_code == 200
```

---

## 🔍 補足：名前空間の仕組み

- `app_name = 'festival'` があると、URLの名前は `"festival:artist_list"` のように参照されます。
- これは複数アプリがある場合の名前の衝突を防ぐためのDjangoの仕組みです。

---

この修正を加えたら、再度 `pytest` を実行してみてください：

```bash
pytest
```

## 実行結果

```
short test summary info =================================================== 
FAILED festival/tests/test_views.py::test_artist_list_view - RuntimeError: Database access not allowed, use the "django_db" mark, or the "db" or "transactional_db" fixtures to enable it.
================================================= 1 failed, 2 passed in 1.29s
```

このエラーはとてもよくあるものなので、すぐに解決できます ✅  
エラーメッセージのポイントはこちらです：

> **RuntimeError: Database access not allowed, use the "django_db" mark, or the "db" or "transactional_db" fixtures to enable it.**

---

## 🧪 原因

`test_artist_list_view` の中で Django のデータベースにアクセスしている（例：アーティスト一覧を表示するビュー）にもかかわらず、**テスト関数に `@pytest.mark.django_db` が付いていない**ため、pytest がDBアクセスをブロックしています。

---

## ✅ 修正方法

テスト関数に `@pytest.mark.django_db` を追加するだけでOKです：

```python
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_artist_list_view(client):
    url = reverse("festival:artist_list")
    response = client.get(url)
    assert response.status_code == 200
```

---

## 🔁 再実行

修正後に再度テストを実行：

```bash
pytest
```

## 実行結果

```

festival\tests\test_models.py .                                                                                          [ 33%]
festival\tests\test_views.py .                                                                                           [ 66%]
festival\tests\test_spotify.py .                                                                                         [100%]

====================================================== 3 passed in 0.69s 
```

完璧なテスト通過、おめでとうございます 🎉  
次におすすめなのは、**フォームのテスト（`test_forms.py`）**です。イベント登録やアーティスト登録など、ユーザー入力が絡む部分はバリデーションの確認が重要です。

---

## 🧪 次のステップ：フォームテストの作成

### ✅ 目的
- 入力値のバリデーションが正しく機能しているか確認
- 保存処理が期待通りに動作するか検証
- 異常系（空欄、重複、無効な日付など）への対応を確認

---

### 🗂 ファイル構成

作成するファイル：  
```
festival/tests/test_forms.py
```

---

### 🧾 テスト例（イベント登録フォーム）

#### ✅ 正常系テスト

```python
import pytest
from festival.forms import EventDayPerformanceForm
from festival.models import Event, Artist, EventDay

@pytest.mark.django_db
def test_event_day_performance_form_valid():
    event = Event.objects.create(
        name="Test Fest",
        description="テストイベント",
        start_date="2025-12-01",
        end_date="2025-12-01",
        event_type="FES"
    )
    EventDay.objects.create(event=event, date="2025-12-01", venue="代々木公園")
    artist1 = Artist.objects.create(name="YOASOBI", spotify_id="abc123")
    artist2 = Artist.objects.create(name="Aimer", spotify_id="def456")

    form_data = {
        "event": event.id,
        "date": "2025-12-01",
        "venue": "代々木公園",
        "artists": [artist1.id, artist2.id],
    }

    form = EventDayPerformanceForm(data=form_data)
    form.fields["date"].choices = [("2025-12-01", "2025-12-01")]  # JSの代替

    assert form.is_valid()
```

---

### ✅ 実行コマンド

```bash
pytest festival/tests/test_forms.py
```

---

`BulkArtistForm` に対するテストを作成して、**カンマ区切りのアーティスト名入力が正しく処理されるか**を確認しましょう ✅

---

## 🧪 `BulkArtistForm` のテスト例（test_forms.py）

```python
import pytest
from festival.forms import BulkArtistForm

def test_bulk_artist_form_valid():
    form_data = {
        "names": "YOASOBI, Aimer, King Gnu"
    }
    form = BulkArtistForm(data=form_data)
    assert form.is_valid()
    assert form.cleaned_data["names"] == "YOASOBI, Aimer, King Gnu"
```

---

### ❌ 異常系テスト（空欄）

```python
def test_bulk_artist_form_invalid_empty():
    form_data = {
        "names": ""
    }
    form = BulkArtistForm(data=form_data)
    assert not form.is_valid()
    assert "names" in form.errors
```

---

### ✅ 補足：このフォームの役割

- `CharField` + `Textarea` によって、複数のアーティスト名をカンマ区切りで入力
- バリデーションは Django の標準機能に依存（空欄チェックなど）
- 実際の処理は `views.bulk_artist_register` 側で `split(',')` などを使って分割しているはず

---

## ✅ テスト実行

```bash
pytest festival/tests/test_forms.py
```

ここでは、**代表的なビューに対するテストコードの強化例**をいくつかご紹介します ✅

---

## 🧪 ビューテスト強化：`test_views.py`

以下のように、正常系・異常系を含めてテストを追加していきましょう。

---

### ✅ 1. トップページ（`index`）

```python
from django.urls import reverse
import pytest

def test_index_view(client):
    url = reverse("festival:index")
    response = client.get(url)
    assert response.status_code == 200
    assert "text/html" in response["Content-Type"]
```

---

### ✅ 2. アーティスト一覧（`artist_list`）

```python
from festival.models import Artist

@pytest.mark.django_db
def test_artist_list_view_with_query(client):
    Artist.objects.create(name="YOASOBI", spotify_id="abc123")
    Artist.objects.create(name="Aimer", spotify_id="def456")

    url = reverse("festival:artist_list") + "?q=YOA"
    response = client.get(url)
    assert response.status_code == 200
    assert "YOASOBI" in response.content.decode()
    assert "Aimer" not in response.content.decode()
```

---

### ✅ 3. アーティスト詳細（`artist_detail`）

```python
@pytest.mark.django_db
def test_artist_detail_view(client):
    artist = Artist.objects.create(name="King Gnu", spotify_id="xyz789")
    url = reverse("festival:artist_detail", args=[artist.id])
    response = client.get(url)
    assert response.status_code == 200
    assert "King Gnu" in response.content.decode()
```

---

### ✅ 4. イベント一覧（`event_list`）

```python
from festival.models import Event

@pytest.mark.django_db
def test_event_list_view(client):
    Event.objects.create(
        name="Test Fest",
        description="説明",
        start_date="2025-12-01",
        end_date="2025-12-02",
        event_type="FES"
    )
    url = reverse("festival:event_list")
    response = client.get(url)
    assert response.status_code == 200
    assert "Test Fest" in response.content.decode()
```

---

### ✅ 5. イベント詳細（`event_detail`）

```python
from festival.models import EventDay, Performance

@pytest.mark.django_db
def test_event_detail_view(client):
    event = Event.objects.create(
        name="Winter Sonic",
        description="冬フェス",
        start_date="2025-12-10",
        end_date="2025-12-10",
        event_type="FES"
    )
    day = EventDay.objects.create(event=event, date="2025-12-10", venue="幕張メッセ")
    artist = Artist.objects.create(name="Aimer", spotify_id="def456")
    Performance.objects.create(event_day=day, artist=artist, is_confirmed=True)

    url = reverse("festival:event_detail", args=[event.id])
    response = client.get(url)
    assert response.status_code == 200
    assert "Aimer" in response.content.decode()
```

---

## ✅ テスト実行

```bash
pytest festival/tests/test_views.py
```

---

ビューのGET系テストが整ったので、次は**POST処理を含むビューのテスト**に進みましょう。特に以下の2つがおすすめです：

---

## 🧪 1. `bulk_artist_register` のPOSTテスト

このビューでは、フォーム送信によってSpotify API連携でアーティストを登録します。テストではSpotify連携をモック化して、登録処理の流れを確認します。

### ✅ テスト例（`test_views.py`）

```python
import pytest
from django.urls import reverse
from unittest.mock import patch
from festival.models import Artist

@patch("festival.views.save_artist_from_spotify")
@pytest.mark.django_db
def test_bulk_artist_register_post(mock_save, client):
    def mock_save_artist(name):
        return Artist.objects.create(name=name, spotify_id="64tJ2EAv1R6UaZqc4iOCyj")

    mock_save.side_effect = mock_save_artist

    url = reverse("festival:bulk_artist_register")
    data = {"names": "YOASOBI"}
    response = client.post(url, data)

    print(response.content.decode())  # デバッグ用

    assert response.status_code == 200
    assert Artist.objects.filter(name="YOASOBI").exists()
    assert "1 件登録" in response.content.decode()
```

---

## 🧪 2. `register_event_day_and_performances` のPOSTテスト

このビューでは、イベント日・会場・出演者を登録します。日付選択肢はJSで生成されるため、テストでは手動で設定します。

### ✅ テスト例（`test_views.py`）

```python
from festival.models import Event, Artist

@pytest.mark.django_db
def test_register_event_day_post(client):
    event = Event.objects.create(
        name="Test Fest",
        description="テスト",
        start_date="2025-12-01",
        end_date="2025-12-01",
        event_type="FES"
    )
    artist = Artist.objects.create(name="Aimer", spotify_id="def456")

    url = reverse("festival:register_event_day")
    data = {
        "event": event.id,
        "date": "2025-12-01",
        "venue": "幕張メッセ",
        "artists": [artist.id],
    }

    # 日付選択肢をフォームに設定するためにGETで一度取得
    client.get(url + f"?event_id={event.id}")

    response = client.post(url + f"?event_id={event.id}", data)
    assert response.status_code == 200
    assert "1 組の出演者を登録しました" in response.content.decode()
```

---

## ✅ テスト実行

```bash
pytest festival/tests/test_views.py
```

---

テストカバレッジを確認するには、Python のテストツール **pytest** と一緒に **coverage.py** を使うのが一般的です。以下の手順で確認できます：

---

## ✅ テストカバレッジ確認手順

### 1. 📦 coverage パッケージをインストール

まだインストールしていない場合は、以下のコマンドでインストールします：

```bash
pip install coverage
```

---

### 2. 🧪 coverage を使ってテストを実行

プロジェクトのルートディレクトリで以下を実行します：

```bash
coverage run -m pytest
```

これで、通常の `pytest` 実行と同時にカバレッジ情報が収集されます。

---

### 3. 📊 カバレッジレポートを表示

ターミナル上で簡易レポートを表示するには：

```bash
coverage report
```

より詳細な HTML レポートを生成するには：

```bash
coverage html
```

その後、`htmlcov/index.html` をブラウザで開くと、**ファイルごとのカバレッジ状況が色付きで確認できます**。

---

## 🛠 よく使うオプション

| コマンド | 説明 |
|----------|------|
| `coverage erase` | 以前のカバレッジデータを削除 |
| `coverage run -m pytest` | カバレッジを計測しながらテスト実行 |
| `coverage report -m` | 行ごとのカバレッジを表示（未実行の行も） |
| `coverage html` | HTMLレポートを生成（`htmlcov/` に出力） |

---

## 💡 Django プロジェクトでの注意点

Django プロジェクトでは、特定のアプリだけを対象にすることもできます：

```bash
coverage run --source='festival' manage.py test
```

---

## ✅ まとめ

1. `coverage` をインストール  
2. `coverage run -m pytest` でテスト実行  
3. `coverage report` または `coverage html` で結果確認  

---
