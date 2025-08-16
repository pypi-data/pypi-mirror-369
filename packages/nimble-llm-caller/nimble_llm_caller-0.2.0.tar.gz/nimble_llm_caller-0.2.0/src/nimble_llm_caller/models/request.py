"""
Request models for LLM calls.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from pathlib import Path


class ResponseFormat(str, Enum):
    """Supported response formats."""
    TEXT = "text"
    JSON = "json_object"
    MARKDOWN = "markdown"
    LATEX = "latex"


class FileAttachment(BaseModel):
    """File attachment for LLM requests."""
    
    file_path: Union[str, Path] = Field(..., description="Path to the file")
    content_type: Optional[str] = Field(None, description="MIME type of the file")
    content: Optional[str] = Field(None, description="Processed file content")
    token_estimate: Optional[int] = Field(None, description="Estimated token count for this file")
    processing_metadata: Dict[str, Any] = Field(default_factory=dict, description="File processing metadata")
    
    class Config:
        arbitrary_types_allowed = True


class ContextAnalysis(BaseModel):
    """Analysis of request context requirements."""
    
    total_tokens: int = Field(..., description="Total estimated tokens for the request")
    text_tokens: int = Field(..., description="Tokens from text content")
    file_tokens: int = Field(..., description="Tokens from file attachments")
    model_capacity: Optional[int] = Field(None, description="Current model's token capacity")
    requires_upshift: bool = Field(False, description="Whether upshifting is needed")
    requires_chunking: bool = Field(False, description="Whether chunking is needed")
    recommended_models: List[str] = Field(default_factory=list, description="Models that can handle this context")


class ProcessedFile(BaseModel):
    """Processed file content with metadata."""
    
    original_path: Union[str, Path] = Field(..., description="Original file path")
    content: str = Field(..., description="Extracted text content")
    content_type: str = Field(..., description="Detected content type")
    token_count: int = Field(..., description="Token count for this content")
    processing_method: str = Field(..., description="Method used to extract content")
    warnings: List[str] = Field(default_factory=list, description="Processing warnings")
    
    class Config:
        arbitrary_types_allowed = True


class LLMRequest(BaseModel):
    """Single LLM request model with context management support."""
    
    prompt_key: str = Field(..., description="Key identifying the prompt to use")
    model: str = Field(..., description="Model name (e.g., 'gpt-4o', 'claude-3-sonnet')")
    substitutions: Dict[str, Any] = Field(default_factory=dict, description="Variables to substitute in prompt")
    response_format: ResponseFormat = Field(default=ResponseFormat.TEXT, description="Expected response format")
    model_params: Dict[str, Any] = Field(default_factory=dict, description="Model-specific parameters")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for tracking")
    
    # Context management fields
    file_attachments: List[FileAttachment] = Field(default_factory=list, description="Files to attach to the request")
    context_analysis: Optional[ContextAnalysis] = Field(None, description="Context analysis results")
    processed_files: List[ProcessedFile] = Field(default_factory=list, description="Processed file contents")
    context_strategy: Optional[str] = Field(None, description="Strategy for handling context overflow")
    max_cost_multiplier: float = Field(2.0, description="Maximum cost multiplier for upshifting")
    
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True


class BatchRequest(BaseModel):
    """Batch request for multiple LLM calls."""
    
    requests: List[LLMRequest] = Field(..., description="List of individual LLM requests")
    shared_substitutions: Dict[str, Any] = Field(default_factory=dict, description="Substitutions applied to all requests")
    default_model: Optional[str] = Field(None, description="Default model if not specified in individual requests")
    parallel: bool = Field(default=True, description="Whether to execute requests in parallel")
    max_concurrent: int = Field(default=5, description="Maximum concurrent requests when parallel=True")
    
    def __post_init__(self):
        """Apply shared substitutions and default model to individual requests."""
        for request in self.requests:
            # Merge shared substitutions (individual request substitutions take precedence)
            merged_substitutions = {**self.shared_substitutions, **request.substitutions}
            request.substitutions = merged_substitutions
            
            # Apply default model if not specified
            if not request.model and self.default_model:
                request.model = self.default_model


class RepromptRequest(BaseModel):
    """Request for reprompting using previous results."""
    
    base_request: LLMRequest = Field(..., description="Base request configuration")
    previous_results: List[Dict[str, Any]] = Field(..., description="Results from previous LLM calls")
    context_key: str = Field(default="previous_context", description="Key to use for previous results in substitutions")
    combine_strategy: str = Field(default="append", description="How to combine previous results (append, merge, replace)")
    
    def to_llm_request(self) -> LLMRequest:
        """Convert to a standard LLM request with previous results as context."""
        # Combine previous results based on strategy
        if self.combine_strategy == "append":
            context_value = "\n\n".join([str(result) for result in self.previous_results])
        elif self.combine_strategy == "merge":
            context_value = {f"result_{i}": result for i, result in enumerate(self.previous_results)}
        else:  # replace
            context_value = self.previous_results[-1] if self.previous_results else {}
        
        # Add context to substitutions
        substitutions = {**self.base_request.substitutions, self.context_key: context_value}
        
        return LLMRequest(
            prompt_key=self.base_request.prompt_key,
            model=self.base_request.model,
            substitutions=substitutions,
            response_format=self.base_request.response_format,
            model_params=self.base_request.model_params,
            metadata={**self.base_request.metadata, "is_reprompt": True}
        )