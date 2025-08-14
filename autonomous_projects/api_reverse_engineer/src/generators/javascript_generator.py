"""
JavaScript SDK generator with JSDoc typing support.
"""

from typing import Dict, List, Any
from pathlib import Path
import textwrap

from .base_generator import BaseGenerator
from ..types import APISpec, Endpoint, Parameter, ParameterType, AuthType


class JavaScriptGenerator(BaseGenerator):
    """Generate JavaScript SDK with JSDoc typing support."""
    
    def get_language_name(self) -> str:
        return "javascript"
        
    def generate(self, output_dir: str) -> Dict[str, str]:
        """Generate JavaScript SDK files."""
        output_path = self._create_output_dir(output_dir)
        files = {}
        
        # Generate main client file
        client_content = self._generate_client()
        client_file = output_path / "client.js"
        self._write_file(str(client_file), client_content)
        files[str(client_file)] = client_content
        
        # Generate types file (JSDoc)
        types_content = self._generate_types()
        types_file = output_path / "types.js"
        self._write_file(str(types_file), types_content)
        files[str(types_file)] = types_content
        
        # Generate index file
        index_content = self._generate_index()
        index_file = output_path / "index.js"
        self._write_file(str(index_file), index_content)
        files[str(index_file)] = index_content
        
        # Generate package.json
        package_content = self._generate_package_json()
        package_file = output_path / "package.json"
        self._write_file(str(package_file), package_content)
        files[str(package_file)] = package_content
        
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
            
        methods_str = "\n\n  ".join(methods)
        
        auth_jsdoc = self._generate_auth_jsdoc()
        auth_init = self._generate_auth_init()
        auth_headers = self._generate_auth_headers()
        
        return f'''/**
 * Generated API client for {self.api_spec.title}
 * 
 * This client was automatically generated from API traffic analysis.
 */

const {{ APIError }} = require('./types');

/**
 * {self.api_spec.description}
 * @class
 */
class {self._get_client_class_name()} {{
  /**
   * Create a new API client instance
   * {auth_jsdoc}
   * @param {{Object}} config - Configuration options
   * @param {{string}} [config.baseUrl] - Base URL for the API
   */
  constructor(config = {{}}) {{
    this.baseUrl = config.baseUrl || '{self.api_spec.base_url}';
    {auth_init}
  }}

  /**
   * Make an HTTP request to the API
   * @private
   * @param {{string}} method - HTTP method
   * @param {{string}} path - API path
   * @param {{Object}} [options={}] - Request options
   * @returns {{Promise<Object>}} API response
   * @throws {{APIError}} When the request fails
   */
  async makeRequest(method, path, options = {{}}) {{
    const url = new URL(path.startsWith('/') ? path.slice(1) : path, this.baseUrl);
    
    const headers = {{
      'Content-Type': 'application/json',
      'User-Agent': 'Generated-JavaScript-SDK/1.0.0',
      ...options.headers,
      ...this.getAuthHeaders()
    }};

    try {{
      const response = await fetch(url.toString(), {{
        method,
        headers,
        ...options
      }});

      if (response.status === 401) {{
        throw new APIError('Invalid authentication credentials', 401);
      }}
      
      if (response.status === 429) {{
        throw new APIError('Rate limit exceeded', 429);
      }}
      
      if (!response.ok) {{
        const errorText = await response.text();
        throw new APIError(`API request failed: ${{response.status}} ${{errorText}}`, response.status);
      }}

      const data = await response.json();
      
      return {{
        data,
        status: response.status,
        headers: Object.fromEntries(response.headers.entries())
      }};
      
    }} catch (error) {{
      if (error instanceof APIError) {{
        throw error;
      }}
      throw new APIError(`Network error: ${{error.message}}`, 0);
    }}
  }}

  /**
   * Get authentication headers
   * @private
   * @returns {{Object}} Authentication headers
   */
  getAuthHeaders() {{
    const headers = {{}};
    
    {auth_headers}
    
    return headers;
  }}

  {methods_str}
}}

module.exports = {{ {self._get_client_class_name()} }};'''
        
    def _generate_method(self, endpoint: Endpoint) -> str:
        """Generate a method for an endpoint."""
        method_name = self._camel_case(self._get_method_name(endpoint))
        
        # Generate JSDoc parameters
        jsdoc_params = []
        js_params = []
        
        # Path parameters
        for param in endpoint.parameters:
            param_type = self._type_to_jsdoc_type(param.type)
            jsdoc_params.append(f"   * @param {{{param_type}}} {param.name} - {param.description or 'Path parameter'}")
            js_params.append(param.name)
            
        # Query parameters
        query_required = [p for p in endpoint.query_params if p.required]
        query_optional = [p for p in endpoint.query_params if not p.required]
        
        for param in query_required:
            param_type = self._type_to_jsdoc_type(param.type)
            jsdoc_params.append(f"   * @param {{{param_type}}} {param.name} - {param.description or 'Query parameter'}")
            js_params.append(param.name)
            
        # Optional parameters object
        if query_optional:
            optional_props = []
            for param in query_optional:
                param_type = self._type_to_jsdoc_type(param.type)
                optional_props.append(f"   * @param {{{param_type}}} [options.{param.name}] - {param.description or 'Optional query parameter'}")
            
            if optional_props:
                jsdoc_params.append("   * @param {Object} [options] - Optional parameters")
                jsdoc_params.extend(optional_props)
                js_params.append("options = {}")
                
        # Request body
        if endpoint.request_body:
            jsdoc_params.append("   * @param {Object} [data] - Request body data")
            js_params.append("data")
            
        jsdoc_params_str = "\n".join(jsdoc_params)
        js_params_str = ", ".join(js_params)
        
        # Generate method body
        path_substitution = self._generate_path_substitution_js(endpoint)
        query_params_code = self._generate_query_params_code_js(endpoint)
        request_body_code = self._generate_request_body_code_js(endpoint)
        
        return f'''/**
   * {endpoint.summary or f"{endpoint.method.value} {endpoint.path}"}
   * 
   * {endpoint.description or "No description available."}
   * 
{jsdoc_params_str}
   * @returns {{Promise<Object>}} API response
   * @throws {{APIError}} When the request fails
   */
  async {method_name}({js_params_str}) {{
    {path_substitution}
    
    const requestOptions = {{}};
    
    {query_params_code}
    
    {request_body_code}
    
    return this.makeRequest('{endpoint.method.value}', path, requestOptions);
  }}'''
        
    def _generate_path_substitution_js(self, endpoint: Endpoint) -> str:
        """Generate path parameter substitution code for JavaScript."""
        if not endpoint.parameters:
            return f'let path = "{endpoint.path}";'
            
        substitutions = []
        for param in endpoint.parameters:
            substitutions.append(f'path = path.replace("{{{param.name}}}", String({param.name}));')
            
        return f'let path = "{endpoint.path}";\n    ' + '\n    '.join(substitutions)
        
    def _generate_query_params_code_js(self, endpoint: Endpoint) -> str:
        """Generate query parameters handling code for JavaScript."""
        if not endpoint.query_params:
            return ""
            
        lines = ["const searchParams = new URLSearchParams();"]
        
        for param in endpoint.query_params:
            if param.required:
                lines.append(f'searchParams.append("{param.name}", String({param.name}));')
            else:
                lines.append(f'if (options.{param.name} !== undefined) {{')
                lines.append(f'  searchParams.append("{param.name}", String(options.{param.name}));')
                lines.append('}')
                
        lines.append("if (searchParams.toString()) {")
        lines.append("  path += '?' + searchParams.toString();")
        lines.append("}")
        
        return "\n    ".join(lines)
        
    def _generate_request_body_code_js(self, endpoint: Endpoint) -> str:
        """Generate request body handling code for JavaScript."""
        if not endpoint.request_body:
            return ""
            
        return '''if (data !== undefined) {
      requestOptions.body = JSON.stringify(data);
    }'''
        
    def _generate_auth_jsdoc(self) -> str:
        """Generate authentication JSDoc."""
        auth_method = self._get_auth_method()
        
        if auth_method == "bearer_token":
            return "   * @param {string} config.token - Bearer token for authentication"
        elif auth_method == "api_key":
            return "   * @param {string} config.apiKey - API key for authentication"
        elif auth_method == "basic_auth":
            return "   * @param {string} config.username - Username for basic authentication\\n   * @param {string} config.password - Password for basic authentication"
        else:
            return ""
            
    def _generate_auth_init(self) -> str:
        """Generate authentication initialization."""
        auth_method = self._get_auth_method()
        
        if auth_method == "bearer_token":
            return "this.token = config.token;"
        elif auth_method == "api_key":
            return "this.apiKey = config.apiKey;"
        elif auth_method == "basic_auth":
            return "this.username = config.username;\\n    this.password = config.password;"
        else:
            return "// No authentication required"
            
    def _generate_auth_headers(self) -> str:
        """Generate authentication headers code."""
        auth_method = self._get_auth_method()
        
        if auth_method == "bearer_token":
            return 'headers["Authorization"] = `Bearer ${this.token}`;'
        elif auth_method == "api_key":
            header_name = "X-API-Key"
            if self.api_spec.auth_patterns:
                header_name = self.api_spec.auth_patterns[0].header_name or "X-API-Key"
            return f'headers["{header_name}"] = this.apiKey;'
        elif auth_method == "basic_auth":
            return '''const authString = Buffer.from(`${this.username}:${this.password}`).toString('base64');
    headers["Authorization"] = `Basic ${authString}`;'''
        else:
            return "// No authentication headers needed"
            
    def _generate_types(self) -> str:
        """Generate types file with JSDoc definitions."""
        return '''/**
 * Type definitions and error classes for the API client.
 */

/**
 * API Error class
 * @class
 * @extends Error
 */
class APIError extends Error {
  /**
   * Create an API error
   * @param {string} message - Error message
   * @param {number} statusCode - HTTP status code
   */
  constructor(message, statusCode) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
  }
}

/**
 * @typedef {Object} APIResponse
 * @property {*} data - Response data
 * @property {number} status - HTTP status code
 * @property {Object} headers - Response headers
 */

module.exports = {
  APIError
};
'''
        
    def _generate_index(self) -> str:
        """Generate index file."""
        client_class = self._get_client_class_name()
        
        return f'''/**
 * {self.api_spec.title} JavaScript SDK
 * 
 * Automatically generated from API traffic analysis.
 */

const {{ {client_class} }} = require('./client');
const {{ APIError }} = require('./types');

module.exports = {{
  {client_class},
  APIError
}};
'''
        
    def _generate_package_json(self) -> str:
        """Generate package.json file."""
        package_name = self._sanitize_name(self.api_spec.title.lower().replace(" ", "-"))
        
        return f'''{{
  "name": "{package_name}-sdk",
  "version": "1.0.0",
  "description": "JavaScript SDK for {self.api_spec.title}",
  "main": "index.js",
  "scripts": {{
    "test": "echo \\"Error: no test specified\\" && exit 1"
  }},
  "keywords": ["api", "sdk", "javascript"],
  "author": "Generated",
  "license": "MIT",
  "engines": {{
    "node": ">=14.0.0"
  }}
}}'''
        
    def _generate_readme(self) -> str:
        """Generate README.md file."""
        client_class = self._get_client_class_name()
        auth_example = self._generate_auth_example_js()
        usage_examples = self._generate_usage_examples_js()
        
        return f'''# {self.api_spec.title} JavaScript SDK

Automatically generated JavaScript SDK for {self.api_spec.title}.

## Installation

```bash
npm install
```

## Usage

### Basic Setup

```javascript
const {{ {client_class} }} = require('./{self._get_client_class_name().lower()}');

// Initialize the client
{auth_example}
```

### API Methods

{usage_examples}

## Error Handling

The SDK includes custom error handling:

```javascript
const {{ APIError }} = require('./types');

try {{
  const result = await client.someMethod();
  console.log(result.data);
}} catch (error) {{
  if (error instanceof APIError) {{
    console.error(`API Error: ${{error.message}} (Status: ${{error.statusCode}})`);
  }} else {{
    console.error('Unexpected error:', error);
  }}
}}
```

## Node.js Compatibility

This SDK requires Node.js 14.0.0 or higher for native fetch support.
For older versions, you may need to install a fetch polyfill.

## Generated from API Traffic

This SDK was automatically generated by analyzing API traffic patterns.
Endpoint coverage: {len(self.api_spec.endpoints)} endpoints discovered.
'''
        
    def _get_client_class_name(self) -> str:
        """Get the client class name."""
        name = self._sanitize_name(self.api_spec.title.replace(" ", ""))
        return f"{name}Client"
        
    def _generate_auth_example_js(self) -> str:
        """Generate authentication example for JavaScript."""
        auth_method = self._get_auth_method()
        client_class = self._get_client_class_name()
        
        if auth_method == "bearer_token":
            return f'''const client = new {client_class}({{
  token: 'your-bearer-token'
}});'''
        elif auth_method == "api_key":
            return f'''const client = new {client_class}({{
  apiKey: 'your-api-key'
}});'''
        elif auth_method == "basic_auth":
            return f'''const client = new {client_class}({{
  username: 'your-username',
  password: 'your-password'
}});'''
        else:
            return f'const client = new {client_class}();'
            
    def _generate_usage_examples_js(self) -> str:
        """Generate usage examples for endpoints."""
        examples = []
        
        for endpoint in self.api_spec.endpoints[:3]:  # Show first 3 endpoints
            method_name = self._camel_case(self._get_method_name(endpoint))
            
            # Generate example call
            args = []
            for param in endpoint.parameters:
                if param.example:
                    args.append(f'"{param.example}"')
                else:
                    args.append('"example_value"')
                    
            # Add options object if there are optional query params
            optional_params = [p for p in endpoint.query_params if not p.required]
            if optional_params:
                options = []
                for param in optional_params:
                    if param.example:
                        options.append(f'{param.name}: "{param.example}"')
                        
                if options:
                    args.append(f'{{ {", ".join(options)} }}')
                    
            args_str = ", ".join(args)
            
            example = f'''#### {endpoint.summary or endpoint.method.value + " " + endpoint.path}

```javascript
const result = await client.{method_name}({args_str});
console.log(result.data);
```'''
            examples.append(example)
            
        return "\n\n".join(examples)
        
    def _camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
        
    def _type_to_jsdoc_type(self, param_type: ParameterType) -> str:
        """Convert ParameterType to JSDoc type string."""
        type_map = {
            ParameterType.STRING: "string",
            ParameterType.INTEGER: "number",
            ParameterType.FLOAT: "number",
            ParameterType.BOOLEAN: "boolean",
            ParameterType.ARRAY: "Array",
            ParameterType.OBJECT: "Object",
            ParameterType.NULL: "*"
        }
        
        return type_map.get(param_type, "*")