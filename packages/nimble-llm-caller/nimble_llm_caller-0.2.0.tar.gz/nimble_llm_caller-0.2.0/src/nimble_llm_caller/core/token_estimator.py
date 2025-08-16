"""
Token estimation utilities for LLM requests.
"""

import tiktoken
from typing import Dict, Optional, Union, List, Any
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)


class TokenEstimator:
    """Estimates token counts for various content types and models with provider-aware tokenization."""
    
    # Provider-specific model configurations
    PROVIDER_CONFIGS = {
        "openai": {
            "tokenizer_type": "tiktoken",
            "models": {
                "gpt-4": {"encoding": "cl100k_base", "supports_vision": False},
                "gpt-4o": {"encoding": "o200k_base", "supports_vision": True},
                "gpt-4o-mini": {"encoding": "o200k_base", "supports_vision": True},
                "gpt-4-turbo": {"encoding": "cl100k_base", "supports_vision": True},
                "gpt-4-vision-preview": {"encoding": "cl100k_base", "supports_vision": True},
                "gpt-3.5-turbo": {"encoding": "cl100k_base", "supports_vision": False},
                "text-embedding-ada-002": {"encoding": "cl100k_base", "supports_vision": False},
                "text-embedding-3-small": {"encoding": "cl100k_base", "supports_vision": False},
                "text-embedding-3-large": {"encoding": "cl100k_base", "supports_vision": False},
            }
        },
        "anthropic": {
            "tokenizer_type": "anthropic",
            "models": {
                "claude-3-opus": {"chars_per_token": 3.5, "supports_vision": True},
                "claude-3-sonnet": {"chars_per_token": 3.5, "supports_vision": True},
                "claude-3-haiku": {"chars_per_token": 3.5, "supports_vision": True},
                "claude-3-5-sonnet": {"chars_per_token": 3.5, "supports_vision": True},
                "claude-2.1": {"chars_per_token": 3.5, "supports_vision": False},
                "claude-2": {"chars_per_token": 3.5, "supports_vision": False},
                "claude-instant": {"chars_per_token": 3.5, "supports_vision": False},
            }
        },
        "google": {
            "tokenizer_type": "google",
            "models": {
                "gemini-pro": {"chars_per_token": 4.0, "supports_vision": False},
                "gemini-1.5-pro": {"chars_per_token": 4.0, "supports_vision": True},
                "gemini-1.5-flash": {"chars_per_token": 4.0, "supports_vision": True},
                "gemini-pro-vision": {"chars_per_token": 4.0, "supports_vision": True},
            }
        },
        "cohere": {
            "tokenizer_type": "cohere",
            "models": {
                "command": {"chars_per_token": 4.2, "supports_vision": False},
                "command-light": {"chars_per_token": 4.2, "supports_vision": False},
                "command-nightly": {"chars_per_token": 4.2, "supports_vision": False},
            }
        },
        "mistral": {
            "tokenizer_type": "mistral",
            "models": {
                "mistral-large": {"chars_per_token": 4.0, "supports_vision": False},
                "mistral-medium": {"chars_per_token": 4.0, "supports_vision": False},
                "mistral-small": {"chars_per_token": 4.0, "supports_vision": False},
                "mistral-tiny": {"chars_per_token": 4.0, "supports_vision": False},
            }
        }
    }
    
    # Default fallback configuration
    DEFAULT_CONFIG = {
        "tokenizer_type": "tiktoken",
        "encoding": "cl100k_base",
        "chars_per_token": 4.0,
        "supports_vision": False
    }
    
    def __init__(self):
        """Initialize the token estimator with caches for different tokenizers."""
        self._tiktoken_cache: Dict[str, tiktoken.Encoding] = {}
        self._anthropic_tokenizer = None
        self._google_tokenizer = None
    
    def _detect_provider_and_model(self, model: str) -> tuple[str, str, Dict[str, Any]]:
        """
        Detect provider and get model configuration.
        
        Args:
            model: Model name (may include provider prefix)
            
        Returns:
            Tuple of (provider, clean_model_name, model_config)
        """
        # Handle provider-prefixed models (e.g., "openai/gpt-4", "anthropic/claude-3-sonnet")
        if "/" in model:
            provider_prefix, model_name = model.split("/", 1)
            if provider_prefix in self.PROVIDER_CONFIGS:
                provider = provider_prefix
                clean_model = model_name
            else:
                # Unknown provider prefix, try to detect from model name
                provider, clean_model = self._detect_provider_from_name(model_name)
        else:
            provider, clean_model = self._detect_provider_from_name(model)
        
        # Get model configuration
        if provider in self.PROVIDER_CONFIGS:
            provider_config = self.PROVIDER_CONFIGS[provider]
            model_config = provider_config["models"].get(clean_model, {})
            model_config["tokenizer_type"] = provider_config["tokenizer_type"]
        else:
            model_config = self.DEFAULT_CONFIG.copy()
        
        return provider, clean_model, model_config
    
    def _detect_provider_from_name(self, model: str) -> tuple[str, str]:
        """Detect provider from model name patterns."""
        model_lower = model.lower()
        
        # OpenAI patterns
        if any(pattern in model_lower for pattern in ["gpt-", "text-embedding", "davinci", "curie", "babbage", "ada"]):
            return "openai", model
        
        # Anthropic patterns
        if any(pattern in model_lower for pattern in ["claude", "anthropic"]):
            return "anthropic", model
        
        # Google patterns
        if any(pattern in model_lower for pattern in ["gemini", "palm", "bison"]):
            return "google", model
        
        # Cohere patterns
        if any(pattern in model_lower for pattern in ["command", "cohere"]):
            return "cohere", model
        
        # Mistral patterns
        if any(pattern in model_lower for pattern in ["mistral", "mixtral"]):
            return "mistral", model
        
        # Default to OpenAI-compatible
        return "openai", model
    
    def _get_tiktoken_encoding(self, encoding_name: str) -> tiktoken.Encoding:
        """Get tiktoken encoding with caching."""
        if encoding_name not in self._tiktoken_cache:
            try:
                self._tiktoken_cache[encoding_name] = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                logger.warning(f"Failed to get encoding {encoding_name}, falling back to default: {e}")
                self._tiktoken_cache[encoding_name] = tiktoken.get_encoding(self.DEFAULT_CONFIG["encoding"])
        
        return self._tiktoken_cache[encoding_name]
    
    def _get_anthropic_tokenizer(self):
        """Get Anthropic tokenizer (lazy loading)."""
        if self._anthropic_tokenizer is None:
            try:
                import anthropic
                self._anthropic_tokenizer = anthropic.Anthropic()
                logger.info("Loaded Anthropic tokenizer")
            except ImportError:
                logger.warning("Anthropic library not available, falling back to character-based estimation")
                self._anthropic_tokenizer = "unavailable"
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic tokenizer: {e}")
                self._anthropic_tokenizer = "unavailable"
        
        return self._anthropic_tokenizer if self._anthropic_tokenizer != "unavailable" else None
    
    def _get_google_tokenizer(self):
        """Get Google tokenizer (lazy loading)."""
        if self._google_tokenizer is None:
            try:
                import google.generativeai as genai
                self._google_tokenizer = genai
                logger.info("Loaded Google tokenizer")
            except ImportError:
                logger.warning("Google GenerativeAI library not available, falling back to character-based estimation")
                self._google_tokenizer = "unavailable"
            except Exception as e:
                logger.warning(f"Failed to initialize Google tokenizer: {e}")
                self._google_tokenizer = "unavailable"
        
        return self._google_tokenizer if self._google_tokenizer != "unavailable" else None
    
    def estimate_text_tokens(self, text: str, model: str) -> int:
        """
        Estimate token count for text content using provider-specific tokenizers.
        
        Args:
            text: The text content to estimate tokens for
            model: The model name to use for tokenization
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        provider, clean_model, model_config = self._detect_provider_and_model(model)
        tokenizer_type = model_config.get("tokenizer_type", "tiktoken")
        
        try:
            if tokenizer_type == "tiktoken":
                encoding_name = model_config.get("encoding", self.DEFAULT_CONFIG["encoding"])
                encoding = self._get_tiktoken_encoding(encoding_name)
                return len(encoding.encode(text))
            
            elif tokenizer_type == "anthropic":
                anthropic_tokenizer = self._get_anthropic_tokenizer()
                if anthropic_tokenizer:
                    # Use Anthropic's count_tokens method if available
                    try:
                        return anthropic_tokenizer.count_tokens(text)
                    except Exception as e:
                        logger.warning(f"Anthropic tokenizer failed, using character estimation: {e}")
                
                # Fallback to character-based estimation
                chars_per_token = model_config.get("chars_per_token", 3.5)
                return int(len(text) / chars_per_token)
            
            elif tokenizer_type == "google":
                google_tokenizer = self._get_google_tokenizer()
                if google_tokenizer:
                    try:
                        # Use Google's count_tokens method if available
                        model_instance = google_tokenizer.GenerativeModel(clean_model)
                        return model_instance.count_tokens(text).total_tokens
                    except Exception as e:
                        logger.warning(f"Google tokenizer failed, using character estimation: {e}")
                
                # Fallback to character-based estimation
                chars_per_token = model_config.get("chars_per_token", 4.0)
                return int(len(text) / chars_per_token)
            
            else:
                # Generic character-based estimation for other providers
                chars_per_token = model_config.get("chars_per_token", 4.0)
                return int(len(text) / chars_per_token)
                
        except Exception as e:
            logger.error(f"Error estimating tokens for text with {model}: {e}")
            # Ultimate fallback
            return int(len(text) / 4.0)
    
    def estimate_file_tokens(self, file_path: Union[str, Path], model: str, content: Optional[str] = None) -> int:
        """
        Estimate token count for file content.
        
        Args:
            file_path: Path to the file
            model: The model name to use for encoding selection
            content: Pre-extracted content (if None, will attempt to read file)
            
        Returns:
            Estimated token count
        """
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                return 0
        
        return self.estimate_text_tokens(content, model)
    
    def estimate_image_tokens(self, image_path: Union[str, Path], model: str) -> int:
        """
        Estimate token count for image content based on provider-specific calculations.
        
        Args:
            image_path: Path to the image file
            model: The model name to determine image token calculation
            
        Returns:
            Estimated token count for the image
        """
        provider, clean_model, model_config = self._detect_provider_and_model(model)
        
        if not model_config.get("supports_vision", False):
            logger.warning(f"Model {model} does not support vision, returning 0 tokens for image")
            return 0
        
        try:
            from PIL import Image
            
            with Image.open(image_path) as img:
                width, height = img.size
                
                if provider == "openai":
                    # OpenAI GPT-4 Vision token calculation
                    # Base cost: 85 tokens
                    # Each 512x512 tile: 170 tokens
                    # Images are resized to fit within 2048x2048, maintaining aspect ratio
                    
                    # Calculate effective dimensions after resizing
                    max_dim = 2048
                    if width > max_dim or height > max_dim:
                        scale = min(max_dim / width, max_dim / height)
                        width = int(width * scale)
                        height = int(height * scale)
                    
                    # Calculate tiles
                    tiles_x = (width + 511) // 512
                    tiles_y = (height + 511) // 512
                    return 85 + (tiles_x * tiles_y * 170)
                
                elif provider == "anthropic":
                    # Claude 3 Vision: approximately 1.15 tokens per pixel
                    # But with a more reasonable scaling factor
                    pixel_count = width * height
                    if pixel_count > 1000000:  # > 1MP
                        return int(pixel_count * 0.0015)  # Reduced rate for large images
                    else:
                        return int(pixel_count * 0.002)   # Standard rate
                
                elif provider == "google":
                    # Gemini Vision: roughly 258 tokens per image regardless of size
                    # But scale slightly based on resolution
                    base_tokens = 258
                    pixel_count = width * height
                    if pixel_count > 1000000:  # > 1MP
                        return int(base_tokens * 1.5)
                    elif pixel_count < 100000:  # < 0.1MP
                        return int(base_tokens * 0.7)
                    else:
                        return base_tokens
                
                else:
                    # Default estimation for other providers
                    pixel_count = width * height
                    return max(500, min(2000, int(pixel_count / 1000)))
                    
        except ImportError:
            logger.warning("PIL not available for image token estimation, using default")
            return 1000 if model_config.get("supports_vision", False) else 0
        except Exception as e:
            logger.error(f"Error estimating image tokens for {image_path}: {e}")
            return 1000 if model_config.get("supports_vision", False) else 0
    
    def estimate_request_tokens(self, 
                              text_content: str, 
                              file_contents: List[str], 
                              image_paths: List[Union[str, Path]], 
                              model: str) -> Dict[str, int]:
        """
        Estimate total token count for a complete request.
        
        Args:
            text_content: Main text content of the request
            file_contents: List of file contents (already extracted)
            image_paths: List of image file paths
            model: The model name to use for estimation
            
        Returns:
            Dictionary with breakdown of token counts
        """
        text_tokens = self.estimate_text_tokens(text_content, model)
        
        file_tokens = sum(
            self.estimate_text_tokens(content, model) 
            for content in file_contents
        )
        
        image_tokens = sum(
            self.estimate_image_tokens(path, model) 
            for path in image_paths
        )
        
        total_tokens = text_tokens + file_tokens + image_tokens
        
        return {
            "text_tokens": text_tokens,
            "file_tokens": file_tokens,
            "image_tokens": image_tokens,
            "total_tokens": total_tokens
        }
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get comprehensive model information including tokenization details.
        
        Args:
            model: The model name
            
        Returns:
            Dictionary with model information
        """
        provider, clean_model, model_config = self._detect_provider_and_model(model)
        
        return {
            "model": model,
            "clean_model": clean_model,
            "provider": provider,
            "tokenizer_type": model_config.get("tokenizer_type", "unknown"),
            "encoding": model_config.get("encoding"),
            "chars_per_token": model_config.get("chars_per_token"),
            "supports_vision": model_config.get("supports_vision", False),
            "is_configured": provider in self.PROVIDER_CONFIGS and clean_model in self.PROVIDER_CONFIGS[provider]["models"]
        }
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """Get list of supported providers."""
        return list(cls.PROVIDER_CONFIGS.keys())
    
    @classmethod
    def get_supported_models(cls) -> Dict[str, List[str]]:
        """Get list of models organized by provider."""
        result = {}
        for provider, config in cls.PROVIDER_CONFIGS.items():
            result[provider] = list(config["models"].keys())
        return result
    
    def supports_vision(self, model: str) -> bool:
        """Check if a model supports vision/image processing."""
        _, _, model_config = self._detect_provider_and_model(model)
        return model_config.get("supports_vision", False)