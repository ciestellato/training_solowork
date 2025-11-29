# 🎧 プレイリスト生成特化型アプリ「Blast!!!」

## 🚀 コンセプト

音楽フェスの予習から、アーティスト個別の“推し掘り”まで。
Spotify API をフル活用して、**欲しいプレイリストを一瞬で生成する**アプリ。

このアプリは2つの柱で成り立っています：

### 1. **フェス予習プレイリスト生成**

* フェス → 日付 → 出演アーティスト選択、と進むだけ
* 代表曲を1〜9曲ずつ自動取得
* 本番に向けて効率よく予習ができるよう最適化

### 2. **アーティスト個別プレイリスト生成**

* 「代表曲モード」：Spotify の人気順トップ曲を使用
* 「砂金モード」：人気度の低い“隠れ名曲”だけを抽出してプレイリスト化

  * マイナー曲掘り・活動支援の再生リストにも最適

---

## 🧩 機能概要

### 🎪 フェス予習プレイリスト

* イベント → 日付 → 出演アーティストの流れでプレイリスト作成
* チェックしたアーティストの代表曲のみで構成
* Spotify へそのまま保存できる

### 🎵 アーティストプレイリスト

アーティストページで次のどちらかを選ぶ：

#### ✔ 代表曲プレイリスト

* `GET /artists/{id}/top-tracks` から取得
* フェス予習と同じテイストの“ハズさないセット”

#### ✔ 砂金モード（Deep Cuts Only）

* アーティストの全曲を取得
* 人気度スコアの低い曲を抽出
* “隠れた名曲だけの裏ベスト”を作れる

### 🔐 Spotify 連携

* OAuth 2.0 による認証
* トークンリフレッシュ完全自動化
* プレイリスト保存後は自動リダイレクト

---

## 🛠 技術構成

| 項目      | 技術                                 |
| ------- | ---------------------------------- |
| フレームワーク | Django                             |
| 言語      | Python, HTML, CSS, JavaScript      |
| DB      | SQLite（Django ORM）                 |
| 外部API   | Spotify Web API                    |
| 認証      | OAuth 2.0（Authorization Code Flow） |
| その他     | .env + python-dotenv / GitHub 管理   |

---

## 🗂 モデル構成（主要）

| モデル           | 役割                      |
| ------------- | ----------------------- |
| `Event`       | フェスやツアー本体               |
| `EventDay`    | 日付＋会場                   |
| `Artist`      | アーティスト情報（Spotify ID 保持） |
| `Performance` | 出演情報（フェス予習に使用）          |

---

## 🧱 ディレクトリ構成（主要）

```plaintext
conf/
├── settings.py
├── urls.py

blast/
├── models.py
├── admin.py
├── urls.py
├── templates/
│   ├── base.html
│   ├── artist_list.html
│   ├── artist_detail.html
│   ├── event_list_base.html
│   ├── event_list_upcoming.html
│   ├── event_list_history.html
│   ├── event_detail.html
│   ├── playlist_create.html
├── views/
│   ├── artist_views.py
│   ├── event_views.py
│   ├── performance_views.py
│   ├── playlist_views.py
│   └── spotify_auth_views.py
├── forms.py
├── utils/
│   ├── spotify_utils.py
│   ├── artist_utils.py
│   └── text_utils.py

.env
```

---

## 🚧 進捗状況

| 機能               | 状況                       |
| ---------------- | ------------------------ |
| Spotify 認証       | ✅ 完了                     |
| フェス予習プレイリスト生成    | ✅ 完了                     |
| 代表曲プレイリスト        | ✅ 完了                     |
| 砂金モード（Deep Cuts） | ⏳ 実装中 |
| プレイリストSpotify保存  | ✅ 完了                     |
| APIユーティリティ整理     | ✅ 完了                     |
| タイムテーブル廃止        | ✅ 完了                     |

---

## ⚙️ セットアップ

```bash
# 仮想環境の作成と起動
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 必要パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
touch .env
# .env に以下を記述
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret

# マイグレーションと起動
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

## 📌 今後の予定

| 機能       | 内容                 |
| -------- | ------------------ |
| UI改善     | アーティスト検索UX強化など     |
| 砂金フィルタ   | 人気度・年別・アルバム別の絞り込み  |
| プレイリスト共有 | ユーザー同士でURL共有できる仕組み |

---
