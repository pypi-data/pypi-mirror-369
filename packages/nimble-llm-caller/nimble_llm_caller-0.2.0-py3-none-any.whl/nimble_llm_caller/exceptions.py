"""
Custom exceptions for nimble-llm-caller with enhanced context management.
"""

from typing import Optional, Dict, Any, List


class NimbleLLMError(Exception):
    """Base exception for all nimble-llm-caller errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ContextOverflowError(NimbleLLMError):
    """Raised when content exceeds available model context limits."""
    
    def __init__(self, 
                 message: str,
                 required_tokens: int,
                 max_tokens: int,
                 model: str,
                 suggested_actions: Optional[List[str]] = None):
        super().__init__(message)
        self.required_tokens = required_tokens
        self.max_tokens = max_tokens
        self.model = model
        self.suggested_actions = suggested_actions or []
        
        self.details = {
            "required_tokens": required_tokens,
            "max_tokens": max_tokens,
            "model": model,
            "overflow_amount": required_tokens - max_tokens,
            "suggested_actions": self.suggested_actions
        }
    
    def get_overflow_ratio(self) -> float:
        """Get the ratio of required tokens to max tokens."""
        return self.required_tokens / self.max_tokens if self.max_tokens > 0 else float('inf')
    
    def suggest_solutions(self) -> List[str]:
        """Get suggested solutions for the context overflow."""
        solutions = []
        
        overflow_ratio = self.get_overflow_ratio()
        
        if overflow_ratio <= 2.0:
            solutions.append("Try upshifting to a model with larger context window")
        
        if overflow_ratio <= 5.0:
            solutions.append("Consider chunking the content into smaller pieces")
        else:
            solutions.append("Content is very large - chunking is recommended")
        
        solutions.append("Remove unnecessary content from the request")
        solutions.append("Summarize large text sections before processing")
        
        return solutions


class FileProcessingError(NimbleLLMError):
    """Raised when file processing fails."""
    
    def __init__(self, 
                 message: str,
                 file_path: str,
                 file_type: Optional[str] = None,
                 processing_stage: Optional[str] = None,
                 recoverable: bool = False):
        super().__init__(message)
        self.file_path = file_path
        self.file_type = file_type
        self.processing_stage = processing_stage
        self.recoverable = recoverable
        
        self.details = {
            "file_path": file_path,
            "file_type": file_type,
            "processing_stage": processing_stage,
            "recoverable": recoverable
        }


class ModelUpshiftError(NimbleLLMError):
    """Raised when model upshifting fails."""
    
    def __init__(self, 
                 message: str,
                 original_model: str,
                 required_tokens: int,
                 attempted_models: Optional[List[str]] = None,
                 cost_constraint: Optional[float] = None):
        super().__init__(message)
        self.original_model = original_model
        self.required_tokens = required_tokens
        self.attempted_models = attempted_models or []
        self.cost_constraint = cost_constraint
        
        self.details = {
            "original_model": original_model,
            "required_tokens": required_tokens,
            "attempted_models": self.attempted_models,
            "cost_constraint": cost_constraint
        }


class ChunkingError(NimbleLLMError):
    """Raised when content chunking fails."""
    
    def __init__(self, 
                 message: str,
                 content_length: int,
                 max_chunk_size: int,
                 chunking_method: Optional[str] = None):
        super().__init__(message)
        self.content_length = content_length
        self.max_chunk_size = max_chunk_size
        self.chunking_method = chunking_method
        
        self.details = {
            "content_length": content_length,
            "max_chunk_size": max_chunk_size,
            "chunking_method": chunking_method
        }


class TokenEstimationError(NimbleLLMError):
    """Raised when token estimation fails."""
    
    def __init__(self, 
                 message: str,
                 content_type: str,
                 model: str,
                 estimation_method: Optional[str] = None):
        super().__init__(message)
        self.content_type = content_type
        self.model = model
        self.estimation_method = estimation_method
        
        self.details = {
            "content_type": content_type,
            "model": model,
            "estimation_method": estimation_method
        }


class InteractionLoggingError(NimbleLLMError):
    """Raised when interaction logging fails."""
    
    def __init__(self, 
                 message: str,
                 log_file_path: Optional[str] = None,
                 operation: Optional[str] = None):
        super().__init__(message)
        self.log_file_path = log_file_path
        self.operation = operation
        
        self.details = {
            "log_file_path": log_file_path,
            "operation": operation
        }


class ContextStrategyError(NimbleLLMError):
    """Raised when context strategy execution fails."""
    
    def __init__(self, 
                 message: str,
                 strategy: str,
                 model: str,
                 required_tokens: int,
                 failed_actions: Optional[List[str]] = None):
        super().__init__(message)
        self.strategy = strategy
        self.model = model
        self.required_tokens = required_tokens
        self.failed_actions = failed_actions or []
        
        self.details = {
            "strategy": strategy,
            "model": model,
            "required_tokens": required_tokens,
            "failed_actions": self.failed_actions
        }


class ModelCapacityError(NimbleLLMError):
    """Raised when model capacity information is invalid or missing."""
    
    def __init__(self, 
                 message: str,
                 model: str,
                 capacity_issue: Optional[str] = None):
        super().__init__(message)
        self.model = model
        self.capacity_issue = capacity_issue
        
        self.details = {
            "model": model,
            "capacity_issue": capacity_issue
        }


class ConfigurationError(NimbleLLMError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, 
                 message: str,
                 config_section: Optional[str] = None,
                 config_key: Optional[str] = None,
                 expected_type: Optional[str] = None):
        super().__init__(message)
        self.config_section = config_section
        self.config_key = config_key
        self.expected_type = expected_type
        
        self.details = {
            "config_section": config_section,
            "config_key": config_key,
            "expected_type": expected_type
        }


class ProviderError(NimbleLLMError):
    """Raised when there are issues with LLM provider integration."""
    
    def __init__(self, 
                 message: str,
                 provider: str,
                 model: str,
                 error_code: Optional[str] = None,
                 retry_after: Optional[int] = None):
        super().__init__(message)
        self.provider = provider
        self.model = model
        self.error_code = error_code
        self.retry_after = retry_after
        
        self.details = {
            "provider": provider,
            "model": model,
            "error_code": error_code,
            "retry_after": retry_after
        }


class ValidationError(NimbleLLMError):
    """Raised when request or response validation fails."""
    
    def __init__(self, 
                 message: str,
                 validation_type: str,
                 failed_checks: Optional[List[str]] = None,
                 field_errors: Optional[Dict[str, str]] = None):
        super().__init__(message)
        self.validation_type = validation_type
        self.failed_checks = failed_checks or []
        self.field_errors = field_errors or {}
        
        self.details = {
            "validation_type": validation_type,
            "failed_checks": self.failed_checks,
            "field_errors": self.field_errors
        }


# Error recovery utilities
class ErrorRecoveryStrategy:
    """Strategies for recovering from various errors."""
    
    @staticmethod
    def handle_context_overflow(error: ContextOverflowError) -> Dict[str, Any]:
        """Provide recovery options for context overflow."""
        recovery_options = {
            "can_upshift": error.get_overflow_ratio() <= 3.0,
            "can_chunk": True,
            "suggested_chunk_size": max(1000, error.max_tokens // 2),
            "alternative_models": [],
            "content_reduction_suggestions": [
                "Remove verbose examples",
                "Summarize background information",
                "Split into multiple requests"
            ]
        }
        
        return recovery_options
    
    @staticmethod
    def handle_file_processing_error(error: FileProcessingError) -> Dict[str, Any]:
        """Provide recovery options for file processing errors."""
        recovery_options = {
            "can_retry": error.recoverable,
            "alternative_formats": [],
            "manual_processing_required": not error.recoverable,
            "suggestions": []
        }
        
        if error.file_type == "application/pdf":
            recovery_options["suggestions"].extend([
                "Try converting PDF to text manually",
                "Use OCR if PDF contains images",
                "Check if PDF is password protected"
            ])
        elif error.file_type and error.file_type.startswith("image/"):
            recovery_options["suggestions"].extend([
                "Verify image format is supported",
                "Check image file integrity",
                "Try resizing large images"
            ])
        
        return recovery_options
    
    @staticmethod
    def handle_model_upshift_error(error: ModelUpshiftError) -> Dict[str, Any]:
        """Provide recovery options for upshift errors."""
        recovery_options = {
            "try_chunking": True,
            "reduce_content": True,
            "alternative_strategies": ["chunk_first", "chunk_only"],
            "cost_optimization": error.cost_constraint is not None
        }
        
        if error.cost_constraint:
            recovery_options["suggestions"] = [
                f"Increase cost multiplier above {error.cost_constraint}",
                "Use chunking instead of upshifting",
                "Reduce content size to fit current model"
            ]
        
        return recovery_options


def create_detailed_error_report(error: Exception) -> Dict[str, Any]:
    """Create a detailed error report for debugging."""
    report = {
        "error_type": type(error).__name__,
        "message": str(error),
        "timestamp": None,  # Would be filled by caller
        "recoverable": False,
        "suggestions": [],
        "details": {}
    }
    
    if isinstance(error, NimbleLLMError):
        report["details"] = error.details
        report["recoverable"] = True
        
        if isinstance(error, ContextOverflowError):
            report["suggestions"] = error.suggest_solutions()
            recovery = ErrorRecoveryStrategy.handle_context_overflow(error)
            report["recovery_options"] = recovery
        
        elif isinstance(error, FileProcessingError):
            recovery = ErrorRecoveryStrategy.handle_file_processing_error(error)
            report["recovery_options"] = recovery
            report["recoverable"] = error.recoverable
        
        elif isinstance(error, ModelUpshiftError):
            recovery = ErrorRecoveryStrategy.handle_model_upshift_error(error)
            report["recovery_options"] = recovery
    
    return report