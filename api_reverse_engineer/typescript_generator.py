from typing import Dict, List, Any
from sdk_generator import SDKGenerator
from traffic_parser import APIEndpoint


class TypeScriptSDKGenerator(SDKGenerator):
    def generate(self, output_dir: str = 'generated_sdks/typescript') -> str:
        interfaces = []
        
        for endpoint_key, endpoint in self.endpoints.items():
            method_name = self._path_to_method_name(endpoint.method, endpoint.path_pattern)
            
            if endpoint.request_body_schema and endpoint.request_body_schema.get('type') == 'object':
                request_interface_name = f"{self._to_class_name(method_name)}Request"
                request_interface = self._generate_interface_from_schema(
                    request_interface_name,
                    endpoint.request_body_schema,
                    'typescript'
                )
                if request_interface and request_interface not in interfaces:
                    interfaces.append(request_interface)
            
            for status, response_schema in endpoint.response_schemas.items():
                if status == 200 and response_schema.get('type') == 'object':
                    response_interface_name = f"{self._to_class_name(method_name)}Response"
                    response_interface = self._generate_interface_from_schema(
                        response_interface_name,
                        response_schema,
                        'typescript'
                    )
                    if response_interface and response_interface not in interfaces:
                        interfaces.append(response_interface)
        
        class_content = self._generate_typescript_class()
        
        content = f"""// Auto-generated TypeScript SDK for {self.api_name} API
// Base URL: {self.base_url}

"""
        
        if interfaces:
            content += "// Type Definitions\n"
            content += '\n\n'.join(interfaces) + '\n\n'
        
        content += "// API Client\n"
        content += class_content
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = f"{output_dir}/{self._to_camel_case(self.api_name)}Client.ts"
        with open(output_file, 'w') as f:
            f.write(content)
        
        self._generate_package_json(output_dir)
        self._generate_tsconfig(output_dir)
        self._generate_readme(output_dir)
        
        return output_file
    
    def _generate_typescript_class(self) -> str:
        lines = [
            f"export class {self.class_name}Client {{",
            f"  private baseUrl: string;",
            f"  private headers: Record<string, string>;",
            f"",
            f"  constructor(baseUrl: string = '{self.base_url}', headers: Record<string, string> = {{}}) {{",
            f"    this.baseUrl = baseUrl.replace(/\\/+$/, '');",
            f"    this.headers = {{",
            f"      'Content-Type': 'application/json',",
            f"      ...headers",
            f"    }};",
            f"  }}",
            f"",
            f"  setAuthToken(token: string): void {{",
            f"    this.headers['Authorization'] = `Bearer ${{token}}`;",
            f"  }}",
            f"",
            f"  setHeader(key: string, value: string): void {{",
            f"    this.headers[key] = value;",
            f"  }}",
            f"",
            f"  private async request<T>(options: {{",
            f"    method: string;",
            f"    path: string;",
            f"    params?: Record<string, any>;",
            f"    body?: any;",
            f"    headers?: Record<string, string>;",
            f"  }}): Promise<T> {{",
            f"    const url = new URL(`${{this.baseUrl}}${{options.path}}`);",
            f"    ",
            f"    if (options.params) {{",
            f"      Object.entries(options.params).forEach(([key, value]) => {{",
            f"        if (value !== null && value !== undefined) {{",
            f"          url.searchParams.append(key, String(value));",
            f"        }}",
            f"      }});",
            f"    }}",
            f"    ",
            f"    const response = await fetch(url.toString(), {{",
            f"      method: options.method,",
            f"      headers: {{",
            f"        ...this.headers,",
            f"        ...options.headers",
            f"      }},",
            f"      body: options.body ? JSON.stringify(options.body) : undefined",
            f"    }});",
            f"    ",
            f"    if (!response.ok) {{",
            f"      throw new Error(`HTTP error! status: ${{response.status}}`);",
            f"    }}",
            f"    ",
            f"    const contentType = response.headers.get('content-type');",
            f"    if (contentType && contentType.includes('application/json')) {{",
            f"      return response.json() as Promise<T>;",
            f"    }}",
            f"    ",
            f"    return {{}} as T;",
            f"  }}",
            f""
        ]
        
        for endpoint_key, endpoint in self.endpoints.items():
            method_lines = self._generate_typescript_method(
                self._path_to_method_name(endpoint.method, endpoint.path_pattern),
                endpoint
            )
            lines.extend(method_lines)
        
        lines.append("}")
        
        return '\n'.join(lines)
    
    def _generate_typescript_method(self, method_name: str, endpoint: APIEndpoint) -> List[str]:
        lines = []
        
        params = []
        param_types = []
        
        for param in sorted(endpoint.path_params):
            param_camel = self._to_camel_case(param)
            params.append(f"{param_camel}: string")
            param_types.append((param_camel, 'path'))
        
        if endpoint.query_params:
            query_params = []
            for param, param_type in endpoint.query_params.items():
                param_camel = self._to_camel_case(param)
                type_hint = self._schema_to_type_hint({'type': param_type}, 'typescript')
                query_params.append(f"{param_camel}?: {type_hint}")
            
            if query_params:
                params.append(f"params?: {{ {'; '.join(query_params)} }}")
                param_types.append(('params', 'query'))
        
        if endpoint.request_body_schema:
            body_type = self._schema_to_type_hint(endpoint.request_body_schema, 'typescript')
            params.append(f"data?: {body_type}")
            param_types.append(('data', 'body'))
        
        response_type = 'any'
        if 200 in endpoint.response_schemas:
            response_type = self._schema_to_type_hint(endpoint.response_schemas[200], 'typescript')
        
        param_str = ', '.join(params) if params else ''
        
        lines.append(f"  async {method_name}({param_str}): Promise<{response_type}> {{")
        
        path = endpoint.path_pattern
        for param in endpoint.path_params:
            param_camel = self._to_camel_case(param)
            path = path.replace(f"{{{param}}}", f"${{{param_camel}}}")
        
        lines.append(f"    const path = `{path}`;")
        lines.append(f"    ")
        lines.append(f"    return this.request<{response_type}>({{")
        lines.append(f"      method: '{endpoint.method}',")
        lines.append(f"      path,")
        
        for param_name, param_type in param_types:
            if param_type == 'query':
                lines.append(f"      params,")
            elif param_type == 'body':
                lines.append(f"      body: data,")
        
        lines.append(f"    }});")
        lines.append(f"  }}")
        lines.append(f"")
        
        return lines
    
    def _generate_package_json(self, output_dir: str):
        package = {
            "name": f"{self._to_snake_case(self.api_name)}-sdk",
            "version": "1.0.0",
            "description": f"Auto-generated TypeScript SDK for {self.api_name} API",
            "main": f"{self._to_camel_case(self.api_name)}Client.js",
            "types": f"{self._to_camel_case(self.api_name)}Client.d.ts",
            "scripts": {
                "build": "tsc",
                "test": "echo \"No tests yet\""
            },
            "keywords": ["api", "sdk", "client", self.api_name],
            "author": "Auto-generated",
            "license": "MIT",
            "devDependencies": {
                "@types/node": "^18.0.0",
                "typescript": "^5.0.0"
            }
        }
        
        import json
        with open(f"{output_dir}/package.json", 'w') as f:
            json.dump(package, f, indent=2)
    
    def _generate_tsconfig(self, output_dir: str):
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["ES2020", "DOM"],
                "declaration": True,
                "outDir": "./",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True
            },
            "include": ["*.ts"],
            "exclude": ["node_modules"]
        }
        
        import json
        with open(f"{output_dir}/tsconfig.json", 'w') as f:
            json.dump(tsconfig, f, indent=2)
    
    def _generate_readme(self, output_dir: str):
        readme = f"""# {self.class_name} TypeScript SDK

Auto-generated TypeScript SDK for {self.api_name} API.

## Installation

```bash
npm install
```

## Usage

```typescript
import {{ {self.class_name}Client }} from './{self._to_camel_case(self.api_name)}Client';

// Initialize the client
const client = new {self.class_name}Client('{self.base_url}');

// Set authentication if needed
client.setAuthToken('your-token-here');

// Make API calls
"""
        
        example_method = None
        for endpoint_key, endpoint in self.endpoints.items():
            if endpoint.method == 'GET' and not endpoint.path_params:
                example_method = self._path_to_method_name(endpoint.method, endpoint.path_pattern)
                readme += f"const response = await client.{example_method}();\n"
                readme += f"console.log(response);\n"
                break
        
        readme += """```

## Available Methods

"""
        
        for endpoint_key, endpoint in self.endpoints.items():
            method_name = self._path_to_method_name(endpoint.method, endpoint.path_pattern)
            readme += f"- `{method_name}()` - {endpoint.method} {endpoint.path_pattern}\n"
        
        readme += """

## Building

```bash
npm run build
```

## Generated from Network Traffic

This SDK was automatically generated by analyzing API network traffic patterns.
"""
        
        with open(f"{output_dir}/README.md", 'w') as f:
            f.write(readme)