import pykakasi
import unicodedata
import re

kks = pykakasi.kakasi()
kks.setMode("H", "H")  # ひらがなをひらがなに
kks.setMode("K", "H")  # カタカナをひらがなに
kks.setMode("J", "H")  # 漢字をひらがなに
kks.setMode("r", "Hepburn")  # ローマ字変換（必要なら）

converter = kks.getConverter()

def get_furigana(text):
    """日本語の文字列からひらがな読みを生成"""
    return converter.do(text)

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