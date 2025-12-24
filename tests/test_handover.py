"""Tests for ApiHandoverProvider functionality"""
import unittest
from unittest.mock import Mock, patch
from handover import ApiHandoverProvider


class TestApiHandoverProviderInitialization(unittest.TestCase):
    """Test ApiHandoverProvider initialization"""
    
    def test_api_handover_provider_initializes_with_correct_base_url(self):
        """Verify ApiHandoverProvider sets base URL correctly on initialization"""
        provider = ApiHandoverProvider()
        self.assertEqual(provider.base_url, "http://192.168.0.100:100/api/basestation")


class TestGetHandoverAvg(unittest.TestCase):
    """Test handover average retrieval from API"""
    
    @patch('handover.requests.get')
    def test_get_handover_avg_returns_float_on_successful_api_call(self, mock_get):
        """Verify get_handover_avg() returns float value when API responds successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "15.5"
        mock_get.return_value = mock_response
        
        provider = ApiHandoverProvider()
        result = provider.get_handover_avg(1)
        
        self.assertEqual(result, 15.5)
        mock_get.assert_called_once_with("http://192.168.0.100:100/api/basestation/1", timeout=2)
    
    @patch('handover.requests.get')
    def test_get_handover_avg_returns_none_when_api_returns_404(self, mock_get):
        """Verify get_handover_avg() returns None when API returns 404 not found"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        provider = ApiHandoverProvider()
        result = provider.get_handover_avg(999)
        
        self.assertIsNone(result)
    
if __name__ == '__main__':
    unittest.main()

