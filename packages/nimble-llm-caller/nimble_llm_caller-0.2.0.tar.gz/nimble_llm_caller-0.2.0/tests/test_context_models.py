"""
Tests for context management data models.
"""

import pytest
from pathlib import Path
from nimble_llm_caller.models.request import FileAttachment, ContextAnalysis, ProcessedFile, LLMRequest
from nimble_llm_caller.models.context_config import ContextConfig, ModelCapacity, ContextStrategy


class TestFileAttachment:
    """Tests for FileAttachment model."""
    
    def test_file_attachment_creation(self):
        """Test basic FileAttachment creation."""
        attachment = FileAttachment(
            file_path="test.txt",
            content_type="text/plain",
            content="Hello world",
            token_estimate=2
        )
        
        assert attachment.file_path == "test.txt"
        assert attachment.content_type == "text/plain"
        assert attachment.content == "Hello world"
        assert attachment.token_estimate == 2
        assert attachment.processing_metadata == {}
    
    def test_file_attachment_with_path_object(self):
        """Test FileAttachment with Path object."""
        path = Path("test.txt")
        attachment = FileAttachment(file_path=path)
        
        assert attachment.file_path == path
        assert attachment.content_type is None
        assert attachment.content is None


class TestContextAnalysis:
    """Tests for ContextAnalysis model."""
    
    def test_context_analysis_creation(self):
        """Test basic ContextAnalysis creation."""
        analysis = ContextAnalysis(
            total_tokens=1000,
            text_tokens=800,
            file_tokens=200,
            model_capacity=4096,
            requires_upshift=False,
            requires_chunking=False,
            recommended_models=["gpt-4o-mini"]
        )
        
        assert analysis.total_tokens == 1000
        assert analysis.text_tokens == 800
        assert analysis.file_tokens == 200
        assert analysis.model_capacity == 4096
        assert not analysis.requires_upshift
        assert not analysis.requires_chunking
        assert analysis.recommended_models == ["gpt-4o-mini"]
    
    def test_context_analysis_overflow_detection(self):
        """Test context analysis with overflow conditions."""
        analysis = ContextAnalysis(
            total_tokens=5000,
            text_tokens=4000,
            file_tokens=1000,
            model_capacity=4096,
            requires_upshift=True,
            requires_chunking=True,
            recommended_models=["gpt-4o", "claude-3-sonnet-20240229"]
        )
        
        assert analysis.requires_upshift
        assert analysis.requires_chunking
        assert len(analysis.recommended_models) == 2


class TestProcessedFile:
    """Tests for ProcessedFile model."""
    
    def test_processed_file_creation(self):
        """Test basic ProcessedFile creation."""
        processed = ProcessedFile(
            original_path="test.txt",
            content="Processed content",
            content_type="text/plain",
            token_count=3,
            processing_method="direct_read"
        )
        
        assert processed.original_path == "test.txt"
        assert processed.content == "Processed content"
        assert processed.content_type == "text/plain"
        assert processed.token_count == 3
        assert processed.processing_method == "direct_read"
        assert processed.warnings == []
    
    def test_processed_file_with_warnings(self):
        """Test ProcessedFile with processing warnings."""
        processed = ProcessedFile(
            original_path="test.pdf",
            content="Extracted text",
            content_type="application/pdf",
            token_count=10,
            processing_method="pdf_extraction",
            warnings=["Some formatting lost", "Images skipped"]
        )
        
        assert len(processed.warnings) == 2
        assert "Some formatting lost" in processed.warnings


class TestEnhancedLLMRequest:
    """Tests for enhanced LLMRequest model."""
    
    def test_enhanced_request_creation(self):
        """Test LLMRequest with context management fields."""
        attachment = FileAttachment(file_path="test.txt", content="Hello")
        
        request = LLMRequest(
            prompt_key="test_prompt",
            model="gpt-4o-mini",
            file_attachments=[attachment],
            context_strategy="upshift_first",
            max_cost_multiplier=3.0
        )
        
        assert request.prompt_key == "test_prompt"
        assert request.model == "gpt-4o-mini"
        assert len(request.file_attachments) == 1
        assert request.context_strategy == "upshift_first"
        assert request.max_cost_multiplier == 3.0
        assert request.context_analysis is None
        assert request.processed_files == []
    
    def test_request_backward_compatibility(self):
        """Test that existing LLMRequest usage still works."""
        request = LLMRequest(
            prompt_key="test_prompt",
            model="gpt-4o-mini",
            substitutions={"name": "test"}
        )
        
        assert request.prompt_key == "test_prompt"
        assert request.model == "gpt-4o-mini"
        assert request.substitutions == {"name": "test"}
        assert request.file_attachments == []
        assert request.max_cost_multiplier == 2.0


class TestModelCapacity:
    """Tests for ModelCapacity model."""
    
    def test_model_capacity_creation(self):
        """Test basic ModelCapacity creation."""
        capacity = ModelCapacity(
            model_name="gpt-4o-mini",
            max_tokens=128000,
            cost_per_token=0.00015,
            cost_per_output_token=0.0006,
            priority=1,
            provider="openai",
            supports_vision=True
        )
        
        assert capacity.model_name == "gpt-4o-mini"
        assert capacity.max_tokens == 128000
        assert capacity.cost_per_token == 0.00015
        assert capacity.cost_per_output_token == 0.0006
        assert capacity.priority == 1
        assert capacity.provider == "openai"
        assert capacity.supports_vision


class TestContextConfig:
    """Tests for ContextConfig model."""
    
    def test_context_config_defaults(self):
        """Test ContextConfig with default values."""
        config = ContextConfig()
        
        assert config.default_strategy == ContextStrategy.UPSHIFT_FIRST
        assert config.max_cost_multiplier == 2.0
        assert config.chunk_overlap_tokens == 100
        assert config.max_chunks == 10
        assert config.max_file_size_mb == 50
        assert config.enable_interaction_logging
        assert config.log_file_path == "llm_interactions.log"
        assert config.max_log_size_mb == 100
        assert len(config.supported_file_types) > 0
    
    def test_context_config_custom_values(self):
        """Test ContextConfig with custom values."""
        config = ContextConfig(
            default_strategy=ContextStrategy.CHUNK_FIRST,
            max_cost_multiplier=5.0,
            chunk_overlap_tokens=200,
            enable_interaction_logging=False
        )
        
        assert config.default_strategy == ContextStrategy.CHUNK_FIRST
        assert config.max_cost_multiplier == 5.0
        assert config.chunk_overlap_tokens == 200
        assert not config.enable_interaction_logging
    
    def test_default_model_capacities(self):
        """Test that default model capacities are loaded."""
        config = ContextConfig()
        default_capacities = config.get_default_model_capacities()
        
        assert len(default_capacities) > 0
        assert any(cap.model_name == "gpt-4o-mini" for cap in default_capacities)
        assert any(cap.model_name == "claude-3-sonnet-20240229" for cap in default_capacities)
        
        # Test that priorities are set correctly
        priorities = [cap.priority for cap in default_capacities]
        assert len(set(priorities)) == len(priorities)  # All priorities should be unique


class TestContextStrategy:
    """Tests for ContextStrategy enum."""
    
    def test_context_strategy_values(self):
        """Test ContextStrategy enum values."""
        assert ContextStrategy.UPSHIFT_FIRST == "upshift_first"
        assert ContextStrategy.CHUNK_FIRST == "chunk_first"
        assert ContextStrategy.UPSHIFT_ONLY == "upshift_only"
        assert ContextStrategy.CHUNK_ONLY == "chunk_only"
    
    def test_context_strategy_in_config(self):
        """Test using ContextStrategy in configuration."""
        config = ContextConfig(default_strategy=ContextStrategy.CHUNK_ONLY)
        assert config.default_strategy == ContextStrategy.CHUNK_ONLY
        assert config.default_strategy == "chunk_only"