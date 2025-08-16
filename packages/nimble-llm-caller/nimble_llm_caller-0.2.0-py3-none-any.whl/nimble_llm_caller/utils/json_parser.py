"""
Robust JSON parsing utilities with multiple fallback strategies.
"""

import json
import re
import logging
from typing import Dict, Any, Optional, List, Union
from json_repair import repair_json

logger = logging.getLogger(__name__)


class JSONParser:
    """Robust JSON parser with multiple fallback strategies for LLM responses."""
    
    def __init__(self):
        self.parsing_strategies = [
            self._direct_parse,
            self._repair_and_parse,
            self._extract_from_markdown,
            self._extract_from_text,
            self._parse_conversational,
            self._parse_key_value_pairs
        ]
    
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse JSON from content using multiple fallback strategies.
        
        Args:
            content: Raw content from LLM response
            
        Returns:
            Parsed JSON dictionary with metadata about parsing
        """
        if not content or not content.strip():
            return {
                "error": "Empty or null content",
                "parsing_strategy": "none",
                "original_content": content
            }
        
        content = content.strip()
        
        # Try each parsing strategy in order
        for i, strategy in enumerate(self.parsing_strategies):
            try:
                result = strategy(content)
                if result is not None:
                    # Add parsing metadata
                    if isinstance(result, dict):
                        result["_parsing_metadata"] = {
                            "strategy": strategy.__name__,
                            "strategy_index": i,
                            "original_length": len(content)
                        }
                    logger.debug(f"Successfully parsed JSON using strategy: {strategy.__name__}")
                    return result
            except Exception as e:
                logger.debug(f"Strategy {strategy.__name__} failed: {e}")
                continue
        
        # All strategies failed
        logger.error(f"All JSON parsing strategies failed for content: {content[:200]}...")
        return {
            "error": "All parsing strategies failed",
            "parsing_strategy": "failed",
            "original_content": content[:1000],  # Truncate for storage
            "strategies_attempted": len(self.parsing_strategies)
        }
    
    def _direct_parse(self, content: str) -> Optional[Dict[str, Any]]:
        """Strategy 1: Direct JSON parsing."""
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return parsed
        return None
    
    def _repair_and_parse(self, content: str) -> Optional[Dict[str, Any]]:
        """Strategy 2: Use json-repair library."""
        repaired = repair_json(content)
        parsed = json.loads(repaired)
        if isinstance(parsed, dict):
            return parsed
        return None
    
    def _extract_from_markdown(self, content: str) -> Optional[Dict[str, Any]]:
        """Strategy 3: Extract JSON from markdown code blocks."""
        # Pattern for JSON code blocks
        patterns = [
            r'```json\s*\n?(.*?)\n?```',
            r'```\s*\n?(.*?)\n?```',
            r'`(.*?)`'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    match = match.strip()
                    if match.startswith('{') and match.endswith('}'):
                        parsed = json.loads(match)
                        if isinstance(parsed, dict):
                            return parsed
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _extract_from_text(self, content: str) -> Optional[Dict[str, Any]]:
        """Strategy 4: Extract JSON objects from mixed text."""
        # Find JSON-like objects in text
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, content, re.DOTALL)
        
        # Try parsing each match, starting with the largest
        matches.sort(key=len, reverse=True)
        
        for match in matches:
            try:
                match = match.strip()
                parsed = json.loads(match)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue
        
        return None
    
    def _parse_conversational(self, content: str) -> Optional[Dict[str, Any]]:
        """Strategy 5: Parse conversational responses with structured information."""
        # Common patterns for different field types
        patterns = {
            'title': r'(?:title|heading):\s*(.+?)(?:\n|$)',
            'summary': r'(?:summary|description):\s*(.+?)(?:\n\n|\n(?=[A-Z])|$)',
            'author': r'(?:author|by):\s*(.+?)(?:\n|$)',
            'keywords': r'(?:keywords?|tags?):\s*(.+?)(?:\n|$)',
            'bibliography': r'(?:bibliography|sources?|references?):\s*(.+?)(?:\n\n|\Z)',
            'back_cover_text': r'(?:back cover|cover text):\s*(.+?)(?:\n\n|\Z)',
            'content': r'(?:content|text|body):\s*(.+?)(?:\n\n|\Z)',
            'result': r'(?:result|output|answer):\s*(.+?)(?:\n\n|\Z)'
        }
        
        result = {}
        content_lower = content.lower()
        
        for field, pattern in patterns.items():
            match = re.search(pattern, content_lower, re.IGNORECASE | re.DOTALL)
            if match:
                value = match.group(1).strip()
                # Clean up the extracted value
                value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
                value = value.strip('"\'')  # Remove quotes
                result[field] = value
        
        # If we found any fields, return them
        if result:
            logger.info(f"Extracted fields from conversational response: {list(result.keys())}")
            return result
        
        return None
    
    def _parse_key_value_pairs(self, content: str) -> Optional[Dict[str, Any]]:
        """Strategy 6: Parse simple key-value pairs."""
        result = {}
        
        # Look for key: value patterns
        kv_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.+?)(?:\n|$)'
        matches = re.findall(kv_pattern, content, re.MULTILINE)
        
        for key, value in matches:
            value = value.strip().strip('"\'')
            
            # Try to parse value as JSON if it looks like it
            if value.startswith(('{', '[')) and value.endswith(('}', ']')):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass  # Keep as string
            
            result[key] = value
        
        return result if result else None
    
    def validate_required_keys(self, parsed_data: Dict[str, Any], required_keys: List[str]) -> Dict[str, Any]:
        """
        Validate that parsed data contains required keys.
        
        Args:
            parsed_data: Parsed JSON data
            required_keys: List of required keys
            
        Returns:
            Validation result with warnings for missing keys
        """
        if not isinstance(parsed_data, dict):
            return {
                "valid": False,
                "error": "Parsed data is not a dictionary",
                "missing_keys": required_keys
            }
        
        missing_keys = [key for key in required_keys if key not in parsed_data]
        
        return {
            "valid": len(missing_keys) == 0,
            "missing_keys": missing_keys,
            "present_keys": [key for key in required_keys if key in parsed_data],
            "extra_keys": [key for key in parsed_data.keys() if key not in required_keys and not key.startswith('_')]
        }
    
    def clean_parsed_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean parsed data by removing metadata and normalizing values.
        
        Args:
            parsed_data: Raw parsed data
            
        Returns:
            Cleaned data
        """
        if not isinstance(parsed_data, dict):
            return parsed_data
        
        cleaned = {}
        
        for key, value in parsed_data.items():
            # Skip internal metadata keys
            if key.startswith('_'):
                continue
            
            # Clean string values
            if isinstance(value, str):
                value = value.strip()
                # Remove common LLM artifacts
                value = re.sub(r'^(Here is|Here\'s|The answer is|Result:)\s*', '', value, flags=re.IGNORECASE)
                value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
            
            cleaned[key] = value
        
        return cleaned