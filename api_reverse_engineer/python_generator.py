from typing import Dict, List, Any
from sdk_generator import SDKGenerator
from traffic_parser import APIEndpoint


class PythonSDKGenerator(SDKGenerator):
    def generate(self, output_dir: str = 'generated_sdks/python') -> str:
        imports = [
            "import requests",
            "from typing import Dict, List, Any, Optional",
            "from dataclasses import dataclass",
            "import json",
            "from urllib.parse import urljoin, quote",
            ""
        ]
        
        class_definition = [
            f"class {self.class_name}Client:",
            f'    """',
            f'    Auto-generated SDK for {self.api_name} API',
            f'    Base URL: {self.base_url}',
            f'    """',
            f'    ',
            f'    def __init__(self, base_url: str = "{self.base_url}", headers: Optional[Dict[str, str]] = None):',
            f'        self.base_url = base_url.rstrip("/")',
            f'        self.session = requests.Session()',
            f'        if headers:',
            f'            self.session.headers.update(headers)',
            f'    ',
            f'    def set_auth_token(self, token: str):',
            f'        """Set the authorization token for all requests"""',
            f'        self.session.headers["Authorization"] = f"Bearer {{token}}"',
            f'    ',
            f'    def set_header(self, key: str, value: str):',
            f'        """Set a custom header for all requests"""',
            f'        self.session.headers[key] = value',
            ''
        ]
        
        data_classes = []
        methods = []
        
        for endpoint_key, endpoint in self.endpoints.items():
            method_name = self._path_to_method_name(endpoint.method, endpoint.path_pattern)
            
            if endpoint.request_body_schema and endpoint.request_body_schema.get('type') == 'object':
                request_class_name = f"{self._to_class_name(method_name)}Request"
                request_interface = self._generate_interface_from_schema(
                    request_class_name, 
                    endpoint.request_body_schema, 
                    'python'
                )
                if request_interface and request_interface not in data_classes:
                    data_classes.append(request_interface)
            
            for status, response_schema in endpoint.response_schemas.items():
                if status == 200 and response_schema.get('type') == 'object':
                    response_class_name = f"{self._to_class_name(method_name)}Response"
                    response_interface = self._generate_interface_from_schema(
                        response_class_name,
                        response_schema,
                        'python'
                    )
                    if response_interface and response_interface not in data_classes:
                        data_classes.append(response_interface)
            
            method_lines = self._generate_python_method(method_name, endpoint)
            methods.extend(method_lines)
        
        if data_classes:
            content = '\n'.join(imports) + '\n# Data Classes\n' + '\n\n'.join(data_classes) + '\n\n\n'
        else:
            content = '\n'.join(imports) + '\n'
        
        content += '\n'.join(class_definition) + '\n'
        content += '\n'.join(methods)
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = f"{output_dir}/{self._to_snake_case(self.api_name)}_client.py"
        with open(output_file, 'w') as f:
            f.write(content)
        
        self._generate_requirements(output_dir)
        self._generate_readme(output_dir)
        
        return output_file
    
    def _generate_python_method(self, method_name: str, endpoint: APIEndpoint) -> List[str]:
        lines = []
        
        params = ['self']
        
        for param in sorted(endpoint.path_params):
            param_snake = self._to_snake_case(param)
            params.append(f"{param_snake}: str")
        
        for param, param_type in endpoint.query_params.items():
            param_snake = self._to_snake_case(param)
            type_hint = self._schema_to_type_hint({'type': param_type}, 'python')
            params.append(f"{param_snake}: Optional[{type_hint}] = None")
        
        if endpoint.request_body_schema:
            body_type = self._schema_to_type_hint(endpoint.request_body_schema, 'python')
            params.append(f"data: Optional[{body_type}] = None")
        
        params.append("**kwargs")
        
        response_type = 'Dict[str, Any]'
        if 200 in endpoint.response_schemas:
            response_type = self._schema_to_type_hint(endpoint.response_schemas[200], 'python')
        
        lines.append(f"    def {method_name}({', '.join(params)}) -> {response_type}:")
        
        lines.append(f'        """')
        lines.append(f'        {endpoint.method} {endpoint.path_pattern}')
        
        if endpoint.path_params:
            lines.append(f'        ')
            lines.append(f'        Path Parameters:')
            for param in sorted(endpoint.path_params):
                lines.append(f'            - {param}: str')
        
        if endpoint.query_params:
            lines.append(f'        ')
            lines.append(f'        Query Parameters:')
            for param, param_type in endpoint.query_params.items():
                lines.append(f'            - {param}: {param_type}')
        
        if endpoint.request_body_schema:
            lines.append(f'        ')
            lines.append(f'        Request Body:')
            lines.append(f'            {self._schema_to_type_hint(endpoint.request_body_schema, "python")}')
        
        lines.append(f'        """')
        
        path = endpoint.path_pattern
        for param in endpoint.path_params:
            param_snake = self._to_snake_case(param)
            path = path.replace(f"{{{param}}}", f"{{quote(str({param_snake}))}}")
        
        lines.append(f'        path = f"{path}"')
        lines.append(f'        url = urljoin(self.base_url, path)')
        
        if endpoint.query_params:
            lines.append(f'        ')
            lines.append(f'        params = {{}}')
            for param in endpoint.query_params:
                param_snake = self._to_snake_case(param)
                lines.append(f'        if {param_snake} is not None:')
                lines.append(f'            params["{param}"] = {param_snake}')
        
        lines.append(f'        ')
        
        request_args = ['url']
        
        if endpoint.query_params:
            request_args.append('params=params')
        
        if endpoint.request_body_schema:
            if endpoint.request_body_schema.get('type') == 'object':
                lines.append(f'        if data and isinstance(data, dict):')
                lines.append(f'            json_data = data')
                lines.append(f'        elif data:')
                lines.append(f'            json_data = data if isinstance(data, dict) else vars(data)')
                lines.append(f'        else:')
                lines.append(f'            json_data = None')
                request_args.append('json=json_data')
            else:
                request_args.append('json=data')
        
        request_args.append('**kwargs')
        
        method_lower = endpoint.method.lower()
        lines.append(f'        response = self.session.{method_lower}({", ".join(request_args)})')
        lines.append(f'        response.raise_for_status()')
        lines.append(f'        return response.json() if response.content else {{}}')
        lines.append(f'    ')
        
        return lines
    
    def _generate_requirements(self, output_dir: str):
        requirements = [
            "requests>=2.28.0",
            "typing-extensions>=4.0.0"
        ]
        
        with open(f"{output_dir}/requirements.txt", 'w') as f:
            f.write('\n'.join(requirements))
    
    def _generate_readme(self, output_dir: str):
        readme = f"""# {self.class_name} Python SDK

Auto-generated Python SDK for {self.api_name} API.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from {self._to_snake_case(self.api_name)}_client import {self.class_name}Client

# Initialize the client
client = {self.class_name}Client(base_url="{self.base_url}")

# Set authentication if needed
client.set_auth_token("your-token-here")

# Make API calls
"""
        
        example_method = None
        for endpoint_key, endpoint in self.endpoints.items():
            if endpoint.method == 'GET' and not endpoint.path_params:
                example_method = self._path_to_method_name(endpoint.method, endpoint.path_pattern)
                readme += f"response = client.{example_method}()\n"
                readme += f"print(response)\n"
                break
        
        readme += """```

## Available Methods

"""
        
        for endpoint_key, endpoint in self.endpoints.items():
            method_name = self._path_to_method_name(endpoint.method, endpoint.path_pattern)
            readme += f"- `{method_name}()` - {endpoint.method} {endpoint.path_pattern}\n"
        
        readme += """

## Generated from Network Traffic

This SDK was automatically generated by analyzing API network traffic patterns.
"""
        
        with open(f"{output_dir}/README.md", 'w') as f:
            f.write(readme)