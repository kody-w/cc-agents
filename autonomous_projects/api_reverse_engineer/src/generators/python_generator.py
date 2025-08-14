"""
Python SDK generator with full typing support.
"""

from typing import Dict, List, Any
from pathlib import Path
import textwrap

from .base_generator import BaseGenerator
from ..types import APISpec, Endpoint, Parameter, ParameterType, AuthType


class PythonGenerator(BaseGenerator):
    """Generate Python SDK with full typing support."""
    
    def get_language_name(self) -> str:
        return "python"
        
    def generate(self, output_dir: str) -> Dict[str, str]:
        """Generate Python SDK files."""
        output_path = self._create_output_dir(output_dir)
        files = {}
        
        # Generate main client file
        client_content = self._generate_client()
        client_file = output_path / "client.py"
        self._write_file(str(client_file), client_content)
        files[str(client_file)] = client_content
        
        # Generate types file
        types_content = self._generate_types()
        types_file = output_path / "types.py"
        self._write_file(str(types_file), types_content)
        files[str(types_file)] = types_content
        
        # Generate exceptions file
        exceptions_content = self._generate_exceptions()
        exceptions_file = output_path / "exceptions.py"
        self._write_file(str(exceptions_file), exceptions_content)
        files[str(exceptions_file)] = exceptions_content
        
        # Generate __init__.py
        init_content = self._generate_init()
        init_file = output_path / "__init__.py"
        self._write_file(str(init_file), init_content)
        files[str(init_file)] = init_content
        
        # Generate requirements.txt
        requirements_content = self._generate_requirements()
        requirements_file = output_path / "requirements.txt"
        self._write_file(str(requirements_file), requirements_content)
        files[str(requirements_file)] = requirements_content
        
        # Generate setup.py
        setup_content = self._generate_setup()
        setup_file = output_path / "setup.py"
        self._write_file(str(setup_file), setup_content)
        files[str(setup_file)] = setup_content
        
        # Generate README.md
        readme_content = self._generate_readme()
        readme_file = output_path / "README.md"
        self._write_file(str(readme_file), readme_content)
        files[str(readme_file)] = readme_content
        
        return files
        
    def _generate_client(self) -> str:
        """Generate the main client class."""
        methods = []
        
        for endpoint in self.api_spec.endpoints:
            method_code = self._generate_method(endpoint)
            methods.append(method_code)
            
        methods_str = "\n\n".join(methods)
        
        auth_init = self._generate_auth_init()
        auth_headers = self._generate_auth_headers()
        
        return f'''"""
Generated API client for {self.api_spec.title}.

This client was automatically generated from API traffic analysis.
"""

import requests
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urljoin

from .types import *
from .exceptions import APIError, AuthenticationError, RateLimitError


class {self._get_client_class_name()}:
    """
    {self.api_spec.description}
    
    Base URL: {self.api_spec.base_url}
    """
    
    def __init__(self, {auth_init}):
        """
        Initialize the API client.
        """
        self.base_url = "{self.api_spec.base_url}"
        self.session = requests.Session()
        {self._generate_auth_assignment()}
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {{
            "Content-Type": "application/json",
            "User-Agent": "Generated-Python-SDK/1.0.0"
        }}
        
        {auth_headers}
        
        return headers
        
    def _make_request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Make an HTTP request to the API."""
        url = urljoin(self.base_url, path.lstrip('/'))
        headers = self._get_headers()
        headers.update(kwargs.pop('headers', {{}}))
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            
            # Handle common HTTP errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid authentication credentials")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 400:
                raise APIError(f"API request failed: {{response.status_code}} {{response.text}}")
                
            return response
            
        except requests.RequestException as e:
            raise APIError(f"Network error: {{str(e)}}")
    
{textwrap.indent(methods_str, "    ")}
'''
        
    def _generate_method(self, endpoint: Endpoint) -> str:
        """Generate a method for an endpoint."""
        method_name = self._get_method_name(endpoint)
        
        # Generate parameters
        params = []
        doc_params = []
        
        # Path parameters
        for param in endpoint.parameters:
            param_type = self._type_to_string(param.type, "python")
            params.append(f"{param.name}: {param_type}")
            doc_params.append(f"        {param.name}: {param.description or 'Path parameter'}")
            
        # Query parameters
        query_required = [p for p in endpoint.query_params if p.required]
        query_optional = [p for p in endpoint.query_params if not p.required]
        
        for param in query_required:
            param_type = self._type_to_string(param.type, "python")
            params.append(f"{param.name}: {param_type}")
            doc_params.append(f"        {param.name}: {param.description or 'Query parameter'}")
            
        # Optional query parameters
        if query_optional:
            for param in query_optional:
                param_type = self._type_to_string(param.type, "python")
                params.append(f"{param.name}: Optional[{param_type}] = None")
                doc_params.append(f"        {param.name}: {param.description or 'Optional query parameter'}")
                
        # Request body
        if endpoint.request_body:
            params.append("data: Optional[Dict[str, Any]] = None")
            doc_params.append("        data: Request body data")
            
        params_str = ", ".join(params)
        doc_params_str = "\n".join(doc_params)
        
        # Generate method body
        path_substitution = self._generate_path_substitution(endpoint)
        query_params_code = self._generate_query_params_code(endpoint)
        request_body_code = self._generate_request_body_code(endpoint)
        
        return f'''def {method_name}(self{", " + params_str if params_str else ""}) -> Dict[str, Any]:
    """
    {endpoint.summary or f"{endpoint.method.value} {endpoint.path}"}
    
    {endpoint.description or "No description available."}
    
    Args:
{doc_params_str}
        
    Returns:
        API response data
        
    Raises:
        APIError: If the request fails
        AuthenticationError: If authentication is invalid
        RateLimitError: If rate limit is exceeded
    """
    {path_substitution}
    
    # Prepare request parameters
    request_kwargs = {{}}
    
    {query_params_code}
    
    {request_body_code}
    
    response = self._make_request("{endpoint.method.value}", path, **request_kwargs)
    
    try:
        return response.json()
    except ValueError:
        return {{"data": response.text}}'''
        
    def _generate_path_substitution(self, endpoint: Endpoint) -> str:
        """Generate path parameter substitution code."""
        if not endpoint.parameters:
            return f'path = "{endpoint.path}"'
            
        substitutions = []
        for param in endpoint.parameters:
            substitutions.append(f'path = path.replace("{{{param.name}}}", str({param.name}))')
            
        return f'path = "{endpoint.path}"\n    ' + '\n    '.join(substitutions)
        
    def _generate_query_params_code(self, endpoint: Endpoint) -> str:
        """Generate query parameters handling code."""
        if not endpoint.query_params:
            return ""
            
        lines = ["params = {}"]
        
        for param in endpoint.query_params:
            if param.required:
                lines.append(f'params["{param.name}"] = {param.name}')
            else:
                lines.append(f'if {param.name} is not None:')
                lines.append(f'    params["{param.name}"] = {param.name}')
                
        lines.append("if params:")
        lines.append("    request_kwargs['params'] = params")
        
        return "\n    ".join(lines)
        
    def _generate_request_body_code(self, endpoint: Endpoint) -> str:
        """Generate request body handling code."""
        if not endpoint.request_body:
            return ""
            
        return '''if data is not None:
        request_kwargs['json'] = data'''
        
    def _generate_auth_init(self) -> str:
        """Generate authentication parameters for __init__."""
        auth_method = self._get_auth_method()
        
        if auth_method == "bearer_token":
            return "token: str"
        elif auth_method == "api_key":
            return "api_key: str"
        elif auth_method == "basic_auth":
            return "username: str, password: str"
        else:
            return ""
            
    def _generate_auth_assignment(self) -> str:
        """Generate authentication assignment in __init__."""
        auth_method = self._get_auth_method()
        
        if auth_method == "bearer_token":
            return "self.token = token"
        elif auth_method == "api_key":
            return "self.api_key = api_key"
        elif auth_method == "basic_auth":
            return "self.username = username\n        self.password = password"
        else:
            return "# No authentication required"
            
    def _generate_auth_headers(self) -> str:
        """Generate authentication headers code."""
        auth_method = self._get_auth_method()
        
        if auth_method == "bearer_token":
            return 'headers["Authorization"] = f"Bearer {self.token}"'
        elif auth_method == "api_key":
            # Find the header name from auth patterns
            header_name = "X-API-Key"
            if self.api_spec.auth_patterns:
                header_name = self.api_spec.auth_patterns[0].header_name or "X-API-Key"
            return f'headers["{header_name}"] = self.api_key'
        elif auth_method == "basic_auth":
            return '''import base64
        auth_string = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers["Authorization"] = f"Basic {auth_string}"'''
        else:
            return "# No authentication headers needed"
            
    def _generate_types(self) -> str:
        """Generate types file."""
        return '''"""
Type definitions for the generated API client.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass


# Add custom types here as needed
'''
        
    def _generate_exceptions(self) -> str:
        """Generate exceptions file."""
        return '''"""
Exception classes for the API client.
"""


class APIError(Exception):
    """Base exception for API errors."""
    pass


class AuthenticationError(APIError):
    """Raised when authentication fails."""
    pass


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    pass


class ValidationError(APIError):
    """Raised when request validation fails."""
    pass
'''
        
    def _generate_init(self) -> str:
        """Generate __init__.py file."""
        client_class = self._get_client_class_name()
        
        return f'''"""
{self.api_spec.title} Python SDK

Automatically generated from API traffic analysis.
"""

from .client import {client_class}
from .exceptions import APIError, AuthenticationError, RateLimitError

__version__ = "1.0.0"
__all__ = ["{client_class}", "APIError", "AuthenticationError", "RateLimitError"]
'''
        
    def _generate_requirements(self) -> str:
        """Generate requirements.txt file."""
        return '''requests>=2.25.0
'''
        
    def _generate_setup(self) -> str:
        """Generate setup.py file."""
        package_name = self._sanitize_name(self.api_spec.title.lower().replace(" ", "_"))
        
        return f'''from setuptools import setup, find_packages

setup(
    name="{package_name}-sdk",
    version="1.0.0",
    description="Python SDK for {self.api_spec.title}",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
'''
        
    def _generate_readme(self) -> str:
        """Generate README.md file."""
        client_class = self._get_client_class_name()
        auth_example = self._generate_auth_example()
        usage_examples = self._generate_usage_examples()
        
        return f'''# {self.api_spec.title} Python SDK

Automatically generated Python SDK for {self.api_spec.title}.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Setup

```python
from client import {client_class}

# Initialize the client
{auth_example}
```

### API Methods

{usage_examples}

## Error Handling

The SDK includes custom exception classes:

- `APIError`: Base exception for all API errors
- `AuthenticationError`: Raised for authentication failures
- `RateLimitError`: Raised when rate limits are exceeded

```python
from exceptions import APIError, AuthenticationError, RateLimitError

try:
    result = client.some_method()
except AuthenticationError:
    print("Invalid credentials")
except RateLimitError:
    print("Rate limit exceeded")
except APIError as e:
    print(f"API error: {{e}}")
```

## Generated from API Traffic

This SDK was automatically generated by analyzing API traffic patterns.
Endpoint coverage: {len(self.api_spec.endpoints)} endpoints discovered.
'''
        
    def _get_client_class_name(self) -> str:
        """Get the client class name."""
        name = self._sanitize_name(self.api_spec.title.replace(" ", ""))
        return f"{name}Client"
        
    def _generate_auth_example(self) -> str:
        """Generate authentication example."""
        auth_method = self._get_auth_method()
        client_class = self._get_client_class_name()
        
        if auth_method == "bearer_token":
            return f'client = {client_class}(token="your-bearer-token")'
        elif auth_method == "api_key":
            return f'client = {client_class}(api_key="your-api-key")'
        elif auth_method == "basic_auth":
            return f'client = {client_class}(username="your-username", password="your-password")'
        else:
            return f'client = {client_class}()'
            
    def _generate_usage_examples(self) -> str:
        """Generate usage examples for endpoints."""
        examples = []
        
        for endpoint in self.api_spec.endpoints[:3]:  # Show first 3 endpoints
            method_name = self._get_method_name(endpoint)
            
            # Generate example call
            args = []
            for param in endpoint.parameters:
                if param.example:
                    args.append(f'{param.name}="{param.example}"')
                else:
                    args.append(f'{param.name}="example_value"')
                    
            for param in endpoint.query_params:
                if param.required and param.example:
                    args.append(f'{param.name}="{param.example}"')
                    
            args_str = ", ".join(args)
            
            example = f'''#### {endpoint.summary or endpoint.method.value + " " + endpoint.path}

```python
result = client.{method_name}({args_str})
print(result)
```'''
            examples.append(example)
            
        return "\n\n".join(examples)