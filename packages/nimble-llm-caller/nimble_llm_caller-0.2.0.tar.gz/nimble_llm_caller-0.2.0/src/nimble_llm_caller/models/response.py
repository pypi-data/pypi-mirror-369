"""
Response models for LLM calls.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ResponseStatus(str, Enum):
    """Response status enumeration."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"


class LLMResponse(BaseModel):
    """Single LLM response model with context management support."""
    
    prompt_key: str = Field(..., description="Key of the prompt that was used")
    model: str = Field(..., description="Model that generated the response")
    status: ResponseStatus = Field(..., description="Response status")
    content: Optional[str] = Field(None, description="Raw response content")
    parsed_content: Optional[Union[Dict[str, Any], str]] = Field(None, description="Parsed response content")
    error_message: Optional[str] = Field(None, description="Error message if status is error")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    execution_time: float = Field(0.0, description="Execution time in seconds")
    attempts: int = Field(1, description="Number of attempts made")
    tokens_used: Optional[Dict[str, int]] = Field(None, description="Token usage information")
    
    # Parsing information
    parsing_strategy: Optional[str] = Field(None, description="Strategy used for parsing (if applicable)")
    parsing_warnings: List[str] = Field(default_factory=list, description="Warnings during parsing")
    
    # Request context
    request_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata from original request")
    
    # Context management information
    original_model: Optional[str] = Field(None, description="Original model before any upshifting")
    upshift_reason: Optional[str] = Field(None, description="Reason for model upshifting")
    context_strategy_used: Optional[str] = Field(None, description="Context strategy that was applied")
    was_chunked: bool = Field(False, description="Whether the request was chunked")
    chunk_info: Optional[Dict[str, Any]] = Field(None, description="Information about chunking if applied")
    files_processed: int = Field(0, description="Number of files processed in the request")
    
    class Config:
        use_enum_values = True
    
    @property
    def is_success(self) -> bool:
        """Check if response was successful."""
        return self.status == ResponseStatus.SUCCESS
    
    @property
    def has_content(self) -> bool:
        """Check if response has usable content."""
        return self.content is not None and len(str(self.content).strip()) > 0
    
    @property
    def has_parsed_content(self) -> bool:
        """Check if response has parsed content."""
        return self.parsed_content is not None
    
    def get_content_preview(self, max_length: int = 100) -> str:
        """Get a preview of the content for logging/display."""
        if not self.content:
            return "No content"
        
        content_str = str(self.content)
        if len(content_str) <= max_length:
            return content_str
        
        return content_str[:max_length] + "..."


class BatchResponse(BaseModel):
    """Response for batch LLM calls."""
    
    responses: List[LLMResponse] = Field(..., description="Individual responses")
    total_requests: int = Field(..., description="Total number of requests")
    successful_requests: int = Field(..., description="Number of successful requests")
    failed_requests: int = Field(..., description="Number of failed requests")
    
    # Timing information
    start_time: datetime = Field(default_factory=datetime.now, description="Batch start time")
    end_time: Optional[datetime] = Field(None, description="Batch end time")
    total_execution_time: float = Field(0.0, description="Total execution time in seconds")
    
    # Aggregated token usage
    total_tokens_used: Dict[str, int] = Field(default_factory=dict, description="Aggregated token usage")
    
    class Config:
        use_enum_values = True
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as a percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def is_complete_success(self) -> bool:
        """Check if all requests were successful."""
        return self.successful_requests == self.total_requests
    
    @property
    def has_any_success(self) -> bool:
        """Check if any requests were successful."""
        return self.successful_requests > 0
    
    def get_successful_responses(self) -> List[LLMResponse]:
        """Get only the successful responses."""
        return [r for r in self.responses if r.is_success]
    
    def get_failed_responses(self) -> List[LLMResponse]:
        """Get only the failed responses."""
        return [r for r in self.responses if not r.is_success]
    
    def get_responses_by_prompt_key(self, prompt_key: str) -> List[LLMResponse]:
        """Get responses for a specific prompt key."""
        return [r for r in self.responses if r.prompt_key == prompt_key]
    
    def get_responses_by_model(self, model: str) -> List[LLMResponse]:
        """Get responses from a specific model."""
        return [r for r in self.responses if r.model == model]
    
    def finalize(self) -> None:
        """Finalize the batch response by calculating aggregated metrics."""
        self.end_time = datetime.now()
        if hasattr(self, 'start_time'):
            self.total_execution_time = (self.end_time - self.start_time).total_seconds()
        
        # Calculate aggregated metrics
        self.total_requests = len(self.responses)
        self.successful_requests = len(self.get_successful_responses())
        self.failed_requests = len(self.get_failed_responses())
        
        # Aggregate token usage
        total_tokens = {}
        for response in self.responses:
            if response.tokens_used:
                for key, value in response.tokens_used.items():
                    total_tokens[key] = total_tokens.get(key, 0) + value
        self.total_tokens_used = total_tokens


class DocumentResponse(BaseModel):
    """Response for document assembly operations."""
    
    document_content: str = Field(..., description="Assembled document content")
    format: str = Field(..., description="Document format (markdown, latex, text)")
    source_responses: List[str] = Field(..., description="Prompt keys of source responses")
    template_used: Optional[str] = Field(None, description="Template file used for assembly")
    
    # Assembly metadata
    assembly_time: datetime = Field(default_factory=datetime.now, description="Assembly timestamp")
    word_count: int = Field(0, description="Approximate word count")
    character_count: int = Field(0, description="Character count")
    
    def __post_init__(self):
        """Calculate document statistics."""
        self.character_count = len(self.document_content)
        self.word_count = len(self.document_content.split())
    
    @property
    def is_empty(self) -> bool:
        """Check if document is empty."""
        return len(self.document_content.strip()) == 0
    
    def save_to_file(self, filepath: str) -> None:
        """Save document to file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.document_content)