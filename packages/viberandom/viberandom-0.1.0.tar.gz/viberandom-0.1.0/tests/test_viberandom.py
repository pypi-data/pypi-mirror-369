import pytest
from unittest.mock import patch, MagicMock
from viberandom import viberandom, viberandom_single


class TestVibeRandom:
    
    def test_viberandom_returns_correct_count(self):
        """Test that viberandom returns the requested number of values."""
        result = viberandom(1, 10, "test", 5)
        assert len(result) == 5
        
    def test_viberandom_respects_range(self):
        """Test that all returned numbers are within the specified range."""
        result = viberandom(10, 20, "test", 10)
        for num in result:
            assert 10 <= num <= 20
            
    def test_viberandom_single_returns_int(self):
        """Test that viberandom_single returns a single integer."""
        result = viberandom_single(1, 100, "lucky")
        assert isinstance(result, int)
        assert 1 <= result <= 100
        
    def test_viberandom_default_parameters(self):
        """Test viberandom with default parameters."""
        result = viberandom()
        assert len(result) == 1
        assert 1 <= result[0] <= 100
        
    @patch('viberandom.ai.genai.GenerativeModel')
    def test_viberandom_with_mocked_ai(self, mock_model):
        """Test viberandom with mocked AI response."""
        # Mock the AI response
        mock_response = MagicMock()
        mock_response.text = '{"numbers": [7, 77, 777]}'
        mock_instance = mock_model.return_value
        mock_instance.generate_content.return_value = mock_response
        
        with patch('viberandom.ai.configure_gemini'):
            result = viberandom(1, 1000, "lucky", 3)
            
        assert result == [7, 77, 777]
        
    @patch('viberandom.ai.genai.GenerativeModel')
    def test_viberandom_fallback_on_error(self, mock_model):
        """Test that viberandom falls back to regular random on AI error."""
        # Make AI throw an exception
        mock_instance = mock_model.return_value
        mock_instance.generate_content.side_effect = Exception("API Error")
        
        with patch('viberandom.ai.configure_gemini'):
            result = viberandom(1, 10, "test", 3)
            
        assert len(result) == 3
        for num in result:
            assert 1 <= num <= 10
            
    def test_viberandom_missing_api_key(self):
        """Test that missing API key raises appropriate error."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable not set"):
                viberandom(1, 10, "test")
                
    @patch('viberandom.ai.genai.GenerativeModel')
    def test_viberandom_invalid_json_response(self, mock_model):
        """Test handling of invalid JSON response from AI."""
        mock_response = MagicMock()
        mock_response.text = 'invalid json response'
        mock_instance = mock_model.return_value
        mock_instance.generate_content.return_value = mock_response
        
        with patch('viberandom.ai.configure_gemini'):
            result = viberandom(1, 10, "test", 2)
            
        # Should fallback to regular random
        assert len(result) == 2
        for num in result:
            assert 1 <= num <= 10