"""
Core LLM caller with robust error handling and response parsing.
"""

import logging
import time
from typing import Dict, Any, Optional, List
import litellm
from litellm.exceptions import APIError, RateLimitError, ServiceUnavailableError, BadRequestError

from ..models.request import LLMRequest, ResponseFormat
from ..models.response import LLMResponse, ResponseStatus
from ..utils.json_parser import JSONParser
from ..utils.retry_strategy import RetryStrategy, DEFAULT_RETRY

logger = logging.getLogger(__name__)


def _normalize_token_usage(usage_data):
    """Normalize token usage data to simple Dict[str, int] format."""
    if not usage_data:
        return {}
    
    normalized = {}
    
    # Handle different token usage formats
    if isinstance(usage_data, dict):
        # Extract simple integer values, skip complex nested structures
        for key, value in usage_data.items():
            if isinstance(value, int):
                normalized[key] = value
            elif isinstance(value, dict):
                # Skip nested dictionaries that contain None values
                continue
            elif value is not None:
                try:
                    normalized[key] = int(value)
                except (ValueError, TypeError):
                    continue
    
    return normalized



class LLMCaller:
    """Core LLM caller with robust error handling and response parsing."""
    
    def __init__(
        self,
        retry_strategy: Optional[RetryStrategy] = None,
        json_parser: Optional[JSONParser] = None,
        default_model_params: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the LLM caller.
        
        Args:
            retry_strategy: Strategy for handling retries
            json_parser: Parser for JSON responses
            default_model_params: Default parameters for all models
        """
        self.retry_strategy = retry_strategy or DEFAULT_RETRY
        self.json_parser = json_parser or JSONParser()
        self.default_model_params = default_model_params or {}
        
        # Configure LiteLLM
        litellm.telemetry = False
        litellm.set_verbose = False
        
        # Statistics tracking
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }
    
    def call(self, request: LLMRequest) -> LLMResponse:
        """
        Make a single LLM call.
        
        Args:
            request: LLM request configuration
            
        Returns:
            LLM response with parsed content
        """
        start_time = time.time()
        self.stats["total_calls"] += 1
        
        try:
            # Prepare the call
            messages = self._extract_messages_from_request(request)
            model_params = self._prepare_model_params(request)
            
            # Execute with retry logic
            def make_call():
                return self._make_litellm_call(request.model, messages, model_params)
            
            raw_response = self.retry_strategy.execute_with_retry(
                make_call, 
                f"LLM call to {request.model}"
            )
            
            # Parse the response
            parsed_content = self._parse_response_content(
                raw_response.get("content", ""),
                request.response_format
            )
            
            # Create response object
            execution_time = time.time() - start_time
            response = LLMResponse(
                prompt_key=request.prompt_key,
                model=request.model,
                status=ResponseStatus.SUCCESS,
                content=raw_response.get("content"),
                parsed_content=parsed_content,
                execution_time=execution_time,
                attempts=raw_response.get("attempts", 1),
                tokens_used=_normalize_token_usage(raw_response.get("usage", {})),
                request_metadata=request.metadata
            )
            
            # Update statistics
            self.stats["successful_calls"] += 1
            if response.tokens_used:
                self.stats["total_tokens"] += response.tokens_used.get("total_tokens", 0)
            
            logger.info(f"✅ Successful LLM call to {request.model} for {request.prompt_key} "
                       f"in {execution_time:.2f}s")
            
            return response
            
        except Exception as e:
            # Create error response
            execution_time = time.time() - start_time
            response = LLMResponse(
                prompt_key=request.prompt_key,
                model=request.model,
                status=ResponseStatus.ERROR,
                error_message=str(e),
                execution_time=execution_time,
                request_metadata=request.metadata
            )
            
            self.stats["failed_calls"] += 1
            
            logger.error(f"❌ Failed LLM call to {request.model} for {request.prompt_key}: {e}")
            
            return response
    
    def _extract_messages_from_request(self, request: LLMRequest) -> List[Dict[str, str]]:
        """Extract messages from request metadata or create default."""
        # This would typically come from the prompt manager
        # For now, create a simple message structure
        if "messages" in request.metadata:
            return request.metadata["messages"]
        
        # Fallback: create simple user message
        content = request.metadata.get("content", f"Process this request: {request.prompt_key}")
        return [{"role": "user", "content": content}]
    
    def _prepare_model_params(self, request: LLMRequest) -> Dict[str, Any]:
        """Prepare model parameters by merging defaults with request-specific params."""
        params = self.default_model_params.copy()
        params.update(request.model_params)
        
        # Ensure minimum token count for complex tasks
        if request.response_format == ResponseFormat.JSON:
            params.setdefault("max_tokens", 4096)
        
        # Remove model from params (it's passed separately)
        params.pop("model", None)
        
        return params
    
    def _make_litellm_call(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make the actual LiteLLM call."""
        logger.debug(f"Making LiteLLM call to {model} with {len(messages)} messages")
        
        response = litellm.completion(
            model=model,
            messages=messages,
            **params
        )
        
        # Extract content safely
        content = None
        if response.choices and len(response.choices) > 0:
            choice = response.choices[0]
            if hasattr(choice, 'message') and choice.message:
                content = choice.message.content
            elif hasattr(choice, 'text'):
                content = choice.text
        
        if content is None:
            logger.warning(f"No content found in response from {model}")
            content = ""
        
        return {
            "content": content,
            "usage": response.usage.dict() if response.usage else {},
            "model": response.model,
            "attempts": 1  # This will be updated by retry logic
        }
    
    def _parse_response_content(self, content: str, response_format: ResponseFormat) -> Any:
        """Parse response content based on expected format."""
        if not content:
            return None
        
        if response_format == ResponseFormat.JSON:
            parsed = self.json_parser.parse(content)
            # Clean the parsed data
            if isinstance(parsed, dict):
                return self.json_parser.clean_parsed_data(parsed)
            return parsed
        
        elif response_format == ResponseFormat.MARKDOWN:
            # Basic markdown cleanup
            return content.strip()
        
        elif response_format == ResponseFormat.LATEX:
            # Basic LaTeX cleanup
            return content.strip()
        
        else:  # TEXT
            return content.strip()
    
    def validate_response(
        self, 
        response: LLMResponse, 
        required_keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate an LLM response.
        
        Args:
            response: Response to validate
            required_keys: Required keys for JSON responses
            
        Returns:
            Validation results
        """
        validation = {
            "valid": True,
            "issues": []
        }
        
        # Check basic response validity
        if not response.is_success:
            validation["valid"] = False
            validation["issues"].append(f"Response status is {response.status}")
        
        if not response.has_content:
            validation["valid"] = False
            validation["issues"].append("Response has no content")
        
        # Validate JSON responses
        if (required_keys and 
            response.parsed_content and 
            isinstance(response.parsed_content, dict)):
            
            key_validation = self.json_parser.validate_required_keys(
                response.parsed_content, 
                required_keys
            )
            
            if not key_validation["valid"]:
                validation["valid"] = False
                validation["issues"].append(
                    f"Missing required keys: {key_validation['missing_keys']}"
                )
        
        return validation
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get caller statistics."""
        success_rate = 0.0
        if self.stats["total_calls"] > 0:
            success_rate = (self.stats["successful_calls"] / self.stats["total_calls"]) * 100
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "retry_strategy": self.retry_strategy.get_stats()
        }
    
    def reset_statistics(self):
        """Reset statistics counters."""
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }