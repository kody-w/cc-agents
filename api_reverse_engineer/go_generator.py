from typing import Dict, List, Any
from sdk_generator import SDKGenerator
from traffic_parser import APIEndpoint


class GoSDKGenerator(SDKGenerator):
    def generate(self, output_dir: str = 'generated_sdks/go') -> str:
        package_name = self._to_snake_case(self.api_name).replace('-', '_')
        
        imports = [
            "package " + package_name,
            "",
            "import (",
            '\t"bytes"',
            '\t"encoding/json"',
            '\t"fmt"',
            '\t"io"',
            '\t"net/http"',
            '\t"net/url"',
            '\t"strings"',
            '\t"time"',
            ")",
            ""
        ]
        
        structs = []
        
        for endpoint_key, endpoint in self.endpoints.items():
            method_name = self._path_to_method_name(endpoint.method, endpoint.path_pattern)
            
            if endpoint.request_body_schema and endpoint.request_body_schema.get('type') == 'object':
                request_struct_name = self._to_class_name(method_name) + "Request"
                request_struct = self._generate_interface_from_schema(
                    request_struct_name,
                    endpoint.request_body_schema,
                    'go'
                )
                if request_struct and request_struct not in structs:
                    structs.append(request_struct)
            
            for status, response_schema in endpoint.response_schemas.items():
                if status == 200 and response_schema.get('type') == 'object':
                    response_struct_name = self._to_class_name(method_name) + "Response"
                    response_struct = self._generate_interface_from_schema(
                        response_struct_name,
                        response_schema,
                        'go'
                    )
                    if response_struct and response_struct not in structs:
                        structs.append(response_struct)
        
        client_struct = self._generate_go_client_struct()
        client_methods = self._generate_go_client_methods()
        
        content = '\n'.join(imports)
        
        if structs:
            content += "// Type Definitions\n"
            content += '\n\n'.join(structs) + '\n\n'
        
        content += "// Client Definition\n"
        content += client_struct + '\n\n'
        content += client_methods
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = f"{output_dir}/client.go"
        with open(output_file, 'w') as f:
            f.write(content)
        
        self._generate_go_mod(output_dir, package_name)
        self._generate_readme(output_dir)
        
        return output_file
    
    def _generate_go_client_struct(self) -> str:
        return f"""type {self.class_name}Client struct {{
\tBaseURL    string
\tHTTPClient *http.Client
\tHeaders    map[string]string
}}

// New{self.class_name}Client creates a new API client
func New{self.class_name}Client(baseURL string) *{self.class_name}Client {{
\tif baseURL == "" {{
\t\tbaseURL = "{self.base_url}"
\t}}
\treturn &{self.class_name}Client{{
\t\tBaseURL:    strings.TrimSuffix(baseURL, "/"),
\t\tHTTPClient: &http.Client{{Timeout: 30 * time.Second}},
\t\tHeaders:    make(map[string]string),
\t}}
}}

// SetAuthToken sets the authorization token
func (c *{self.class_name}Client) SetAuthToken(token string) {{
\tc.Headers["Authorization"] = fmt.Sprintf("Bearer %s", token)
}}

// SetHeader sets a custom header
func (c *{self.class_name}Client) SetHeader(key, value string) {{
\tc.Headers[key] = value
}}

// doRequest performs the HTTP request
func (c *{self.class_name}Client) doRequest(method, path string, params url.Values, body interface{{}}) ([]byte, error) {{
\tfullURL := c.BaseURL + path
\tif params != nil && len(params) > 0 {{
\t\tfullURL = fullURL + "?" + params.Encode()
\t}}
\t
\tvar bodyReader io.Reader
\tif body != nil {{
\t\tjsonBody, err := json.Marshal(body)
\t\tif err != nil {{
\t\t\treturn nil, err
\t\t}}
\t\tbodyReader = bytes.NewBuffer(jsonBody)
\t}}
\t
\treq, err := http.NewRequest(method, fullURL, bodyReader)
\tif err != nil {{
\t\treturn nil, err
\t}}
\t
\tif body != nil {{
\t\treq.Header.Set("Content-Type", "application/json")
\t}}
\t
\tfor key, value := range c.Headers {{
\t\treq.Header.Set(key, value)
\t}}
\t
\tresp, err := c.HTTPClient.Do(req)
\tif err != nil {{
\t\treturn nil, err
\t}}
\tdefer resp.Body.Close()
\t
\tresponseBody, err := io.ReadAll(resp.Body)
\tif err != nil {{
\t\treturn nil, err
\t}}
\t
\tif resp.StatusCode >= 400 {{
\t\treturn nil, fmt.Errorf("API error: status=%d, body=%s", resp.StatusCode, string(responseBody))
\t}}
\t
\treturn responseBody, nil
}}"""
    
    def _generate_go_client_methods(self) -> str:
        methods = []
        
        for endpoint_key, endpoint in self.endpoints.items():
            method_name = self._path_to_method_name(endpoint.method, endpoint.path_pattern)
            method_name_go = self._to_class_name(method_name)
            
            method_lines = self._generate_go_method(method_name_go, endpoint)
            methods.append('\n'.join(method_lines))
        
        return '\n\n'.join(methods)
    
    def _generate_go_method(self, method_name: str, endpoint: APIEndpoint) -> List[str]:
        lines = []
        
        params = []
        path_replacements = []
        
        for param in sorted(endpoint.path_params):
            param_go = self._to_camel_case(param)
            params.append(f"{param_go} string")
            path_replacements.append((f"{{{param}}}", param_go))
        
        if endpoint.query_params:
            for param, param_type in endpoint.query_params.items():
                param_go = self._to_camel_case(param)
                type_hint = self._schema_to_type_hint({'type': param_type}, 'go')
                params.append(f"{param_go} *{type_hint}")
        
        if endpoint.request_body_schema:
            body_type = self._schema_to_type_hint(endpoint.request_body_schema, 'go')
            if endpoint.request_body_schema.get('type') == 'object' and endpoint.request_body_schema.get('properties'):
                struct_name = self._to_class_name(self._path_to_method_name(endpoint.method, endpoint.path_pattern)) + "Request"
                params.append(f"data *{struct_name}")
            else:
                params.append(f"data {body_type}")
        
        response_type = "map[string]interface{}"
        if 200 in endpoint.response_schemas:
            if endpoint.response_schemas[200].get('type') == 'object' and endpoint.response_schemas[200].get('properties'):
                response_type = "*" + self._to_class_name(self._path_to_method_name(endpoint.method, endpoint.path_pattern)) + "Response"
            else:
                response_type = self._schema_to_type_hint(endpoint.response_schemas[200], 'go')
        
        param_str = ', '.join(params) if params else ''
        
        lines.append(f"// {method_name} performs {endpoint.method} {endpoint.path_pattern}")
        lines.append(f"func (c *{self.class_name}Client) {method_name}({param_str}) ({response_type}, error) {{")
        
        path = endpoint.path_pattern
        if path_replacements:
            lines.append(f"\tpath := `{path}`")
            for old, new in path_replacements:
                lines.append(f"\tpath = strings.Replace(path, \"{old}\", {new}, 1)")
        else:
            lines.append(f"\tpath := \"{path}\"")
        
        if endpoint.query_params:
            lines.append(f"\t")
            lines.append(f"\tparams := url.Values{{}}")
            for param, _ in endpoint.query_params.items():
                param_go = self._to_camel_case(param)
                lines.append(f"\tif {param_go} != nil {{")
                lines.append(f"\t\tparams.Set(\"{param}\", fmt.Sprintf(\"%v\", *{param_go}))")
                lines.append(f"\t}}")
        
        lines.append(f"\t")
        
        if endpoint.query_params:
            params_arg = "params"
        else:
            params_arg = "nil"
        
        if endpoint.request_body_schema:
            body_arg = "data"
        else:
            body_arg = "nil"
        
        lines.append(f"\tresponseBody, err := c.doRequest(\"{endpoint.method}\", path, {params_arg}, {body_arg})")
        lines.append(f"\tif err != nil {{")
        lines.append(f"\t\treturn nil, err")
        lines.append(f"\t}}")
        lines.append(f"\t")
        
        if response_type.startswith("*"):
            lines.append(f"\tvar result {response_type[1:]}")
            lines.append(f"\tif err := json.Unmarshal(responseBody, &result); err != nil {{")
            lines.append(f"\t\treturn nil, err")
            lines.append(f"\t}}")
            lines.append(f"\treturn &result, nil")
        elif response_type == "map[string]interface{}":
            lines.append(f"\tvar result {response_type}")
            lines.append(f"\tif err := json.Unmarshal(responseBody, &result); err != nil {{")
            lines.append(f"\t\treturn nil, err")
            lines.append(f"\t}}")
            lines.append(f"\treturn result, nil")
        else:
            lines.append(f"\tvar result {response_type}")
            lines.append(f"\tif err := json.Unmarshal(responseBody, &result); err != nil {{")
            lines.append(f"\t\tvar zero {response_type}")
            lines.append(f"\t\treturn zero, err")
            lines.append(f"\t}}")
            lines.append(f"\treturn result, nil")
        
        lines.append(f"}}")
        
        return lines
    
    def _generate_go_mod(self, output_dir: str, package_name: str):
        go_mod = f"""module github.com/example/{package_name}

go 1.20
"""
        
        with open(f"{output_dir}/go.mod", 'w') as f:
            f.write(go_mod)
    
    def _generate_readme(self, output_dir: str):
        package_name = self._to_snake_case(self.api_name).replace('-', '_')
        
        readme = f"""# {self.class_name} Go SDK

Auto-generated Go SDK for {self.api_name} API.

## Installation

```bash
go get github.com/example/{package_name}
```

## Usage

```go
package main

import (
    "fmt"
    "log"
    "{package_name}"
)

func main() {{
    // Initialize the client
    client := {package_name}.New{self.class_name}Client("{self.base_url}")
    
    // Set authentication if needed
    client.SetAuthToken("your-token-here")
    
    // Make API calls
"""
        
        example_method = None
        for endpoint_key, endpoint in self.endpoints.items():
            if endpoint.method == 'GET' and not endpoint.path_params:
                method_name = self._path_to_method_name(endpoint.method, endpoint.path_pattern)
                method_name_go = self._to_class_name(method_name)
                readme += f"    response, err := client.{method_name_go}()\n"
                readme += f"    if err != nil {{\n"
                readme += f"        log.Fatal(err)\n"
                readme += f"    }}\n"
                readme += f"    fmt.Printf(\"%+v\\n\", response)\n"
                break
        
        readme += """}}
```

## Available Methods

"""
        
        for endpoint_key, endpoint in self.endpoints.items():
            method_name = self._path_to_method_name(endpoint.method, endpoint.path_pattern)
            method_name_go = self._to_class_name(method_name)
            readme += f"- `{method_name_go}()` - {endpoint.method} {endpoint.path_pattern}\n"
        
        readme += """

## Generated from Network Traffic

This SDK was automatically generated by analyzing API network traffic patterns.
"""
        
        with open(f"{output_dir}/README.md", 'w') as f:
            f.write(readme)