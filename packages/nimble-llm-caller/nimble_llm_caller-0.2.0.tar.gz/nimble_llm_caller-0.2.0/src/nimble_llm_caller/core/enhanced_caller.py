"""
Enhanced LLM caller with additional features for complex workflows.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta

from .llm_caller import LLMCaller
from ..models.request import LLMRequest, BatchRequest
from ..models.response import LLMResponse, BatchResponse
from ..utils.retry_strategy import AdaptiveRetryStrategy

logger = logging.getLogger(__name__)


class EnhancedLLMCaller(LLMCaller):
    """Enhanced LLM caller with additional features for complex workflows."""
    
    def __init__(self, *args, **kwargs):
        # Use adaptive retry strategy by default
        if 'retry_strategy' not in kwargs:
            kwargs['retry_strategy'] = AdaptiveRetryStrategy()
        
        super().__init__(*args, **kwargs)
        
        # Enhanced features
        self.response_cache = {}
        self.cost_tracking = {}
        self.performance_metrics = {}
        self.custom_validators = {}
    
    def call_with_caching(
        self, 
        request: LLMRequest, 
        cache_ttl: int = 3600,
        cache_key: Optional[str] = None
    ) -> LLMResponse:
        """
        Make an LLM call with response caching.
        
        Args:
            request: LLM request
            cache_ttl: Cache time-to-live in seconds
            cache_key: Custom cache key (auto-generated if None)
            
        Returns:
            LLM response (potentially from cache)
        """
        # Generate cache key
        if not cache_key:
            cache_key = self._generate_cache_key(request)
        
        # Check cache
        if cache_key in self.response_cache:
            cached_entry = self.response_cache[cache_key]
            if datetime.now() - cached_entry['timestamp'] < timedelta(seconds=cache_ttl):
                logger.info(f"Returning cached response for {request.prompt_key}")
                return cached_entry['response']
        
        # Make fresh call
        response = self.call(request)
        
        # Cache successful responses
        if response.is_success:
            self.response_cache[cache_key] = {
                'response': response,
                'timestamp': datetime.now()
            }
        
        return response
    
    def call_with_validation(
        self,
        request: LLMRequest,
        validator: Callable[[LLMResponse], Dict[str, Any]],
        max_validation_retries: int = 3
    ) -> LLMResponse:
        """
        Make an LLM call with custom validation and retry on validation failure.
        
        Args:
            request: LLM request
            validator: Function that validates the response
            max_validation_retries: Maximum retries for validation failures
            
        Returns:
            Validated LLM response
        """
        for attempt in range(max_validation_retries + 1):
            response = self.call(request)
            
            if not response.is_success:
                return response
            
            # Validate response
            validation_result = validator(response)
            
            if validation_result.get('valid', False):
                return response
            
            if attempt < max_validation_retries:
                logger.warning(f"Validation failed for {request.prompt_key}, "
                             f"retrying ({attempt + 1}/{max_validation_retries})")
                # Optionally modify request based on validation feedback
                if 'feedback' in validation_result:
                    request = self._apply_validation_feedback(request, validation_result['feedback'])
            else:
                logger.error(f"Validation failed after {max_validation_retries} retries")
                response.parsing_warnings.append("Validation failed after retries")
        
        return response
    
    def call_with_cost_limit(
        self,
        request: LLMRequest,
        max_cost: float,
        cost_calculator: Optional[Callable[[LLMResponse], float]] = None
    ) -> LLMResponse:
        """
        Make an LLM call with cost limiting.
        
        Args:
            request: LLM request
            max_cost: Maximum allowed cost for this call
            cost_calculator: Function to calculate cost from response
            
        Returns:
            LLM response or error if cost limit exceeded
        """
        # Estimate cost before call (if possible)
        estimated_cost = self._estimate_call_cost(request)
        
        if estimated_cost > max_cost:
            logger.error(f"Estimated cost ({estimated_cost}) exceeds limit ({max_cost})")
            return LLMResponse(
                prompt_key=request.prompt_key,
                model=request.model,
                status="error",
                error_message=f"Estimated cost ({estimated_cost}) exceeds limit ({max_cost})"
            )
        
        # Make the call
        response = self.call(request)
        
        # Calculate actual cost
        if cost_calculator:
            actual_cost = cost_calculator(response)
        else:
            actual_cost = self._calculate_response_cost(response)
        
        # Track cost
        self._track_cost(request.model, actual_cost)
        
        if actual_cost > max_cost:
            logger.warning(f"Actual cost ({actual_cost}) exceeded limit ({max_cost})")
            response.parsing_warnings.append(f"Cost exceeded limit: {actual_cost} > {max_cost}")
        
        return response
    
    def call_with_performance_monitoring(
        self,
        request: LLMRequest,
        performance_thresholds: Optional[Dict[str, float]] = None
    ) -> LLMResponse:
        """
        Make an LLM call with performance monitoring.
        
        Args:
            request: LLM request
            performance_thresholds: Thresholds for performance metrics
            
        Returns:
            LLM response with performance metadata
        """
        thresholds = performance_thresholds or {
            'max_response_time': 30.0,
            'min_content_length': 10
        }
        
        # Make the call
        response = self.call(request)
        
        # Check performance thresholds
        warnings = []
        
        if response.execution_time > thresholds.get('max_response_time', 30.0):
            warnings.append(f"Slow response: {response.execution_time:.2f}s")
        
        if response.content and len(response.content) < thresholds.get('min_content_length', 10):
            warnings.append(f"Short response: {len(response.content)} characters")
        
        # Add warnings to response
        response.parsing_warnings.extend(warnings)
        
        # Track performance metrics
        self._track_performance(request.model, response)
        
        return response
    
    def batch_call_with_load_balancing(
        self,
        requests: List[LLMRequest],
        models: List[str],
        load_balance_strategy: str = "round_robin"
    ) -> BatchResponse:
        """
        Execute batch requests with load balancing across models.
        
        Args:
            requests: List of requests
            models: List of models to balance across
            load_balance_strategy: Strategy for load balancing
            
        Returns:
            Batch response
        """
        if load_balance_strategy == "round_robin":
            # Assign models in round-robin fashion
            for i, request in enumerate(requests):
                request.model = models[i % len(models)]
        
        elif load_balance_strategy == "performance_based":
            # Assign based on historical performance
            model_performance = self._get_model_performance_scores(models)
            for request in requests:
                request.model = max(models, key=lambda m: model_performance.get(m, 0))
        
        elif load_balance_strategy == "cost_optimized":
            # Assign based on cost efficiency
            model_costs = self._get_model_cost_efficiency(models)
            for request in requests:
                request.model = min(models, key=lambda m: model_costs.get(m, float('inf')))
        
        # Execute batch
        responses = []
        for request in requests:
            response = self.call(request)
            responses.append(response)
        
        # Create batch response
        batch_response = BatchResponse(responses=responses, total_requests=len(requests))
        batch_response.finalize()
        
        return batch_response
    
    def _generate_cache_key(self, request: LLMRequest) -> str:
        """Generate a cache key for a request."""
        import hashlib
        
        # Create key from prompt, model, and substitutions
        key_data = f"{request.prompt_key}:{request.model}:{str(sorted(request.substitutions.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _apply_validation_feedback(
        self, 
        request: LLMRequest, 
        feedback: str
    ) -> LLMRequest:
        """Apply validation feedback to modify request."""
        # This could modify the prompt or parameters based on feedback
        # For now, just add feedback to metadata
        request.metadata['validation_feedback'] = feedback
        return request
    
    def _estimate_call_cost(self, request: LLMRequest) -> float:
        """Estimate the cost of an LLM call."""
        # Simplified cost estimation based on model and estimated tokens
        model_costs = {
            'gpt-4o': 0.03,  # per 1K tokens
            'gpt-4': 0.06,
            'claude-3-sonnet': 0.015,
            'gemini-pro': 0.001
        }
        
        base_cost = model_costs.get(request.model, 0.02)
        estimated_tokens = 1000  # Default estimate
        
        return (estimated_tokens / 1000) * base_cost
    
    def _calculate_response_cost(self, response: LLMResponse) -> float:
        """Calculate actual cost of a response."""
        if not response.tokens_used:
            return 0.0
        
        # Simplified cost calculation
        total_tokens = response.tokens_used.get('total_tokens', 0)
        model_costs = {
            'gpt-4o': 0.03,
            'gpt-4': 0.06,
            'claude-3-sonnet': 0.015,
            'gemini-pro': 0.001
        }
        
        base_cost = model_costs.get(response.model, 0.02)
        return (total_tokens / 1000) * base_cost
    
    def _track_cost(self, model: str, cost: float):
        """Track cost for a model."""
        if model not in self.cost_tracking:
            self.cost_tracking[model] = {'total_cost': 0.0, 'call_count': 0}
        
        self.cost_tracking[model]['total_cost'] += cost
        self.cost_tracking[model]['call_count'] += 1
    
    def _track_performance(self, model: str, response: LLMResponse):
        """Track performance metrics for a model."""
        if model not in self.performance_metrics:
            self.performance_metrics[model] = {
                'total_time': 0.0,
                'call_count': 0,
                'success_count': 0
            }
        
        metrics = self.performance_metrics[model]
        metrics['total_time'] += response.execution_time
        metrics['call_count'] += 1
        
        if response.is_success:
            metrics['success_count'] += 1
    
    def _get_model_performance_scores(self, models: List[str]) -> Dict[str, float]:
        """Get performance scores for models."""
        scores = {}
        
        for model in models:
            if model in self.performance_metrics:
                metrics = self.performance_metrics[model]
                avg_time = metrics['total_time'] / metrics['call_count']
                success_rate = metrics['success_count'] / metrics['call_count']
                # Higher score is better (fast + reliable)
                scores[model] = success_rate / (avg_time + 0.1)
            else:
                scores[model] = 0.5  # Default score
        
        return scores
    
    def _get_model_cost_efficiency(self, models: List[str]) -> Dict[str, float]:
        """Get cost efficiency scores for models."""
        efficiency = {}
        
        for model in models:
            if model in self.cost_tracking:
                tracking = self.cost_tracking[model]
                avg_cost = tracking['total_cost'] / tracking['call_count']
                efficiency[model] = avg_cost
            else:
                efficiency[model] = 0.02  # Default cost
        
        return efficiency
    
    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Get enhanced statistics including cost and performance data."""
        base_stats = self.get_statistics()
        
        return {
            **base_stats,
            "cost_tracking": self.cost_tracking,
            "performance_metrics": self.performance_metrics,
            "cache_size": len(self.response_cache),
            "total_cached_responses": sum(1 for entry in self.response_cache.values() 
                                        if datetime.now() - entry['timestamp'] < timedelta(hours=1))
        }
    
    def clear_cache(self):
        """Clear the response cache."""
        self.response_cache.clear()
        logger.info("Response cache cleared")
    
    def cleanup_expired_cache(self, max_age_hours: int = 24):
        """Remove expired entries from cache."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        expired_keys = [
            key for key, entry in self.response_cache.items()
            if entry['timestamp'] < cutoff_time
        ]
        
        for key in expired_keys:
            del self.response_cache[key]
        
        logger.info(f"Removed {len(expired_keys)} expired cache entries")