# 🎧 (名称未定) — 音楽フェス予習プレイリスト作成アプリ

## 🧭 プロジェクト概要

**目的**  
音楽フェスティバルの出演アーティスト情報を管理するWebアプリケーションを構築し、ユーザーと管理者が情報を閲覧・登録・検索できる環境を提供します。

**主な機能**  
- イベント・アーティスト情報の管理（一覧・詳細・検索）
- Spotify APIからアーティスト情報取得・保存
<!-- - 類似アーティスト・出演予測ロジック（Spotify API仕様変更により頓挫） -->
- 管理画面による手動登録・修正
- 予習用プレイリスト作成機能
- タイムテーブル登録・表示・編集機能（2025/11/13追加）

---

## 🛠 技術構成

| 項目         | 使用技術                          |
|--------------|-----------------------------------|
| フレームワーク | Django                            |
| 言語         | Python, HTML, CSS, JavaScript     |
| データベース | SQLite（Django ORM）              |
| 外部API      | Spotify Web API（Client Credentials Flow） |
| バージョン管理 | GitHub                            |
| 環境管理     | `.env` + `python-dotenv`          |

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

### 🎧 プレイリスト作成機能
- イベント日程と出演アーティストを選択
- Spotify APIから代表曲を取得
- プレイリストとして画面表示（曲名・アーティスト名・Spotifyリンク）
- Spotify連携によるプレイリスト保存機能

### 🕒 タイムテーブル管理機能（2025/11/13追加）
- 出演アーティスト・ステージ・時間の登録（未登録アーティストのみ表示）
- ステージの選択または新規作成に対応
- 開始・終了時間のバリデーション（開始 < 終了）
- タイムテーブル表示（ステージごと・日程ごとに分離）
- 同イベント内の日程切り替えリンクを表示
- 編集画面からステージ・時間の修正が可能

---

## 📁 ディレクトリ構成（主要部分）

```plaintext
conf/
├── settings.py
├── urls.py

festival/
├── models.py
├── admin.py
├── urls.py
├── templates/
│   ├── artist_list.html
│   ├── artist_detail.html
│   ├── event_list.html
│   ├── event_detail.html
│   ├── playlist_create.html
│   ├── register_event_day.html
│   ├── timetable_register.html
│   ├── timetable_view.html
│   └── edit_performance.html
├── views/
│   ├── artist_views.py
│   ├── event_views.py
│   ├── base_views.py
│   ├── performance_views.py
│   └── playlist_views.py
├── forms.py
├── utils/
│   ├── text_utils.py
│   └── spotify_utils.py

.env  # APIキー管理
```

---

## 🧪 テスト・デバッグ

- Djangoのテストフレームワークを使用予定
- 管理画面・API連携・検索機能の動作確認済み
- プレイリスト作成機能の動作確認済み
- タイムテーブル登録・表示・編集機能の動作確認済み
- UI調整・Bootstrap導入は今後の課題

---

## 📌 今後の予定

<!-- - 類似アーティスト予測ロジックの実装 -->
- ユーザー認証・お気に入りアーティスト保存機能
- UI改善（Bootstrap強化、検索結果の表示調整）
- タイムテーブルPDF出力機能
- 出演者ごとの出演履歴表示
