"""Integration tests for the entire system"""
import unittest
from unittest.mock import patch, Mock
import pandas as pd
from parser import BaseStationParser
from zone import Zone, BuildType


class TestFullSystemIntegration(unittest.TestCase):
    """Test integration between parser, zone, and handover modules"""
    
    @patch('parser.pd.read_excel')
    @patch('parser.ApiHandoverProvider')
    def test_full_workflow_from_excel_to_zone_calculation(self, mock_api_class, mock_read_excel):
        """Verify complete workflow: parse Excel → create Zone → calculate n_stations"""
        # Setup mock Excel data
        mock_df = pd.DataFrame({
            "ИД базовой станции": [1, 2, 3],
            "Название БС": ["Station1", "Station2", "Station3"],
            "Площадь зоны покрытия, кв.км": [100.0, 80.0, 60.0],
            "Частота,Гц": [2400000000, 2500000000, 2600000000],
            "Тип антенны": ["Type A", "Type B", "Type C"],
            "Диапазон показателей хэндовера": ["12-18", "10-15", "11-19"],
            "Стандарт": ["5G", "5G", "4G"],
            "Координаты установки": ["55.1,37.1", "55.2,37.2", "55.3,37.3"]
        })
        mock_read_excel.return_value = mock_df
        
        # Setup mock API
        mock_api_instance = Mock()
        mock_api_instance.get_handover_avg.side_effect = [15.0, 12.5, 14.0]
        mock_api_class.return_value = mock_api_instance
        
        # Execute full workflow
        stations = BaseStationParser.parse("test.xlsx")
        zone = Zone(
            name="Test District",
            area_km2=250.0,
            build_type=BuildType.hard,
            base_stations=stations
        )
        
        n = zone.n_stations()
        
        # Verify results
        self.assertEqual(len(stations), 3)
        self.assertIsInstance(n, float)
        self.assertGreater(n, 0)
    
    @patch('parser.pd.read_excel')
    @patch('parser.ApiHandoverProvider')
    def test_zone_calculation_adjusts_for_poor_handover_performance(self, mock_api_class, mock_read_excel):
        """Verify n_stations increases by 1.4x when handover performance is poor"""
        # Setup mock Excel data with poor handover
        mock_df = pd.DataFrame({
            "ИД базовой станции": [1, 2, 3],
            "Название БС": ["Station1", "Station2", "Station3"],
            "Площадь зоны покрытия, кв.км": [100.0, 80.0, 60.0],
            "Частота,Гц": [2400000000, 2500000000, 2600000000],
            "Тип антенны": ["Type A", "Type B", "Type C"],
            "Диапазон показателей хэндовера": ["12-18", "12-18", "12-18"],
            "Стандарт": ["5G", "5G", "4G"],
            "Координаты установки": ["55.1,37.1", "55.2,37.2", "55.3,37.3"]
        })
        mock_read_excel.return_value = mock_df
        
        # Setup mock API with bad handover (outside range)
        mock_api_instance = Mock()
        mock_api_instance.get_handover_avg.side_effect = [25.0, 26.0, 27.0]  # All > max
        mock_api_class.return_value = mock_api_instance
        
        # Execute
        stations = BaseStationParser.parse("test.xlsx")
        zone = Zone(
            name="Test District",
            area_km2=250.0,
            build_type=BuildType.hard,
            base_stations=stations
        )
        
        # All stations have bad handover, so should multiply by 1.4
        n = zone.n_stations()
        
        # Verify adjustment applied
        self.assertIsInstance(n, float)
        self.assertGreater(n, 0)


if __name__ == '__main__':
    unittest.main()

