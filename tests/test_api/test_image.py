import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestImageEndpoint:
    """Tests for GET /api/v1/countries/image endpoint"""

    def test_get_image_when_not_exists(self, client):
        """Test 404 error when image doesn't exist"""
        # Make request
        response = client.get("/api/v1/countries/image")
        
        # Assertions
        assert response.status_code == 404
        data = response.json()
        
        # Verify exact error format
        assert data == {"error": "Summary image not found"}
        assert "error" in data
        assert data["error"] == "Summary image not found"

    @patch('app.api.v1.services.image_service.ImageService.image_exists')
    @patch('app.api.v1.services.image_service.ImageService.get_image_path')
    def test_get_image_when_exists(self, mock_get_path, mock_exists, client, tmp_path):
        """Test successful image retrieval when it exists"""
        # Create a temporary image file
        test_image = tmp_path / "test_summary.png"
        test_image.write_bytes(b"fake image data")
        
        # Mock the image service
        mock_exists.return_value = True
        mock_get_path.return_value = str(test_image)
        
        # Make request
        response = client.get("/api/v1/countries/image")
        
        # Assertions
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert "content-disposition" in response.headers
        assert "summary.png" in response.headers["content-disposition"]

    def test_image_endpoint_path(self, client):
        """Test that the endpoint is at the correct path"""
        response = client.get("/api/v1/countries/image")
        
        # Should return 404 (image not found) not 404 (endpoint not found)
        # This confirms the endpoint exists
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        # If endpoint didn't exist, we'd get a different 404 format from FastAPI

    def test_image_error_response_format(self, client):
        """Test that error response matches specification exactly"""
        response = client.get("/api/v1/countries/image")
        
        # Verify response format matches spec
        assert response.status_code == 404
        data = response.json()
        
        # Should have exactly one key: "error"
        assert len(data) == 1
        assert list(data.keys()) == ["error"]
        assert isinstance(data["error"], str)
        assert data["error"] == "Summary image not found"
        
        # Should NOT have "detail" wrapper (common FastAPI mistake)
        assert "detail" not in data

    @patch('app.api.v1.services.image_service.ImageService.image_exists')
    def test_image_service_is_called(self, mock_exists, client):
        """Test that ImageService.image_exists is actually called"""
        mock_exists.return_value = False
        
        response = client.get("/api/v1/countries/image")
        
        # Verify the service method was called
        mock_exists.assert_called_once()
        assert response.status_code == 404
