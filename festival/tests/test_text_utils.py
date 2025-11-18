import unittest
from festival.utils import text_utils

class TestTextUtils(unittest.TestCase):

    # get_furigana
    def test_get_furigana_empty(self):
        self.assertEqual(text_utils.get_furigana(""), "")

    def test_get_furigana_hiragana(self):
        self.assertEqual(text_utils.get_furigana("あいうえお"), "あいうえお")

    def test_get_furigana_katakana(self):
        self.assertEqual(text_utils.get_furigana("アイウエオ"), "あいうえお")

    def test_get_furigana_kanji(self):
        self.assertEqual(text_utils.get_furigana("東京"), "とうきょう")

    def test_get_furigana_mixed(self):
        self.assertEqual(text_utils.get_furigana("山田タロウ"), "やまだたろう")

    def test_get_furigana_english(self):
        self.assertEqual(text_utils.get_furigana("Hello"), "Hello")

    def test_get_furigana_symbols(self):
        self.assertEqual(text_utils.get_furigana("★"), "★")

    # get_initial_group
    def test_get_initial_group_empty(self):
        self.assertEqual(text_utils.get_initial_group(""), "")

    def test_get_initial_group_hiragana(self):
        self.assertEqual(text_utils.get_initial_group("あいうえお"), "あ")

    def test_get_initial_group_katakana(self):
        self.assertEqual(text_utils.get_initial_group("カキクケコ"), "か")

    def test_get_initial_group_kanji(self):
        self.assertEqual(text_utils.get_initial_group("佐藤"), "さ")

    def test_get_initial_group_dakuon(self):
        self.assertEqual(text_utils.get_initial_group("ぎんこう"), "か")

    def test_get_initial_group_handakuon(self):
        self.assertEqual(text_utils.get_initial_group("ぴあ"), "は")

    def test_get_initial_group_english(self):
        self.assertEqual(text_utils.get_initial_group("Apple"), "A")

    def test_get_initial_group_lowercase(self):
        self.assertEqual(text_utils.get_initial_group("banana"), "B")

    def test_get_initial_group_symbol(self):
        self.assertEqual(text_utils.get_initial_group("★スター"), "★")

    def test_get_initial_group_number(self):
        self.assertEqual(text_utils.get_initial_group("123"), "1")