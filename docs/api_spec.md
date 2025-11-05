# 🎧 API仕様書（api_spec.md）

## 🧭 概要

このドキュメントは、Spotify Web API を用いたアーティスト情報取得・予測ロジックの実装に関する仕様をまとめたものです。主に `spotify.py` にて使用される処理を対象とします。

---

## 🔐 認証方式

| 項目 | 内容 |
|------|------|
| 認証方式 | Client Credentials Flow |
| 認証URL | `https://accounts.spotify.com/api/token` |
| 必要情報 | `Client ID`, `Client Secret`（`.env` に保存） |
| トークン取得方法 | `POST` リクエスト（`grant_type=client_credentials`） |
| トークン有効期限 | 約1時間（3600秒） |

---

## 📡 使用エンドポイント一覧

### 1. アーティスト検索

| 項目 | 内容 |
|------|------|
| URL | `https://api.spotify.com/v1/search` |
| メソッド | `GET` |
| パラメータ | `q=アーティスト名`, `type=artist`, `limit=1` |
| 認証 | Bearerトークン |
| 主なレスポンス項目 | `id`, `name`, `genres`, `popularity`, `images`, `followers.total` |

**使用例**：  
```python
search_artist("YOASOBI")
```

---

### 2. 類似アーティスト取得（予測ロジック用）

| 項目 | 内容 |
|------|------|
| URL | `https://api.spotify.com/v1/artists/{id}/related-artists` |
| メソッド | `GET` |
| 認証 | Bearerトークン |
| 主なレスポンス項目 | `artists`（類似アーティストの配列） |
| 備考 | 類似度スコアは明示されないが、順序は関連性順 |

**使用例**：  
```python
get_related_artists("アーティストID")
```

---

### 3. トラック取得（プレイリスト作成用・予定）

| 項目 | 内容 |
|------|------|
| URL | `https://api.spotify.com/v1/artists/{id}/top-tracks` |
| メソッド | `GET` |
| パラメータ | `market=JP`（国指定） |
| 認証 | Bearerトークン |
| 主なレスポンス項目 | `tracks`（人気トラック一覧） |

---

## 🧪 実装済み関数（spotify.py）

| 関数名 | 概要 |
|--------|------|
| `get_token()` | Client Credentials Flow によるアクセストークン取得 |
| `search_artist(name)` | アーティスト名でSpotify検索し、基本情報を取得 |
| `save_artist_from_spotify(name)` | アーティスト情報をモデルに保存（重複チェックあり） |
| `get_related_artists(artist_id)` | 類似アーティスト一覧を取得（予測ロジック用） |

---

## 📌 備考

- APIの利用にはレート制限があります（通常1秒あたり数リクエストまで）。
- トークンの有効期限切れに備えて、再取得処理を組み込むことを推奨。
- 今後、プレイリスト作成やイベント予測に応じてエンドポイント追加予定。

---
