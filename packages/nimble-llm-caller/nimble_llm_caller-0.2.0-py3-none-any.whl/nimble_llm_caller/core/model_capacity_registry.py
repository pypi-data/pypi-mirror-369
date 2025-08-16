"""
Model capacity registry and management utilities.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelCapacity:
    """Model capacity and capability information."""
    model_name: str
    max_context_tokens: int
    provider: str
    cost_multiplier: float = 1.0
    supports_vision: bool = False
    supported_file_types: List[str] = None
    priority: int = 100  # Lower numbers = higher priority
    
    def __post_init__(self):
        if self.supported_file_types is None:
            self.supported_file_types = []


class ModelCapacityRegistry:
    """Registry for model capacity information and upshift logic."""
    
    # Default model capacity configurations
    DEFAULT_CAPACITIES = {
        # OpenAI models
        "gpt-4": ModelCapacity("gpt-4", 8192, "openai", 1.0, False, [], 50),
        "gpt-4-32k": ModelCapacity("gpt-4-32k", 32768, "openai", 2.0, False, [], 60),
        "gpt-4-turbo": ModelCapacity("gpt-4-turbo", 128000, "openai", 1.5, True, ["image", "text"], 40),
        "gpt-4o": ModelCapacity("gpt-4o", 128000, "openai", 1.2, True, ["image", "text"], 30),
        "gpt-4o-mini": ModelCapacity("gpt-4o-mini", 128000, "openai", 0.8, True, ["image", "text"], 35),
        "gpt-3.5-turbo": ModelCapacity("gpt-3.5-turbo", 16385, "openai", 0.5, False, [], 70),
        "gpt-3.5-turbo-16k": ModelCapacity("gpt-3.5-turbo-16k", 16385, "openai", 0.7, False, [], 65),
        
        # Anthropic models
        "claude-3-opus": ModelCapacity("claude-3-opus", 200000, "anthropic", 3.0, True, ["image", "text"], 10),
        "claude-3-sonnet": ModelCapacity("claude-3-sonnet", 200000, "anthropic", 1.5, True, ["image", "text"], 20),
        "claude-3-haiku": ModelCapacity("claude-3-haiku", 200000, "anthropic", 0.8, True, ["image", "text"], 25),
        "claude-3-5-sonnet": ModelCapacity("claude-3-5-sonnet", 200000, "anthropic", 1.8, True, ["image", "text"], 15),
        "claude-2.1": ModelCapacity("claude-2.1", 200000, "anthropic", 1.2, False, [], 45),
        "claude-2": ModelCapacity("claude-2", 100000, "anthropic", 1.0, False, [], 55),
        "claude-instant": ModelCapacity("claude-instant", 100000, "anthropic", 0.6, False, [], 75),
        
        # Google models
        "gemini-pro": ModelCapacity("gemini-pro", 32768, "google", 1.0, False, [], 80),
        "gemini-1.5-pro": ModelCapacity("gemini-1.5-pro", 1000000, "google", 2.0, True, ["image", "text", "video"], 5),
        "gemini-1.5-flash": ModelCapacity("gemini-1.5-flash", 1000000, "google", 1.0, True, ["image", "text"], 12),
        "gemini-pro-vision": ModelCapacity("gemini-pro-vision", 32768, "google", 1.2, True, ["image", "text"], 85),
        
        # Cohere models
        "command": ModelCapacity("command", 4096, "cohere", 1.0, False, [], 90),
        "command-light": ModelCapacity("command-light", 4096, "cohere", 0.8, False, [], 95),
        "command-nightly": ModelCapacity("command-nightly", 4096, "cohere", 1.2, False, [], 88),
        
        # Mistral models
        "mistral-large": ModelCapacity("mistral-large", 32768, "mistral", 2.0, False, [], 82),
        "mistral-medium": ModelCapacity("mistral-medium", 32768, "mistral", 1.5, False, [], 87),
        "mistral-small": ModelCapacity("mistral-small", 32768, "mistral", 1.0, False, [], 92),
        "mistral-tiny": ModelCapacity("mistral-tiny", 32768, "mistral", 0.8, False, [], 97),
    }
    
    # Provider preference order (lower index = higher preference)
    DEFAULT_PROVIDER_PREFERENCES = ["openai", "anthropic", "google", "mistral", "cohere"]
    
    def __init__(self, 
                 custom_capacities: Optional[Dict[str, ModelCapacity]] = None,
                 provider_preferences: Optional[List[str]] = None):
        """
        Initialize the model capacity registry.
        
        Args:
            custom_capacities: Custom model capacity definitions
            provider_preferences: Ordered list of preferred providers
        """
        self.capacities = self.DEFAULT_CAPACITIES.copy()
        if custom_capacities:
            self.capacities.update(custom_capacities)
        
        self.provider_preferences = provider_preferences or self.DEFAULT_PROVIDER_PREFERENCES.copy()
        
        # Build reverse lookup for provider preference
        self._provider_priority = {
            provider: idx for idx, provider in enumerate(self.provider_preferences)
        }
    
    def get_model_capacity(self, model: str) -> Optional[ModelCapacity]:
        """
        Get capacity information for a model.
        
        Args:
            model: Model name (may include provider prefix)
            
        Returns:
            ModelCapacity object or None if not found
        """
        # Handle provider-prefixed models
        clean_model = model.split("/")[-1] if "/" in model else model
        
        # Direct lookup
        if clean_model in self.capacities:
            return self.capacities[clean_model]
        
        # Try pattern matching for model variants
        for known_model, capacity in self.capacities.items():
            if clean_model.startswith(known_model.split("-")[0]):
                logger.info(f"Using capacity from {known_model} for similar model {clean_model}")
                return capacity
        
        logger.warning(f"No capacity information found for model: {model}")
        return None
    
    def find_suitable_models(self, 
                           required_tokens: int, 
                           current_model: str,
                           max_cost_multiplier: float = 3.0,
                           requires_vision: bool = False) -> List[str]:
        """
        Find models that can handle the required token count.
        
        Args:
            required_tokens: Number of tokens needed
            current_model: Current model name
            max_cost_multiplier: Maximum cost multiplier allowed
            requires_vision: Whether vision support is required
            
        Returns:
            List of model names sorted by preference
        """
        current_capacity = self.get_model_capacity(current_model)
        current_provider = current_capacity.provider if current_capacity else "unknown"
        current_cost = current_capacity.cost_multiplier if current_capacity else 1.0
        
        suitable_models = []
        
        # Find models with sufficient capacity
        for model_name, capacity in self.capacities.items():
            # Check capacity
            if capacity.max_context_tokens < required_tokens:
                continue
            
            # Check cost constraint
            if capacity.cost_multiplier > current_cost * max_cost_multiplier:
                continue
            
            # Check vision requirement
            if requires_vision and not capacity.supports_vision:
                continue
            
            suitable_models.append((model_name, capacity))
        
        # Sort by preference
        def sort_key(item):
            model_name, capacity = item
            # Same provider gets priority boost
            provider_priority = self._provider_priority.get(capacity.provider, 999)
            if capacity.provider == current_provider:
                provider_priority -= 0.5  # Slight boost for same provider
            
            return (
                provider_priority,           # Provider preference
                capacity.priority,           # Model priority within provider
                capacity.cost_multiplier,    # Cost (lower is better)
                -capacity.max_context_tokens # Capacity (higher is better, so negative)
            )
        
        suitable_models.sort(key=sort_key)
        
        return [model_name for model_name, _ in suitable_models]
    
    def get_upshift_priority(self, from_model: str) -> List[str]:
        """
        Get prioritized list of models for upshifting from a given model.
        
        Args:
            from_model: Current model name
            
        Returns:
            List of model names in upshift priority order
        """
        current_capacity = self.get_model_capacity(from_model)
        if not current_capacity:
            # If we don't know the current model, return all models by priority
            all_models = list(self.capacities.items())
            all_models.sort(key=lambda x: (
                self._provider_priority.get(x[1].provider, 999),
                x[1].priority,
                x[1].cost_multiplier
            ))
            return [model_name for model_name, _ in all_models]
        
        # Find models with higher capacity than current
        upshift_candidates = []
        for model_name, capacity in self.capacities.items():
            if capacity.max_context_tokens > current_capacity.max_context_tokens:
                upshift_candidates.append((model_name, capacity))
        
        # Sort by preference (same logic as find_suitable_models)
        def sort_key(item):
            model_name, capacity = item
            provider_priority = self._provider_priority.get(capacity.provider, 999)
            if capacity.provider == current_capacity.provider:
                provider_priority -= 0.5
            
            return (
                provider_priority,
                capacity.priority,
                capacity.cost_multiplier,
                -capacity.max_context_tokens
            )
        
        upshift_candidates.sort(key=sort_key)
        
        return [model_name for model_name, _ in upshift_candidates]
    
    def add_model_capacity(self, model_name: str, capacity: ModelCapacity) -> None:
        """Add or update a model capacity."""
        self.capacities[model_name] = capacity
        logger.info(f"Added/updated capacity for model: {model_name}")
    
    def remove_model_capacity(self, model_name: str) -> bool:
        """
        Remove a model capacity.
        
        Args:
            model_name: Name of the model to remove
            
        Returns:
            True if model was removed, False if not found
        """
        if model_name in self.capacities:
            del self.capacities[model_name]
            logger.info(f"Removed capacity for model: {model_name}")
            return True
        return False
    
    def get_models_by_provider(self, provider: str) -> List[Tuple[str, ModelCapacity]]:
        """
        Get all models for a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            List of (model_name, capacity) tuples
        """
        return [
            (model_name, capacity) 
            for model_name, capacity in self.capacities.items()
            if capacity.provider == provider
        ]
    
    def get_all_providers(self) -> List[str]:
        """Get list of all known providers."""
        providers = set(capacity.provider for capacity in self.capacities.values())
        return sorted(providers)
    
    def get_models_with_vision(self) -> List[str]:
        """Get list of models that support vision."""
        return [
            model_name for model_name, capacity in self.capacities.items()
            if capacity.supports_vision
        ]
    
    def get_models_by_capacity_range(self, 
                                   min_tokens: int, 
                                   max_tokens: Optional[int] = None) -> List[str]:
        """
        Get models within a specific capacity range.
        
        Args:
            min_tokens: Minimum token capacity
            max_tokens: Maximum token capacity (None for no limit)
            
        Returns:
            List of model names
        """
        models = []
        for model_name, capacity in self.capacities.items():
            if capacity.max_context_tokens >= min_tokens:
                if max_tokens is None or capacity.max_context_tokens <= max_tokens:
                    models.append(model_name)
        
        return models
    
    def update_provider_preferences(self, preferences: List[str]) -> None:
        """
        Update provider preference order.
        
        Args:
            preferences: Ordered list of provider names
        """
        self.provider_preferences = preferences.copy()
        self._provider_priority = {
            provider: idx for idx, provider in enumerate(preferences)
        }
        logger.info(f"Updated provider preferences: {preferences}")
    
    def get_capacity_summary(self) -> Dict[str, Any]:
        """Get summary statistics about registered models."""
        if not self.capacities:
            return {"total_models": 0}
        
        capacities_list = list(self.capacities.values())
        token_capacities = [c.max_context_tokens for c in capacities_list]
        cost_multipliers = [c.cost_multiplier for c in capacities_list]
        
        providers = {}
        vision_models = 0
        
        for capacity in capacities_list:
            if capacity.provider not in providers:
                providers[capacity.provider] = 0
            providers[capacity.provider] += 1
            
            if capacity.supports_vision:
                vision_models += 1
        
        return {
            "total_models": len(self.capacities),
            "providers": providers,
            "vision_models": vision_models,
            "token_capacity_range": {
                "min": min(token_capacities),
                "max": max(token_capacities),
                "avg": sum(token_capacities) / len(token_capacities)
            },
            "cost_multiplier_range": {
                "min": min(cost_multipliers),
                "max": max(cost_multipliers),
                "avg": sum(cost_multipliers) / len(cost_multipliers)
            }
        }