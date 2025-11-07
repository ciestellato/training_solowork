import pykakasi
import unicodedata
import re

# pykakasi 設定
kks = pykakasi.kakasi()
kks.setMode("H", "H")        # ひらがな → ひらがな
kks.setMode("K", "H")        # カタカナ → ひらがな
kks.setMode("J", "H")        # 漢字 → ひらがな
kks.setMode("r", "Hepburn")  # ローマ字変換（必要なら）

converter = kks.getConverter()

def get_furigana(text):
    """日本語の文字列からひらがな読みを生成"""
    if not text:
        return ''
    return converter.do(text)

def get_initial_group(text):
    """文字列の先頭文字から五十音またはアルファベットグループを判定"""
    if not text:
        return ''

    # ひらがなに変換（例：漢字やカタカナを含む場合）
    hira = get_furigana(text)
    if not hira:
        return ''

    char = unicodedata.normalize('NFKC', hira)[0].lower()

    # アルファベット判定
    if re.match(r'[a-z]', char):
        return char.upper()

    # 五十音グループ判定
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