"""
Integration tests for nimble-llm-caller package.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, Mock

from nimble_llm_caller import LLMContentGenerator, ConfigManager
from nimble_llm_caller.models.request import ResponseFormat


class TestIntegration:
    """Integration tests for the complete package."""
    
    @patch('nimble_llm_caller.core.llm_caller.litellm.completion')
    def test_end_to_end_single_call(self, mock_completion, temp_prompts_file, temp_output_dir, mock_env_vars):
        """Test complete end-to-end single call workflow."""
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Hello World! This is a test response."
        mock_response.usage = Mock()
        mock_response.usage.dict.return_value = {"total_tokens": 25}
        mock_response.model = "gpt-4o"
        mock_completion.return_value = mock_response
        
        # Create generator
        generator = LLMContentGenerator(
            prompt_file_path=temp_prompts_file,
            output_dir=temp_output_dir
        )
        
        # Make call
        response = generator.call_single(
            prompt_key="simple_prompt",
            substitutions={"name": "World"},
            response_format=ResponseFormat.TEXT
        )
        
        # Verify response
        assert response.is_success
        assert response.content == "Hello World! This is a test response."
        assert response.prompt_key == "simple_prompt"
        assert response.model == "gpt-4o"
        
        # Verify LiteLLM was called correctly
        mock_completion.assert_called_once()
        call_args = mock_completion.call_args
        assert call_args[1]["model"] == "gpt-4o"
        assert len(call_args[1]["messages"]) > 0
        assert "Say hello to World" in call_args[1]["messages"][0]["content"]
    
    @patch('nimble_llm_caller.core.llm_caller.litellm.completion')
    def test_end_to_end_batch_call(self, mock_completion, temp_prompts_file, temp_output_dir, mock_env_vars):
        """Test complete end-to-end batch call workflow."""
        # Setup mock responses
        mock_responses = []
        for i in range(2):
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = f"Response {i+1}"
            mock_response.usage = Mock()
            mock_response.usage.dict.return_value = {"total_tokens": 20}
            mock_response.model = "gpt-4o"
            mock_responses.append(mock_response)
        
        mock_completion.side_effect = mock_responses
        
        # Create generator
        generator = LLMContentGenerator(
            prompt_file_path=temp_prompts_file,
            output_dir=temp_output_dir
        )
        
        # Make batch call
        batch_response = generator.call_batch(
            prompt_keys=["simple_prompt", "complex_prompt"],
            shared_substitutions={"name": "World", "topic": "AI", "detail_level": "high"},
            parallel=False  # Sequential for predictable testing
        )
        
        # Verify batch response
        assert batch_response.total_requests == 2
        assert len(batch_response.responses) == 2
        assert batch_response.success_rate == 100.0
        
        # Verify individual responses
        successful_responses = batch_response.get_successful_responses()
        assert len(successful_responses) == 2
        
        for i, response in enumerate(successful_responses):
            assert response.is_success
            assert response.content == f"Response {i+1}"
    
    def test_config_manager_integration(self, mock_env_vars):
        """Test configuration manager integration."""
        # Create temporary config file
        config_data = {
            "models": {
                "test-model": {
                    "provider": "openai",
                    "api_key_env": "OPENAI_API_KEY",
                    "default_params": {
                        "temperature": 0.5,
                        "max_tokens": 1000
                    }
                }
            },
            "output": {
                "default_format": "json",
                "save_raw_responses": True
            },
            "logging": {
                "level": "DEBUG"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            # Test config manager
            config_manager = ConfigManager(config_path)
            
            # Verify configuration loaded
            assert "test-model" in config_manager.list_available_models()
            
            # Test API key retrieval
            api_key = config_manager.get_api_key("test-model")
            assert api_key == "test-openai-key"
            
            # Test parameter merging
            params = config_manager.get_model_params(
                "test-model",
                prompt_params={"temperature": 0.7},
                call_params={"max_tokens": 2000}
            )
            
            assert params["temperature"] == 0.7  # Prompt override
            assert params["max_tokens"] == 2000  # Call override
            
        finally:
            os.unlink(config_path)
    
    @patch('nimble_llm_caller.core.llm_caller.litellm.completion')
    def test_json_response_parsing(self, mock_completion, temp_prompts_file, temp_output_dir, mock_env_vars):
        """Test JSON response parsing integration."""
        # Setup mock JSON response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '{"title": "Test Title", "summary": "Test summary"}'
        mock_response.usage = Mock()
        mock_response.usage.dict.return_value = {"total_tokens": 30}
        mock_response.model = "gpt-4o"
        mock_completion.return_value = mock_response
        
        # Create generator
        generator = LLMContentGenerator(
            prompt_file_path=temp_prompts_file,
            output_dir=temp_output_dir
        )
        
        # Make call expecting JSON
        response = generator.call_single(
            prompt_key="json_prompt",
            substitutions={"content": "Test content"},
            response_format=ResponseFormat.JSON
        )
        
        # Verify JSON parsing
        assert response.is_success
        assert isinstance(response.parsed_content, dict)
        assert response.parsed_content["title"] == "Test Title"
        assert response.parsed_content["summary"] == "Test summary"
    
    @patch('nimble_llm_caller.core.llm_caller.litellm.completion')
    def test_error_handling_integration(self, mock_completion, temp_prompts_file, temp_output_dir, mock_env_vars):
        """Test error handling integration."""
        # Setup mock to raise exception
        mock_completion.side_effect = Exception("API Error")
        
        # Create generator
        generator = LLMContentGenerator(
            prompt_file_path=temp_prompts_file,
            output_dir=temp_output_dir
        )
        
        # Make call that will fail
        response = generator.call_single(
            prompt_key="simple_prompt",
            substitutions={"name": "World"}
        )
        
        # Verify error handling
        assert not response.is_success
        assert "API Error" in response.error_message
        assert response.content is None
    
    def test_prompt_validation_integration(self, temp_prompts_file):
        """Test prompt validation integration."""
        from nimble_llm_caller import PromptManager
        
        # Create prompt manager
        manager = PromptManager(temp_prompts_file)
        
        # Test validation of existing prompt
        validation = manager.validate_prompt_structure("simple_prompt")
        assert validation["valid"] is True
        
        # Test validation of non-existent prompt
        validation = manager.validate_prompt_structure("nonexistent_prompt")
        assert validation["valid"] is False
        
        # Test variable extraction
        variables = manager.extract_variables("simple_prompt")
        assert "name" in variables
    
    def test_statistics_integration(self, temp_prompts_file, temp_output_dir, mock_env_vars):
        """Test statistics collection integration."""
        # Create generator
        generator = LLMContentGenerator(
            prompt_file_path=temp_prompts_file,
            output_dir=temp_output_dir
        )
        
        # Get initial statistics
        initial_stats = generator.get_session_statistics()
        assert initial_stats["total_requests"] == 0
        
        # Mock a successful call
        with patch('nimble_llm_caller.core.llm_caller.litellm.completion') as mock_completion:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Test response"
            mock_response.usage = Mock()
            mock_response.usage.dict.return_value = {"total_tokens": 25}
            mock_response.model = "gpt-4o"
            mock_completion.return_value = mock_response
            
            # Make call
            generator.call_single(
                prompt_key="simple_prompt",
                substitutions={"name": "World"}
            )
        
        # Check updated statistics
        updated_stats = generator.get_session_statistics()
        assert updated_stats["total_requests"] == 1
        assert updated_stats["successful_requests"] == 1
        assert updated_stats["success_rate"] == 100.0