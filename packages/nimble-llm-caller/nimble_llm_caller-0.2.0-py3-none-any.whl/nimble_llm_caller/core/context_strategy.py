"""
Context strategy management for handling context overflow scenarios.
"""

from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass
import logging

from ..models.request import LLMRequest
from .model_upshifter import ModelUpshifter, UpshiftResult
from .content_chunker import ContentChunker, ChunkingResult

logger = logging.getLogger(__name__)


class ContextOverflowStrategy(Enum):
    """Strategies for handling context overflow."""
    UPSHIFT_FIRST = "upshift_first"      # Try upshifting first, then chunking
    CHUNK_FIRST = "chunk_first"          # Try chunking first, then upshifting
    UPSHIFT_ONLY = "upshift_only"        # Only try upshifting, fail if not possible
    CHUNK_ONLY = "chunk_only"            # Only try chunking, never upshift
    FAIL_FAST = "fail_fast"              # Fail immediately on overflow


@dataclass
class StrategyResult:
    """Result of applying a context strategy."""
    success: bool
    strategy_used: ContextOverflowStrategy
    action_taken: str  # "none", "upshift", "chunk", "failed"
    modified_requests: List[LLMRequest] = None
    upshift_result: Optional[UpshiftResult] = None
    chunking_result: Optional[ChunkingResult] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.modified_requests is None:
            self.modified_requests = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}


class ContextStrategy:
    """Manages user preferences for handling context overflow scenarios."""
    
    def __init__(self, 
                 default_strategy: ContextOverflowStrategy = ContextOverflowStrategy.UPSHIFT_FIRST,
                 upshifter: Optional[ModelUpshifter] = None,
                 chunker: Optional[ContentChunker] = None,
                 max_cost_multiplier: float = 3.0,
                 enable_fallback: bool = True):
        """
        Initialize the context strategy manager.
        
        Args:
            default_strategy: Default strategy to use
            upshifter: Model upshifter instance
            chunker: Content chunker instance
            max_cost_multiplier: Maximum cost multiplier for upshifting
            enable_fallback: Whether to enable fallback strategies
        """
        self.default_strategy = default_strategy
        self.upshifter = upshifter or ModelUpshifter()
        self.chunker = chunker or ContentChunker()
        self.max_cost_multiplier = max_cost_multiplier
        self.enable_fallback = enable_fallback
        
        # Per-model strategy overrides
        self.model_strategies: Dict[str, ContextOverflowStrategy] = {}
        
        # Per-request-type strategy overrides
        self.request_type_strategies: Dict[str, ContextOverflowStrategy] = {}
    
    def handle_context_overflow(self, 
                              request: LLMRequest,
                              required_tokens: int,
                              max_tokens: int,
                              requires_vision: bool = False,
                              strategy_override: Optional[ContextOverflowStrategy] = None) -> StrategyResult:
        """
        Handle context overflow using the configured strategy.
        
        Args:
            request: Original LLM request
            required_tokens: Number of tokens needed
            max_tokens: Maximum tokens the current model can handle
            requires_vision: Whether vision support is required
            strategy_override: Override the default strategy for this request
            
        Returns:
            StrategyResult with the outcome
        """
        # Determine which strategy to use
        strategy = self._determine_strategy(request, strategy_override)
        
        logger.info(f"Handling context overflow with strategy: {strategy.value}")
        logger.info(f"Required tokens: {required_tokens}, Max tokens: {max_tokens}")
        
        # Apply the strategy
        if strategy == ContextOverflowStrategy.UPSHIFT_FIRST:
            return self._handle_upshift_first(request, required_tokens, requires_vision)
        elif strategy == ContextOverflowStrategy.CHUNK_FIRST:
            return self._handle_chunk_first(request, required_tokens, max_tokens)
        elif strategy == ContextOverflowStrategy.UPSHIFT_ONLY:
            return self._handle_upshift_only(request, required_tokens, requires_vision)
        elif strategy == ContextOverflowStrategy.CHUNK_ONLY:
            return self._handle_chunk_only(request, required_tokens, max_tokens)
        elif strategy == ContextOverflowStrategy.FAIL_FAST:
            return self._handle_fail_fast(request, required_tokens, max_tokens)
        else:
            return StrategyResult(
                success=False,
                strategy_used=strategy,
                action_taken="failed",
                warnings=[f"Unknown strategy: {strategy}"]
            )
    
    def _determine_strategy(self, 
                          request: LLMRequest, 
                          strategy_override: Optional[ContextOverflowStrategy]) -> ContextOverflowStrategy:
        """Determine which strategy to use for a request."""
        if strategy_override:
            return strategy_override
        
        # Check for model-specific strategy
        if request.model in self.model_strategies:
            return self.model_strategies[request.model]
        
        # Check for request-type strategy
        request_type = request.metadata.get("request_type") if request.metadata else None
        if request_type and request_type in self.request_type_strategies:
            return self.request_type_strategies[request_type]
        
        # Check request-level strategy preference
        if hasattr(request, 'context_strategy') and request.context_strategy:
            try:
                return ContextOverflowStrategy(request.context_strategy)
            except ValueError:
                logger.warning(f"Invalid context strategy in request: {request.context_strategy}")
        
        return self.default_strategy
    
    def _handle_upshift_first(self, 
                            request: LLMRequest, 
                            required_tokens: int, 
                            requires_vision: bool) -> StrategyResult:
        """Handle overflow by trying upshift first, then chunking."""
        # Try upshifting first
        upshift_result = self.upshifter.find_suitable_model(
            request, required_tokens, requires_vision
        )
        
        if upshift_result.success and upshift_result.selected_model != request.model:
            # Upshift successful
            upshifted_request, _ = self.upshifter.upshift_request(
                request, required_tokens, requires_vision
            )
            
            return StrategyResult(
                success=True,
                strategy_used=ContextOverflowStrategy.UPSHIFT_FIRST,
                action_taken="upshift",
                modified_requests=[upshifted_request],
                upshift_result=upshift_result,
                metadata={
                    "original_model": request.model,
                    "upshifted_model": upshift_result.selected_model,
                    "cost_multiplier": upshift_result.cost_multiplier
                }
            )
        
        # Upshift failed or not needed, try chunking if fallback enabled
        if self.enable_fallback:
            logger.info("Upshift failed or not beneficial, trying chunking")
            
            # Estimate max tokens for current model (conservative)
            current_capacity = self.upshifter.registry.get_model_capacity(request.model)
            max_tokens = current_capacity.max_context_tokens if current_capacity else 4096
            chunk_max_tokens = int(max_tokens * 0.8)  # Leave some buffer
            
            chunked_requests = self.chunker.chunk_request(
                request, chunk_max_tokens
            )
            
            if len(chunked_requests) > 1:
                return StrategyResult(
                    success=True,
                    strategy_used=ContextOverflowStrategy.UPSHIFT_FIRST,
                    action_taken="chunk",
                    modified_requests=chunked_requests,
                    upshift_result=upshift_result,
                    warnings=["Upshift failed, used chunking as fallback"],
                    metadata={
                        "chunk_count": len(chunked_requests),
                        "fallback_used": True
                    }
                )
        
        # Both strategies failed
        return StrategyResult(
            success=False,
            strategy_used=ContextOverflowStrategy.UPSHIFT_FIRST,
            action_taken="failed",
            upshift_result=upshift_result,
            warnings=["Both upshift and chunking failed"]
        )
    
    def _handle_chunk_first(self, 
                          request: LLMRequest, 
                          required_tokens: int, 
                          max_tokens: int) -> StrategyResult:
        """Handle overflow by trying chunking first, then upshifting."""
        # Try chunking first
        chunk_max_tokens = int(max_tokens * 0.8)  # Leave buffer
        chunked_requests = self.chunker.chunk_request(request, chunk_max_tokens)
        
        if len(chunked_requests) > 1:
            # Chunking successful
            return StrategyResult(
                success=True,
                strategy_used=ContextOverflowStrategy.CHUNK_FIRST,
                action_taken="chunk",
                modified_requests=chunked_requests,
                metadata={"chunk_count": len(chunked_requests)}
            )
        
        # Chunking failed or not needed, try upshifting if fallback enabled
        if self.enable_fallback:
            logger.info("Chunking failed or not beneficial, trying upshift")
            
            upshift_result = self.upshifter.find_suitable_model(
                request, required_tokens, False  # Vision requirement TBD
            )
            
            if upshift_result.success and upshift_result.selected_model != request.model:
                upshifted_request, _ = self.upshifter.upshift_request(
                    request, required_tokens, False
                )
                
                return StrategyResult(
                    success=True,
                    strategy_used=ContextOverflowStrategy.CHUNK_FIRST,
                    action_taken="upshift",
                    modified_requests=[upshifted_request],
                    upshift_result=upshift_result,
                    warnings=["Chunking failed, used upshift as fallback"],
                    metadata={
                        "fallback_used": True,
                        "upshifted_model": upshift_result.selected_model
                    }
                )
        
        # Both strategies failed
        return StrategyResult(
            success=False,
            strategy_used=ContextOverflowStrategy.CHUNK_FIRST,
            action_taken="failed",
            warnings=["Both chunking and upshift failed"]
        )
    
    def _handle_upshift_only(self, 
                           request: LLMRequest, 
                           required_tokens: int, 
                           requires_vision: bool) -> StrategyResult:
        """Handle overflow by only trying upshift."""
        upshift_result = self.upshifter.find_suitable_model(
            request, required_tokens, requires_vision
        )
        
        if upshift_result.success and upshift_result.selected_model != request.model:
            upshifted_request, _ = self.upshifter.upshift_request(
                request, required_tokens, requires_vision
            )
            
            return StrategyResult(
                success=True,
                strategy_used=ContextOverflowStrategy.UPSHIFT_ONLY,
                action_taken="upshift",
                modified_requests=[upshifted_request],
                upshift_result=upshift_result,
                metadata={
                    "upshifted_model": upshift_result.selected_model,
                    "cost_multiplier": upshift_result.cost_multiplier
                }
            )
        
        return StrategyResult(
            success=False,
            strategy_used=ContextOverflowStrategy.UPSHIFT_ONLY,
            action_taken="failed",
            upshift_result=upshift_result,
            warnings=["Upshift failed and chunking not allowed"]
        )
    
    def _handle_chunk_only(self, 
                         request: LLMRequest, 
                         required_tokens: int, 
                         max_tokens: int) -> StrategyResult:
        """Handle overflow by only trying chunking."""
        chunk_max_tokens = int(max_tokens * 0.8)  # Leave buffer
        chunked_requests = self.chunker.chunk_request(request, chunk_max_tokens)
        
        if len(chunked_requests) > 1:
            return StrategyResult(
                success=True,
                strategy_used=ContextOverflowStrategy.CHUNK_ONLY,
                action_taken="chunk",
                modified_requests=chunked_requests,
                metadata={"chunk_count": len(chunked_requests)}
            )
        
        return StrategyResult(
            success=False,
            strategy_used=ContextOverflowStrategy.CHUNK_ONLY,
            action_taken="failed",
            warnings=["Chunking failed and upshift not allowed"]
        )
    
    def _handle_fail_fast(self, 
                        request: LLMRequest, 
                        required_tokens: int, 
                        max_tokens: int) -> StrategyResult:
        """Handle overflow by failing immediately."""
        return StrategyResult(
            success=False,
            strategy_used=ContextOverflowStrategy.FAIL_FAST,
            action_taken="failed",
            warnings=[f"Context overflow detected ({required_tokens} > {max_tokens} tokens), failing fast as requested"]
        )
    
    def set_model_strategy(self, model: str, strategy: ContextOverflowStrategy) -> None:
        """Set strategy for a specific model."""
        self.model_strategies[model] = strategy
        logger.info(f"Set strategy for model {model}: {strategy.value}")
    
    def set_request_type_strategy(self, request_type: str, strategy: ContextOverflowStrategy) -> None:
        """Set strategy for a specific request type."""
        self.request_type_strategies[request_type] = strategy
        logger.info(f"Set strategy for request type {request_type}: {strategy.value}")
    
    def clear_model_strategies(self) -> None:
        """Clear all model-specific strategies."""
        self.model_strategies.clear()
        logger.info("Cleared all model-specific strategies")
    
    def clear_request_type_strategies(self) -> None:
        """Clear all request-type-specific strategies."""
        self.request_type_strategies.clear()
        logger.info("Cleared all request-type-specific strategies")
    
    def get_strategy_for_request(self, request: LLMRequest) -> ContextOverflowStrategy:
        """Get the strategy that would be used for a request."""
        return self._determine_strategy(request, None)
    
    def estimate_strategy_cost(self, 
                             request: LLMRequest, 
                             required_tokens: int,
                             strategy: Optional[ContextOverflowStrategy] = None) -> Dict[str, Any]:
        """
        Estimate the cost implications of different strategies.
        
        Args:
            request: LLM request to analyze
            required_tokens: Number of tokens needed
            strategy: Strategy to analyze (None for all strategies)
            
        Returns:
            Dictionary with cost estimates
        """
        current_capacity = self.upshifter.registry.get_model_capacity(request.model)
        current_cost = current_capacity.cost_multiplier if current_capacity else 1.0
        
        estimates = {}
        
        strategies_to_check = [strategy] if strategy else list(ContextOverflowStrategy)
        
        for strat in strategies_to_check:
            if strat == ContextOverflowStrategy.UPSHIFT_FIRST or strat == ContextOverflowStrategy.UPSHIFT_ONLY:
                # Estimate upshift cost
                upshift_result = self.upshifter.find_suitable_model(request, required_tokens, False)
                if upshift_result.success:
                    cost_increase = upshift_result.cost_multiplier / current_cost
                    estimates[strat.value] = {
                        "feasible": True,
                        "cost_multiplier": cost_increase,
                        "recommended_model": upshift_result.selected_model,
                        "method": "upshift"
                    }
                else:
                    estimates[strat.value] = {
                        "feasible": False,
                        "reason": upshift_result.reason,
                        "method": "upshift"
                    }
            
            elif strat == ContextOverflowStrategy.CHUNK_FIRST or strat == ContextOverflowStrategy.CHUNK_ONLY:
                # Estimate chunking cost (multiple requests)
                max_tokens = current_capacity.max_context_tokens if current_capacity else 4096
                chunk_max_tokens = int(max_tokens * 0.8)
                
                # Rough estimate of chunk count
                estimated_chunks = max(1, (required_tokens + chunk_max_tokens - 1) // chunk_max_tokens)
                
                estimates[strat.value] = {
                    "feasible": True,
                    "cost_multiplier": estimated_chunks,  # Multiple requests
                    "estimated_chunks": estimated_chunks,
                    "method": "chunk"
                }
            
            elif strat == ContextOverflowStrategy.FAIL_FAST:
                estimates[strat.value] = {
                    "feasible": False,
                    "cost_multiplier": 0,
                    "method": "fail"
                }
        
        return estimates
    
    def get_strategy_recommendations(self, 
                                   request: LLMRequest, 
                                   required_tokens: int) -> List[Dict[str, Any]]:
        """
        Get recommendations for the best strategy to use.
        
        Args:
            request: LLM request to analyze
            required_tokens: Number of tokens needed
            
        Returns:
            List of strategy recommendations sorted by preference
        """
        cost_estimates = self.estimate_strategy_cost(request, required_tokens)
        
        recommendations = []
        
        for strategy_name, estimate in cost_estimates.items():
            if estimate["feasible"]:
                score = 0
                
                # Prefer lower cost multipliers
                if "cost_multiplier" in estimate:
                    score += max(0, 10 - estimate["cost_multiplier"])
                
                # Prefer upshift over chunking (simpler)
                if estimate["method"] == "upshift":
                    score += 2
                elif estimate["method"] == "chunk":
                    score += 1
                
                recommendations.append({
                    "strategy": strategy_name,
                    "score": score,
                    "cost_multiplier": estimate.get("cost_multiplier", 1.0),
                    "method": estimate["method"],
                    "details": estimate
                })
        
        # Sort by score (higher is better)
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations
    
    def configure_from_dict(self, config: Dict[str, Any]) -> None:
        """
        Configure strategy from a dictionary.
        
        Args:
            config: Configuration dictionary
        """
        if "default_strategy" in config:
            try:
                self.default_strategy = ContextOverflowStrategy(config["default_strategy"])
            except ValueError:
                logger.warning(f"Invalid default strategy: {config['default_strategy']}")
        
        if "max_cost_multiplier" in config:
            self.max_cost_multiplier = float(config["max_cost_multiplier"])
        
        if "enable_fallback" in config:
            self.enable_fallback = bool(config["enable_fallback"])
        
        if "model_strategies" in config:
            for model, strategy_name in config["model_strategies"].items():
                try:
                    strategy = ContextOverflowStrategy(strategy_name)
                    self.set_model_strategy(model, strategy)
                except ValueError:
                    logger.warning(f"Invalid strategy for model {model}: {strategy_name}")
        
        if "request_type_strategies" in config:
            for req_type, strategy_name in config["request_type_strategies"].items():
                try:
                    strategy = ContextOverflowStrategy(strategy_name)
                    self.set_request_type_strategy(req_type, strategy)
                except ValueError:
                    logger.warning(f"Invalid strategy for request type {req_type}: {strategy_name}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration to dictionary."""
        return {
            "default_strategy": self.default_strategy.value,
            "max_cost_multiplier": self.max_cost_multiplier,
            "enable_fallback": self.enable_fallback,
            "model_strategies": {
                model: strategy.value 
                for model, strategy in self.model_strategies.items()
            },
            "request_type_strategies": {
                req_type: strategy.value 
                for req_type, strategy in self.request_type_strategies.items()
            }
        }