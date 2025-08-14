"""
TypeScript SDK generator with full typing support.
"""

from typing import Dict, List, Any
from pathlib import Path
import textwrap

from .base_generator import BaseGenerator
from ..types import APISpec, Endpoint, Parameter, ParameterType, AuthType


class TypeScriptGenerator(BaseGenerator):
    """Generate TypeScript SDK with full typing support."""
    
    def get_language_name(self) -> str:
        return "typescript"
        
    def generate(self, output_dir: str) -> Dict[str, str]:
        """Generate TypeScript SDK files."""
        output_path = self._create_output_dir(output_dir)
        files = {}
        
        # Generate main client file
        client_content = self._generate_client()
        client_file = output_path / "client.ts"
        self._write_file(str(client_file), client_content)
        files[str(client_file)] = client_content
        
        # Generate types file
        types_content = self._generate_types()
        types_file = output_path / "types.ts"
        self._write_file(str(types_file), types_content)
        files[str(types_file)] = types_content
        
        # Generate index file
        index_content = self._generate_index()
        index_file = output_path / "index.ts"
        self._write_file(str(index_file), index_content)
        files[str(index_file)] = index_content
        
        # Generate package.json
        package_content = self._generate_package_json()
        package_file = output_path / "package.json"
        self._write_file(str(package_file), package_content)
        files[str(package_file)] = package_content
        
        # Generate tsconfig.json
        tsconfig_content = self._generate_tsconfig()
        tsconfig_file = output_path / "tsconfig.json"
        self._write_file(str(tsconfig_file), tsconfig_content)
        files[str(tsconfig_file)] = tsconfig_content
        
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
        
        auth_interface = self._generate_auth_interface()
        auth_init = self._generate_auth_init()
        auth_headers = self._generate_auth_headers()
        
        return f'''/**
 * Generated API client for {self.api_spec.title}
 * 
 * This client was automatically generated from API traffic analysis.
 */

import {{ {auth_interface}APIResponse, APIError }} from './types';

{self._generate_config_interface()}

export class {self._get_client_class_name()} {{
  private baseUrl: string;
  {self._generate_auth_properties()}

  constructor(config: ClientConfig) {{
    this.baseUrl = config.baseUrl || '{self.api_spec.base_url}';
    {auth_init}
  }}

  private async makeRequest<T>(
    method: string,
    path: string,
    options: RequestInit = {{}}
  ): Promise<APIResponse<T>> {{
    const url = new URL(path.startsWith('/') ? path.slice(1) : path, this.baseUrl);
    
    const headers = new Headers({{
      'Content-Type': 'application/json',
      'User-Agent': 'Generated-TypeScript-SDK/1.0.0',
      ...options.headers,
      ...this.getAuthHeaders()
    }});

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
      throw new APIError(`Network error: ${{error}}`, 0);
    }}
  }}

  private getAuthHeaders(): Record<string, string> {{
    const headers: Record<string, string> = {{}};
    
    {auth_headers}
    
    return headers;
  }}

  {methods_str}
}}'''
        
    def _generate_method(self, endpoint: Endpoint) -> str:
        """Generate a method for an endpoint."""
        method_name = self._camel_case(self._get_method_name(endpoint))
        
        # Generate parameters
        params = []
        doc_params = []
        
        # Path parameters
        for param in endpoint.parameters:
            param_type = self._type_to_string(param.type, "typescript")
            params.append(f"{param.name}: {param_type}")
            doc_params.append(f"   * @param {param.name} {param.description or 'Path parameter'}")
            
        # Query parameters
        query_required = [p for p in endpoint.query_params if p.required]
        query_optional = [p for p in endpoint.query_params if not p.required]
        
        for param in query_required:
            param_type = self._type_to_string(param.type, "typescript")
            params.append(f"{param.name}: {param_type}")
            doc_params.append(f"   * @param {param.name} {param.description or 'Query parameter'}")
            
        # Optional query parameters
        if query_optional:
            optional_params = []
            for param in query_optional:
                param_type = self._type_to_string(param.type, "typescript")
                optional_params.append(f"{param.name}?: {param_type}")
                doc_params.append(f"   * @param {param.name} {param.description or 'Optional query parameter'}")
            
            if optional_params:
                params.append(f"options?: {{ {'; '.join(optional_params)} }}")
                
        # Request body
        if endpoint.request_body:
            params.append("data?: any")
            doc_params.append("   * @param data Request body data")
            
        params_str = ", ".join(params)
        doc_params_str = "\n".join(doc_params)
        
        # Generate method body
        path_substitution = self._generate_path_substitution_ts(endpoint)
        query_params_code = self._generate_query_params_code_ts(endpoint)
        request_body_code = self._generate_request_body_code_ts(endpoint)
        
        return f'''/**
   * {endpoint.summary or f"{endpoint.method.value} {endpoint.path}"}
   * 
   * {endpoint.description or "No description available."}
   * 
{doc_params_str}
   * @returns Promise<APIResponse<any>>
   */
  async {method_name}({params_str}): Promise<APIResponse<any>> {{
    {path_substitution}
    
    const requestOptions: RequestInit = {{}};
    
    {query_params_code}
    
    {request_body_code}
    
    return this.makeRequest<any>('{endpoint.method.value}', path, requestOptions);
  }}'''
        
    def _generate_path_substitution_ts(self, endpoint: Endpoint) -> str:
        """Generate path parameter substitution code for TypeScript."""
        if not endpoint.parameters:
            return f'let path = "{endpoint.path}";'
            
        substitutions = []
        for param in endpoint.parameters:
            substitutions.append(f'path = path.replace("{{{param.name}}}", String({param.name}));')
            
        return f'let path = "{endpoint.path}";\n    ' + '\n    '.join(substitutions)
        
    def _generate_query_params_code_ts(self, endpoint: Endpoint) -> str:
        """Generate query parameters handling code for TypeScript."""
        if not endpoint.query_params:
            return ""
            
        lines = ["const searchParams = new URLSearchParams();"]
        
        for param in endpoint.query_params:
            if param.required:
                lines.append(f'searchParams.append("{param.name}", String({param.name}));')
            else:
                lines.append(f'if (options?.{param.name} !== undefined) {{')
                lines.append(f'  searchParams.append("{param.name}", String(options.{param.name}));')
                lines.append('}')
                
        lines.append("if (searchParams.toString()) {")
        lines.append("  path += '?' + searchParams.toString();")
        lines.append("}")
        
        return "\n    ".join(lines)
        
    def _generate_request_body_code_ts(self, endpoint: Endpoint) -> str:
        """Generate request body handling code for TypeScript."""
        if not endpoint.request_body:
            return ""
            
        return '''if (data !== undefined) {
      requestOptions.body = JSON.stringify(data);
    }'''
        
    def _generate_auth_interface(self) -> str:
        """Generate authentication interface name."""
        auth_method = self._get_auth_method()
        
        if auth_method in ["bearer_token", "api_key", "basic_auth"]:
            return "AuthConfig, "
        else:
            return ""
            
    def _generate_config_interface(self) -> str:
        """Generate client configuration interface."""
        auth_method = self._get_auth_method()
        auth_props = ""
        
        if auth_method == "bearer_token":
            auth_props = "\n  token: string;"
        elif auth_method == "api_key":
            auth_props = "\n  apiKey: string;"
        elif auth_method == "basic_auth":
            auth_props = "\n  username: string;\n  password: string;"
            
        if auth_props:
            return f'''export interface AuthConfig {{{auth_props}
}}

export interface ClientConfig extends AuthConfig {{
  baseUrl?: string;
}}'''
        else:
            return '''export interface ClientConfig {
  baseUrl?: string;
}'''
        
    def _generate_auth_properties(self) -> str:
        """Generate authentication properties."""
        auth_method = self._get_auth_method()
        
        if auth_method == "bearer_token":
            return "private token: string;"
        elif auth_method == "api_key":
            return "private apiKey: string;"
        elif auth_method == "basic_auth":
            return "private username: string;\n  private password: string;"
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
            return "this.username = config.username;\n    this.password = config.password;"
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
            return '''const authString = btoa(`${this.username}:${this.password}`);
    headers["Authorization"] = `Basic ${authString}`;'''
        else:
            return "// No authentication headers needed"
            
    def _generate_types(self) -> str:
        """Generate types file."""
        return '''/**
 * Type definitions for the generated API client.
 */

export interface APIResponse<T> {
  data: T;
  status: number;
  headers: Record<string, string>;
}

export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// Add custom types here as needed
export type ApiData = any;
'''
        
    def _generate_index(self) -> str:
        """Generate index file."""
        client_class = self._get_client_class_name()
        
        return f'''/**
 * {self.api_spec.title} TypeScript SDK
 * 
 * Automatically generated from API traffic analysis.
 */

export {{ {client_class} }} from './client';
export {{ APIResponse, APIError }} from './types';
export type {{ ClientConfig }} from './client';
'''
        
    def _generate_package_json(self) -> str:
        """Generate package.json file."""
        package_name = self._sanitize_name(self.api_spec.title.lower().replace(" ", "-"))
        
        return f'''{{
  "name": "{package_name}-sdk",
  "version": "1.0.0",
  "description": "TypeScript SDK for {self.api_spec.title}",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {{
    "build": "tsc",
    "prepublishOnly": "npm run build"
  }},
  "keywords": ["api", "sdk", "typescript"],
  "author": "Generated",
  "license": "MIT",
  "devDependencies": {{
    "typescript": "^4.9.0",
    "@types/node": "^18.0.0"
  }},
  "files": [
    "dist/**/*"
  ]
}}'''
        
    def _generate_tsconfig(self) -> str:
        """Generate tsconfig.json file."""
        return '''{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020", "DOM"],
    "outDir": "./dist",
    "rootDir": "./",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": [
    "*.ts"
  ],
  "exclude": [
    "node_modules",
    "dist"
  ]
}'''
        
    def _generate_readme(self) -> str:
        """Generate README.md file."""
        client_class = self._get_client_class_name()
        auth_example = self._generate_auth_example_ts()
        usage_examples = self._generate_usage_examples_ts()
        
        return f'''# {self.api_spec.title} TypeScript SDK

Automatically generated TypeScript SDK for {self.api_spec.title}.

## Installation

```bash
npm install
npm run build
```

## Usage

### Basic Setup

```typescript
import {{ {client_class} }} from './{self._get_client_class_name().lower()}';

// Initialize the client
{auth_example}
```

### API Methods

{usage_examples}

## Error Handling

The SDK includes custom error handling:

```typescript
import {{ APIError }} from './types';

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

## Generated from API Traffic

This SDK was automatically generated by analyzing API traffic patterns.
Endpoint coverage: {len(self.api_spec.endpoints)} endpoints discovered.
'''
        
    def _get_client_class_name(self) -> str:
        """Get the client class name."""
        name = self._sanitize_name(self.api_spec.title.replace(" ", ""))
        return f"{name}Client"
        
    def _generate_auth_example_ts(self) -> str:
        """Generate authentication example for TypeScript."""
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
            return f'const client = new {client_class}({{}});'
            
    def _generate_usage_examples_ts(self) -> str:
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

```typescript
const result = await client.{method_name}({args_str});
console.log(result.data);
```'''
            examples.append(example)
            
        return "\n\n".join(examples)
        
    def _camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])