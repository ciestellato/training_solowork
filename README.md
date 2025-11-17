# 🎧 音楽フェス予習プレイリスト作成＆タイムテーブル管理アプリ「Blast!!!」

## 🎯 目的

- 音楽フェスティバルやライブイベントの**タイムテーブルを視覚的に管理・表示**できるWebアプリケーションを構築する  
- 管理者が出演者情報やステージ構成を柔軟に編集でき、ユーザーが見やすくイベント全体を把握できるUIを提供する  
- Spotify連携により、**出演アーティストの代表曲を使った予習プレイリストを自動生成・保存**できる  
- ステージカラーや並び順など、イベントごとの個性を反映できる**カスタマイズ性の高い設計**を目指す

---

## 🧩 構成

### モデル設計（Django ORM）

| モデル名     | 役割 |
|--------------|------|
| `Event`      | イベント全体（フェス、ツアーなど） |
| `EventDay`   | 公演日＋会場 |
| `Stage`      | ステージ情報（並び順・カラー付き） |
| `Artist`     | アーティスト情報（Spotify連携あり） |
| `Performance`| 出演情報（ステージ・時間帯） |

- `Stage` モデルに `order`（並び順）と `color_code`（カラーコード）を追加
- `Artist` モデルは Spotify ID を保持し、API連携で代表曲を取得可能
- `EventDay` 経由でプレイリスト作成対象を固定できる設計

### テンプレート構成

- `base.html`: 共通レイアウト（ナビバー、CSS・JS読み込みブロックあり）
- `timetable_view.html`: タイムテーブル表示ページ（ステージごとの色分け、時間スロット制御）
- `playlist_create.html`: 出演アーティスト選択＋Spotify連携プレイリスト作成画面

### スタイル（CSS）

- スロット間の余白をなくし、出演者のブロックをひとかたまりに見せる
- ステージ間には区切り線を表示
- 出演者が複数スロットにまたがる場合は、最初のスロットのみ表示し、以降は背景色のみ
- ステージカラーは `Stage.color_code` に基づいて反映

---

## 🚧 進捗

| 項目 | 状況 |
|------|------|
| モデル設計 | ✅ 完了（Stage拡張・Spotify対応含む） |
| 管理画面対応 | ✅ 完了（並び順・カラー編集可能） |
| タイムテーブル表示 | ✅ 完了（時間・ステージごとの表示制御） |
| CSS調整 | ✅ 完了（余白・高さ・色分け対応） |
| スロット統合表示 | ✅ 完了（rowspan未使用） |
| ステージカラー反映 | ✅ 完了（ステージ名＋出演スロット） |
| Spotify認証 | ✅ 完了（OAuth2.0＋トークン管理） |
| プレイリスト作成 | ✅ 完了（イベント日程固定＋代表曲取得） |
| Spotify保存 | ✅ 完了（トークンリフレッシュ＋保存後リダイレクト） |

---

## 📝 成果物

### 🎧 プレイリスト作成機能
- イベント詳細ページからプレイリスト作成画面へ遷移
- 出演アーティストをチェックボックスで選択
- Spotify APIから代表曲を取得し、画面に表示
- 「Spotifyに保存する」ボタンでプレイリストをユーザーのSpotifyアカウントに保存
- トークンの期限切れにも自動対応（リフレッシュ処理）

### 🕒 タイムテーブル管理機能
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
│   ├── base.html
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
│   ├── base_views.py
│   ├── artist_views.py
│   ├── event_views.py
│   ├── performance_views.py
│   ├── playlist_views.py
│   └── spotify_auth_views.py
├── forms.py
├── utils/
│   ├── text_utils.py
│   └── spotify_utils.py

.env  # APIキー管理
```

---

## ⚙️ セットアップ手順

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
python manage.py runserver 8888
```

---

## 📌 今後の予定

| 機能 | 内容 |
|------|------|
| UI改善 | Bootstrap強化・検索結果の表示調整 |
| 履歴 | 出演者ごとの出演履歴表示 |

---
