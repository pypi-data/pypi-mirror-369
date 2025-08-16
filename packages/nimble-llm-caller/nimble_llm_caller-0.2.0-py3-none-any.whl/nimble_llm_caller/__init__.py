"""
Nimble LLM Caller - A robust, multi-model LLM calling package.

This package provides comprehensive LLM calling capabilities with:
- Multi-model support through LiteLLM
- Robust JSON parsing with fallback strategies
- Batch processing for multiple prompts
- Document assembly and formatting
- Retry logic with exponential backoff
- Secure secret management
"""

from .core.llm_caller import LLMCaller
from .core.enhanced_caller import EnhancedLLMCaller as LegacyEnhancedLLMCaller
from .core.enhanced_llm_caller import EnhancedLLMCaller
from .core.enhanced_llm_caller import EnhancedLLMCaller as ContextAwareLLMCaller  # Alias for backward compatibility
from .core.content_generator import LLMContentGenerator
from .core.prompt_manager import PromptManager
from .core.document_assembler import DocumentAssembler
from .core.config_manager import ConfigManager
from .core.token_estimator import TokenEstimator
from .core.context_analyzer import ContextAnalyzer, ModelCapacity as AnalyzerModelCapacity
from .core.model_capacity_registry import ModelCapacityRegistry
from .core.model_upshifter import ModelUpshifter
from .core.file_processor import FileProcessor
from .core.content_chunker import ContentChunker
from .core.context_strategy import ContextStrategy, ContextOverflowStrategy
from .core.interaction_logger import InteractionLogger
from .models.request import LLMRequest, BatchRequest, FileAttachment, ContextAnalysis, ProcessedFile
from .models.response import LLMResponse, BatchResponse
from .models.context_config import ContextConfig, ModelCapacity, ContextStrategy as LegacyContextStrategy
from .utils.json_parser import JSONParser
from .utils.retry_strategy import RetryStrategy
from .exceptions import (
    NimbleLLMError, ContextOverflowError, FileProcessingError, 
    ModelUpshiftError, ChunkingError, TokenEstimationError,
    InteractionLoggingError, ContextStrategyError, ModelCapacityError,
    ConfigurationError, ProviderError, ValidationError
)
from .compatibility import (
    create_legacy_caller, migrate_request_format, check_compatibility,
    LegacyConfigAdapter
)

__version__ = "0.1.0"
__author__ = "Nimble Books LLC"
__email__ = "info@nimblebooks.com"

__all__ = [
    # Core classes (backward compatible)
    "LLMCaller",
    "EnhancedLLMCaller",  # New context-aware enhanced caller
    "LegacyEnhancedLLMCaller",  # Original enhanced caller
    "ContextAwareLLMCaller",  # Alias for enhanced caller
    "LLMContentGenerator",
    "PromptManager",
    "DocumentAssembler",
    "ConfigManager",
    
    # New context management classes
    "TokenEstimator",
    "ContextAnalyzer",
    "ModelCapacityRegistry",
    "ModelUpshifter",
    "FileProcessor",
    "ContentChunker",
    "ContextStrategy",
    "ContextOverflowStrategy",
    "InteractionLogger",
    
    # Model classes
    "AnalyzerModelCapacity",
    "LLMRequest",
    "BatchRequest",
    "LLMResponse", 
    "BatchResponse",
    "FileAttachment",
    "ContextAnalysis",
    "ProcessedFile",
    
    # Legacy model classes (backward compatible)
    "ContextConfig",
    "ModelCapacity",
    "LegacyContextStrategy",
    
    # Utility classes
    "JSONParser",
    "RetryStrategy",
    
    # Exception classes
    "NimbleLLMError",
    "ContextOverflowError", 
    "FileProcessingError",
    "ModelUpshiftError",
    "ChunkingError",
    "TokenEstimationError",
    "InteractionLoggingError",
    "ContextStrategyError",
    "ModelCapacityError",
    "ConfigurationError",
    "ProviderError",
    "ValidationError",
    
    # Compatibility utilities
    "create_legacy_caller",
    "migrate_request_format",
    "check_compatibility",
    "LegacyConfigAdapter",
]