"""
Document assembly system for combining LLM outputs into formatted documents.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
import re

logger = logging.getLogger(__name__)


class DocumentAssembler:
    """Assembles LLM outputs into formatted documents using templates."""
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the document assembler.
        
        Args:
            template_dir: Directory containing document templates
        """
        self.template_dir = Path(template_dir) if template_dir else None
        self.template_env = None
        
        if self.template_dir and self.template_dir.exists():
            self.template_env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        
        # Built-in templates
        self.builtin_templates = {
            "markdown": self._get_default_markdown_template(),
            "latex": self._get_default_latex_template(),
            "text": self._get_default_text_template()
        }
    
    def assemble(
        self,
        content_sections: Dict[str, str],
        format: str = "markdown",
        template: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Assemble content sections into a formatted document.
        
        Args:
            content_sections: Dictionary of section_name -> content
            format: Output format (markdown, latex, text)
            template: Template file name or template string
            metadata: Additional metadata for template rendering
            
        Returns:
            Assembled document content
        """
        metadata = metadata or {}
        
        # Get template
        template_obj = self._get_template(template, format)
        if not template_obj:
            # Fallback to simple concatenation
            return self._simple_assembly(content_sections, format)
        
        # Prepare template variables
        template_vars = {
            "sections": content_sections,
            "metadata": metadata,
            "format": format,
            **content_sections,  # Allow direct access to sections by name
            **metadata  # Allow direct access to metadata
        }
        
        try:
            return template_obj.render(**template_vars)
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return self._simple_assembly(content_sections, format)
    
    def _get_template(self, template: Optional[str], format: str) -> Optional[Template]:
        """Get template object from file or built-in templates."""
        if template:
            # Try to load from file first
            if self.template_env:
                try:
                    return self.template_env.get_template(template)
                except TemplateNotFound:
                    logger.warning(f"Template file not found: {template}")
            
            # Try as template string
            try:
                return Template(template)
            except Exception as e:
                logger.warning(f"Invalid template string: {e}")
        
        # Use built-in template
        if format in self.builtin_templates:
            return Template(self.builtin_templates[format])
        
        return None
    
    def _simple_assembly(self, content_sections: Dict[str, str], format: str) -> str:
        """Simple assembly without templates."""
        if format == "markdown":
            return self._assemble_markdown(content_sections)
        elif format == "latex":
            return self._assemble_latex(content_sections)
        else:
            return self._assemble_text(content_sections)
    
    def _assemble_markdown(self, sections: Dict[str, str]) -> str:
        """Assemble sections into markdown format."""
        parts = []
        
        for section_name, content in sections.items():
            # Create section header
            header = f"## {self._format_section_name(section_name)}"
            parts.append(header)
            parts.append("")  # Empty line
            parts.append(content.strip())
            parts.append("")  # Empty line between sections
        
        return "\n".join(parts)
    
    def _assemble_latex(self, sections: Dict[str, str]) -> str:
        """Assemble sections into LaTeX format."""
        parts = [
            "\\documentclass{article}",
            "\\usepackage[utf8]{inputenc}",
            "\\usepackage{geometry}",
            "\\geometry{margin=1in}",
            "\\begin{document}",
            ""
        ]
        
        for section_name, content in sections.items():
            # Create section
            section_title = self._format_section_name(section_name)
            parts.append(f"\\section{{{section_title}}}")
            parts.append("")
            
            # Clean content for LaTeX
            cleaned_content = self._clean_latex_content(content)
            parts.append(cleaned_content)
            parts.append("")
        
        parts.extend(["", "\\end{document}"])
        return "\n".join(parts)
    
    def _assemble_text(self, sections: Dict[str, str]) -> str:
        """Assemble sections into plain text format."""
        parts = []
        
        for section_name, content in sections.items():
            # Create section header
            header = self._format_section_name(section_name).upper()
            separator = "=" * len(header)
            
            parts.append(separator)
            parts.append(header)
            parts.append(separator)
            parts.append("")
            parts.append(content.strip())
            parts.append("")
            parts.append("")  # Extra space between sections
        
        return "\n".join(parts)
    
    def _format_section_name(self, section_name: str) -> str:
        """Format section name for display."""
        # Convert snake_case or kebab-case to Title Case
        formatted = re.sub(r'[_-]', ' ', section_name)
        return formatted.title()
    
    def _clean_latex_content(self, content: str) -> str:
        """Clean content for LaTeX output."""
        # Escape special LaTeX characters
        latex_chars = {
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
            '#': '\\#',
            '^': '\\textasciicircum{}',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '~': '\\textasciitilde{}',
            '\\': '\\textbackslash{}'
        }
        
        for char, replacement in latex_chars.items():
            content = content.replace(char, replacement)
        
        return content
    
    def _get_default_markdown_template(self) -> str:
        """Get default markdown template."""
        return """# Document

{% if metadata.title %}
# {{ metadata.title }}
{% endif %}

{% if metadata.author %}
**Author:** {{ metadata.author }}
{% endif %}

{% if metadata.date %}
**Date:** {{ metadata.date }}
{% endif %}

{% for section_name, content in sections.items() %}
## {{ section_name | replace('_', ' ') | title }}

{{ content }}

{% endfor %}

---
*Generated by Nimble LLM Caller*
"""
    
    def _get_default_latex_template(self) -> str:
        """Get default LaTeX template."""
        return """\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage{geometry}
\\geometry{margin=1in}

{% if metadata.title %}
\\title{{ "{{" }}{{ metadata.title }}{{ "}}" }}
{% endif %}

{% if metadata.author %}
\\author{{ "{{" }}{{ metadata.author }}{{ "}}" }}
{% endif %}

\\begin{document}

{% if metadata.title %}
\\maketitle
{% endif %}

{% for section_name, content in sections.items() %}
\\section{{ "{{" }}{{ section_name | replace('_', ' ') | title }}{{ "}}" }}

{{ content }}

{% endfor %}

\\end{document}
"""
    
    def _get_default_text_template(self) -> str:
        """Get default text template."""
        return """{% if metadata.title %}
{{ "=" * metadata.title|length }}
{{ metadata.title }}
{{ "=" * metadata.title|length }}

{% endif %}
{% if metadata.author %}
Author: {{ metadata.author }}
{% endif %}

{% if metadata.date %}
Date: {{ metadata.date }}
{% endif %}

{% for section_name, content in sections.items() %}
{{ "-" * 50 }}
{{ section_name | replace('_', ' ') | upper }}
{{ "-" * 50 }}

{{ content }}

{% endfor %}

Generated by Nimble LLM Caller
"""
    
    def create_custom_template(
        self,
        template_name: str,
        template_content: str,
        format: str = "markdown"
    ) -> bool:
        """
        Create a custom template file.
        
        Args:
            template_name: Name of the template file
            template_content: Template content
            format: Format type for organization
            
        Returns:
            True if successful
        """
        if not self.template_dir:
            logger.error("No template directory configured")
            return False
        
        try:
            self.template_dir.mkdir(exist_ok=True)
            template_file = self.template_dir / f"{template_name}.{format}"
            
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            logger.info(f"Created custom template: {template_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            return False
    
    def list_available_templates(self) -> Dict[str, List[str]]:
        """List all available templates."""
        templates = {
            "builtin": list(self.builtin_templates.keys()),
            "custom": []
        }
        
        if self.template_dir and self.template_dir.exists():
            for template_file in self.template_dir.glob("*"):
                if template_file.is_file():
                    templates["custom"].append(template_file.name)
        
        return templates
    
    def validate_template(self, template: str) -> Dict[str, Any]:
        """
        Validate a template for syntax errors.
        
        Args:
            template: Template string or file name
            
        Returns:
            Validation results
        """
        try:
            # Try to get template object
            template_obj = self._get_template(template, "markdown")
            
            if not template_obj:
                return {
                    "valid": False,
                    "error": "Template not found or invalid"
                }
            
            # Try to render with sample data
            sample_data = {
                "sections": {"sample": "Sample content"},
                "metadata": {"title": "Sample Title"}
            }
            
            template_obj.render(**sample_data)
            
            return {
                "valid": True,
                "message": "Template is valid"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }