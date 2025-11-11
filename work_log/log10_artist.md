# アーティストモデル：デフォルトの並び順制御

並び順の制御は、Djangoのクエリセットやモデル定義、フォーム、テンプレートなど複数のレイヤーで柔軟に行えます。以下に代表的な方法を整理してご紹介します。

---

## 🔢 並び順の制御方法（Artistモデルを例に）

### 1. **モデルレベルでの並び順指定**

`Meta`クラスの`ordering`属性を使うと、デフォルトの並び順を指定できます。

```python
class Artist(models.Model):
    name = models.CharField(max_length=255)
    furigana = models.CharField(max_length=100, blank=True, null=True)
    popularity = models.IntegerField(null=True, blank=True)
    genres = models.JSONField(default=list, blank=True)
    spotify_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['furigana']  # ふりがな順で並び替え
```

---

### 2. **ビューやクエリセットでの並び順指定**

ビュー関数やクラスベースビューで、任意のフィールドで並び替えできます。

```python
# ふりがな順
artists = Artist.objects.all().order_by('furigana')

# 人気順（降順）
popular_artists = Artist.objects.all().order_by('-popularity')
```

---

### 3. **フォームの選択肢並び順制御**

`ModelChoiceField` や `ModelMultipleChoiceField` の `queryset` に並び順を指定できます。

```python
from django import forms

class EventDayPerformanceForm(forms.Form):
    event_day = forms.ModelChoiceField(queryset=EventDay.objects.all())
    artists = forms.ModelMultipleChoiceField(
        queryset=Artist.objects.all().order_by('furigana'),
        widget=forms.CheckboxSelectMultiple
    )
```

---

### 4. **テンプレートでの並び順制御（補助的）**

テンプレート内で並び替えたい場合は、Pythonの`sorted`やDjangoの`dictsort`フィルターを使うことも可能です。

```django
{% for artist in artists|dictsort:"furigana" %}
  {{ artist.name }}
{% endfor %}
```

---

### ✅ おすすめの並び順フィールド

| 並び順 | フィールド | 用途例 |
|--------|------------|--------|
| 50音順 | `furigana` | 日本語表示の整列 |
| 人気順 | `popularity` | 注目度の高い順に表示 |
| 登録順 | `id` または `created_at` | 新着順表示 |
| 出演順 | `Performance.event_day.date` | イベント順に出演者表示 |

---

# イベント出演日登録画面：検索バー追加

以下は、検索バーが正しく機能するように修正された**完全なHTMLテンプレート**です。Djangoのフォーム構造に合わせて、JavaScriptのセレクタも正しく調整済みです。

---

## ✅ 修正済みテンプレート（検索バー付き出演者登録ページ）

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>イベント日程と出演者登録</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-4">
    <h1>📅 イベント日程と出演者登録</h1>

    {% if message %}
        <div class="alert alert-success">{{ message }}</div>
    {% endif %}

    <form method="post">
        {% csrf_token %}
        <input type="hidden" name="event" value="{{ selected_event_id }}">

        {{ form.date }}
        {{ form.venue }}

        <!-- 🔍 検索バー -->
        <div class="mb-3">
            <label for="artistSearch" class="form-label">出演者検索</label>
            <input type="text" id="artistSearch" class="form-control" placeholder="アーティスト名を入力" autocomplete="off" aria-label="出演者検索">
        </div>

        {{ form.artists }}

        <button type="submit" class="btn btn-primary">登録する</button>
    </form>

    <a href="{% url 'festival:event_list' %}" class="btn btn-secondary mt-3">イベント一覧に戻る</a>

    <script type="text/javascript">
        const eventData = JSON.parse('{{ event_data_json|escapejs }}' || '{}');
        const selectedEventId = "{{ selected_event_id }}";

        function updateDateOptions() {
            const dateSelect = document.getElementById("id_date");
            if (!dateSelect) return;
            dateSelect.innerHTML = "";

            if (eventData[selectedEventId]) {
                const start = new Date(eventData[selectedEventId].start);
                const end = new Date(eventData[selectedEventId].end);

                for (let d = new Date(start); d.getTime() <= new Date(end).getTime(); d.setDate(d.getDate() + 1)) {
                    const dateStr = d.toISOString().split('T')[0];
                    const option = document.createElement("option");
                    option.value = dateStr;
                    option.text = dateStr;
                    dateSelect.appendChild(option);
                }
            }
        }

        document.addEventListener("DOMContentLoaded", function () {
            updateDateOptions();

            // 🔍 検索バーによる出演者フィルタリング
            const searchInput = document.getElementById("artistSearch");
            const artistLabels = document.querySelectorAll("#id_artists label");

            if (searchInput && artistLabels.length > 0) {
                searchInput.addEventListener("input", function () {
                    const keyword = this.value.toLowerCase();
                    artistLabels.forEach(label => {
                        const text = label.textContent.toLowerCase();
                        label.style.display = text.includes(keyword) ? "block" : "none";
                    });
                });
            }
        });
    </script>
</body>
</html>
```

---

## ✅ このテンプレートのポイント

- `#id_artists label` を対象にしているため、Djangoの標準フォーム構造に対応。
- `autocomplete="off"` と `aria-label` によりUXとアクセシビリティを向上。
- `updateDateOptions()` は `id_date` が存在する場合のみ実行されるように安全化。
- 不要な `id_event` 操作は削除済み。

---

このテンプレートで検索バーが正しく動作するはずです！  
次は「選択済み出演者を先頭に表示する」や「検索結果のハイライト表示」なども追加できますので、必要があればお知らせください。

以下は、選択済みのアーティストを上に表示し、出演者の総数（組数）も表示するように改修した**完全なテンプレートコード**です。

---

## ✅ 改修ポイント

- 選択済みのアーティストを上に並べるように、JavaScriptでチェック済みの要素を先に表示。
- チェックボックスの総数（組数）をカウントして表示。
- 検索バーとの連携も維持。

---

## 🧾 フルテンプレートコード（並び順＋組数表示付き）

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>イベント日程と出演者登録</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-4">
    <h1>📅 イベント日程と出演者登録</h1>

    {% if message %}
        <div class="alert alert-success">{{ message }}</div>
    {% endif %}

    <form method="post">
        {% csrf_token %}
        <input type="hidden" name="event" value="{{ selected_event_id }}">

        {{ form.date }}
        {{ form.venue }}

        <!-- 🔍 検索バー -->
        <div class="mb-3">
            <label for="artistSearch" class="form-label">出演者検索</label>
            <input type="text" id="artistSearch" class="form-control" placeholder="アーティスト名を入力" autocomplete="off" aria-label="出演者検索">
        </div>

        <!-- ✅ 組数表示 -->
        <div class="mb-2">
            <span id="artistCount" class="text-muted">出演者数: 0組</span>
        </div>

        {{ form.artists }}

        <button type="submit" class="btn btn-primary">登録する</button>
    </form>

    <a href="{% url 'festival:event_list' %}" class="btn btn-secondary mt-3">イベント一覧に戻る</a>

    <script type="text/javascript">
        const eventData = JSON.parse('{{ event_data_json|escapejs }}' || '{}');
        const selectedEventId = "{{ selected_event_id }}";

        function updateDateOptions() {
            const dateSelect = document.getElementById("id_date");
            if (!dateSelect) return;
            dateSelect.innerHTML = "";

            if (eventData[selectedEventId]) {
                const start = new Date(eventData[selectedEventId].start);
                const end = new Date(eventData[selectedEventId].end);

                for (let d = new Date(start); d.getTime() <= new Date(end).getTime(); d.setDate(d.getDate() + 1)) {
                    const dateStr = d.toISOString().split('T')[0];
                    const option = document.createElement("option");
                    option.value = dateStr;
                    option.text = dateStr;
                    dateSelect.appendChild(option);
                }
            }
        }

        function sortArtistsByChecked() {
            const container = document.getElementById("id_artists");
            const items = Array.from(container.querySelectorAll("label"));
            const checked = items.filter(label => label.querySelector("input").checked);
            const unchecked = items.filter(label => !label.querySelector("input").checked);

            // 並び替え
            container.innerHTML = "";
            [...checked, ...unchecked].forEach(label => container.appendChild(label));
        }

        function updateArtistCount() {
            const count = document.querySelectorAll("#id_artists input[type='checkbox']:checked").length;
            document.getElementById("artistCount").textContent = `出演者数: ${count}組`;
        }

        document.addEventListener("DOMContentLoaded", function () {
            updateDateOptions();
            sortArtistsByChecked();
            updateArtistCount();

            const searchInput = document.getElementById("artistSearch");
            const artistLabels = document.querySelectorAll("#id_artists label");

            if (searchInput && artistLabels.length > 0) {
                searchInput.addEventListener("input", function () {
                    const keyword = this.value.toLowerCase();
                    artistLabels.forEach(label => {
                        const text = label.textContent.toLowerCase();
                        label.style.display = text.includes(keyword) ? "block" : "none";
                    });
                });
            }

            // チェック状態変更時に組数更新
            document.querySelectorAll("#id_artists input[type='checkbox']").forEach(checkbox => {
                checkbox.addEventListener("change", updateArtistCount);
            });
        });
    </script>
</body>
</html>
```

---

## 🎯 このテンプレートでできること

- ✅ 検索バーで出演者を絞り込み
- ✅ チェック済みの出演者を上に表示
- ✅ 出演者数（組数）をリアルタイムで表示

---

アーティスト情報の編集機能を追加するには、以下の4ステップで構成するのがベストです：

---

## ✅ ステップ1：フォームクラスを作成（`forms.py`）

```python
from django import forms
from .models import Artist

class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['name', 'furigana', 'popularity', 'genres', 'spotify_id']
        widgets = {
            'genres': forms.Textarea(attrs={'rows': 2}),
        }
```

> 🔹 `genres` は JSONField ですが、編集画面では文字列リストとして扱うため、テキストエリアで表示します。

---

## ✅ ステップ2：ビュー関数を追加（`views.py`）

```python
from django.shortcuts import render, get_object_or_404, redirect
from .models import Artist
from .forms import ArtistForm

def edit_artist(request, artist_id):
    artist = get_object_or_404(Artist, pk=artist_id)

    if request.method == 'POST':
        form = ArtistForm(request.POST, instance=artist)
        if form.is_valid():
            form.save()
            return redirect('artist_detail', artist_id=artist.id)
    else:
        form = ArtistForm(instance=artist)

    return render(request, 'artist_form.html', {
        'form': form,
        'artist': artist,
        'mode': 'edit'
    })
```

---

## ✅ ステップ3：URLルーティングを追加（`urls.py`）

```python
from django.urls import path
from . import views

urlpatterns = [
    path('artist/edit/<int:artist_id>/', views.edit_artist, name='edit_artist'),
]
```

---

## ✅ ステップ4：テンプレートを作成（`artist_form.html`）

```django
<h1>🎤 アーティスト情報編集</h1>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-primary">更新</button>
</form>

<a href="{% url 'artist_detail' artist.id %}" class="btn btn-secondary mt-3">← アーティスト詳細に戻る</a>
```

---

## ✅ オプション：詳細ページに「編集」リンクを追加

```django
{% if request.user.is_staff %}
    <a href="{% url 'edit_artist' artist.id %}" class="btn btn-sm btn-outline-primary">編集</a>
{% endif %}
```

---

素晴らしい流れです！  
アーティスト詳細画面に「出演確定済みのイベント一覧」を追加するには、以下の2ステップで実装できます：

---

## ✅ ステップ①：ビュー関数で出演情報を取得（`views.py`）

```python
from .models import Performance

def artist_detail(request, pk):
    artist = get_object_or_404(Artist, pk=pk)

    # 出演確定済みのイベント日程を取得
    confirmed_performances = Performance.objects.filter(artist=artist, is_confirmed=True).select_related('event_day__event')

    return render(request, 'artist_detail.html', {
        'artist': artist,
        'confirmed_performances': confirmed_performances,
    })
```

---

## ✅ ステップ②：テンプレートに出演イベント一覧を追加（`artist_detail.html`）

```django
<h2 class="mt-4">🎤 出演確定イベント</h2>
{% if confirmed_performances %}
    <ul class="list-group mb-4">
        {% for perf in confirmed_performances %}
            <li class="list-group-item">
                <strong>{{ perf.event_day.date }}</strong> @ {{ perf.event_day.venue }}<br>
                <a href="{% url 'festival:event_detail' perf.event_day.event.id %}">{{ perf.event_day.event.name }}</a>
            </li>
        {% endfor %}
    </ul>
{% else %}
    <p class="text-muted">出演確定イベントはまだありません。</p>
{% endif %}
```

---

## ✅ 出力例

```
🎤 出演確定イベント

- 2025-11-15 @ 幕張メッセ
  フェスティバル2025

- 2025-12-03 @ Zepp Tokyo
  冬のツアー2025
```

---

**アーティストの名前とふりがなを一括編集できる画面は、Djangoのフォーム＋JavaScriptで実装可能です。頭文字タブによる絞り込みもJSで動的に制御できます。**

---

## ✅ 機能概要

- 登録済みのアーティスト一覧を表示
- 各行に `name` と `furigana` の入力欄を設置
- 頭文字（あ〜わ）で絞り込みタブを表示
- 編集後に「保存」ボタンで一括更新

---

## 🧾 フォームクラス（`forms.py`）

```python
from django import forms
from .models import Artist

class ArtistBulkEditForm(forms.Form):
    def __init__(self, *args, artists=None, **kwargs):
        super().__init__(*args, **kwargs)
        for artist in artists:
            self.fields[f'name_{artist.id}'] = forms.CharField(initial=artist.name, label='', required=False)
            self.fields[f'furigana_{artist.id}'] = forms.CharField(initial=artist.furigana, label='', required=False)
```

---

## 🧠 ビュー関数（`views.py`）

```python
from django.shortcuts import render, redirect
from .models import Artist
from .forms import ArtistBulkEditForm

def edit_artist_bulk(request):
    artists = Artist.objects.all().order_by('furigana')
    if request.method == 'POST':
        form = ArtistBulkEditForm(request.POST, artists=artists)
        if form.is_valid():
            for artist in artists:
                new_name = form.cleaned_data.get(f'name_{artist.id}')
                new_furigana = form.cleaned_data.get(f'furigana_{artist.id}')
                if new_name != artist.name or new_furigana != artist.furigana:
                    artist.name = new_name
                    artist.furigana = new_furigana
                    artist.save()
            return redirect('festival:artist_list')
    else:
        form = ArtistBulkEditForm(artists=artists)
    return render(request, 'artist_bulk_edit.html', {'form': form, 'artists': artists})
```

---

## 🌐 URL設定（`urls.py`）

```python
path('artist/bulk_edit/', views.edit_artist_bulk, name='edit_artist_bulk'),
```

---

## 🎨 テンプレート（`artist_bulk_edit.html`）

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>アーティスト一括編集</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .tab-button { margin: 0 4px; }
        .artist-row { display: flex; gap: 1rem; margin-bottom: 0.5rem; }
    </style>
</head>
<body class="container mt-4">
    <h1>🎶 アーティスト一括編集</h1>

    <!-- 頭文字タブ -->
    <div class="mb-3">
        <button class="btn btn-outline-secondary tab-button" data-initial="all">すべて</button>
        {% for kana in "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわ" %}
            <button class="btn btn-outline-secondary tab-button" data-initial="{{ kana }}">{{ kana }}</button>
        {% endfor %}
    </div>

    <form method="post">
        {% csrf_token %}
        {% for artist in artists %}
            <div class="artist-row artist-block" data-initial="{{ artist.furigana|slice:":1" }}">
                <input type="text" name="name_{{ artist.id }}" value="{{ artist.name }}" class="form-control" placeholder="名前">
                <input type="text" name="furigana_{{ artist.id }}" value="{{ artist.furigana }}" class="form-control" placeholder="ふりがな">
            </div>
        {% endfor %}
        <button type="submit" class="btn btn-primary mt-3">保存</button>
    </form>

<script>
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.addEventListener('click', () => {
            const initial = btn.dataset.initial;
            document.querySelectorAll('.artist-block').forEach(row => {
                if (initial === 'all' || row.dataset.initial.startsWith(initial)) {
                    row.style.display = 'flex';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
</script>
</body>
</html>
```

---

## ✅ 補足

- `furigana|slice:":1"` で頭文字を抽出
- JavaScriptで `.artist-block[data-initial]` を絞り込み
- Bootstrapで見た目も整えられます

---

この一括編集画面で、管理者はアーティスト名とふりがなを効率的に修正できます！  
次は「CSVインポート」「ジャンル編集」「人気度一括更新」なども追加できます。どれに進めましょう？
