# 🎧 Festival Forecast — 音楽フェス出演予測アプリ

## 🧭 プロジェクト概要

**目的**  
音楽フェスティバルの出演アーティスト情報を管理・予測するWebアプリケーションを構築し、ユーザーと管理者が情報を閲覧・登録・検索できる環境を提供します。

**主な機能**  
- イベント・アーティスト情報の管理（一覧・詳細・検索）
- Spotify APIからアーティスト情報取得・保存
- 類似アーティスト・出演予測ロジック（予定）
- 管理画面による手動登録・修正
- プレイリスト作成機能（予定）

---

## 🛠 技術構成

| 項目 | 使用技術 |
|------|----------|
| フレームワーク | Django |
| 言語 | Python, HTML, CSS, JavaScript |
| データベース | SQLite（Django ORM） |
| 外部API | Spotify Web API（Client Credentials Flow） |
| バージョン管理 | GitHub |
| 環境管理 | `.env` + `python-dotenv` |

---

## ⚙️ セットアップ手順

```bash
# 仮想環境の作成と起動
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 必要パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
touch .env
# .env に以下を記述
# SPOTIFY_CLIENT_ID=your_client_id
# SPOTIFY_CLIENT_SECRET=your_client_secret

# マイグレーションと起動
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

## 🗂️ 機能概要

### 🎵 アーティスト管理
- 一覧表示（ListView）
- 詳細表示（DetailView）
- 検索機能（クエリパラメータ or フォーム）
- Spotify API連携による一括登録

### 📅 イベント管理
- 一覧表示（開催日順）
- 詳細表示（出演者・会場・日程）
- 管理者向け登録フォーム（JSによる日付選択）

### 🔍 予測ロジック（予定）
- 類似アーティストの取得（Spotify `/related-artists`）
- 出演可能イベントの予測

---

## 📁 ディレクトリ構成（主要部分）

```
conf/
├── settings.py
├── urls.py
festival/
├── models.py
├── admin.py
├── views.py
├── spotify.py        # Spotify API連携処理
├── templates/
│   ├── artist_list.html
│   ├── artist_detail.html
│   ├── event_list.html
│   ├── event_detail.html
│   └── register_event_day.html
.env                   # APIキー管理
```

---

## 🧪 テスト・デバッグ

- Djangoのテストフレームワークを使用予定
- 管理画面・API連携・検索機能の動作確認済み
- UI調整・Bootstrap導入は今後の課題

---

## 📌 今後の予定

- 類似アーティスト予測ロジックの実装
- プレイリスト作成機能の追加
- UI改善（Bootstrap導入、検索結果の表示調整）
- READMEの英語版作成（必要に応じて）
