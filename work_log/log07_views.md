# 修正ポイント

## GET / POSTの処理をわかりやすく

```
    # POST処理：フォーム送信された場合
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['event'] = selected_event.id  # hiddenで送ったeventを強制セット
        form = EventDayPerformanceForm(post_data)
        form.fields['date'].choices = date_choices  # 日付選択肢を設定

        if form.is_valid():
            # EventDay と Performance を登録
            event_day = EventDay.objects.create(
                event=form.cleaned_data['event'],
                date=form.cleaned_data['date'],
                venue=form.cleaned_data['venue']
            )
            for artist in form.cleaned_data['artists']:
                Performance.objects.create(event_day=event_day, artist=artist, is_confirmed=True)

            # 成功メッセージをセッションに保存してリダイレクト（PRG）
            request.session['message'] = f"{event_day} に {form.cleaned_data['artists'].count()} 組の出演者を登録しました。"
            return redirect(f"{request.path}?event_id={selected_event.id}")

    else:
        # GET処理：フォーム初期表示
        form = EventDayPerformanceForm(initial={'event': selected_event})
        form.fields['date'].choices = date_choices  # 日付選択肢を設定
```

## register_event_day_and_performancesをPRGパターンに対応させた

これでフォーム送信後に更新しても再送信されないようになった。

## アーティスト一括登録

コンマ区切り以外に、改行区切りもOKにした

## ふりがな

Artistモデルにふりがなフィールドを追加
```
class Artist(models.Model):
    name = models.CharField(max_length=100)
    furigana = models.CharField(max_length=100, blank=True, null=True)  # 読み仮名

    def __str__(self):
        return self.name
```

マイグレーション
```
python manage.py makemigrations
python manage.py migrate
```

ビューを編集
```
artists = Artist.objects.all().order_by('furigana')
```

### pykakasiでふりがな自動生成

ライブラリをインストール
```
pip install pykakasi
```

ふりがな関数を作成
```
# festival/utils.py
import pykakasi

kks = pykakasi.kakasi()
kks.setMode("H", "H")  # ひらがなをひらがなに
kks.setMode("K", "H")  # カタカナをひらがなに
kks.setMode("J", "H")  # 漢字をひらがなに
kks.setMode("r", "Hepburn")  # ローマ字変換（必要なら）

converter = kks.getConverter()

def get_furigana(text):
    """日本語の文字列からひらがな読みを生成"""
    return converter.do(text)
```

Spotify関数に上記関数を組み込む
```
from .utils import get_furigana

def save_artist_from_spotify(name):
    # Spotify APIでアーティスト情報を取得（略）

    # 取得成功時に保存
    furigana = get_furigana(name)
    artist = Artist.objects.create(name=name, furigana=furigana)
    return artist
```

管理画面でもふりがなを表示
```
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'furigana')
    search_fields = ('name', 'furigana')
```

ふりがなが未設定の場合、Django Shellで一括登録が可能
```
from festival.models import Artist
from festival.utils import get_furigana

for artist in Artist.objects.filter(furigana__isnull=True):
    artist.furigana = get_furigana(artist.name)
    artist.save()
```