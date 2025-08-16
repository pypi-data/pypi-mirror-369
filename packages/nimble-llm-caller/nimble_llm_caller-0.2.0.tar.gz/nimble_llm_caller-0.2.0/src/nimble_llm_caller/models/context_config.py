"""
Configuration models for context management.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ContextStrategy(str, Enum):
    """Context overflow handling strategies."""
    UPSHIFT_FIRST = "upshift_first"
    CHUNK_FIRST = "chunk_first"
    UPSHIFT_ONLY = "upshift_only"
    CHUNK_ONLY = "chunk_only"


class ModelCapacity(BaseModel):
    """Model capacity and priority information."""
    
    model_name: str = Field(..., description="Model identifier")
    max_tokens: int = Field(..., description="Maximum context tokens")
    cost_per_token: float = Field(..., description="Cost per token (input)")
    cost_per_output_token: float = Field(..., description="Cost per output token")
    priority: int = Field(1, description="Priority for upshifting (lower = higher priority)")
    provider: str = Field(..., description="Model provider (openai, anthropic, etc.)")
    supports_vision: bool = Field(False, description="Whether model supports vision/images")
    
    class Config:
        use_enum_values = True


class ContextConfig(BaseModel):
    """Configuration for context management features."""
    
    # Strategy settings
    default_strategy: ContextStrategy = Field(ContextStrategy.UPSHIFT_FIRST, description="Default context overflow strategy")
    max_cost_multiplier: float = Field(2.0, description="Maximum cost multiplier for upshifting")
    
    # Chunking settings
    chunk_overlap_tokens: int = Field(100, description="Token overlap between chunks")
    max_chunks: int = Field(10, description="Maximum number of chunks to create")
    
    # File processing settings
    max_file_size_mb: int = Field(50, description="Maximum file size in MB")
    supported_file_types: List[str] = Field(
        default_factory=lambda: [".txt", ".md", ".json", ".csv", ".pdf", ".docx"],
        description="Supported file extensions"
    )
    
    # Model capacity registry
    model_capacities: List[ModelCapacity] = Field(default_factory=list, description="Model capacity definitions")
    
    # Logging settings
    enable_interaction_logging: bool = Field(True, description="Enable interaction logging")
    log_file_path: str = Field("llm_interactions.log", description="Path to interaction log file")
    max_log_size_mb: int = Field(100, description="Maximum log file size in MB")
    
    class Config:
        use_enum_values = True
    
    def get_default_model_capacities(self) -> List[ModelCapacity]:
        """Get default model capacity configurations."""
        return [
            ModelCapacity(
                model_name="gpt-4o-mini",
                max_tokens=128000,
                cost_per_token=0.00015,
                cost_per_output_token=0.0006,
                priority=1,
                provider="openai",
                supports_vision=True
            ),
            ModelCapacity(
                model_name="gpt-4o",
                max_tokens=128000,
                cost_per_token=0.005,
                cost_per_output_token=0.015,
                priority=2,
                provider="openai",
                supports_vision=True
            ),
            ModelCapacity(
                model_name="claude-3-haiku-20240307",
                max_tokens=200000,
                cost_per_token=0.00025,
                cost_per_output_token=0.00125,
                priority=3,
                provider="anthropic",
                supports_vision=False
            ),
            ModelCapacity(
                model_name="claude-3-sonnet-20240229",
                max_tokens=200000,
                cost_per_token=0.003,
                cost_per_output_token=0.015,
                priority=4,
                provider="anthropic",
                supports_vision=True
            ),
            ModelCapacity(
                model_name="claude-3-opus-20240229",
                max_tokens=200000,
                cost_per_token=0.015,
                cost_per_output_token=0.075,
                priority=5,
                provider="anthropic",
                supports_vision=True
            ),
        ]
    
    def __post_init__(self):
        """Initialize with default model capacities if none provided."""
        if not self.model_capacities:
            self.model_capacities = self.get_default_model_capacities()