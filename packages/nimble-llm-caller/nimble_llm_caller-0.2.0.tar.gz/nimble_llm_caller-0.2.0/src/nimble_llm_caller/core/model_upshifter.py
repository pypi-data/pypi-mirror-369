"""
Model upshifter for automatic model selection based on context requirements.
"""

from typing import Optional, Dict, Any, List, Tuple
import logging
from dataclasses import dataclass

from .model_capacity_registry import ModelCapacityRegistry, ModelCapacity
from ..models.request import LLMRequest

logger = logging.getLogger(__name__)


@dataclass
class UpshiftResult:
    """Result of an upshift operation."""
    success: bool
    original_model: str
    selected_model: Optional[str] = None
    reason: str = ""
    cost_multiplier: float = 1.0
    capacity_increase: int = 0
    alternatives_considered: List[str] = None
    
    def __post_init__(self):
        if self.alternatives_considered is None:
            self.alternatives_considered = []


class ModelUpshifter:
    """Handles automatic model upshifting based on context requirements."""
    
    def __init__(self, 
                 registry: Optional[ModelCapacityRegistry] = None,
                 default_max_cost_multiplier: float = 3.0,
                 enable_logging: bool = True):
        """
        Initialize the model upshifter.
        
        Args:
            registry: Model capacity registry (creates default if None)
            default_max_cost_multiplier: Default maximum cost multiplier
            enable_logging: Whether to log upshift decisions
        """
        self.registry = registry or ModelCapacityRegistry()
        self.default_max_cost_multiplier = default_max_cost_multiplier
        self.enable_logging = enable_logging
        
        # Track upshift history for analysis
        self.upshift_history: List[UpshiftResult] = []
    
    def find_suitable_model(self, 
                          request: LLMRequest,
                          required_tokens: int,
                          requires_vision: bool = False) -> UpshiftResult:
        """
        Find a suitable model for the given requirements.
        
        Args:
            request: The LLM request
            required_tokens: Number of tokens needed
            requires_vision: Whether vision support is required
            
        Returns:
            UpshiftResult with the decision
        """
        original_model = request.model
        max_cost_multiplier = getattr(request, 'max_cost_multiplier', self.default_max_cost_multiplier)
        
        # Check if current model can handle the request
        current_capacity = self.registry.get_model_capacity(original_model)
        if current_capacity and current_capacity.max_context_tokens >= required_tokens:
            if not requires_vision or current_capacity.supports_vision:
                return UpshiftResult(
                    success=True,
                    original_model=original_model,
                    selected_model=original_model,
                    reason="Current model has sufficient capacity",
                    cost_multiplier=current_capacity.cost_multiplier
                )
        
        # Find suitable alternatives
        suitable_models = self.registry.find_suitable_models(
            required_tokens=required_tokens,
            current_model=original_model,
            max_cost_multiplier=max_cost_multiplier,
            requires_vision=requires_vision
        )
        
        if not suitable_models:
            reason = self._build_failure_reason(required_tokens, max_cost_multiplier, requires_vision)
            result = UpshiftResult(
                success=False,
                original_model=original_model,
                reason=reason
            )
        else:
            # Select the best model (first in the sorted list)
            selected_model = suitable_models[0]
            selected_capacity = self.registry.get_model_capacity(selected_model)
            
            capacity_increase = 0
            if current_capacity:
                capacity_increase = selected_capacity.max_context_tokens - current_capacity.max_context_tokens
            
            result = UpshiftResult(
                success=True,
                original_model=original_model,
                selected_model=selected_model,
                reason=f"Upshifted to handle {required_tokens} tokens",
                cost_multiplier=selected_capacity.cost_multiplier,
                capacity_increase=capacity_increase,
                alternatives_considered=suitable_models[1:5]  # Top 5 alternatives
            )
        
        # Log the decision
        if self.enable_logging:
            self._log_upshift_decision(result, required_tokens, requires_vision)
        
        # Store in history
        self.upshift_history.append(result)
        
        return result
    
    def upshift_request(self, 
                       request: LLMRequest,
                       required_tokens: int,
                       requires_vision: bool = False) -> Tuple[LLMRequest, UpshiftResult]:
        """
        Create an upshifted version of the request.
        
        Args:
            request: Original LLM request
            required_tokens: Number of tokens needed
            requires_vision: Whether vision support is required
            
        Returns:
            Tuple of (modified_request, upshift_result)
        """
        result = self.find_suitable_model(request, required_tokens, requires_vision)
        
        if result.success and result.selected_model != request.model:
            # Create a copy of the request with the new model
            upshifted_request = request.model_copy()
            upshifted_request.model = result.selected_model
            
            # Add metadata about the upshift
            if not upshifted_request.metadata:
                upshifted_request.metadata = {}
            
            upshifted_request.metadata.update({
                "upshifted": True,
                "original_model": result.original_model,
                "upshift_reason": result.reason,
                "cost_multiplier": result.cost_multiplier
            })
            
            return upshifted_request, result
        
        return request, result
    
    def _build_failure_reason(self, 
                            required_tokens: int, 
                            max_cost_multiplier: float,
                            requires_vision: bool) -> str:
        """Build a descriptive failure reason."""
        reasons = []
        
        # Check what models exist with sufficient capacity
        high_capacity_models = self.registry.get_models_by_capacity_range(required_tokens)
        
        if not high_capacity_models:
            reasons.append(f"No models found with capacity >= {required_tokens} tokens")
        else:
            # Check cost constraints
            affordable_models = []
            vision_compatible_models = []
            
            for model_name in high_capacity_models:
                capacity = self.registry.get_model_capacity(model_name)
                if capacity.cost_multiplier <= max_cost_multiplier:
                    affordable_models.append(model_name)
                
                if not requires_vision or capacity.supports_vision:
                    vision_compatible_models.append(model_name)
            
            if not affordable_models:
                reasons.append(f"Models with sufficient capacity exceed cost limit ({max_cost_multiplier}x)")
            
            if requires_vision and not vision_compatible_models:
                reasons.append("No vision-capable models found with sufficient capacity")
        
        return "; ".join(reasons) if reasons else "No suitable models found"
    
    def _log_upshift_decision(self, 
                            result: UpshiftResult, 
                            required_tokens: int,
                            requires_vision: bool) -> None:
        """Log the upshift decision."""
        if result.success:
            if result.selected_model == result.original_model:
                logger.info(f"Model {result.original_model} has sufficient capacity for {required_tokens} tokens")
            else:
                logger.info(
                    f"Upshifted from {result.original_model} to {result.selected_model} "
                    f"for {required_tokens} tokens (cost: {result.cost_multiplier:.1f}x, "
                    f"capacity increase: +{result.capacity_increase:,} tokens)"
                )
        else:
            logger.warning(
                f"Failed to upshift from {result.original_model} for {required_tokens} tokens"
                f"{' with vision' if requires_vision else ''}: {result.reason}"
            )
    
    def get_upshift_recommendations(self, 
                                  current_model: str,
                                  target_tokens: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get upshift recommendations for a model.
        
        Args:
            current_model: Current model name
            target_tokens: Target token capacity (None for general recommendations)
            
        Returns:
            List of recommendation dictionaries
        """
        current_capacity = self.registry.get_model_capacity(current_model)
        if not current_capacity:
            return []
        
        if target_tokens:
            suitable_models = self.registry.find_suitable_models(
                required_tokens=target_tokens,
                current_model=current_model,
                max_cost_multiplier=10.0  # High limit for recommendations
            )
        else:
            suitable_models = self.registry.get_upshift_priority(current_model)
        
        recommendations = []
        for model_name in suitable_models[:10]:  # Top 10 recommendations
            capacity = self.registry.get_model_capacity(model_name)
            
            recommendations.append({
                "model": model_name,
                "provider": capacity.provider,
                "max_tokens": capacity.max_context_tokens,
                "cost_multiplier": capacity.cost_multiplier,
                "supports_vision": capacity.supports_vision,
                "capacity_increase": capacity.max_context_tokens - current_capacity.max_context_tokens,
                "cost_increase": capacity.cost_multiplier / current_capacity.cost_multiplier
            })
        
        return recommendations
    
    def analyze_upshift_patterns(self) -> Dict[str, Any]:
        """Analyze historical upshift patterns."""
        if not self.upshift_history:
            return {"total_upshifts": 0}
        
        successful_upshifts = [r for r in self.upshift_history if r.success]
        failed_upshifts = [r for r in self.upshift_history if not r.success]
        
        # Model transition patterns
        transitions = {}
        for result in successful_upshifts:
            if result.selected_model != result.original_model:
                key = f"{result.original_model} -> {result.selected_model}"
                transitions[key] = transitions.get(key, 0) + 1
        
        # Cost analysis
        cost_multipliers = [r.cost_multiplier for r in successful_upshifts if r.cost_multiplier > 1.0]
        
        # Failure reasons
        failure_reasons = {}
        for result in failed_upshifts:
            failure_reasons[result.reason] = failure_reasons.get(result.reason, 0) + 1
        
        return {
            "total_upshifts": len(self.upshift_history),
            "successful_upshifts": len(successful_upshifts),
            "failed_upshifts": len(failed_upshifts),
            "success_rate": len(successful_upshifts) / len(self.upshift_history) if self.upshift_history else 0,
            "common_transitions": dict(sorted(transitions.items(), key=lambda x: x[1], reverse=True)[:5]),
            "cost_analysis": {
                "avg_cost_multiplier": sum(cost_multipliers) / len(cost_multipliers) if cost_multipliers else 1.0,
                "max_cost_multiplier": max(cost_multipliers) if cost_multipliers else 1.0,
                "min_cost_multiplier": min(cost_multipliers) if cost_multipliers else 1.0
            },
            "failure_reasons": dict(sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True))
        }
    
    def clear_history(self) -> None:
        """Clear upshift history."""
        self.upshift_history.clear()
        logger.info("Cleared upshift history")
    
    def set_provider_preferences(self, preferences: List[str]) -> None:
        """Update provider preferences in the registry."""
        self.registry.update_provider_preferences(preferences)
        logger.info(f"Updated provider preferences: {preferences}")
    
    def add_custom_model(self, model_name: str, capacity: ModelCapacity) -> None:
        """Add a custom model to the registry."""
        self.registry.add_model_capacity(model_name, capacity)
        logger.info(f"Added custom model: {model_name}")