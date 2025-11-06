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