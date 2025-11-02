"""
Unit tests for inference.py module.
Tests model loading, text generation, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import inference
import config


class TestGetLLM:
    """Tests for _get_llm() function."""
    
    def setup_method(self):
        """Reset global model instance before each test."""
        inference._llm = None
    
    @patch('inference.Llama')
    @patch('inference.Path')
    def test_model_loads_successfully(self, mock_path, mock_llama):
        """Test that model loads correctly on first call."""
        # Setup mocks
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        mock_llm_instance = Mock()
        mock_llama.return_value = mock_llm_instance
        
        # Call function
        result = inference._get_llm()
        
        # Verify
        assert result == mock_llm_instance
        mock_llama.assert_called_once_with(
            model_path=config.MODEL_PATH,
            n_ctx=config.N_CTX,
            n_threads=config.N_THREADS,
            n_gpu_layers=config.N_GPU_LAYERS,
            verbose=False
        )
    
    @patch('inference.Llama')
    @patch('inference.Path')
    def test_model_reused_on_subsequent_calls(self, mock_path, mock_llama):
        """Test that model is loaded once and reused."""
        # Setup mocks
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        mock_llm_instance = Mock()
        mock_llama.return_value = mock_llm_instance
        
        # Call function twice
        result1 = inference._get_llm()
        result2 = inference._get_llm()
        
        # Verify model loaded only once
        assert result1 == result2
        assert mock_llama.call_count == 1
    
    @patch('inference.Path')
    def test_raises_error_when_model_not_found(self, mock_path):
        """Test that FileNotFoundError is raised when model doesn't exist."""
        # Setup mock
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        
        # Verify error is raised
        with pytest.raises(FileNotFoundError) as exc_info:
            inference._get_llm()
        
        assert "Model file not found" in str(exc_info.value)
    
    @patch('inference.Llama')
    @patch('inference.Path')
    def test_raises_runtime_error_on_load_failure(self, mock_path, mock_llama):
        """Test that RuntimeError is raised when model loading fails."""
        # Setup mocks
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        mock_llama.side_effect = Exception("CUDA out of memory")
        
        # Verify error is raised
        with pytest.raises(RuntimeError) as exc_info:
            inference._get_llm()
        
        assert "Model loading failed" in str(exc_info.value)


class TestRunLocalLLM:
    """Tests for run_local_llm() function."""
    
    def setup_method(self):
        """Reset global model instance before each test."""
        inference._llm = None
    
    def test_raises_error_on_empty_prompt(self):
        """Test that ValueError is raised for empty prompt."""
        with pytest.raises(ValueError) as exc_info:
            inference.run_local_llm("")
        
        assert "Prompt cannot be empty" in str(exc_info.value)
    
    def test_raises_error_on_whitespace_only_prompt(self):
        """Test that ValueError is raised for whitespace-only prompt."""
        with pytest.raises(ValueError) as exc_info:
            inference.run_local_llm("   \n\t  ")
        
        assert "Prompt cannot be empty" in str(exc_info.value)
    
    @patch('inference._get_llm')
    def test_formats_prompt_correctly(self, mock_get_llm):
        """Test that prompt is formatted with Mistral instruction tags."""
        # Setup mock
        mock_llm = Mock()
        mock_llm.return_value = {
            'choices': [{'text': 'Generated summary'}]
        }
        mock_get_llm.return_value = mock_llm
        
        # Call function
        inference.run_local_llm("Test prompt")
        
        # Verify prompt formatting
        call_args = mock_llm.call_args
        assert call_args[0][0] == "[INST] Test prompt [/INST]"
    
    @patch('inference._get_llm')
    def test_returns_generated_text(self, mock_get_llm):
        """Test that generated text is returned correctly."""
        # Setup mock
        mock_llm = Mock()
        mock_llm.return_value = {
            'choices': [{'text': '  Generated summary  '}]
        }
        mock_get_llm.return_value = mock_llm
        
        # Call function
        result = inference.run_local_llm("Test prompt")
        
        # Verify
        assert result == "Generated summary"  # Should be stripped
    
    @patch('inference._get_llm')
    def test_uses_correct_parameters(self, mock_get_llm):
        """Test that LLM is called with correct parameters."""
        # Setup mock
        mock_llm = Mock()
        mock_llm.return_value = {
            'choices': [{'text': 'Summary'}]
        }
        mock_get_llm.return_value = mock_llm
        
        # Call function with custom max_tokens
        inference.run_local_llm("Test prompt", max_tokens=256)
        
        # Verify parameters
        call_kwargs = mock_llm.call_args[1]
        assert call_kwargs['max_tokens'] == 256
        assert call_kwargs['temperature'] == config.TEMPERATURE
        assert call_kwargs['top_p'] == config.TOP_P
        assert call_kwargs['stop'] == ["[INST]", "</s>"]
        assert call_kwargs['echo'] is False
    
    @patch('inference._get_llm')
    def test_retries_on_failure(self, mock_get_llm):
        """Test that function retries on generation failure."""
        # Setup mock to fail twice then succeed
        mock_llm = Mock()
        mock_llm.side_effect = [
            Exception("Generation failed"),
            Exception("Generation failed again"),
            {'choices': [{'text': 'Success'}]}
        ]
        mock_get_llm.return_value = mock_llm
        
        # Call function
        result = inference.run_local_llm("Test prompt")
        
        # Verify retried 3 times and got result
        assert result == "Success"
        assert mock_llm.call_count == 3
    
    @patch('inference._get_llm')
    def test_raises_error_after_max_retries(self, mock_get_llm):
        """Test that RuntimeError is raised after max retries."""
        # Setup mock to always fail
        mock_llm = Mock()
        mock_llm.side_effect = Exception("Persistent failure")
        mock_get_llm.return_value = mock_llm
        
        # Verify error is raised
        with pytest.raises(RuntimeError) as exc_info:
            inference.run_local_llm("Test prompt")
        
        assert "Failed to generate text" in str(exc_info.value)
        assert mock_llm.call_count == 3  # Should try 3 times
