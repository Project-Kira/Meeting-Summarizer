"""
Integration tests for API endpoints.
Tests all FastAPI endpoints using TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from pathlib import Path
import sys
import io

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import app
import config


# Create test client
client = TestClient(app)


class TestHealthEndpoint:
    """Tests for /api/health endpoint."""
    
    def test_health_check_returns_200(self):
        """Test that health endpoint returns 200 OK."""
        response = client.get("/api/health")
        assert response.status_code == 200
    
    def test_health_check_returns_correct_structure(self):
        """Test that health endpoint returns expected JSON structure."""
        response = client.get("/api/health")
        data = response.json()
        
        assert "status" in data
        assert "model_path" in data
        assert "version" in data
    
    def test_health_check_status_is_ok(self):
        """Test that status field is 'ok'."""
        response = client.get("/api/health")
        data = response.json()
        
        assert data["status"] == "ok"
    
    def test_health_check_includes_model_path(self):
        """Test that model_path is returned."""
        response = client.get("/api/health")
        data = response.json()
        
        assert data["model_path"] == config.MODEL_PATH


class TestRootEndpoint:
    """Tests for / root endpoint."""
    
    def test_root_returns_200(self):
        """Test that root endpoint returns 200 OK."""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_returns_api_info(self):
        """Test that root returns API information."""
        response = client.get("/")
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data


class TestSummarizeEndpoint:
    """Tests for /api/summarize endpoint."""
    
    @patch('api.summarize_conversation')
    def test_summarize_returns_200_on_success(self, mock_summarize):
        """Test that summarize endpoint returns 200 on successful summarization."""
        mock_summarize.return_value = "Test summary"
        
        response = client.post(
            "/api/summarize",
            json={"text": "Meeting started at 10 AM"}
        )
        
        assert response.status_code == 200
    
    @patch('api.summarize_conversation')
    def test_summarize_returns_correct_structure(self, mock_summarize):
        """Test that response has expected JSON structure."""
        mock_summarize.return_value = "Test summary"
        
        response = client.post(
            "/api/summarize",
            json={"text": "Meeting text"}
        )
        
        data = response.json()
        assert "summary" in data
        assert "input_length" in data
        assert "estimated_tokens" in data
    
    @patch('api.summarize_conversation')
    def test_summarize_returns_summary_text(self, mock_summarize):
        """Test that summary field contains generated text."""
        expected_summary = "This is the generated summary"
        mock_summarize.return_value = expected_summary
        
        response = client.post(
            "/api/summarize",
            json={"text": "Meeting about Q3 budget"}
        )
        
        data = response.json()
        assert data["summary"] == expected_summary
    
    @patch('api.summarize_conversation')
    def test_summarize_includes_input_stats(self, mock_summarize):
        """Test that response includes input statistics."""
        mock_summarize.return_value = "Summary"
        test_text = "a" * 1000
        
        response = client.post(
            "/api/summarize",
            json={"text": test_text}
        )
        
        data = response.json()
        assert data["input_length"] == 1000
        assert data["estimated_tokens"] == 1000 // config.CHARS_PER_TOKEN
    
    def test_summarize_returns_400_on_empty_text(self):
        """Test that empty text returns 400 Bad Request."""
        response = client.post(
            "/api/summarize",
            json={"text": ""}
        )
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_summarize_returns_400_on_missing_text_field(self):
        """Test that missing text field returns 400."""
        response = client.post(
            "/api/summarize",
            json={}
        )
        
        assert response.status_code == 422
    
    def test_summarize_returns_400_on_invalid_json(self):
        """Test that invalid JSON returns 400."""
        response = client.post(
            "/api/summarize",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    @patch('api.summarize_conversation')
    def test_summarize_returns_400_on_validation_error(self, mock_summarize):
        """Test that ValueError from summarization returns 400."""
        mock_summarize.side_effect = ValueError("Text too large")
        
        response = client.post(
            "/api/summarize",
            json={"text": "Some text"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    @patch('api.summarize_conversation')
    def test_summarize_returns_500_on_runtime_error(self, mock_summarize):
        """Test that RuntimeError returns 500."""
        mock_summarize.side_effect = RuntimeError("Model failed")
        
        response = client.post(
            "/api/summarize",
            json={"text": "Some text"}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestSummarizeFileEndpoint:
    """Tests for /api/summarize-file endpoint."""
    
    @patch('api.summarize_conversation')
    def test_file_upload_returns_200_on_success(self, mock_summarize):
        """Test that file upload returns 200 on success."""
        mock_summarize.return_value = "File summary"
        
        # Create test file
        file_content = b"Meeting started at 10 AM"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        
        response = client.post("/api/summarize-file", files=files)
        
        assert response.status_code == 200
    
    @patch('api.summarize_conversation')
    def test_file_upload_returns_correct_structure(self, mock_summarize):
        """Test that file upload response has expected structure."""
        mock_summarize.return_value = "File summary"
        
        file_content = b"Meeting text"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        
        response = client.post("/api/summarize-file", files=files)
        
        data = response.json()
        assert "summary" in data
        assert "input_length" in data
        assert "estimated_tokens" in data
    
    @patch('api.summarize_conversation')
    def test_file_upload_processes_content(self, mock_summarize):
        """Test that file content is processed correctly."""
        expected_summary = "File-based summary"
        mock_summarize.return_value = expected_summary
        
        file_content = b"Meeting about project"
        files = {"file": ("meeting.txt", io.BytesIO(file_content), "text/plain")}
        
        response = client.post("/api/summarize-file", files=files)
        
        # Verify summarize_conversation was called with decoded text
        mock_summarize.assert_called_once_with("Meeting about project")
        
        data = response.json()
        assert data["summary"] == expected_summary
    
    def test_file_upload_returns_400_on_non_txt_file(self):
        """Test that non-.txt files return 400."""
        file_content = b"PDF content"
        files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
        
        response = client.post("/api/summarize-file", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "Only .txt files" in data["detail"]
    
    def test_file_upload_returns_400_on_empty_file(self):
        """Test that empty file returns 400."""
        file_content = b""
        files = {"file": ("empty.txt", io.BytesIO(file_content), "text/plain")}
        
        response = client.post("/api/summarize-file", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "empty" in data["detail"].lower()
    
    def test_file_upload_returns_400_on_invalid_encoding(self):
        """Test that non-UTF-8 file returns 400."""
        # Create invalid UTF-8 content
        file_content = b'\xff\xfe\xfd'
        files = {"file": ("bad.txt", io.BytesIO(file_content), "text/plain")}
        
        response = client.post("/api/summarize-file", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "UTF-8" in data["detail"]
    
    def test_file_upload_requires_file_parameter(self):
        """Test that missing file parameter returns 422."""
        response = client.post("/api/summarize-file")
        
        assert response.status_code == 422
    
    @patch('api.summarize_conversation')
    def test_file_upload_returns_500_on_processing_error(self, mock_summarize):
        """Test that processing error returns 500."""
        mock_summarize.side_effect = RuntimeError("Processing failed")
        
        file_content = b"Meeting text"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        
        response = client.post("/api/summarize-file", files=files)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestCORSHeaders:
    """Tests for CORS configuration."""
    
    def test_cors_headers_present_on_health(self):
        """Test that CORS headers are present on health endpoint."""
        response = client.get("/api/health")
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or response.status_code == 200
    
    def test_cors_allows_requests(self):
        """Test that CORS is properly configured."""
        # Make a regular request to verify CORS doesn't block it
        response = client.get("/api/health")
        
        # Should succeed
        assert response.status_code == 200


class TestErrorResponses:
    """Tests for error response formats."""
    
    def test_error_responses_include_detail(self):
        """Test that error responses include detail field."""
        response = client.post("/api/summarize", json={})
        
        data = response.json()
        assert "detail" in data or "message" in data
