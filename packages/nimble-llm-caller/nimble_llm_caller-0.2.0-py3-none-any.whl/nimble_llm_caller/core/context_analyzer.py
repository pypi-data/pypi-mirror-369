"""
Context analysis utilities for LLM requests.
"""

from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import logging

from ..models.request import LLMRequest, ContextAnalysis, FileAttachment, ProcessedFile
from .token_estimator import TokenEstimator

logger = logging.getLogger(__name__)


class ModelCapacity:
    """Model capacity information."""
    
    def __init__(self, 
                 model_name: str, 
                 max_context_tokens: int, 
                 provider: str,
                 cost_multiplier: float = 1.0,
                 supports_vision: bool = False,
                 supported_file_types: Optional[List[str]] = None):
        self.model_name = model_name
        self.max_context_tokens = max_context_tokens
        self.provider = provider
        self.cost_multiplier = cost_multiplier
        self.supports_vision = supports_vision
        self.supported_file_types = supported_file_types or []


class ContextAnalyzer:
    """Analyzes LLM request context requirements and model capacity."""
    
    # Default model capacities (tokens)
    DEFAULT_MODEL_CAPACITIES = {
        # OpenAI models
        "gpt-4": ModelCapacity("gpt-4", 8192, "openai", 1.0, False),
        "gpt-4-32k": ModelCapacity("gpt-4-32k", 32768, "openai", 2.0, False),
        "gpt-4-turbo": ModelCapacity("gpt-4-turbo", 128000, "openai", 1.5, True, ["image", "text"]),
        "gpt-4o": ModelCapacity("gpt-4o", 128000, "openai", 1.2, True, ["image", "text"]),
        "gpt-4o-mini": ModelCapacity("gpt-4o-mini", 128000, "openai", 0.8, True, ["image", "text"]),
        "gpt-3.5-turbo": ModelCapacity("gpt-3.5-turbo", 16385, "openai", 0.5, False),
        "gpt-3.5-turbo-16k": ModelCapacity("gpt-3.5-turbo-16k", 16385, "openai", 0.7, False),
        
        # Anthropic models
        "claude-3-opus": ModelCapacity("claude-3-opus", 200000, "anthropic", 3.0, True, ["image", "text"]),
        "claude-3-sonnet": ModelCapacity("claude-3-sonnet", 200000, "anthropic", 1.5, True, ["image", "text"]),
        "claude-3-haiku": ModelCapacity("claude-3-haiku", 200000, "anthropic", 0.8, True, ["image", "text"]),
        "claude-3-5-sonnet": ModelCapacity("claude-3-5-sonnet", 200000, "anthropic", 1.8, True, ["image", "text"]),
        "claude-2.1": ModelCapacity("claude-2.1", 200000, "anthropic", 1.2, False),
        "claude-2": ModelCapacity("claude-2", 100000, "anthropic", 1.0, False),
        "claude-instant": ModelCapacity("claude-instant", 100000, "anthropic", 0.6, False),
        
        # Google models
        "gemini-pro": ModelCapacity("gemini-pro", 32768, "google", 1.0, False),
        "gemini-1.5-pro": ModelCapacity("gemini-1.5-pro", 1000000, "google", 2.0, True, ["image", "text", "video"]),
        "gemini-1.5-flash": ModelCapacity("gemini-1.5-flash", 1000000, "google", 1.0, True, ["image", "text"]),
        "gemini-pro-vision": ModelCapacity("gemini-pro-vision", 32768, "google", 1.2, True, ["image", "text"]),
        
        # Cohere models
        "command": ModelCapacity("command", 4096, "cohere", 1.0, False),
        "command-light": ModelCapacity("command-light", 4096, "cohere", 0.8, False),
        "command-nightly": ModelCapacity("command-nightly", 4096, "cohere", 1.2, False),
        
        # Mistral models
        "mistral-large": ModelCapacity("mistral-large", 32768, "mistral", 2.0, False),
        "mistral-medium": ModelCapacity("mistral-medium", 32768, "mistral", 1.5, False),
        "mistral-small": ModelCapacity("mistral-small", 32768, "mistral", 1.0, False),
        "mistral-tiny": ModelCapacity("mistral-tiny", 32768, "mistral", 0.8, False),
    }
    
    def __init__(self, 
                 token_estimator: Optional[TokenEstimator] = None,
                 custom_capacities: Optional[Dict[str, ModelCapacity]] = None):
        """
        Initialize the context analyzer.
        
        Args:
            token_estimator: Token estimator instance (creates new if None)
            custom_capacities: Custom model capacity definitions
        """
        self.token_estimator = token_estimator or TokenEstimator()
        self.model_capacities = self.DEFAULT_MODEL_CAPACITIES.copy()
        
        if custom_capacities:
            self.model_capacities.update(custom_capacities)
    
    def get_model_capacity(self, model: str) -> Optional[ModelCapacity]:
        """
        Get capacity information for a model.
        
        Args:
            model: Model name (may include provider prefix)
            
        Returns:
            ModelCapacity object or None if not found
        """
        # Handle provider-prefixed models
        clean_model = model.split("/")[-1] if "/" in model else model
        
        # Direct lookup
        if clean_model in self.model_capacities:
            return self.model_capacities[clean_model]
        
        # Try pattern matching for model variants
        for known_model, capacity in self.model_capacities.items():
            if clean_model.startswith(known_model.split("-")[0]):
                logger.info(f"Using capacity from {known_model} for similar model {clean_model}")
                return capacity
        
        logger.warning(f"No capacity information found for model: {model}")
        return None
    
    def analyze_request(self, request: LLMRequest) -> ContextAnalysis:
        """
        Analyze the context requirements of an LLM request.
        
        Args:
            request: The LLM request to analyze
            
        Returns:
            ContextAnalysis with token counts and recommendations
        """
        # Get model capacity
        model_capacity = self.get_model_capacity(request.model)
        max_tokens = model_capacity.max_context_tokens if model_capacity else 4096
        
        # Calculate text tokens from prompt and substitutions
        text_content = self._extract_text_content(request)
        text_tokens = self.token_estimator.estimate_text_tokens(text_content, request.model)
        
        # Calculate tokens from file attachments
        file_tokens = 0
        image_paths = []
        file_contents = []
        
        for attachment in request.file_attachments:
            if attachment.content:
                # Content already extracted
                tokens = self.token_estimator.estimate_text_tokens(attachment.content, request.model)
                file_tokens += tokens
                file_contents.append(attachment.content)
            else:
                # Need to estimate from file
                file_path = Path(attachment.file_path)
                if self._is_image_file(file_path):
                    if model_capacity and model_capacity.supports_vision:
                        image_tokens = self.token_estimator.estimate_image_tokens(file_path, request.model)
                        file_tokens += image_tokens
                        image_paths.append(file_path)
                    else:
                        logger.warning(f"Model {request.model} does not support images, skipping {file_path}")
                else:
                    # Text file
                    try:
                        tokens = self.token_estimator.estimate_file_tokens(file_path, request.model)
                        file_tokens += tokens
                    except Exception as e:
                        logger.error(f"Error estimating tokens for file {file_path}: {e}")
        
        # Calculate tokens from processed files
        processed_file_tokens = 0
        for processed_file in request.processed_files:
            tokens = self.token_estimator.estimate_text_tokens(processed_file.content, request.model)
            processed_file_tokens += tokens
        
        total_tokens = text_tokens + file_tokens + processed_file_tokens
        
        # Determine if upshifting or chunking is needed
        requires_upshift = total_tokens > max_tokens
        requires_chunking = False
        
        # Find recommended models if current model is insufficient
        recommended_models = []
        if requires_upshift:
            recommended_models = self._find_suitable_models(total_tokens, request.model)
            # If no suitable models found, chunking might be needed
            if not recommended_models:
                requires_chunking = True
                requires_upshift = False  # Can't upshift if no suitable models
        
        return ContextAnalysis(
            total_tokens=total_tokens,
            text_tokens=text_tokens,
            file_tokens=file_tokens + processed_file_tokens,
            model_capacity=max_tokens,
            requires_upshift=requires_upshift,
            requires_chunking=requires_chunking,
            recommended_models=recommended_models
        )
    
    def _extract_text_content(self, request: LLMRequest) -> str:
        """Extract all text content from a request for token estimation."""
        content_parts = []
        
        # Add prompt key (this would be resolved to actual prompt text in real usage)
        content_parts.append(f"Prompt: {request.prompt_key}")
        
        # Add substitutions
        for key, value in request.substitutions.items():
            content_parts.append(f"{key}: {str(value)}")
        
        # Add model parameters that might affect token count
        if request.model_params:
            content_parts.append(f"Model params: {str(request.model_params)}")
        
        return "\n".join(content_parts)
    
    def _is_image_file(self, file_path: Path) -> bool:
        """Check if a file is an image based on extension."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg'}
        return file_path.suffix.lower() in image_extensions
    
    def _find_suitable_models(self, required_tokens: int, current_model: str) -> List[str]:
        """
        Find models that can handle the required token count.
        
        Args:
            required_tokens: Number of tokens needed
            current_model: Current model name
            
        Returns:
            List of model names that can handle the token count, sorted by preference
        """
        current_capacity = self.get_model_capacity(current_model)
        current_provider = current_capacity.provider if current_capacity else "unknown"
        
        suitable_models = []
        
        # Find models with sufficient capacity
        for model_name, capacity in self.model_capacities.items():
            if capacity.max_context_tokens >= required_tokens:
                suitable_models.append((model_name, capacity))
        
        # Sort by preference: same provider first, then by cost, then by capacity
        def sort_key(item):
            model_name, capacity = item
            same_provider = 0 if capacity.provider == current_provider else 1
            return (same_provider, capacity.cost_multiplier, -capacity.max_context_tokens)
        
        suitable_models.sort(key=sort_key)
        
        return [model_name for model_name, _ in suitable_models]
    
    def estimate_tokens_for_content(self, 
                                  text_content: str,
                                  file_paths: List[Union[str, Path]],
                                  model: str) -> Dict[str, int]:
        """
        Estimate tokens for arbitrary content and files.
        
        Args:
            text_content: Text content to analyze
            file_paths: List of file paths to include
            model: Model name for token estimation
            
        Returns:
            Dictionary with token breakdown
        """
        text_tokens = self.token_estimator.estimate_text_tokens(text_content, model)
        
        file_tokens = 0
        image_tokens = 0
        
        for file_path in file_paths:
            path_obj = Path(file_path)
            if self._is_image_file(path_obj):
                tokens = self.token_estimator.estimate_image_tokens(path_obj, model)
                image_tokens += tokens
            else:
                tokens = self.token_estimator.estimate_file_tokens(path_obj, model)
                file_tokens += tokens
        
        total_tokens = text_tokens + file_tokens + image_tokens
        
        return {
            "text_tokens": text_tokens,
            "file_tokens": file_tokens,
            "image_tokens": image_tokens,
            "total_tokens": total_tokens
        }
    
    def check_model_compatibility(self, model: str, has_images: bool = False) -> Dict[str, Any]:
        """
        Check if a model is compatible with the request requirements.
        
        Args:
            model: Model name to check
            has_images: Whether the request includes images
            
        Returns:
            Dictionary with compatibility information
        """
        capacity = self.get_model_capacity(model)
        
        if not capacity:
            return {
                "compatible": False,
                "reason": "Unknown model",
                "max_tokens": None,
                "supports_vision": False
            }
        
        compatible = True
        reason = "Compatible"
        
        if has_images and not capacity.supports_vision:
            compatible = False
            reason = "Model does not support vision/images"
        
        return {
            "compatible": compatible,
            "reason": reason,
            "max_tokens": capacity.max_context_tokens,
            "supports_vision": capacity.supports_vision,
            "provider": capacity.provider,
            "cost_multiplier": capacity.cost_multiplier
        }
    
    def add_custom_model_capacity(self, model_name: str, capacity: ModelCapacity) -> None:
        """Add or update a custom model capacity."""
        self.model_capacities[model_name] = capacity
        logger.info(f"Added custom capacity for model: {model_name}")
    
    def get_all_model_capacities(self) -> Dict[str, ModelCapacity]:
        """Get all known model capacities."""
        return self.model_capacities.copy()
    
    def get_models_by_provider(self, provider: str) -> List[str]:
        """Get all models for a specific provider."""
        return [
            model_name for model_name, capacity in self.model_capacities.items()
            if capacity.provider == provider
        ]