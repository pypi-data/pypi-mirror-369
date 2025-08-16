"""
Backward compatibility utilities for nimble-llm-caller.
"""

import warnings
from typing import Dict, Any, Optional, List, Union
from .core.enhanced_llm_caller import EnhancedLLMCaller
from .core.llm_caller import LLMCaller
from .models.request import LLMRequest


def create_legacy_caller(**kwargs) -> LLMCaller:
    """
    Create a legacy LLMCaller instance with backward compatibility.
    
    This function ensures that existing code using LLMCaller continues to work
    while optionally enabling new features through configuration.
    """
    # Check if user wants enhanced features
    enable_context_management = kwargs.pop('enable_context_management', False)
    enable_file_processing = kwargs.pop('enable_file_processing', False)
    enable_interaction_logging = kwargs.pop('enable_interaction_logging', False)
    
    if enable_context_management or enable_file_processing or enable_interaction_logging:
        # Use enhanced caller with specific features enabled
        return EnhancedLLMCaller(
            enable_context_management=enable_context_management,
            enable_file_processing=enable_file_processing,
            enable_interaction_logging=enable_interaction_logging,
            **kwargs
        )
    else:
        # Use original caller for full backward compatibility
        return LLMCaller(**kwargs)


def migrate_request_format(old_request: Dict[str, Any]) -> LLMRequest:
    """
    Migrate old request format to new LLMRequest format.
    
    Args:
        old_request: Dictionary with old request format
        
    Returns:
        New LLMRequest object
    """
    # Handle legacy field names
    field_mapping = {
        'prompt': 'prompt_key',
        'llm_model': 'model',
        'variables': 'substitutions',
        'params': 'model_params',
        'format': 'response_format'
    }
    
    # Convert old fields to new fields
    new_request_data = {}
    for old_field, new_field in field_mapping.items():
        if old_field in old_request:
            new_request_data[new_field] = old_request[old_field]
    
    # Copy other fields directly
    for key, value in old_request.items():
        if key not in field_mapping:
            new_request_data[key] = value
    
    # Ensure required fields have defaults
    if 'prompt_key' not in new_request_data:
        new_request_data['prompt_key'] = 'default'
    
    if 'model' not in new_request_data:
        new_request_data['model'] = 'gpt-4o'
    
    return LLMRequest(**new_request_data)


def enable_context_features_globally():
    """
    Enable context management features globally for backward compatibility.
    
    This function modifies the default LLMCaller behavior to include
    context management features without breaking existing code.
    """
    warnings.warn(
        "enable_context_features_globally() is deprecated. "
        "Use EnhancedLLMCaller directly for new code.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Monkey patch the LLMCaller class to use enhanced features
    import nimble_llm_caller
    nimble_llm_caller.LLMCaller = EnhancedLLMCaller


class LegacyConfigAdapter:
    """Adapter to make old configuration work with new enhanced features."""
    
    def __init__(self, legacy_config: Dict[str, Any]):
        """
        Initialize with legacy configuration format.
        
        Args:
            legacy_config: Old configuration dictionary
        """
        self.legacy_config = legacy_config
    
    def to_enhanced_config(self) -> Dict[str, Any]:
        """Convert legacy config to enhanced config format."""
        enhanced_config = self.legacy_config.copy()
        
        # Add default enhanced feature configurations if not present
        if 'context_management' not in enhanced_config:
            enhanced_config['context_management'] = {
                'enable_auto_upshift': True,
                'enable_chunking': True,
                'default_strategy': 'upshift_first',
                'max_cost_multiplier': 3.0
            }
        
        if 'file_processing' not in enhanced_config:
            enhanced_config['file_processing'] = {
                'enable_file_processing': True,
                'max_file_size': 10 * 1024 * 1024
            }
        
        if 'interaction_logging' not in enhanced_config:
            enhanced_config['interaction_logging'] = {
                'enable_logging': False,  # Disabled by default for backward compatibility
                'log_file_path': 'llm_interactions.jsonl'
            }
        
        return enhanced_config


def check_compatibility(request: Union[LLMRequest, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Check compatibility of a request with enhanced features.
    
    Args:
        request: LLMRequest object or legacy request dictionary
        
    Returns:
        Compatibility report
    """
    report = {
        'compatible': True,
        'warnings': [],
        'recommendations': []
    }
    
    if isinstance(request, dict):
        # Legacy dictionary format
        report['warnings'].append('Using legacy dictionary request format')
        report['recommendations'].append('Migrate to LLMRequest objects for better type safety')
        
        # Check for deprecated fields
        deprecated_fields = ['prompt', 'llm_model', 'variables', 'params', 'format']
        for field in deprecated_fields:
            if field in request:
                report['warnings'].append(f'Field "{field}" is deprecated')
    
    elif isinstance(request, LLMRequest):
        # Check for new features that might not be supported in legacy mode
        if request.file_attachments:
            report['recommendations'].append('File attachments require EnhancedLLMCaller')
        
        if hasattr(request, 'context_strategy') and request.context_strategy:
            report['recommendations'].append('Context strategy requires EnhancedLLMCaller')
    
    return report


def get_migration_guide() -> str:
    """Get migration guide for upgrading to enhanced features."""
    return """
    Migration Guide: Upgrading to Enhanced LLM Caller
    
    1. Basic Migration:
       Old: caller = LLMCaller()
       New: caller = EnhancedLLMCaller()
    
    2. Enable Specific Features:
       caller = EnhancedLLMCaller(
           enable_context_management=True,
           enable_file_processing=True,
           enable_interaction_logging=True
       )
    
    3. Request Format Migration:
       Old: {"prompt": "my_prompt", "llm_model": "gpt-4", "variables": {...}}
       New: LLMRequest(prompt_key="my_prompt", model="gpt-4", substitutions={...})
    
    4. Configuration Migration:
       Use ConfigManager.export_enhanced_config() to get new format
    
    5. File Attachments (New Feature):
       request.file_attachments = [
           FileAttachment(file_path="document.pdf", content_type="application/pdf")
       ]
    
    6. Context Strategy (New Feature):
       request.context_strategy = "upshift_first"  # or "chunk_first", etc.
    
    For more details, see the documentation.
    """


# Backward compatibility aliases
ContextAwareCaller = EnhancedLLMCaller  # Alternative name
SmartLLMCaller = EnhancedLLMCaller      # Alternative name