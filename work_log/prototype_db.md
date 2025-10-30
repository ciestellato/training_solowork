## 🧱 仮DB設計の進め方

### ① 必要なデータを洗い出す
まずはアプリで扱う「もの（エンティティ）」を整理しましょう。今回のプロジェクトでは以下が中心です：

- **イベント（フェス）**
- **アーティスト**
- **出演情報（どのイベントに誰が出るか）**
- **Spotifyから取得するデータ**
- **管理者による手動登録・修正情報**

### ② 各エンティティの項目（カラム）を考える

#### 🎪 イベント（Festival/Event）
- `id`: イベントID（主キー）
- `name`: イベント名
- `location`: 開催地
- `start_date`: 開始日
- `end_date`: 終了日
- `description`: 説明文

#### 🎤 アーティスト（Artist）
- `id`: アーティストID（主キー）
- `name`: 名前
- `popularity`: 人気度（Spotify APIから取得）
- `genres`: ジャンル（複数可）
- `spotify_id`: Spotify上のID

#### 📅 出演情報（Performance）
- `id`: 出演ID（主キー）
- `event_id`: イベントID（外部キー）
- `artist_id`: アーティストID（外部キー）
- `performance_date`: 出演日
- `is_confirmed`: 出演確定かどうか（True/False）

#### 🧠 類似アーティスト（RelatedArtist）
- `id`: 関係ID（主キー）
- `artist_id`: 元のアーティストID
- `related_artist_id`: 類似アーティストID
- `similarity_score`: 類似度（数値）

#### 🛠️ 管理者登録（ManualEntry）
- `id`: 登録ID
- `event_id`: イベントID
- `artist_id`: アーティストID
- `notes`: 備考・修正メモ

### ③ 関係性（リレーション）を整理
- アーティストは複数のイベントに出演可能（多対多）
- イベントは複数のアーティストを持つ（多対多）
- 類似アーティストはアーティスト同士の関係（自己参照）

---

## ✅ 次にやること

1. 上記の項目をもとに **ER図（Entity Relationship Diagram）** を紙やツールで描いてみる  
2. Djangoのモデルクラスに落とし込む準備をする（まだコードにしなくてOK）
3. Spotify APIで取得できるデータ形式を確認して、必要な項目を調整する

---

図にしてみたい場合は、Lucidchart、draw.io、DBDiagram.io などの無料ツールが便利です。希望があれば、ER図の例も作成できますよ！どうしますか？

画像生成の上限に達しているため、今回は画像としてのER図を作成できませんが、代わりに**テキストベースのER図構造**を以下に示します。これをもとに、後で図に起こすことも可能です。

---

## 🧩 仮ER図（テキスト構造）

### 🎪 Event（イベント）
- `id` (PK)
- `name`
- `location`
- `start_date`
- `end_date`
- `description`

### 🎤 Artist（アーティスト）
- `id` (PK)
- `name`
- `popularity`
- `genres`
- `spotify_id`

### 📅 Performance（出演情報）
- `id` (PK)
- `event_id` (FK → Event.id)
- `artist_id` (FK → Artist.id)
- `performance_date`
- `is_confirmed`

### 🧠 RelatedArtist（類似アーティスト）
- `id` (PK)
- `artist_id` (FK → Artist.id)
- `related_artist_id` (FK → Artist.id)
- `similarity_score`

### 🛠️ ManualEntry（手動登録）
- `id` (PK)
- `event_id` (FK → Event.id)
- `artist_id` (FK → Artist.id)
- `notes`

---

## 🔗 リレーション概要

- **Event ⇄ Artist**：多対多（中間テーブル：Performance）
- **Artist ⇄ Artist**：自己参照（RelatedArtist）
- **ManualEntry**：管理者による補足情報（EventとArtistを結ぶ）

---

この構造をもとに、draw.io や dbdiagram.io などで図にすることができます。もし図に起こしたい場合は、ER図用のコード（dbdiagram形式など）も提供できますよ。どうしますか？
こちらが **dbdiagram.io** などで使える仮DB設計のコード形式（DBML）です。これをそのまま貼り付ければ、ER図が自動生成されます。

---

```dbml
Table Event {
  id int [pk, increment]
  name varchar
  location varchar
  start_date date
  end_date date
  description text
}

Table Artist {
  id int [pk, increment]
  name varchar
  popularity int
  genres varchar
  spotify_id varchar
}

Table Performance {
  id int [pk, increment]
  event_id int [ref: > Event.id]
  artist_id int [ref: > Artist.id]
  performance_date date
  is_confirmed boolean
}

Table RelatedArtist {
  id int [pk, increment]
  artist_id int [ref: > Artist.id]
  related_artist_id int [ref: > Artist.id]
  similarity_score float
}

Table ManualEntry {
  id int [pk, increment]
  event_id int [ref: > Event.id]
  artist_id int [ref: > Artist.id]
  notes text
}
```

---

この形式は、**dbdiagram.io** に貼り付けるだけで視覚的なER図が表示されます。さらに拡張したい場合は、`created_at` や `updated_at` などのタイムスタンプを追加することもできます。

他の形式（PlantUML, Mermaid, SQLなど）が必要であれば、すぐに変換できますよ！
