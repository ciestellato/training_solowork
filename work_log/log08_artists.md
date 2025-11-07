# アーティスト関連

## 一覧にタブ検索を追加

`views.py`

```
def artist_list(request):
    query = request.GET.get('q')
    initial = request.GET.get('initial')

    # 全アーティスト（initials生成用）
    all_artists = Artist.objects.exclude(furigana__isnull=True).exclude(furigana__exact='')

    # 表示対象アーティスト（絞り込み）
    artists = all_artists
    if query:
        artists = artists.filter(name__icontains=query)
    if initial:
        artists = artists.filter(furigana__startswith=initial)

    artists = artists.order_by('furigana')

    # initialsは全アーティストから生成（絞り込みに依存しない）
    def get_initial_group(char):
        import unicodedata, re
        char = unicodedata.normalize('NFKC', char)[0].lower()
        if re.match(r'[a-z]', char):
            return char.upper()
        kana_groups = {
            'あ': 'あ', 'い': 'あ', 'う': 'あ', 'え': 'あ', 'お': 'あ',
            'か': 'か', 'き': 'か', 'く': 'か', 'け': 'か', 'こ': 'か',
            'さ': 'さ', 'し': 'さ', 'す': 'さ', 'せ': 'さ', 'そ': 'さ',
            'た': 'た', 'ち': 'た', 'つ': 'た', 'て': 'た', 'と': 'た',
            'な': 'な', 'に': 'な', 'ぬ': 'な', 'ね': 'な', 'の': 'な',
            'は': 'は', 'ひ': 'は', 'ふ': 'は', 'へ': 'は', 'ほ': 'は',
            'ま': 'ま', 'み': 'ま', 'む': 'ま', 'め': 'ま', 'も': 'ま',
            'や': 'や', 'ゆ': 'や', 'よ': 'や',
            'ら': 'ら', 'り': 'ら', 'る': 'ら', 'れ': 'ら', 'ろ': 'ら',
            'わ': 'わ', 'を': 'わ', 'ん': 'わ',
        }
        return kana_groups.get(char, char)

    initials = sorted(set(get_initial_group(a.furigana) for a in all_artists if a.furigana))
    kana_order = ['あ', 'か', 'さ', 'た', 'な', 'は', 'ま', 'や', 'ら', 'わ']
    alpha_order = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    sorted_initials = [i for i in kana_order + alpha_order if i in initials]

    return render(request, 'artist_list.html', {
        'artists': artists,
        'query': query,
        'initial': initial,
        'initials': sorted_initials,
    })
```

`utils.py`

```
import unicodedata
import re

def get_initial_group(char):
    """頭文字を五十音またはアルファベットグループに分類"""
    if not char:
        return ''
    char = unicodedata.normalize('NFKC', char)[0].lower()

    # アルファベット
    if re.match(r'[a-z]', char):
        return char.upper()

    # ひらがなグループ
    kana_groups = {
        'あ': 'あ', 'い': 'あ', 'う': 'あ', 'え': 'あ', 'お': 'あ',
        'か': 'か', 'き': 'か', 'く': 'か', 'け': 'か', 'こ': 'か',
        'さ': 'さ', 'し': 'さ', 'す': 'さ', 'せ': 'さ', 'そ': 'さ',
        'た': 'た', 'ち': 'た', 'つ': 'た', 'て': 'た', 'と': 'た',
        'な': 'な', 'に': 'な', 'ぬ': 'な', 'ね': 'な', 'の': 'な',
        'は': 'は', 'ひ': 'は', 'ふ': 'は', 'へ': 'は', 'ほ': 'は',
        'ま': 'ま', 'み': 'ま', 'む': 'ま', 'め': 'ま', 'も': 'ま',
        'や': 'や', 'ゆ': 'や', 'よ': 'や',
        'ら': 'ら', 'り': 'ら', 'る': 'ら', 'れ': 'ら', 'ろ': 'ら',
        'わ': 'わ', 'を': 'わ', 'ん': 'わ',
    }
    return kana_groups.get(char, char)
```

## ツアー日程登録機能

`forms.py`

```
from django import forms
from .models import Artist

class ArtistSchedulePasteForm(forms.Form):
    artist = forms.ModelChoiceField(queryset=Artist.objects.all(), label='アーティスト')
    event_name = forms.CharField(label='イベント名')
    raw_text = forms.CharField(
        label='出演日程（コピペ）',
        widget=forms.Textarea(attrs={'rows': 10}),
        help_text='例:\n2025-11-10 Zepp Tokyo\n2025-11-12 名古屋ダイアモンドホール'
    )
```

`views.py`

```
from django.shortcuts import render, redirect
from .forms import ArtistSchedulePasteForm
from .models import Event, EventDay, Performance
from datetime import datetime

def paste_schedule_register(request):
    message = ''
    if request.method == 'POST':
        form = ArtistSchedulePasteForm(request.POST)
        if form.is_valid():
            artist = form.cleaned_data['artist']
            event_name = form.cleaned_data['event_name']
            raw_text = form.cleaned_data['raw_text']

            # イベント作成または取得
            event, _ = Event.objects.get_or_create(
                name=event_name,
                defaults={
                    'start_date': '2025-01-01',
                    'end_date': '2025-12-31',
                    'event_type': 'TOUR'
                }
            )

            count = 0
            for line in raw_text.splitlines():
                parts = line.strip().split(maxsplit=1)
                if len(parts) != 2:
                    continue
                date_str, venue = parts
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    event_day = EventDay.objects.create(event=event, date=date, venue=venue)
                    Performance.objects.create(event_day=event_day, artist=artist, is_confirmed=True)
                    count += 1
                except Exception:
                    continue  # 無効な行はスキップ

            message = f"{count} 件の出演日程を登録しました。"
            return redirect(request.path)
    else:
        form = ArtistSchedulePasteForm()

    return render(request, 'paste_schedule_register.html', {
        'form': form,
        'message': message
    })
```

`paste_schedule_register.html`

```
<h2>📋 出演日程の一括登録</h2>

<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit" class="btn btn-primary">登録</button>
</form>

{% if message %}
  <div class="alert alert-success mt-3">{{ message }}</div>
{% endif %}
```

`urls.py`

```
    # ツアー詳細登録
    path('tour/register/', views.paste_schedule_register, name='paste_schedule_register'),
```

`artist_detail.html`

```
    {% if request.user.is_staff %}
        <a href="{% url 'festival:paste_schedule_register' %}?artist_id={{ artist.id }}" class="btn btn-outline-primary mb-3">
            出演日程を一括登録（管理者用）
        </a>
    {% endif %}
```