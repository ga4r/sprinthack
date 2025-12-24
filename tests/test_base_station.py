"""Tests for BaseStation dataclass functionality"""
import unittest
from parser import BaseStation

class TestBaseStationHandoverValidation(unittest.TestCase):
    """Test handover validation logic"""
    
    def test_is_handover_ok_returns_true_when_avg_within_range(self):
        """Verify handover is OK when average is within min-max range"""
        station = BaseStation(
            base_station_id=1,
            base_station_name="Test",
            coverage_area_sq_km=10.0,
            frequency_hz=2400000000,
            antenna_type="directional",
            handover_min=10.0,
            handover_max=20.0,
            handover_avg=15.0,
            standard="5G"
        )
        
        self.assertTrue(station.is_handover_ok())
    
    def test_is_handover_ok_returns_false_when_avg_below_min(self):
        """Verify handover is not OK when average is below minimum"""
        station = BaseStation(
            base_station_id=1,
            base_station_name="Test",
            coverage_area_sq_km=10.0,
            frequency_hz=2400000000,
            antenna_type="directional",
            handover_min=10.0,
            handover_max=20.0,
            handover_avg=5.0,
            standard="5G"
        )
        
        self.assertFalse(station.is_handover_ok())
    
    def test_is_handover_ok_returns_false_when_avg_above_max(self):
        """Verify handover is not OK when average exceeds maximum"""
        station = BaseStation(
            base_station_id=1,
            base_station_name="Test",
            coverage_area_sq_km=10.0,
            frequency_hz=2400000000,
            antenna_type="directional",
            handover_min=10.0,
            handover_max=20.0,
            handover_avg=25.0,
            standard="5G"
        )
        
        self.assertFalse(station.is_handover_ok())
    
    def test_is_handover_ok_returns_none_when_handover_data_missing(self):
        """Verify handover returns None when any handover value is missing"""
        station = BaseStation(
            base_station_id=1,
            base_station_name="Test",
            coverage_area_sq_km=10.0,
            frequency_hz=2400000000,
            antenna_type="directional",
            handover_min=None,
            handover_max=None,
            handover_avg=None,
            standard="5G"
        )
        
        self.assertIsNone(station.is_handover_ok())


class TestBaseStationGeometry(unittest.TestCase):
    """Test geometric calculations for coverage area"""
    
    def test_radius_km_calculates_correct_radius_from_area(self):
        """Verify radius calculation using formula r = sqrt(area/π)"""
        station = BaseStation(
            base_station_id=1,
            base_station_name="Test",
            coverage_area_sq_km=100.0,
            frequency_hz=2400000000,
            antenna_type="directional",
            handover_min=10.0,
            handover_max=20.0,
            handover_avg=15.0,
            standard="5G"
        )
        
        # r = sqrt(100/π) ≈ 5.64
        radius = station.radius_km()
        self.assertAlmostEqual(radius, 5.64, places=2)
    
    def test_diameter_km_returns_twice_the_radius(self):
        """Verify diameter calculation as 2 times radius"""
        station = BaseStation(
            base_station_id=1,
            base_station_name="Test",
            coverage_area_sq_km=100.0,
            frequency_hz=2400000000,
            antenna_type="directional",
            handover_min=10.0,
            handover_max=20.0,
            handover_avg=15.0,
            standard="5G"
        )
        
        radius = station.radius_km()
        diameter = station.diameter_km()
        self.assertAlmostEqual(diameter, 2 * radius, places=10)


if __name__ == '__main__':
    unittest.main()

