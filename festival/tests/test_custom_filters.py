import unittest
from unittest.mock import MagicMock
from festival.templatetags import custom_filters

class TestCustomFilters(unittest.TestCase):

    def test_get_by_id_calls_filter_and_first(self):
        mock_queryset = MagicMock()
        mock_filtered = MagicMock()
        mock_first = MagicMock(return_value="expected_result")

        mock_queryset.filter.return_value = mock_filtered
        mock_filtered.first = mock_first

        result = custom_filters.get_by_id(mock_queryset, 42)

        mock_queryset.filter.assert_called_once_with(id=42)
        mock_filtered.first.assert_called_once()
        self.assertEqual(result, "expected_result")

    def test_get_item_with_valid_dict_and_existing_key(self):
        data = {"name": "YOASOBI"}
        self.assertEqual(custom_filters.get_item(data, "name"), "YOASOBI")

    def test_get_item_with_valid_dict_and_missing_key(self):
        data = {"name": "YOASOBI"}
        self.assertIsNone(custom_filters.get_item(data, "age"))

    def test_get_item_with_non_dict(self):
        not_a_dict = ["not", "a", "dict"]
        self.assertIsNone(custom_filters.get_item(not_a_dict, "key"))