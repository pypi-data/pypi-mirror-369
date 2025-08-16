"""
Configuration management system for nimble-llm-caller.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ModelCapacityConfig:
    """Configuration for model capacity information."""
    max_context_tokens: Optional[int] = None
    supports_vision: bool = False
    supported_file_types: List[str] = field(default_factory=list)
    cost_multiplier: float = 1.0
    priority: int = 100  # Lower numbers = higher priority


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    provider: str
    api_key_env: str
    default_params: Dict[str, Any] = field(default_factory=dict)
    retry_config: Dict[str, Any] = field(default_factory=dict)
    cost_per_token: Optional[float] = None
    max_tokens_limit: Optional[int] = None
    # Enhanced context management fields
    capacity_config: Optional[ModelCapacityConfig] = None


@dataclass
class OutputConfig:
    """Configuration for output handling."""
    default_format: str = "json"
    save_raw_responses: bool = True
    timestamp_results: bool = True
    output_directory: str = "./output"
    session_tracking: bool = True


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: str = "10MB"
    backup_count: int = 5


@dataclass
class ContextManagementConfig:
    """Configuration for context management features."""
    enable_auto_upshift: bool = True
    enable_chunking: bool = True
    default_strategy: str = "upshift_first"  # upshift_first, chunk_first, upshift_only, chunk_only, fail_fast
    max_cost_multiplier: float = 3.0
    preferred_providers: List[str] = field(default_factory=lambda: ["openai", "anthropic", "google"])
    chunk_overlap_tokens: int = 100
    min_chunk_tokens: int = 500
    model_strategies: Dict[str, str] = field(default_factory=dict)  # model -> strategy overrides


@dataclass
class FileProcessingConfig:
    """Configuration for file processing."""
    enable_file_processing: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    supported_extensions: List[str] = field(default_factory=lambda: [
        '.txt', '.md', '.json', '.csv', '.xml', '.yaml', '.yml', '.pdf', '.docx', '.rtf',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg'
    ])
    text_encoding: str = "utf-8"
    image_processing: bool = True


@dataclass
class InteractionLoggingConfig:
    """Configuration for interaction logging."""
    enable_logging: bool = True
    log_file_path: str = "llm_interactions.jsonl"
    max_log_size: int = 100 * 1024 * 1024  # 100MB
    max_files: int = 5
    async_logging: bool = True
    log_content: bool = True
    log_metadata: bool = True


class ConfigurationError(Exception):
    """Raised when there's a configuration error."""
    pass


class ConfigManager:
    """Manages configuration for nimble-llm-caller."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, searches for default locations.
        """
        self.config_path = config_path or self._find_config_file()
        self.config_data = {}
        self.models = {}
        self.output_config = OutputConfig()
        self.logging_config = LoggingConfig()
        self.context_management_config = ContextManagementConfig()
        self.file_processing_config = FileProcessingConfig()
        self.interaction_logging_config = InteractionLoggingConfig()
        
        self._load_config()
        self._validate_config()
        self._setup_logging()
    
    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations."""
        search_paths = [
            "./nimble_llm_config.json",
            "~/.nimble_llm_config.json",
            os.path.join(os.path.expanduser("~"), ".config", "nimble-llm-caller", "config.json"),
            "/etc/nimble-llm-caller/config.json"
        ]
        
        for path in search_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                logger.info(f"Found configuration file: {expanded_path}")
                return expanded_path
        
        logger.info("No configuration file found, using defaults")
        return None
    
    def _load_config(self):
        """Load configuration from file."""
        if not self.config_path or not os.path.exists(self.config_path):
            logger.info("Using default configuration")
            self._load_default_config()
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            
            logger.info(f"Loaded configuration from {self.config_path}")
            self._parse_config()
            
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load configuration from {self.config_path}: {e}")
            logger.info("Falling back to default configuration")
            self._load_default_config()
    
    def _load_default_config(self):
        """Load default configuration."""
        self.config_data = {
            "models": {
                "gpt-4o": {
                    "provider": "openai",
                    "api_key_env": "OPENAI_API_KEY",
                    "default_params": {
                        "temperature": 0.7,
                        "max_tokens": 2000
                    },
                    "retry_config": {
                        "max_retries": 3,
                        "base_delay": 1.0,
                        "max_delay": 60.0
                    }
                },
                "claude-3-sonnet": {
                    "provider": "anthropic",
                    "api_key_env": "ANTHROPIC_API_KEY",
                    "default_params": {
                        "temperature": 0.7,
                        "max_tokens": 2000
                    },
                    "retry_config": {
                        "max_retries": 3,
                        "base_delay": 1.0,
                        "max_delay": 60.0
                    }
                },
                "gemini/gemini-2.5-flash": {
                    "provider": "google",
                    "api_key_env": "GOOGLE_API_KEY",
                    "default_params": {
                        "temperature": 0.7,
                        "max_tokens": 2000
                    },
                    "retry_config": {
                        "max_retries": 3,
                        "base_delay": 1.0,
                        "max_delay": 60.0
                    }
                }
            },
            "output": {
                "default_format": "json",
                "save_raw_responses": True,
                "timestamp_results": True,
                "output_directory": "./output",
                "session_tracking": True
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "context_management": {
                "enable_auto_upshift": True,
                "enable_chunking": True,
                "default_strategy": "upshift_first",
                "max_cost_multiplier": 3.0,
                "preferred_providers": ["openai", "anthropic", "google"],
                "chunk_overlap_tokens": 100,
                "min_chunk_tokens": 500
            },
            "file_processing": {
                "enable_file_processing": True,
                "max_file_size": 10485760,  # 10MB
                "text_encoding": "utf-8",
                "image_processing": True
            },
            "interaction_logging": {
                "enable_logging": True,
                "log_file_path": "llm_interactions.jsonl",
                "max_log_size": 104857600,  # 100MB
                "max_files": 5,
                "async_logging": True,
                "log_content": True,
                "log_metadata": True
            }
        }
        
        self._parse_config()
    
    def _parse_config(self):
        """Parse configuration data into structured objects."""
        # Parse model configurations
        models_config = self.config_data.get("models", {})
        for model_name, model_data in models_config.items():
            # Parse capacity config if present
            capacity_config = None
            if "capacity" in model_data:
                capacity_data = model_data["capacity"]
                capacity_config = ModelCapacityConfig(
                    max_context_tokens=capacity_data.get("max_context_tokens"),
                    supports_vision=capacity_data.get("supports_vision", False),
                    supported_file_types=capacity_data.get("supported_file_types", []),
                    cost_multiplier=capacity_data.get("cost_multiplier", 1.0),
                    priority=capacity_data.get("priority", 100)
                )
            
            self.models[model_name] = ModelConfig(
                provider=model_data.get("provider", "unknown"),
                api_key_env=model_data.get("api_key_env", f"{model_name.upper()}_API_KEY"),
                default_params=model_data.get("default_params", {}),
                retry_config=model_data.get("retry_config", {}),
                cost_per_token=model_data.get("cost_per_token"),
                max_tokens_limit=model_data.get("max_tokens_limit"),
                capacity_config=capacity_config
            )
        
        # Parse output configuration
        output_data = self.config_data.get("output", {})
        self.output_config = OutputConfig(
            default_format=output_data.get("default_format", "json"),
            save_raw_responses=output_data.get("save_raw_responses", True),
            timestamp_results=output_data.get("timestamp_results", True),
            output_directory=output_data.get("output_directory", "./output"),
            session_tracking=output_data.get("session_tracking", True)
        )
        
        # Parse logging configuration
        logging_data = self.config_data.get("logging", {})
        self.logging_config = LoggingConfig(
            level=logging_data.get("level", "INFO"),
            format=logging_data.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            file_path=logging_data.get("file_path"),
            max_file_size=logging_data.get("max_file_size", "10MB"),
            backup_count=logging_data.get("backup_count", 5)
        )
        
        # Parse context management configuration
        context_data = self.config_data.get("context_management", {})
        self.context_management_config = ContextManagementConfig(
            enable_auto_upshift=context_data.get("enable_auto_upshift", True),
            enable_chunking=context_data.get("enable_chunking", True),
            default_strategy=context_data.get("default_strategy", "upshift_first"),
            max_cost_multiplier=context_data.get("max_cost_multiplier", 3.0),
            preferred_providers=context_data.get("preferred_providers", ["openai", "anthropic", "google"]),
            chunk_overlap_tokens=context_data.get("chunk_overlap_tokens", 100),
            min_chunk_tokens=context_data.get("min_chunk_tokens", 500),
            model_strategies=context_data.get("model_strategies", {})
        )
        
        # Parse file processing configuration
        file_data = self.config_data.get("file_processing", {})
        self.file_processing_config = FileProcessingConfig(
            enable_file_processing=file_data.get("enable_file_processing", True),
            max_file_size=file_data.get("max_file_size", 10 * 1024 * 1024),
            supported_extensions=file_data.get("supported_extensions", [
                '.txt', '.md', '.json', '.csv', '.xml', '.yaml', '.yml', '.pdf', '.docx', '.rtf',
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg'
            ]),
            text_encoding=file_data.get("text_encoding", "utf-8"),
            image_processing=file_data.get("image_processing", True)
        )
        
        # Parse interaction logging configuration
        interaction_data = self.config_data.get("interaction_logging", {})
        self.interaction_logging_config = InteractionLoggingConfig(
            enable_logging=interaction_data.get("enable_logging", True),
            log_file_path=interaction_data.get("log_file_path", "llm_interactions.jsonl"),
            max_log_size=interaction_data.get("max_log_size", 100 * 1024 * 1024),
            max_files=interaction_data.get("max_files", 5),
            async_logging=interaction_data.get("async_logging", True),
            log_content=interaction_data.get("log_content", True),
            log_metadata=interaction_data.get("log_metadata", True)
        )
    
    def _validate_config(self):
        """Validate configuration data."""
        errors = []
        
        # Validate models
        if not self.models:
            errors.append("No models configured")
        
        for model_name, model_config in self.models.items():
            if not model_config.provider:
                errors.append(f"Model {model_name} missing provider")
            
            if not model_config.api_key_env:
                errors.append(f"Model {model_name} missing api_key_env")
        
        # Validate output directory
        try:
            output_dir = Path(self.output_config.output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create output directory: {e}")
        
        if errors:
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def _setup_logging(self):
        """Setup logging based on configuration."""
        level = getattr(logging, self.logging_config.level.upper(), logging.INFO)
        
        # Configure root logger
        logging.basicConfig(
            level=level,
            format=self.logging_config.format
        )
        
        # Setup file logging if specified
        if self.logging_config.file_path:
            from logging.handlers import RotatingFileHandler
            
            file_handler = RotatingFileHandler(
                self.logging_config.file_path,
                maxBytes=self._parse_size(self.logging_config.max_file_size),
                backupCount=self.logging_config.backup_count
            )
            file_handler.setFormatter(logging.Formatter(self.logging_config.format))
            
            # Add to nimble_llm_caller logger
            nimble_logger = logging.getLogger("nimble_llm_caller")
            nimble_logger.addHandler(file_handler)
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes."""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model."""
        return self.models.get(model_name)
    
    def get_api_key(self, model_name: str) -> str:
        """Get API key for a model from environment variables."""
        model_config = self.get_model_config(model_name)
        if not model_config:
            raise ConfigurationError(f"Model {model_name} not configured")
        
        api_key = os.getenv(model_config.api_key_env)
        if not api_key:
            raise ConfigurationError(
                f"API key not found in environment variable: {model_config.api_key_env}"
            )
        
        return api_key
    
    def get_model_params(
        self,
        model_name: str,
        prompt_params: Optional[Dict[str, Any]] = None,
        call_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get merged model parameters with proper precedence.
        
        Precedence: call_params > prompt_params > model_defaults
        """
        model_config = self.get_model_config(model_name)
        if not model_config:
            raise ConfigurationError(f"Model {model_name} not configured")
        
        # Start with model defaults
        params = model_config.default_params.copy()
        
        # Apply prompt-specific params
        if prompt_params:
            params.update(prompt_params)
        
        # Apply call-specific params (highest precedence)
        if call_params:
            params.update(call_params)
        
        return params
    
    def get_retry_config(self, model_name: str) -> Dict[str, Any]:
        """Get retry configuration for a model."""
        model_config = self.get_model_config(model_name)
        if not model_config:
            return {"max_retries": 3, "base_delay": 1.0, "max_delay": 60.0}
        
        return model_config.retry_config or {"max_retries": 3, "base_delay": 1.0, "max_delay": 60.0}
    
    def list_available_models(self) -> List[str]:
        """Get list of configured model names."""
        return list(self.models.keys())
    
    def validate_model(self, model_name: str) -> Dict[str, Any]:
        """
        Validate a model configuration.
        
        Returns:
            Dictionary with validation results
        """
        validation = {
            "valid": True,
            "issues": []
        }
        
        model_config = self.get_model_config(model_name)
        if not model_config:
            validation["valid"] = False
            validation["issues"].append(f"Model {model_name} not configured")
            return validation
        
        # Check API key availability
        try:
            self.get_api_key(model_name)
        except ConfigurationError as e:
            validation["valid"] = False
            validation["issues"].append(str(e))
        
        # Validate provider
        if not model_config.provider:
            validation["valid"] = False
            validation["issues"].append("Provider not specified")
        
        return validation
    
    def save_config(self, output_path: Optional[str] = None):
        """Save current configuration to file."""
        output_path = output_path or self.config_path or "./nimble_llm_config.json"
        
        # Convert back to dictionary format
        config_dict = {
            "models": {},
            "output": {
                "default_format": self.output_config.default_format,
                "save_raw_responses": self.output_config.save_raw_responses,
                "timestamp_results": self.output_config.timestamp_results,
                "output_directory": self.output_config.output_directory,
                "session_tracking": self.output_config.session_tracking
            },
            "logging": {
                "level": self.logging_config.level,
                "format": self.logging_config.format,
                "file_path": self.logging_config.file_path,
                "max_file_size": self.logging_config.max_file_size,
                "backup_count": self.logging_config.backup_count
            }
        }
        
        for model_name, model_config in self.models.items():
            config_dict["models"][model_name] = {
                "provider": model_config.provider,
                "api_key_env": model_config.api_key_env,
                "default_params": model_config.default_params,
                "retry_config": model_config.retry_config,
                "cost_per_token": model_config.cost_per_token,
                "max_tokens_limit": model_config.max_tokens_limit
            }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to {output_path}")
            
        except IOError as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def update_model_config(self, model_name: str, updates: Dict[str, Any]):
        """Update configuration for a specific model."""
        if model_name not in self.models:
            raise ConfigurationError(f"Model {model_name} not configured")
        
        model_config = self.models[model_name]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(model_config, key):
                setattr(model_config, key, value)
            else:
                logger.warning(f"Unknown model config field: {key}")
        
        logger.info(f"Updated configuration for model {model_name}")
    
    def add_model(self, model_name: str, model_config: Dict[str, Any]):
        """Add a new model configuration."""
        self.models[model_name] = ModelConfig(
            provider=model_config.get("provider", "unknown"),
            api_key_env=model_config.get("api_key_env", f"{model_name.upper()}_API_KEY"),
            default_params=model_config.get("default_params", {}),
            retry_config=model_config.get("retry_config", {}),
            cost_per_token=model_config.get("cost_per_token"),
            max_tokens_limit=model_config.get("max_tokens_limit")
        )
        
        logger.info(f"Added model configuration: {model_name}")
    
    def remove_model(self, model_name: str):
        """Remove a model configuration."""
        if model_name in self.models:
            del self.models[model_name]
            logger.info(f"Removed model configuration: {model_name}")
        else:
            logger.warning(f"Model {model_name} not found in configuration")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        return {
            "config_file": self.config_path,
            "models_configured": len(self.models),
            "model_names": list(self.models.keys()),
            "output_directory": self.output_config.output_directory,
            "logging_level": self.logging_config.level,
            "default_format": self.output_config.default_format
        }    

    def get_context_management_config(self) -> ContextManagementConfig:
        """Get context management configuration."""
        return self.context_management_config
    
    def get_file_processing_config(self) -> FileProcessingConfig:
        """Get file processing configuration."""
        return self.file_processing_config
    
    def get_interaction_logging_config(self) -> InteractionLoggingConfig:
        """Get interaction logging configuration."""
        return self.interaction_logging_config
    
    def update_context_strategy(self, model_name: str, strategy: str) -> None:
        """Update context strategy for a specific model."""
        self.context_management_config.model_strategies[model_name] = strategy
        logger.info(f"Updated context strategy for {model_name}: {strategy}")
    
    def add_model_capacity(self, 
                          model_name: str, 
                          max_context_tokens: int,
                          supports_vision: bool = False,
                          cost_multiplier: float = 1.0,
                          priority: int = 100) -> None:
        """Add or update model capacity configuration."""
        if model_name not in self.models:
            logger.warning(f"Model {model_name} not in configuration, capacity info may not be used")
        
        capacity_config = ModelCapacityConfig(
            max_context_tokens=max_context_tokens,
            supports_vision=supports_vision,
            cost_multiplier=cost_multiplier,
            priority=priority
        )
        
        if model_name in self.models:
            self.models[model_name].capacity_config = capacity_config
        
        logger.info(f"Added capacity config for {model_name}: {max_context_tokens} tokens")
    
    def get_model_capacity_info(self, model_name: str) -> Optional[ModelCapacityConfig]:
        """Get model capacity information."""
        model_config = self.get_model_config(model_name)
        return model_config.capacity_config if model_config else None
    
    def export_enhanced_config(self) -> Dict[str, Any]:
        """Export complete configuration including enhanced features."""
        config_dict = {
            "models": {},
            "output": {
                "default_format": self.output_config.default_format,
                "save_raw_responses": self.output_config.save_raw_responses,
                "timestamp_results": self.output_config.timestamp_results,
                "output_directory": self.output_config.output_directory,
                "session_tracking": self.output_config.session_tracking
            },
            "logging": {
                "level": self.logging_config.level,
                "format": self.logging_config.format,
                "file_path": self.logging_config.file_path,
                "max_file_size": self.logging_config.max_file_size,
                "backup_count": self.logging_config.backup_count
            },
            "context_management": {
                "enable_auto_upshift": self.context_management_config.enable_auto_upshift,
                "enable_chunking": self.context_management_config.enable_chunking,
                "default_strategy": self.context_management_config.default_strategy,
                "max_cost_multiplier": self.context_management_config.max_cost_multiplier,
                "preferred_providers": self.context_management_config.preferred_providers,
                "chunk_overlap_tokens": self.context_management_config.chunk_overlap_tokens,
                "min_chunk_tokens": self.context_management_config.min_chunk_tokens,
                "model_strategies": self.context_management_config.model_strategies
            },
            "file_processing": {
                "enable_file_processing": self.file_processing_config.enable_file_processing,
                "max_file_size": self.file_processing_config.max_file_size,
                "supported_extensions": self.file_processing_config.supported_extensions,
                "text_encoding": self.file_processing_config.text_encoding,
                "image_processing": self.file_processing_config.image_processing
            },
            "interaction_logging": {
                "enable_logging": self.interaction_logging_config.enable_logging,
                "log_file_path": self.interaction_logging_config.log_file_path,
                "max_log_size": self.interaction_logging_config.max_log_size,
                "max_files": self.interaction_logging_config.max_files,
                "async_logging": self.interaction_logging_config.async_logging,
                "log_content": self.interaction_logging_config.log_content,
                "log_metadata": self.interaction_logging_config.log_metadata
            }
        }
        
        # Export model configurations
        for model_name, model_config in self.models.items():
            model_dict = {
                "provider": model_config.provider,
                "api_key_env": model_config.api_key_env,
                "default_params": model_config.default_params,
                "retry_config": model_config.retry_config
            }
            
            if model_config.cost_per_token is not None:
                model_dict["cost_per_token"] = model_config.cost_per_token
            
            if model_config.max_tokens_limit is not None:
                model_dict["max_tokens_limit"] = model_config.max_tokens_limit
            
            # Add capacity configuration if present
            if model_config.capacity_config:
                capacity = model_config.capacity_config
                model_dict["capacity"] = {
                    "max_context_tokens": capacity.max_context_tokens,
                    "supports_vision": capacity.supports_vision,
                    "supported_file_types": capacity.supported_file_types,
                    "cost_multiplier": capacity.cost_multiplier,
                    "priority": capacity.priority
                }
            
            config_dict["models"][model_name] = model_dict
        
        return config_dict
    
    def save_enhanced_config(self, output_path: Optional[str] = None) -> None:
        """Save enhanced configuration to file."""
        output_path = output_path or self.config_path or "./nimble_llm_config.json"
        
        config_dict = self.export_enhanced_config()
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved enhanced configuration to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {output_path}: {e}")
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def validate_enhanced_config(self) -> Dict[str, Any]:
        """Validate enhanced configuration features."""
        validation = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Validate context management settings
        valid_strategies = ["upshift_first", "chunk_first", "upshift_only", "chunk_only", "fail_fast"]
        if self.context_management_config.default_strategy not in valid_strategies:
            validation["valid"] = False
            validation["issues"].append(f"Invalid default strategy: {self.context_management_config.default_strategy}")
        
        # Validate file processing settings
        if self.file_processing_config.max_file_size <= 0:
            validation["valid"] = False
            validation["issues"].append("File processing max_file_size must be positive")
        
        # Validate interaction logging settings
        if self.interaction_logging_config.max_log_size <= 0:
            validation["valid"] = False
            validation["issues"].append("Interaction logging max_log_size must be positive")
        
        # Check for model capacity configurations
        models_with_capacity = sum(1 for m in self.models.values() if m.capacity_config)
        if models_with_capacity == 0:
            validation["warnings"].append("No models have capacity configuration - context management may use defaults")
        
        return validation