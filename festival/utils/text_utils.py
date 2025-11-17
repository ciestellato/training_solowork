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

    # 五十音グループ判定（濁音・半濁音含む）
    kana_groups = {
        'あ': ['あ', 'い', 'う', 'え', 'お'],
        'か': ['か', 'き', 'く', 'け', 'こ', 'が', 'ぎ', 'ぐ', 'げ', 'ご'],
        'さ': ['さ', 'し', 'す', 'せ', 'そ', 'ざ', 'じ', 'ず', 'ぜ', 'ぞ'],
        'た': ['た', 'ち', 'つ', 'て', 'と', 'だ', 'ぢ', 'づ', 'で', 'ど'],
        'な': ['な', 'に', 'ぬ', 'ね', 'の'],
        'は': ['は', 'ひ', 'ふ', 'へ', 'ほ', 'ば', 'び', 'ぶ', 'べ', 'ぼ', 'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ'],
        'ま': ['ま', 'み', 'む', 'め', 'も'],
        'や': ['や', 'ゆ', 'よ'],
        'ら': ['ら', 'り', 'る', 'れ', 'ろ'],
        'わ': ['わ', 'を', 'ん'],
    }

    for group, chars in kana_groups.items():
        if char in chars:
            return group

    return char  # fallback