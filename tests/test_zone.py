"""Tests for Zone class and BuildType functionality"""
import unittest
import math
from zone import Zone, BuildType, BUILD_COEFF
from parser import BaseStation


class TestBuildType(unittest.TestCase):
    """Test BuildType enum values"""
    
    def test_build_coeff_dictionary_has_correct_coefficients(self):
        """Verify BUILD_COEFF dictionary contains correct coefficient values"""
        self.assertEqual(BUILD_COEFF[BuildType.hard], 1.21)
        self.assertEqual(BUILD_COEFF[BuildType.medium], 0.9)
        self.assertEqual(BUILD_COEFF[BuildType.light], 0.47)


class TestZoneBuildCoeff(unittest.TestCase):
    """Test Zone build coefficient retrieval"""
    
    def test_build_coeff_returns_correct_coefficient_for_zone_build_type(self):
        """Verify build_coeff() returns the correct coefficient for zone's build type"""
        station = BaseStation(
            base_station_id=1,
            base_station_name="Test",
            coverage_area_sq_km=10.0,
            frequency_hz=2400000000,
            antenna_type="A",
            handover_min=10.0,
            handover_max=20.0,
            handover_avg=15.0,
            standard="5G"
        )
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=[station]
        )
        
        self.assertEqual(zone.build_coeff(), 1.21)


class TestZoneR0Calculation(unittest.TestCase):
    """Test R0 (zone radius) calculation"""
    
    def test_r0_km_calculates_zone_radius_using_area_formula(self):
        """Verify r0_km() calculates radius correctly as sqrt(area/π)"""
        station = BaseStation(
            base_station_id=1,
            base_station_name="Test",
            coverage_area_sq_km=10.0,
            frequency_hz=2400000000,
            antenna_type="A",
            handover_min=10.0,
            handover_max=20.0,
            handover_avg=15.0,
            standard="5G"
        )
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=[station]
        )
        
        expected_r0 = math.sqrt(100.0 / math.pi)
        self.assertAlmostEqual(zone.r0_km(), expected_r0, places=10)


class TestZoneLCalculations(unittest.TestCase):
    """Test L (number of cells) calculations"""
    
    def test_l_for_station_calculates_cell_count_using_formula(self):
        """Verify l_for_station() calculates L = K*(R0/R)^2 correctly"""
        station = BaseStation(
            base_station_id=1,
            base_station_name="Test",
            coverage_area_sq_km=10.0,
            frequency_hz=2400000000,
            antenna_type="A",
            handover_min=10.0,
            handover_max=20.0,
            handover_avg=15.0,
            standard="5G"
        )
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=[station]
        )
        
        r0 = zone.r0_km()
        r = station.radius_km()
        k = BUILD_COEFF[BuildType.hard]
        expected_l = k * (r0 / r) ** 2
        
        self.assertAlmostEqual(zone.l_for_station(station), expected_l, places=10)
    
    def test_l_avg_calculates_arithmetic_mean_of_all_stations(self):
        """Verify l_avg() returns arithmetic mean of L values for all stations"""
        station1 = BaseStation(
            base_station_id=1,
            base_station_name="Test1",
            coverage_area_sq_km=10.0,
            frequency_hz=2400000000,
            antenna_type="A",
            handover_min=10.0,
            handover_max=20.0,
            handover_avg=15.0,
            standard="5G"
        )
        
        station2 = BaseStation(
            base_station_id=2,
            base_station_name="Test2",
            coverage_area_sq_km=20.0,
            frequency_hz=2500000000,
            antenna_type="B",
            handover_min=10.0,
            handover_max=20.0,
            handover_avg=15.0,
            standard="4G"
        )
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=[station1, station2]
        )
        
        l1 = zone.l_for_station(station1)
        l2 = zone.l_for_station(station2)
        expected_avg = (l1 + l2) / 2
        
        self.assertAlmostEqual(zone.l_avg(), expected_avg, places=10)
    
    def test_l_avg_raises_error_when_no_base_stations(self):
        """Verify l_avg() raises ValueError when zone has no base stations"""
        zone = Zone(
            name="Empty Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=[]
        )
        
        with self.assertRaises(ValueError) as context:
            zone.l_avg()
        
        self.assertIn("no base stations", str(context.exception))


class TestZoneClusterSelection(unittest.TestCase):
    """Test cluster station selection logic"""
    
    def test_choose_cluster_stations_selects_three_stations_with_different_frequencies(self):
        """Verify choose_cluster_stations() selects 3 stations with distinct frequencies"""
        stations = [
            BaseStation(1, "S1", 100.0, 2400000000, "A", 10.0, 20.0, 15.0, "5G"),
            BaseStation(2, "S2", 80.0, 2500000000, "B", 10.0, 20.0, 15.0, "5G"),
            BaseStation(3, "S3", 60.0, 2600000000, "C", 10.0, 20.0, 15.0, "5G"),
            BaseStation(4, "S4", 40.0, 2400000000, "D", 10.0, 20.0, 15.0, "5G"),
        ]
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=stations
        )
        
        chosen = zone.choose_cluster_stations()
        
        self.assertEqual(len(chosen), 3)
        frequencies = {st.frequency_hz for st in chosen}
        self.assertEqual(len(frequencies), 3)
    
    def test_choose_cluster_stations_selects_largest_diameter_stations(self):
        """Verify choose_cluster_stations() prioritizes stations with largest diameters"""
        stations = [
            BaseStation(1, "S1", 100.0, 2400000000, "A", 10.0, 20.0, 15.0, "5G"),
            BaseStation(2, "S2", 80.0, 2500000000, "B", 10.0, 20.0, 15.0, "5G"),
            BaseStation(3, "S3", 60.0, 2600000000, "C", 10.0, 20.0, 15.0, "5G"),
        ]
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=stations
        )
        
        chosen = zone.choose_cluster_stations()
        
        # Should choose all 3 as they have different frequencies
        self.assertEqual(chosen[0].base_station_id, 1)  # Largest
        self.assertEqual(chosen[1].base_station_id, 2)  # Second
        self.assertEqual(chosen[2].base_station_id, 3)  # Third
    
    def test_choose_cluster_stations_raises_error_with_less_than_three_stations(self):
        """Verify choose_cluster_stations() raises ValueError with fewer than 3 stations"""
        stations = [
            BaseStation(1, "S1", 100.0, 2400000000, "A", 10.0, 20.0, 15.0, "5G"),
            BaseStation(2, "S2", 80.0, 2500000000, "B", 10.0, 20.0, 15.0, "5G"),
        ]
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=stations
        )
        
        with self.assertRaises(ValueError) as context:
            zone.choose_cluster_stations()
        
        self.assertIn("at least 3", str(context.exception))
    
    def test_choose_cluster_stations_raises_error_without_three_distinct_frequencies(self):
        """Verify choose_cluster_stations() raises ValueError when stations lack 3 distinct frequencies"""
        stations = [
            BaseStation(1, "S1", 100.0, 2400000000, "A", 10.0, 20.0, 15.0, "5G"),
            BaseStation(2, "S2", 80.0, 2400000000, "B", 10.0, 20.0, 15.0, "5G"),
            BaseStation(3, "S3", 60.0, 2500000000, "C", 10.0, 20.0, 15.0, "5G"),
        ]
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=stations
        )
        
        with self.assertRaises(ValueError) as context:
            zone.choose_cluster_stations()
        
        self.assertIn("distinct frequencies", str(context.exception))


class TestZoneClusterC(unittest.TestCase):
    """Test cluster C value calculation"""
    
    def test_cluster_c_calculates_using_formula_with_sorted_diameters(self):
        """Verify cluster_c() calculates C = D1^(5/2) + D2^(3/2) + D3^(1/2) with sorted diameters"""
        stations = [
            BaseStation(1, "S1", 100.0, 2400000000, "A", 10.0, 20.0, 15.0, "5G"),
            BaseStation(2, "S2", 80.0, 2500000000, "B", 10.0, 20.0, 15.0, "5G"),
            BaseStation(3, "S3", 60.0, 2600000000, "C", 10.0, 20.0, 15.0, "5G"),
        ]
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=stations
        )
        
        c = zone.cluster_c(stations)
        
        diameters = sorted([st.diameter_km() for st in stations], reverse=True)
        expected_c = (diameters[0] ** (5/2)) + (diameters[1] ** (3/2)) + (diameters[2] ** (1/2))
        
        self.assertAlmostEqual(c, expected_c, places=10)
    
    def test_cluster_c_raises_error_when_not_exactly_three_stations(self):
        """Verify cluster_c() raises ValueError when stations list length is not 3"""
        stations = [
            BaseStation(1, "S1", 100.0, 2400000000, "A", 10.0, 20.0, 15.0, "5G"),
            BaseStation(2, "S2", 80.0, 2500000000, "B", 10.0, 20.0, 15.0, "5G"),
        ]
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=stations
        )
        
        with self.assertRaises(ValueError) as context:
            zone.cluster_c(stations)
        
        self.assertIn("length 3", str(context.exception))


class TestZoneNStations(unittest.TestCase):
    """Test total base station count calculation"""
    
    def test_n_stations_calculates_as_l_divided_by_c_when_handover_ok(self):
        """Verify n_stations() returns L/C when handover is OK"""
        stations = [
            BaseStation(1, "S1", 100.0, 2400000000, "A", 10.0, 20.0, 15.0, "5G"),
            BaseStation(2, "S2", 80.0, 2500000000, "B", 10.0, 20.0, 15.0, "5G"),
            BaseStation(3, "S3", 60.0, 2600000000, "C", 10.0, 20.0, 15.0, "5G"),
        ]
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=stations
        )
        
        l = zone.l_avg()
        c = zone.cluster_c(stations)
        expected_n = l / c
        
        n = zone.n_stations(cluster_stations=stations)
        
        self.assertAlmostEqual(n, expected_n, places=10)
    
    def test_n_stations_multiplies_by_1_4_when_handover_not_ok(self):
        """Verify n_stations() multiplies result by 1.4 when handover is not OK"""
        stations = [
            BaseStation(1, "S1", 100.0, 2400000000, "A", 10.0, 20.0, 25.0, "5G"),  # handover_avg > max
            BaseStation(2, "S2", 80.0, 2500000000, "B", 10.0, 20.0, 25.0, "5G"),
            BaseStation(3, "S3", 60.0, 2600000000, "C", 10.0, 20.0, 25.0, "5G"),
        ]
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=stations
        )
        
        l = zone.l_avg()
        c = zone.cluster_c(stations)
        expected_n = (l / c) * 1.4
        
        n = zone.n_stations(cluster_stations=stations)
        
        self.assertAlmostEqual(n, expected_n, places=10)


class TestZoneIsHandoverOk(unittest.TestCase):
    """Test zone-level handover validation"""
    
    def test_is_handover_ok_returns_true_when_all_stations_have_good_handover(self):
        """Verify is_handover_ok() returns True when all stations have valid handover"""
        stations = [
            BaseStation(1, "S1", 100.0, 2400000000, "A", 10.0, 20.0, 15.0, "5G"),
            BaseStation(2, "S2", 80.0, 2500000000, "B", 10.0, 20.0, 12.0, "5G"),
        ]
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=stations
        )
        
        self.assertTrue(zone.is_handover_ok())
    
    def test_is_handover_ok_returns_false_when_any_station_has_bad_handover(self):
        """Verify is_handover_ok() returns False when at least one station has invalid handover"""
        stations = [
            BaseStation(1, "S1", 100.0, 2400000000, "A", 10.0, 20.0, 15.0, "5G"),
            BaseStation(2, "S2", 80.0, 2500000000, "B", 10.0, 20.0, 25.0, "5G"),  # Bad handover
        ]
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=stations
        )
        
        self.assertFalse(zone.is_handover_ok())
    
    def test_is_handover_ok_returns_none_when_all_stations_have_missing_handover(self):
        """Verify is_handover_ok() returns None when all stations have no handover data"""
        stations = [
            BaseStation(1, "S1", 100.0, 2400000000, "A", None, None, None, "5G"),
            BaseStation(2, "S2", 80.0, 2500000000, "B", None, None, None, "5G"),
        ]
        
        zone = Zone(
            name="Test Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=stations
        )
        
        self.assertIsNone(zone.is_handover_ok())
    
    def test_is_handover_ok_returns_none_when_no_base_stations(self):
        """Verify is_handover_ok() returns None for empty zone"""
        zone = Zone(
            name="Empty Zone",
            area_km2=100.0,
            build_type=BuildType.hard,
            base_stations=[]
        )
        
        self.assertIsNone(zone.is_handover_ok())


if __name__ == '__main__':
    unittest.main()

