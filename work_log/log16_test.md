テストの進め方としては、以下のようなステップで整理すると効率的かつ網羅的に進められます ✅

---

## 🧪 テストの進め方

### ① テスト方針の確認
- **目的を明確に**：今回のテストは「UI改善後の動作確認」「Spotify連携の安定性」「絞り込み・履歴表示の正確性」が主眼。
- **対象範囲を定義**：以下の機能を重点的に確認。
  - プレイリスト作成・保存
  - アーティスト頭文字絞り込み
  - 出演履歴と今後の予定の分離表示

---

### ② テストファイルごとの役割と進め方

| ファイル名 | テスト対象 | 進め方 |
|------------|------------|--------|
| `test_forms.py` | 入力フォームのバリデーション | - アーティスト登録・イベント登録フォームの必須項目・形式チェック<br>- 無効な入力（空欄・不正な日付など）でエラーが出るか |
| `test_models.py` | モデルの保存・関連性 | - `EventDay`と`Stage`の関連付け<br>- `Performance`のステージ・時間の整合性<br>- Spotify連携用フィールドの保存確認 |
| `test_spotify.py` | Spotify API連携 | - トークン取得・リフレッシュの動作<br>- 代表曲取得の成功・失敗ケース<br>- プレイリスト保存時の上限エラー処理 |
| `test_views.py` | 各画面の表示・遷移 | - アーティスト一覧の絞り込み（濁音含む）<br>- 詳細ページの履歴分離表示<br>- プレイリスト作成画面のUI要素（選択数表示など） |

---

### ③ 手動テストの併用（UI・Spotify連携）

- **UI改善の確認**（11/17対応分）
  - 検索バーが機能しているか
  - 選択補助が正しく動作するか
  - 選択数表示がリアルタイムで更新されるか

- **Spotify連携の確認**
  - トークン期限切れ時に再認証されるか
  - プレイリスト保存後に正しくリダイレクトされるか
  - 保存上限に達した場合の警告表示

---

### ④ バグ・修正の記録

- 発見したバグは `issues/` や `CHANGELOG.md` に記録
- 修正後は再テストして、**修正が副作用を起こしていないか**確認

---

### ⑤ カバレッジ確認（任意）

- `coverage.py` や `pytest-cov` を使って、テストの網羅率を確認
- 特に `playlist_views.py` や `text_utils.py` はロジックが多いため、重点的にカバー

---

このエラーは、`tests` モジュールのインポートパスが Django のテストランナーにとって不正確であるために発生しています。特に `tests` フォルダが Django アプリケーションのルートに正しく配置されていない、または `manage.py test` の引数が誤っている可能性があります。

---

## ✅ 解決ステップ

### ① `tests` フォルダの配置確認

- `tests` フォルダは Django アプリ（例：`festival`）の中にある必要があります。
  ```
  solowork/
  ├── manage.py
  ├── festival/
  │   ├── __init__.py
  │   ├── models.py
  │   ├── views.py
  │   ├── tests/
  │   │   ├── __init__.py
  │   │   ├── test_forms.py
  │   │   ├── test_models.py
  │   │   ├── test_spotify.py
  │   │   └── test_views.py
  ```

- `tests` フォルダが `festival` アプリの外にある場合、Django はそれを正しく認識できません。

---

### ② テスト実行コマンドの修正

以下のように、**アプリ名を指定して**テストを実行してください：

```bash
coverage run manage.py test festival
```

これで Django は `festival/tests/` 以下のテストを正しく認識します。

---

### ③ coverage レポートの確認

テストが通ったら、以下でカバレッジを確認できます：

```bash
coverage report
coverage html
```

---

## 🔍 補足：__init__.py の役割

- `tests/__init__.py` を追加したのは正解です。
- Python にそのフォルダを「パッケージ」として認識させるために必要です。
- ただし、配置場所が正しくないと `__init__.py` があってもエラーになります。

---

## ✅ まとめ

| ステップ | 内容 |
|---------|------|
| 1 | `tests` フォルダが Django アプリ内にあるか確認 |
| 2 | `__init__.py` を `tests/` に追加 |
| 3 | `coverage run manage.py test festival` で実行 |
| 4 | `coverage report` / `coverage html` で確認 |

---
管理者（`is_staff=True`）でログインした状態で `pytest` を使って Django のビューをテストするには、以下のような手順で進めるのがベストです ✅

---

## ✅ 1. `pytest-django` をインストール

まず `pytest-django` がインストールされていることを確認します：

```bash
pip install pytest pytest-django
```

---

## ✅ 2. `pytest.ini` をプロジェクトルートに作成

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = conf.settings
python_files = tests.py test_*.py *_tests.py
```

---

## ✅ 3. 管理者ユーザーを作成してログイン

`pytest` でも Django の `Client()` を使ってログインできます。以下は `conftest.py` に書くと便利です：

```python
# conftest.py
import pytest
from django.contrib.auth.models import User
from django.test import Client

@pytest.fixture
def staff_client(db):
    user = User.objects.create_user(username='admin', password='pass', is_staff=True)
    client = Client()
    client.login(username='admin', password='pass')
    return client
```

---

## ✅ 4. テスト関数で `staff_client` を使う

```python
def test_register_event_day_get(staff_client, event):
    url = reverse("festival:register_event_day") + f"?event_id={event.id}"
    response = staff_client.get(url)
    assert response.status_code == 200
    assert "イベント" in response.content.decode()
```

---

## ✅ 5. モデル用フィクスチャも定義可能

```python
@pytest.fixture
def event(db):
    from festival.models import Event
    return Event.objects.create(
        name="Test Event",
        start_date="2025-11-18",
        end_date="2025-11-20",
        event_type="FES"
    )
```

---

## ✅ 実行コマンド

```bash
pytest festival/tests/
```

---

これで `@staff_member_required` が付いたビューも `pytest` で安全にテストできます！  
必要なら `conftest.py` のテンプレートや、複数モデルのフィクスチャも一緒に整えますよ。次はどこを進めましょう？
