"""Tests for BaseStationParser functionality"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from parser import BaseStationParser, BaseStation


class TestParseHandoverRange(unittest.TestCase):
    """Test handover range parsing from various text formats"""
    
    def test_parse_handover_range_parses_dash_format_correctly(self):
        """Verify parsing of '12-18' format returns tuple (12.0, 18.0)"""
        result = BaseStationParser.parse_handover_range("12-18")
        self.assertEqual(result, (12.0, 18.0))
    
    def test_parse_handover_range_parses_russian_text_format(self):
        """Verify parsing of 'от 11 до 19' format returns tuple (11.0, 19.0)"""
        result = BaseStationParser.parse_handover_range("от 11 до 19")
        self.assertEqual(result, (11.0, 19.0))
    
    def test_parse_handover_range_handles_comma_decimal_separator(self):
        """Verify parsing handles comma as decimal separator"""
        result = BaseStationParser.parse_handover_range("12,5-18,7")
        self.assertEqual(result, (12.5, 18.7))
    
    def test_parse_handover_range_returns_none_for_missing_value(self):
        """Verify parsing returns None for None input"""
        result = BaseStationParser.parse_handover_range(None)
        self.assertIsNone(result)
    
    def test_parse_handover_range_returns_none_for_nan_value(self):
        """Verify parsing returns None for NaN pandas value"""
        result = BaseStationParser.parse_handover_range(float('nan'))
        self.assertIsNone(result)
    
    def test_parse_handover_range_returns_none_for_invalid_format(self):
        """Verify parsing returns None for text without dash separator"""
        result = BaseStationParser.parse_handover_range("invalid")
        self.assertIsNone(result)
    
    def test_parse_handover_range_returns_none_for_empty_string(self):
        """Verify parsing returns None for empty string"""
        result = BaseStationParser.parse_handover_range("")
        self.assertIsNone(result)
    
    def test_parse_handover_range_handles_extra_whitespace(self):
        """Verify parsing handles extra whitespace in input"""
        result = BaseStationParser.parse_handover_range("  12  -  18  ")
        self.assertEqual(result, (12.0, 18.0))


class TestBaseStationParserParse(unittest.TestCase):
    """Test full Excel file parsing functionality"""
    
    @patch('parser.pd.read_excel')
    @patch('parser.ApiHandoverProvider')
    def test_parse_reads_excel_file_and_creates_base_stations(self, mock_api_class, mock_read_excel):
        """Verify parse() reads Excel and creates BaseStation objects correctly"""
        # Setup mock DataFrame
        mock_df = pd.DataFrame({
            "ИД базовой станции": [1, 2],
            "Название БС": ["Station1", "Station2"],
            "Площадь зоны покрытия, кв.км": [10.0, 20.0],
            "Частота,Гц": [2400000000, 2500000000],
            "Тип антенны": ["Type A", "Type B"],
            "Диапазон показателей хэндовера": ["12-18", "10-15"],
            "Стандарт": ["5G", "4G"],
            "Координаты установки": ["55.7558,37.6173", "55.7559,37.6174"]
        })
        mock_read_excel.return_value = mock_df
        
        # Setup mock API
        mock_api_instance = Mock()
        mock_api_instance.get_handover_avg.side_effect = [15.0, 12.5]
        mock_api_class.return_value = mock_api_instance
        
        # Execute
        result = BaseStationParser.parse("test.xlsx")
        
        # Verify
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], BaseStation)
        self.assertEqual(result[0].base_station_id, 1)
        self.assertEqual(result[0].base_station_name, "Station1")
        self.assertEqual(result[0].handover_min, 12.0)
        self.assertEqual(result[0].handover_max, 18.0)
        self.assertEqual(result[0].handover_avg, 15.0)

if __name__ == '__main__':
    unittest.main()

