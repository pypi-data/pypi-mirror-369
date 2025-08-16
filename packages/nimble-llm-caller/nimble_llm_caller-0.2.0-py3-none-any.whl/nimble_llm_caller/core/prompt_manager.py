"""
Prompt management system for loading and preparing prompts from JSON files.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from jinja2 import Template, Environment, FileSystemLoader, TemplateNotFound

logger = logging.getLogger(__name__)


class PromptManager:
    """Manages loading and preparation of prompts from JSON files."""
    
    def __init__(self, prompt_file_path: Optional[str] = None, template_dir: Optional[str] = None):
        """
        Initialize the prompt manager.
        
        Args:
            prompt_file_path: Path to the main prompt JSON file
            template_dir: Directory containing Jinja2 templates for advanced substitution
        """
        self.prompt_file_path = prompt_file_path
        self.prompts_cache = {}
        self.template_env = None
        
        if template_dir and os.path.exists(template_dir):
            self.template_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Load prompts if file path provided
        if prompt_file_path:
            self.load_prompts(prompt_file_path)
    
    def load_prompts(self, prompt_file_path: str) -> bool:
        """
        Load prompts from a JSON file.
        
        Args:
            prompt_file_path: Path to the prompt JSON file
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(prompt_file_path):
            logger.error(f"Prompt file not found: {prompt_file_path}")
            return False
        
        try:
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
            
            self.prompts_cache.update(prompts_data)
            self.prompt_file_path = prompt_file_path
            
            logger.info(f"Loaded {len(prompts_data)} prompt entries from {prompt_file_path}")
            return True
            
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Could not load or parse prompt file {prompt_file_path}: {e}")
            return False
    
    def load_multiple_prompt_files(self, file_paths: List[str]) -> bool:
        """
        Load prompts from multiple JSON files.
        
        Args:
            file_paths: List of paths to prompt JSON files
            
        Returns:
            True if at least one file was loaded successfully
        """
        success_count = 0
        
        for file_path in file_paths:
            if self.load_prompts(file_path):
                success_count += 1
        
        logger.info(f"Successfully loaded {success_count}/{len(file_paths)} prompt files")
        return success_count > 0
    
    def get_prompt(self, prompt_key: str) -> Optional[Dict[str, Any]]:
        """
        Get a prompt by key.
        
        Args:
            prompt_key: Key of the prompt to retrieve
            
        Returns:
            Prompt data or None if not found
        """
        return self.prompts_cache.get(prompt_key)
    
    def has_prompt(self, prompt_key: str) -> bool:
        """Check if a prompt key exists."""
        return prompt_key in self.prompts_cache
    
    def list_prompt_keys(self) -> List[str]:
        """Get list of all available prompt keys."""
        return list(self.prompts_cache.keys())
    
    def prepare_prompt(
        self, 
        prompt_key: str, 
        substitutions: Dict[str, Any],
        use_jinja: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Prepare a single prompt with substitutions.
        
        Args:
            prompt_key: Key of the prompt to prepare
            substitutions: Dictionary of values to substitute
            use_jinja: Whether to use Jinja2 templating (more powerful than str.format)
            
        Returns:
            Prepared prompt configuration or None if not found
        """
        if prompt_key not in self.prompts_cache:
            logger.warning(f"Prompt key '{prompt_key}' not found")
            return None
        
        prompt_data = self.prompts_cache[prompt_key].copy()
        prompt_config = {}
        
        # Handle 'messages' format (preferred)
        if "messages" in prompt_data and isinstance(prompt_data["messages"], list):
            formatted_messages = []
            
            for message in prompt_data["messages"]:
                content = message.get("content", "")
                
                try:
                    if use_jinja and self.template_env:
                        # Use Jinja2 templating
                        template = Template(content)
                        formatted_content = template.render(**substitutions)
                    else:
                        # Use simple string formatting
                        formatted_content = content.format(**substitutions)
                    
                    formatted_messages.append({
                        "role": message.get("role", "user"),
                        "content": formatted_content
                    })
                    
                except (KeyError, TemplateNotFound) as e:
                    logger.warning(f"In prompt '{prompt_key}', substitution failed: {e}. "
                                 f"Available substitutions: {list(substitutions.keys())}")
                    # Use original content as fallback
                    formatted_messages.append({
                        "role": message.get("role", "user"),
                        "content": content
                    })
            
            prompt_config["messages"] = formatted_messages
        
        # Handle simple 'prompt' string format
        elif "prompt" in prompt_data:
            content = prompt_data.get("prompt", "")
            
            try:
                if use_jinja and self.template_env:
                    template = Template(content)
                    formatted_content = template.render(**substitutions)
                else:
                    formatted_content = content.format(**substitutions)
            except (KeyError, TemplateNotFound) as e:
                logger.warning(f"In prompt '{prompt_key}', substitution failed: {e}")
                formatted_content = content
            
            # Wrap in standard messages structure
            prompt_config["messages"] = [{"role": "user", "content": formatted_content}]
        
        else:
            logger.warning(f"Prompt key '{prompt_key}' has neither 'messages' nor 'prompt' key")
            return None
        
        # Carry over parameters
        if "params" in prompt_data:
            prompt_config["params"] = prompt_data["params"].copy()
        
        # Add metadata
        prompt_config["prompt_key"] = prompt_key
        prompt_config["substitutions_applied"] = list(substitutions.keys())
        
        return prompt_config
    
    def prepare_multiple_prompts(
        self,
        prompt_keys: List[str],
        substitutions: Dict[str, Any],
        use_jinja: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Prepare multiple prompts with the same substitutions.
        
        Args:
            prompt_keys: List of prompt keys to prepare
            substitutions: Dictionary of values to substitute
            use_jinja: Whether to use Jinja2 templating
            
        Returns:
            List of prepared prompt configurations
        """
        prepared_prompts = []
        
        for prompt_key in prompt_keys:
            prepared = self.prepare_prompt(prompt_key, substitutions, use_jinja)
            if prepared:
                prepared_prompts.append({
                    "key": prompt_key,
                    "prompt_config": prepared
                })
            else:
                logger.warning(f"Failed to prepare prompt: {prompt_key}")
        
        logger.info(f"Prepared {len(prepared_prompts)}/{len(prompt_keys)} prompts")
        return prepared_prompts
    
    def validate_prompt_structure(self, prompt_key: str) -> Dict[str, Any]:
        """
        Validate the structure of a prompt.
        
        Args:
            prompt_key: Key of the prompt to validate
            
        Returns:
            Validation results
        """
        if prompt_key not in self.prompts_cache:
            return {
                "valid": False,
                "error": "Prompt key not found",
                "issues": []
            }
        
        prompt_data = self.prompts_cache[prompt_key]
        issues = []
        
        # Check for required structure
        has_messages = "messages" in prompt_data
        has_prompt = "prompt" in prompt_data
        
        if not has_messages and not has_prompt:
            issues.append("Prompt must have either 'messages' or 'prompt' key")
        
        # Validate messages structure
        if has_messages:
            messages = prompt_data["messages"]
            if not isinstance(messages, list):
                issues.append("'messages' must be a list")
            else:
                for i, message in enumerate(messages):
                    if not isinstance(message, dict):
                        issues.append(f"Message {i} must be a dictionary")
                        continue
                    
                    if "role" not in message:
                        issues.append(f"Message {i} missing 'role' field")
                    
                    if "content" not in message:
                        issues.append(f"Message {i} missing 'content' field")
        
        # Validate parameters
        if "params" in prompt_data:
            params = prompt_data["params"]
            if not isinstance(params, dict):
                issues.append("'params' must be a dictionary")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "has_messages": has_messages,
            "has_prompt": has_prompt,
            "has_params": "params" in prompt_data
        }
    
    def extract_variables(self, prompt_key: str) -> List[str]:
        """
        Extract variable names from a prompt template.
        
        Args:
            prompt_key: Key of the prompt to analyze
            
        Returns:
            List of variable names found in the prompt
        """
        if prompt_key not in self.prompts_cache:
            return []
        
        prompt_data = self.prompts_cache[prompt_key]
        variables = set()
        
        # Extract from messages
        if "messages" in prompt_data:
            for message in prompt_data["messages"]:
                content = message.get("content", "")
                variables.update(self._extract_variables_from_text(content))
        
        # Extract from simple prompt
        elif "prompt" in prompt_data:
            content = prompt_data["prompt"]
            variables.update(self._extract_variables_from_text(content))
        
        return sorted(list(variables))
    
    def _extract_variables_from_text(self, text: str) -> List[str]:
        """Extract variable names from text using regex."""
        import re
        
        # Find {variable_name} patterns
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, text)
        
        # Filter out format specifiers and complex expressions
        variables = []
        for match in matches:
            # Skip format specifiers like {:.2f}
            if ':' not in match and '.' not in match:
                variables.append(match.strip())
        
        return variables
    
    def get_prompt_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded prompts."""
        total_prompts = len(self.prompts_cache)
        
        # Count by type
        message_prompts = 0
        simple_prompts = 0
        prompts_with_params = 0
        
        for prompt_data in self.prompts_cache.values():
            if isinstance(prompt_data, dict):
                if "messages" in prompt_data:
                    message_prompts += 1
                elif "prompt" in prompt_data:
                    simple_prompts += 1
                
                if "params" in prompt_data:
                    prompts_with_params += 1
        
        return {
            "total_prompts": total_prompts,
            "message_format_prompts": message_prompts,
            "simple_format_prompts": simple_prompts,
            "prompts_with_params": prompts_with_params,
            "prompt_file": self.prompt_file_path,
            "jinja_enabled": self.template_env is not None
        }