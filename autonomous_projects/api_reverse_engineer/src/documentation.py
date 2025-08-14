"""
Documentation generator for API specifications.
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import textwrap

from .types import APISpec, Endpoint, Parameter, ResponseSchema, AuthType


class DocumentationGenerator:
    """Generate comprehensive documentation from API specifications."""
    
    def __init__(self, api_spec: APISpec):
        self.api_spec = api_spec
        
    def generate_markdown(self, output_file: Optional[str] = None) -> str:
        """Generate Markdown documentation."""
        content = self._generate_markdown_content()
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        return content
        
    def generate_openapi(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification."""
        spec = self._generate_openapi_spec()
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(spec, f, indent=2)
                
        return spec
        
    def generate_postman(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Generate Postman collection."""
        collection = self._generate_postman_collection()
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(collection, f, indent=2)
                
        return collection
        
    def _generate_markdown_content(self) -> str:
        """Generate the complete Markdown documentation."""
        sections = [
            self._generate_title_section(),
            self._generate_overview_section(),
            self._generate_authentication_section(),
            self._generate_rate_limiting_section(),
            self._generate_endpoints_section(),
            self._generate_examples_section(),
            self._generate_error_handling_section()
        ]
        
        return "\n\n".join(filter(None, sections))
        
    def _generate_title_section(self) -> str:
        """Generate the title and description section."""
        return f"""# {self.api_spec.title}

{self.api_spec.description}

**Base URL:** `{self.api_spec.base_url}`
**Version:** {self.api_spec.version}

---

## Table of Contents

- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
- [Examples](#examples)
- [Error Handling](#error-handling)"""
        
    def _generate_overview_section(self) -> str:
        """Generate the API overview section."""
        endpoint_count = len(self.api_spec.endpoints)
        methods = set(ep.method.value for ep in self.api_spec.endpoints)
        
        return f"""## Overview

This API documentation was automatically generated from network traffic analysis.

**Discovered Endpoints:** {endpoint_count}
**HTTP Methods:** {', '.join(sorted(methods))}
**Authentication:** {len(self.api_spec.auth_patterns)} pattern(s) detected"""
        
    def _generate_authentication_section(self) -> str:
        """Generate the authentication section."""
        if not self.api_spec.auth_patterns:
            return "## Authentication\n\nNo authentication required."
            
        content = ["## Authentication"]
        
        for i, auth_pattern in enumerate(self.api_spec.auth_patterns):
            content.append(f"\n### Method {i + 1}: {auth_pattern.type.value.replace('_', ' ').title()}")
            
            if auth_pattern.type == AuthType.BEARER_TOKEN:
                content.append("Include the Bearer token in the Authorization header:")
                content.append("```")
                content.append("Authorization: Bearer YOUR_TOKEN")
                content.append("```")
                
            elif auth_pattern.type == AuthType.API_KEY:
                header_name = auth_pattern.header_name or "X-API-Key"
                content.append(f"Include your API key in the `{header_name}` header:")
                content.append("```")
                content.append(f"{header_name}: YOUR_API_KEY")
                content.append("```")
                
            elif auth_pattern.type == AuthType.BASIC_AUTH:
                content.append("Use HTTP Basic Authentication:")
                content.append("```")
                content.append("Authorization: Basic BASE64(username:password)")
                content.append("```")
                
            elif auth_pattern.type == AuthType.CUSTOM_HEADER:
                header_name = auth_pattern.header_name or "Authorization"
                content.append(f"Include authentication in the `{header_name}` header:")
                content.append("```")
                content.append(f"{header_name}: YOUR_AUTH_VALUE")
                content.append("```")
                
        return "\n".join(content)
        
    def _generate_rate_limiting_section(self) -> str:
        """Generate the rate limiting section."""
        if not self.api_spec.rate_limits:
            return "## Rate Limiting\n\nNo rate limiting detected."
            
        content = ["## Rate Limiting"]
        rate_limits = self.api_spec.rate_limits
        
        if rate_limits.requests_per_minute:
            content.append(f"- **Per minute:** {rate_limits.requests_per_minute} requests")
        if rate_limits.requests_per_hour:
            content.append(f"- **Per hour:** {rate_limits.requests_per_hour} requests")
        if rate_limits.requests_per_day:
            content.append(f"- **Per day:** {rate_limits.requests_per_day} requests")
            
        if rate_limits.headers:
            content.append("\n**Rate limiting headers detected:**")
            for header, description in rate_limits.headers.items():
                content.append(f"- `{header}`: {description}")
                
        return "\n".join(content)
        
    def _generate_endpoints_section(self) -> str:
        """Generate the endpoints section."""
        content = ["## Endpoints"]
        
        # Group endpoints by path for better organization
        path_groups = {}
        for endpoint in self.api_spec.endpoints:
            base_path = endpoint.path.split('/')[1] if endpoint.path.startswith('/') else endpoint.path
            if base_path not in path_groups:
                path_groups[base_path] = []
            path_groups[base_path].append(endpoint)
            
        for path_group, endpoints in path_groups.items():
            if path_group:
                content.append(f"\n### {path_group.title()} Operations")
            else:
                content.append(f"\n### Root Operations")
                
            for endpoint in endpoints:
                content.append(self._generate_endpoint_documentation(endpoint))
                
        return "\n".join(content)
        
    def _generate_endpoint_documentation(self, endpoint: Endpoint) -> str:
        """Generate documentation for a single endpoint."""
        content = []
        
        # Endpoint header
        method_badge = self._get_method_badge(endpoint.method.value)
        content.append(f"\n#### {method_badge} `{endpoint.path}`")
        
        if endpoint.summary:
            content.append(f"\n**{endpoint.summary}**")
            
        if endpoint.description:
            content.append(f"\n{endpoint.description}")
            
        # Authentication requirement
        if endpoint.auth_required:
            content.append("\n🔒 **Authentication required**")
            
        # Parameters
        all_params = endpoint.parameters + endpoint.query_params + endpoint.headers
        if all_params:
            content.append("\n**Parameters:**")
            content.append("\n| Name | Type | Location | Required | Description |")
            content.append("|------|------|----------|----------|-------------|")
            
            for param in endpoint.parameters:
                location = "path"
                required = "✅" if param.required else "❌"
                description = param.description or "-"
                content.append(f"| `{param.name}` | {param.type.value} | {location} | {required} | {description} |")
                
            for param in endpoint.query_params:
                location = "query"
                required = "✅" if param.required else "❌"
                description = param.description or "-"
                content.append(f"| `{param.name}` | {param.type.value} | {location} | {required} | {description} |")
                
            for param in endpoint.headers:
                location = "header"
                required = "✅" if param.required else "❌"
                description = param.description or "-"
                content.append(f"| `{param.name}` | {param.type.value} | {location} | {required} | {description} |")
                
        # Request body
        if endpoint.request_body:
            content.append("\n**Request Body:**")
            content.append("```json")
            content.append(json.dumps(endpoint.request_body, indent=2))
            content.append("```")
            
        # Responses
        if endpoint.responses:
            content.append("\n**Responses:**")
            for response in endpoint.responses:
                content.append(f"\n**{response.status_code}** - {self._get_status_description(response.status_code)}")
                
                if response.content_type:
                    content.append(f"Content-Type: `{response.content_type}`")
                    
                if response.schema:
                    content.append("```json")
                    content.append(json.dumps(response.schema, indent=2))
                    content.append("```")
                    
                if response.examples:
                    content.append("**Example response:**")
                    content.append("```json")
                    content.append(json.dumps(response.examples[0], indent=2))
                    content.append("```")
                    
        return "\n".join(content)
        
    def _generate_examples_section(self) -> str:
        """Generate usage examples section."""
        content = ["## Examples"]
        
        # Show examples for first few endpoints
        for i, endpoint in enumerate(self.api_spec.endpoints[:3]):
            content.append(f"\n### Example {i + 1}: {endpoint.summary or endpoint.method.value + ' ' + endpoint.path}")
            
            # cURL example
            content.append("\n**cURL:**")
            curl_cmd = self._generate_curl_example(endpoint)
            content.append(f"```bash\n{curl_cmd}\n```")
            
            # Python example
            content.append("\n**Python (requests):**")
            python_code = self._generate_python_example(endpoint)
            content.append(f"```python\n{python_code}\n```")
            
            # JavaScript example
            content.append("\n**JavaScript (fetch):**")
            js_code = self._generate_javascript_example(endpoint)
            content.append(f"```javascript\n{js_code}\n```")
            
        return "\n".join(content)
        
    def _generate_error_handling_section(self) -> str:
        """Generate error handling section."""
        return """## Error Handling

The API uses standard HTTP status codes to indicate success or failure of requests.

### Common Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource does not exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

### Error Response Format

Error responses typically include additional information:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request parameters are invalid",
    "details": {}
  }
}
```"""
        
    def _generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": self.api_spec.title,
                "description": self.api_spec.description,
                "version": self.api_spec.version
            },
            "servers": [
                {
                    "url": self.api_spec.base_url,
                    "description": "API server"
                }
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {}
            }
        }
        
        # Add security schemes
        for auth_pattern in self.api_spec.auth_patterns:
            if auth_pattern.type == AuthType.BEARER_TOKEN:
                spec["components"]["securitySchemes"]["bearerAuth"] = {
                    "type": "http",
                    "scheme": "bearer"
                }
            elif auth_pattern.type == AuthType.API_KEY:
                header_name = auth_pattern.header_name or "X-API-Key"
                spec["components"]["securitySchemes"]["apiKey"] = {
                    "type": "apiKey",
                    "in": "header",
                    "name": header_name
                }
            elif auth_pattern.type == AuthType.BASIC_AUTH:
                spec["components"]["securitySchemes"]["basicAuth"] = {
                    "type": "http",
                    "scheme": "basic"
                }
                
        # Add paths
        for endpoint in self.api_spec.endpoints:
            path = endpoint.path
            method = endpoint.method.value.lower()
            
            if path not in spec["paths"]:
                spec["paths"][path] = {}
                
            spec["paths"][path][method] = self._endpoint_to_openapi(endpoint)
            
        return spec
        
    def _endpoint_to_openapi(self, endpoint: Endpoint) -> Dict[str, Any]:
        """Convert an endpoint to OpenAPI format."""
        operation = {
            "summary": endpoint.summary,
            "description": endpoint.description,
            "parameters": [],
            "responses": {}
        }
        
        # Add parameters
        for param in endpoint.parameters:
            operation["parameters"].append({
                "name": param.name,
                "in": "path",
                "required": param.required,
                "description": param.description,
                "schema": {"type": param.type.value}
            })
            
        for param in endpoint.query_params:
            operation["parameters"].append({
                "name": param.name,
                "in": "query", 
                "required": param.required,
                "description": param.description,
                "schema": {"type": param.type.value}
            })
            
        # Add request body
        if endpoint.request_body:
            operation["requestBody"] = {
                "content": {
                    "application/json": {
                        "schema": endpoint.request_body
                    }
                }
            }
            
        # Add responses
        for response in endpoint.responses:
            response_obj = {
                "description": self._get_status_description(response.status_code)
            }
            
            if response.schema:
                response_obj["content"] = {
                    response.content_type or "application/json": {
                        "schema": response.schema
                    }
                }
                
            operation["responses"][str(response.status_code)] = response_obj
            
        # Add security
        if endpoint.auth_required:
            if any(auth.type == AuthType.BEARER_TOKEN for auth in self.api_spec.auth_patterns):
                operation["security"] = [{"bearerAuth": []}]
            elif any(auth.type == AuthType.API_KEY for auth in self.api_spec.auth_patterns):
                operation["security"] = [{"apiKey": []}]
            elif any(auth.type == AuthType.BASIC_AUTH for auth in self.api_spec.auth_patterns):
                operation["security"] = [{"basicAuth": []}]
                
        return operation
        
    def _generate_postman_collection(self) -> Dict[str, Any]:
        """Generate Postman collection."""
        collection = {
            "info": {
                "name": self.api_spec.title,
                "description": self.api_spec.description,
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [],
            "variable": [
                {
                    "key": "baseUrl",
                    "value": self.api_spec.base_url,
                    "type": "string"
                }
            ]
        }
        
        # Group endpoints by resource
        resource_groups = {}
        for endpoint in self.api_spec.endpoints:
            resource = endpoint.path.split('/')[1] if endpoint.path.startswith('/') else 'root'
            if resource not in resource_groups:
                resource_groups[resource] = []
            resource_groups[resource].append(endpoint)
            
        # Create folders for each resource
        for resource, endpoints in resource_groups.items():
            folder = {
                "name": resource.title(),
                "item": []
            }
            
            for endpoint in endpoints:
                request_item = self._endpoint_to_postman_request(endpoint)
                folder["item"].append(request_item)
                
            collection["item"].append(folder)
            
        return collection
        
    def _endpoint_to_postman_request(self, endpoint: Endpoint) -> Dict[str, Any]:
        """Convert an endpoint to a Postman request."""
        request = {
            "name": endpoint.summary or f"{endpoint.method.value} {endpoint.path}",
            "request": {
                "method": endpoint.method.value,
                "header": [],
                "url": {
                    "raw": "{{baseUrl}}" + endpoint.path,
                    "host": ["{{baseUrl}}"],
                    "path": endpoint.path.strip('/').split('/') if endpoint.path != '/' else []
                }
            }
        }
        
        # Add headers
        if endpoint.auth_required:
            for auth_pattern in self.api_spec.auth_patterns:
                if auth_pattern.type == AuthType.BEARER_TOKEN:
                    request["request"]["header"].append({
                        "key": "Authorization",
                        "value": "Bearer {{token}}",
                        "type": "text"
                    })
                elif auth_pattern.type == AuthType.API_KEY:
                    header_name = auth_pattern.header_name or "X-API-Key"
                    request["request"]["header"].append({
                        "key": header_name,
                        "value": "{{apiKey}}",
                        "type": "text"
                    })
                    
        # Add query parameters
        if endpoint.query_params:
            query_params = []
            for param in endpoint.query_params:
                query_params.append({
                    "key": param.name,
                    "value": str(param.example) if param.example else "",
                    "description": param.description
                })
            request["request"]["url"]["query"] = query_params
            
        # Add request body
        if endpoint.request_body:
            request["request"]["header"].append({
                "key": "Content-Type",
                "value": "application/json",
                "type": "text"
            })
            request["request"]["body"] = {
                "mode": "raw",
                "raw": json.dumps(endpoint.request_body, indent=2)
            }
            
        return request
        
    def _get_method_badge(self, method: str) -> str:
        """Get a colored badge for HTTP method."""
        badges = {
            "GET": "🟢 GET",
            "POST": "🟡 POST", 
            "PUT": "🔵 PUT",
            "DELETE": "🔴 DELETE",
            "PATCH": "🟠 PATCH",
            "HEAD": "⚪ HEAD",
            "OPTIONS": "⚫ OPTIONS"
        }
        return badges.get(method, f"⚪ {method}")
        
    def _get_status_description(self, status_code: int) -> str:
        """Get description for HTTP status code."""
        descriptions = {
            200: "OK",
            201: "Created",
            202: "Accepted",
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            422: "Unprocessable Entity",
            429: "Too Many Requests",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable"
        }
        return descriptions.get(status_code, "Unknown")
        
    def _generate_curl_example(self, endpoint: Endpoint) -> str:
        """Generate a cURL example for an endpoint."""
        parts = [f"curl -X {endpoint.method.value}"]
        
        # URL with path parameters
        url = self.api_spec.base_url + endpoint.path
        for param in endpoint.parameters:
            example_value = param.example or "123"
            url = url.replace(f"{{{param.name}}}", str(example_value))
            
        # Add query parameters
        query_parts = []
        for param in endpoint.query_params:
            if param.example:
                query_parts.append(f"{param.name}={param.example}")
                
        if query_parts:
            url += "?" + "&".join(query_parts)
            
        parts.append(f'"{url}"')
        
        # Add headers
        parts.append('-H "Content-Type: application/json"')
        
        if endpoint.auth_required:
            for auth_pattern in self.api_spec.auth_patterns:
                if auth_pattern.type == AuthType.BEARER_TOKEN:
                    parts.append('-H "Authorization: Bearer YOUR_TOKEN"')
                elif auth_pattern.type == AuthType.API_KEY:
                    header_name = auth_pattern.header_name or "X-API-Key"
                    parts.append(f'-H "{header_name}: YOUR_API_KEY"')
                    
        # Add request body
        if endpoint.request_body:
            body = json.dumps(endpoint.request_body, separators=(',', ':'))
            parts.append(f"-d '{body}'")
            
        return " \\\n  ".join(parts)
        
    def _generate_python_example(self, endpoint: Endpoint) -> str:
        """Generate a Python example for an endpoint."""
        lines = ["import requests"]
        
        # URL
        url_parts = [f'url = "{self.api_spec.base_url}{endpoint.path}"']
        for param in endpoint.parameters:
            example_value = param.example or "123"
            url_parts.append(f'url = url.replace("{{{param.name}}}", "{example_value}")')
            
        lines.extend(url_parts)
        
        # Headers
        headers = ['headers = {', '    "Content-Type": "application/json"']
        
        if endpoint.auth_required:
            for auth_pattern in self.api_spec.auth_patterns:
                if auth_pattern.type == AuthType.BEARER_TOKEN:
                    headers.append('    "Authorization": "Bearer YOUR_TOKEN"')
                elif auth_pattern.type == AuthType.API_KEY:
                    header_name = auth_pattern.header_name or "X-API-Key"
                    headers.append(f'    "{header_name}": "YOUR_API_KEY"')
                    
        headers.append('}')
        lines.extend(headers)
        
        # Parameters
        if endpoint.query_params:
            params = ['params = {']
            for param in endpoint.query_params:
                if param.example:
                    params.append(f'    "{param.name}": "{param.example}"')
            params.append('}')
            lines.extend(params)
            
        # Request
        request_args = ['url', 'headers=headers']
        if endpoint.query_params:
            request_args.append('params=params')
        if endpoint.request_body:
            lines.append(f'data = {json.dumps(endpoint.request_body)}')
            request_args.append('json=data')
            
        lines.append(f'response = requests.{endpoint.method.value.lower()}({", ".join(request_args)})')
        lines.append('print(response.json())')
        
        return "\n".join(lines)
        
    def _generate_javascript_example(self, endpoint: Endpoint) -> str:
        """Generate a JavaScript example for an endpoint."""
        lines = []
        
        # URL
        url_parts = [f'let url = "{self.api_spec.base_url}{endpoint.path}";']
        for param in endpoint.parameters:
            example_value = param.example or "123"
            url_parts.append(f'url = url.replace("{{{param.name}}}", "{example_value}");')
            
        lines.extend(url_parts)
        
        # Query parameters
        if endpoint.query_params:
            lines.append('const params = new URLSearchParams();')
            for param in endpoint.query_params:
                if param.example:
                    lines.append(f'params.append("{param.name}", "{param.example}");')
            lines.append('if (params.toString()) url += "?" + params.toString();')
            
        # Headers
        headers = ['const headers = {', '    "Content-Type": "application/json"']
        
        if endpoint.auth_required:
            for auth_pattern in self.api_spec.auth_patterns:
                if auth_pattern.type == AuthType.BEARER_TOKEN:
                    headers.append('    "Authorization": "Bearer YOUR_TOKEN"')
                elif auth_pattern.type == AuthType.API_KEY:
                    header_name = auth_pattern.header_name or "X-API-Key"
                    headers.append(f'    "{header_name}": "YOUR_API_KEY"')
                    
        headers.append('};')
        lines.extend(headers)
        
        # Fetch options
        fetch_options = ['const options = {', f'    method: "{endpoint.method.value}"', '    headers']
        
        if endpoint.request_body:
            lines.append(f'const data = {json.dumps(endpoint.request_body)};')
            fetch_options.append('    body: JSON.stringify(data)')
            
        fetch_options.append('};')
        lines.extend(fetch_options)
        
        # Fetch call
        lines.extend([
            'fetch(url, options)',
            '    .then(response => response.json())',
            '    .then(data => console.log(data))',
            '    .catch(error => console.error(error));'
        ])
        
        return "\n".join(lines)