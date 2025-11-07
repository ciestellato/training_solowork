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