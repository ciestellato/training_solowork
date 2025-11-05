# 個人開発を始めよう

## 個人開発の流れ

1. 企画出し（参考例）
   1. 自分が使えるスキルを洗い出す
   2. 開発期間・上記スキルを伝えてAIに考えてもらう
2. アプリの機能を箇条書きにする
   - 〇〇情報一覧表示
   - 〇〇データの登録・修正・削除
   - 画像のアップロード登録
   - Excelファイルのアップロード登録
   - etc
3. アプリの画面遷移イメージを作る
   - ネットの画像検索で自分のイメージに近いものをスクリーンショットを撮り、ワードやエクセル、パワーポイントなどに貼り付ける
   - AIにアプリの機能を伝え、HTMLでサンプル画面を生成してもらいイメージを固める
4. アプリが扱うデータ項目を明確にする
   - 例：ログインシステムならば
     - ユーザー名
     - パスワード

## GitHubでのバージョン管理

参考：[【GitHub】ローカルリポジトリを新しいリポジトリにプッシュする方法](https://qiita.com/EasyCoder/items/354e5db2e1af8a4f2c7d)

1. Gitのサイト上で新規リポジトリを作成する
2. ローカルリポジトリを設定する
   1. 新規フォルダ作成
   2. 1のフォルダをVSCodeのターミナルで開く
   3. 各コマンド(後述)を実行する

### Gitコマンド

#### ローカルリポジトリを設定、プッシュする

##### ローカルマシン上でGitの初期化

```
git init //カレントディレクトリをgitの対象として初期化する
```

##### ファイルをステージングする

```
git add . // 変更されたすべてのファイルをステージング
```

##### ステージングしたファイルをコミットする

```
git commit -m "コミットメッセージ" //変更履歴を保存する
```

#### ローカルリポジトリを操作する

##### gitの履歴を確認する

```
git log // コミットした履歴を確認する
```

#### GitHubと連携する

##### GitHubのリポジトリと連携する

```
git remote add origin GitHubのリポジトリURL 
```

##### GitHubにプッシュする

```
git push -u origin main
// git push -u origin ブランチ名
```

##### ブランチ名の変更(master → main)

```
git branch -M main
git push -u origin main
```

### 感想

- 何も見ないで新規リポジトリとローカルリポジトリを接続することはできないが、手順を参照すればスムーズに進めるようになった
- 参考URLに従い初回コミットを実行しようとしたが、ファイルが何もなかったため失敗した（そのため作業メモをつけることにした）
- ブランチ名がmasterになっていたため、mainに変更してプッシュした

## アイデア出し

### やりたいこと

フェスの出演予想

### 実装したい機能

- 音楽イベント一覧表示
- 出演者一覧表示
- 未発表出演者予想一覧表示
- データの取り込み機能（SpotifyAPIを利用）
  - アーティスト名
  - スケジュール
  - （できれば）似ているアーティスト
- アーティスト一覧表示
- 出演可能イベント予想機能
- 取り込みデータの精査・修正
  - フェスの各日への振り分け（手動による登録）
- イベント予習用プレイリスト作成

### 画面遷移イメージ

- ホームページ(近日開催のイベント一覧 or フェス一覧)
- 管理者ページ
  - データの取り込み
  - 登録・修正
- イベント一覧（デフォルトは今日以降）
  - イベント検索
  - イベント詳細ページ
- アーティスト一覧（人気度順？50音順？）
  - アーティスト検索
  - アーティスト詳細ページ
- カレンダー機能
- マップ機能

### 感想

- とりあえずやりたいことを列挙しておいて、シンプルな機能から実装していこう。
- アイデア出しはたのしいね

## スケジュール

### 相談用プロンプト

以下のプロジェクトのスケジュールを組んで表形式で出力ください。
全てを実装しなくて構いません。基本的な機能から作成していって複雑な処理は時間の余裕があれば実装するつもりです。
スケジュールに以下のことを明記してください。

- 日付
- やること
- 使うツール・言語等
- 備考

```
# プロジェクト名

Spotify Web APIを利用したフェス出演アーティスト予想アプリ

## 制作期間

10月31日から11月21日まで（土日祝除く）
15日間(1日50分×6コマ)

## スキル

- HTML, CSS
- JavaScript
- SQL（SQLite）
- Python
- Django

## やりたいこと

### 優先順位

★★★：必須機能
★★：基本機能
★：できれば実装したい
無印：時間が余った場合

### 実装したい機能

- ★★★音楽イベント一覧表示
- ★★★出演者一覧表示
- ★★未発表出演者予想一覧表示
- ★★★データの取り込み機能（SpotifyAPIを利用）
  - ★★★アーティスト名
  - ★★★スケジュール
  - ★似ているアーティスト
- ★★★アーティスト一覧表示
- ★★出演可能イベント予想機能
- ★★★取り込みデータの精査・修正
  - ★★★フェスの各日への振り分け（手動による登録）
- ★イベント予習用プレイリスト作成

### 画面遷移イメージ

- ★★★ホームページ(近日開催のイベント一覧 or フェス一覧)
- ★★★管理者ページ
  - ★★★データの取り込み
  - ★★★登録・修正
- ★★★イベント一覧（デフォルトは今日以降）
  - ★★イベント検索
  - ★★イベント詳細ページ
- ★★★アーティスト一覧（人気度順？50音順？）
  - ★★アーティスト検索
  - ★★アーティスト詳細ページ
- ★カレンダー機能
- ★マップ機能
```

### 回答

以下は「Spotify Web APIを利用したフェス出演アーティスト予想アプリ」の制作スケジュール案です。基本機能から優先的に着手し、時間に余裕があれば追加機能を検討する構成になっています。

---

### 📅 プロジェクトスケジュール表（2025年10月31日〜11月21日）

| 日付         | やること                                      | 使うツール・言語等            | 備考 |
|--------------|-----------------------------------------------|-------------------------------|------|
| 10/31 (金)   | プロジェクト概要確認・環境構築                | Python, Django, GitHub        | 仮DB設計・Spotify APIの仕様確認 |
| 11/4 (火)    | Djangoプロジェクト作成・基本ルーティング設定   | Django, HTML, CSS             | ホームページ・管理者ページの枠組み |
| 11/5 (水)    | モデル設計（イベント・アーティスト）           | Django ORM, SQLite            | 必須データ構造の定義 |
| 11/6 (木)    | Spotify APIからアーティスト情報取得            | Python, Spotify Web API       | 認証・基本データ取得（★★★） |
| 11/7 (金)    | イベント一覧・アーティスト一覧表示             | Django, HTML, CSS             | 表示テンプレート作成（★★★） |
| 11/10 (月)   | 管理者ページ：データ登録・修正機能             | Django Admin, Forms           | 手動登録・修正機能（★★★） |
| 11/11 (火)   | フェス日程への振り分け機能                     | Django Admin, SQLite          | 手動登録（★★★） |
| 11/12 (水)   | 未発表出演者予想ロジック（類似アーティスト）   | Python, Spotify API           | 時間があれば（★★） |
| 11/13 (木)   | 出演可能イベント予測ロジック                   | Python, SQLite                | 時間があれば（★★） |
| 11/14 (金)   | アーティスト詳細ページ・検索機能               | Django, JavaScript            | 時間があれば（★★） |
| 11/17 (月)   | イベント詳細ページ・検索機能                   | Django, JavaScript            | 時間があれば（★★） |
| 11/18 (火)   | プレイリスト作成機能（予習用）                 | Spotify API, JavaScript       | 時間があれば（★） |
| 11/19 (水)   | UI調整・CSSデザイン                            | HTML, CSS                     | レスポンシブ対応など |
| 11/20 (木)   | テスト・デバッグ                               | Django Test, Manual Testing   | バグ修正・動作確認 |
| 11/21 (金)   | 最終調整・ドキュメント作成・発表準備           | GitHub, Markdown, プレゼン資料 | README・スライド・デモ |

---

## DB仮設計

Copilotに相談して、ER図を作成した

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

## Djangoアプリ開発開始

### 下準備

仮想環境を作成

```
python -m venv venv
venv\Scripts\activate
```

Djangoインストール

```
pip install --upgrade pip
pip install django
```

### プロジェクト作成開始

Djangoプロジェクトを作成

```
django-admin startproject conf .
python manage.py migrate
python manage.py runserver
```

アプリケーションの作成

```
python manage.py startapp festival
```

models.py にエンティティを定義する

```
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

モデル設計のポイント
- 外部キー：ForeignKey を使ってリレーションを表現
- 自己参照：RelatedArtist で Artist を2回参照（related_name を使って区別）
- 文字列表示：__str__() を定義して管理画面で見やすく
- バリデーション：blank=True や null=True で柔軟性を確保

モデルを登録(setting.py)

```
INSTALLED_APPS = [
    # 作成したアプリ
    'festival',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
```

モデルの変更をマイグレーションに変換

```
python manage.py makemigrations
```

DBに反映

```
python manage.py migrate
```

### admin.pyにモデルを登録

スーパーユーザーを設定する

```python
python manage.py createsuperuser
```

言語・タイムゾーンの設定

```python
# conf\settings.py
LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'
```

管理サイトにモデルを登録する

```python
# admin.py
from django.contrib import admin

from .models import Artist, Event, ManualEntry, Performance, RelatedArtist

# Register your models here.
admin.site.register(Artist)
admin.site.register(Event)
admin.site.register(ManualEntry)
admin.site.register(Performance)
admin.site.register(RelatedArtist)
```

管理画面からダミーデータを登録

管理画面のカスタマイズ

> Djangoの管理画面（admin site）のカスタマイズは、admin.py にクラスを定義して登録することで、表示項目や検索機能、フィルターなどを追加できます。

---

### 🛠️ 管理画面カスタマイズの基本

#### 1. モデルをカスタムクラスで登録する

たとえば `Artist` モデルをカスタマイズするには、`festival/admin.py` に以下のように書きます：

```python
from django.contrib import admin
from .models import Artist

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'popularity', 'spotify_id')  # 一覧に表示する項目
    search_fields = ('name', 'genres')                   # 検索ボックスで検索可能な項目
    list_filter = ('popularity',)                        # サイドバーにフィルターを追加
```

---

#### 2. 他のモデルも同様に登録

```python
from .models import Event, Performance, RelatedArtist, ManualEntry

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'start_date', 'end_date')
    search_fields = ('name', 'location')
    list_filter = ('start_date',)

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'artist', 'performance_date', 'is_confirmed')
    list_filter = ('is_confirmed', 'performance_date')
    search_fields = ('event__name', 'artist__name')

@admin.register(RelatedArtist)
class RelatedArtistAdmin(admin.ModelAdmin):
    list_display = ('artist', 'related_artist', 'similarity_score')
    search_fields = ('artist__name', 'related_artist__name')

@admin.register(ManualEntry)
class ManualEntryAdmin(admin.ModelAdmin):
    list_display = ('event', 'artist', 'notes')
    search_fields = ('event__name', 'artist__name', 'notes')
```

---

#### 3. 管理画面での表示確認

ローカルサーバーを起動して、管理画面にアクセス：

```bash
python manage.py runserver
```

ブラウザで `http://127.0.0.1:8000/admin/` にアクセスし、ログイン後にカスタマイズされた一覧表示や検索機能が反映されているか確認できます。

---

#### ✅ よく使うオプション一覧

| オプション         | 説明 |
|------------------|------|
| `list_display`   | 一覧ページに表示するフィールド |
| `search_fields`  | 検索ボックスで検索可能なフィールド |
| `list_filter`    | サイドバーに表示されるフィルター |
| `ordering`       | デフォルトの並び順 |
| `readonly_fields`| 編集不可にするフィールド |

---

## Spotify API連携

### ✅ 安全なトークン管理の方法

#### 1. `.env` ファイルに保存する（推奨）

プロジェクトルートに `.env` ファイルを作成し、以下のように記述します：

```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

#### 2. `.gitignore` に `.env` を追加

```gitignore
# Pythonキャッシュファイル
*.py[cod]
__pycache__/

# 仮想環境
venv/

# DBファイル
db.sqlite3

# 環境変数
.env
```

これで `.env` ファイルは Git に含まれなくなります。

#### 3. Pythonから読み込む（例：`python-dotenv` を使用）

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
```

#### 履歴管理から除外

Gitのキャッシュから除外

```
git rm --cached db.sqlite3
git rm --cached -r venv/
```

venv/ の方で実行エラーが出たが、中身を確認したところ空っぽだったため履歴を追跡していなかった。

コミットして履歴を更新

```
git commit -m "Remove sensitive files from Git tracking"
git push
```

### Spotify APIの認証（Client Credentials Flow）

必要な準備
- Spotify Developer Dashboard でアプリを作成
- Client ID と Client Secret を取得
- .env に保存

[Spotify Developer Dashboard](https://developer.spotify.com/)

入力項目

- App name
- App description
- Redirect URIs

開発中ダミーURL

https://example.com/callback/

Which API/SDKs are you planning to use?

WebAPIに✅

conf/setting.pyに追加

```
# Spotify Web API
from dotenv import load_dotenv
import os

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
```

ライブラリインストール

```
pip install requests
```

festival/spotify.py

```
import requests

from conf.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from .models import Artist

def get_spotify_token():
    """トークン取得関数"""
    auth_url = "https://accounts.spotify.com/api/token"
    response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    })

    data = response.json()
    return data['access_token']

def search_artist(name):
    """アーティスト検索関数"""
    token = get_spotify_token()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    params = {
        'q': name,
        'type': 'artist',
        'limit': 1
    }
    response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
    data = response.json()

    if data['artists']['items']:
        artist = data['artists']['items'][0]
        return {
            'name': artist['name'],
            'spotify_id': artist['id'],
            'popularity': artist['popularity'],
            'genres': ', '.join(artist['genres'])
        }
    return None


def save_artist_from_spotify(name):
    """Djangoモデルに保存"""
    artist_data = search_artist(name)
    if artist_data:
        artist, created = Artist.objects.get_or_create(
            spotify_id=artist_data['spotify_id'],
            defaults={
                'name': artist_data['name'],
                'popularity': artist_data['popularity'],
                'genres': artist_data['genres']
            }
        )
        return artist
    return None
```

動作確認

```
python manage.py shell
```

```
from festival.spotify import save_artist_from_spotify
artist = save_artist_from_spotify("YOASOBI")
print(artist)
```

出力内容✅

> YOASOBI

管理画面から、「YOASOBI」が登録されているか確認✅

他のアーティストも試す

```
from festival.spotify import save_artist_from_spotify
save_artist_from_spotify("King Gnu")
save_artist_from_spotify("Aimer")
```

同じアーティスト名を再度実行して重複登録されないことを確認✅