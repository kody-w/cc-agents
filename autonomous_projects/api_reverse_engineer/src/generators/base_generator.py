"""
Base class for SDK generators.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path

from ..types import APISpec, Endpoint, Parameter, ParameterType


class BaseGenerator(ABC):
    """Base class for all SDK generators."""
    
    def __init__(self, api_spec: APISpec):
        self.api_spec = api_spec
        
    @abstractmethod
    def generate(self, output_dir: str) -> Dict[str, str]:
        """
        Generate SDK files.
        
        Args:
            output_dir: Directory to write generated files
            
        Returns:
            Dict mapping file paths to generated content
        """
        pass
        
    @abstractmethod
    def get_language_name(self) -> str:
        """Get the name of the target language."""
        pass
        
    def _create_output_dir(self, output_dir: str) -> Path:
        """Create output directory if it doesn't exist."""
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path
        
    def _write_file(self, file_path: str, content: str):
        """Write content to a file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def _sanitize_name(self, name: str) -> str:
        """Sanitize a name for use as an identifier."""
        # Remove non-alphanumeric characters and replace with underscore
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = f"_{sanitized}"
            
        return sanitized or "unknown"
        
    def _get_method_name(self, endpoint: Endpoint) -> str:
        """Generate a method name for an endpoint."""
        # Extract resource name from path
        path_parts = [part for part in endpoint.path.split('/') if part and not part.startswith('{')]
        resource = path_parts[-1] if path_parts else "resource"
        
        # Create method name based on HTTP method
        method_prefixes = {
            "GET": "get",
            "POST": "create", 
            "PUT": "update",
            "DELETE": "delete",
            "PATCH": "patch"
        }
        
        prefix = method_prefixes.get(endpoint.method.value, endpoint.method.value.lower())
        method_name = f"{prefix}_{resource}"
        
        return self._sanitize_name(method_name)
        
    def _type_to_string(self, param_type: ParameterType, language: str) -> str:
        """Convert ParameterType to language-specific type string."""
        type_maps = {
            "python": {
                ParameterType.STRING: "str",
                ParameterType.INTEGER: "int", 
                ParameterType.FLOAT: "float",
                ParameterType.BOOLEAN: "bool",
                ParameterType.ARRAY: "List[Any]",
                ParameterType.OBJECT: "Dict[str, Any]",
                ParameterType.NULL: "Optional[Any]"
            },
            "typescript": {
                ParameterType.STRING: "string",
                ParameterType.INTEGER: "number",
                ParameterType.FLOAT: "number", 
                ParameterType.BOOLEAN: "boolean",
                ParameterType.ARRAY: "any[]",
                ParameterType.OBJECT: "object",
                ParameterType.NULL: "null"
            },
            "javascript": {
                ParameterType.STRING: "string",
                ParameterType.INTEGER: "number",
                ParameterType.FLOAT: "number",
                ParameterType.BOOLEAN: "boolean", 
                ParameterType.ARRAY: "Array",
                ParameterType.OBJECT: "Object",
                ParameterType.NULL: "null"
            }
        }
        
        return type_maps.get(language, {}).get(param_type, "any")
        
    def _get_auth_method(self) -> str:
        """Get the primary authentication method."""
        if not self.api_spec.auth_patterns:
            return "none"
            
        # Return the first auth pattern type
        return self.api_spec.auth_patterns[0].type.value