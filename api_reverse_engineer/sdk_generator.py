import os
import re
from typing import Dict, List, Any
from dataclasses import dataclass
from traffic_parser import APIEndpoint


class SDKGenerator:
    def __init__(self, api_name: str, base_url: str, endpoints: Dict[str, APIEndpoint]):
        self.api_name = api_name
        self.base_url = base_url
        self.endpoints = endpoints
        self.class_name = self._to_class_name(api_name)
    
    def _to_class_name(self, name: str) -> str:
        return ''.join(word.capitalize() for word in re.split(r'[_\-\s]+', name))
    
    def _to_snake_case(self, name: str) -> str:
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _to_camel_case(self, name: str) -> str:
        components = name.split('_')
        return components[0] + ''.join(x.capitalize() for x in components[1:])
    
    def _path_to_method_name(self, method: str, path: str) -> str:
        path_parts = [p for p in path.split('/') if p and not p.startswith('{')]
        
        if not path_parts:
            return method.lower()
        
        if method == 'GET':
            if path_parts[-1].endswith('s'):
                return f"list_{self._to_snake_case(path_parts[-1])}"
            else:
                return f"get_{self._to_snake_case(path_parts[-1])}"
        elif method == 'POST':
            return f"create_{self._to_snake_case(path_parts[-1].rstrip('s'))}"
        elif method == 'PUT':
            return f"update_{self._to_snake_case(path_parts[-1].rstrip('s'))}"
        elif method == 'PATCH':
            return f"patch_{self._to_snake_case(path_parts[-1].rstrip('s'))}"
        elif method == 'DELETE':
            return f"delete_{self._to_snake_case(path_parts[-1].rstrip('s'))}"
        else:
            return f"{method.lower()}_{self._to_snake_case('_'.join(path_parts))}"
    
    def _schema_to_type_hint(self, schema: Dict[str, Any], lang: str) -> str:
        if not schema:
            return 'Any' if lang == 'python' else 'any' if lang == 'typescript' else 'interface{}'
        
        schema_type = schema.get('type', 'any')
        
        if lang == 'python':
            type_map = {
                'string': 'str',
                'integer': 'int',
                'number': 'float',
                'boolean': 'bool',
                'null': 'None',
                'array': 'List[Any]',
                'object': 'Dict[str, Any]',
                'any': 'Any'
            }
            base_type = type_map.get(schema_type, 'Any')
            
            if schema_type == 'array' and 'items' in schema:
                item_type = self._schema_to_type_hint(schema['items'], lang)
                base_type = f"List[{item_type}]"
            
            if schema.get('nullable'):
                base_type = f"Optional[{base_type}]"
            
            return base_type
        
        elif lang == 'typescript':
            type_map = {
                'string': 'string',
                'integer': 'number',
                'number': 'number',
                'boolean': 'boolean',
                'null': 'null',
                'array': 'any[]',
                'object': 'Record<string, any>',
                'any': 'any'
            }
            base_type = type_map.get(schema_type, 'any')
            
            if schema_type == 'array' and 'items' in schema:
                item_type = self._schema_to_type_hint(schema['items'], lang)
                base_type = f"{item_type}[]"
            
            if schema.get('nullable'):
                base_type = f"{base_type} | null"
            
            return base_type
        
        elif lang == 'go':
            type_map = {
                'string': 'string',
                'integer': 'int',
                'number': 'float64',
                'boolean': 'bool',
                'null': 'interface{}',
                'array': '[]interface{}',
                'object': 'map[string]interface{}',
                'any': 'interface{}'
            }
            base_type = type_map.get(schema_type, 'interface{}')
            
            if schema_type == 'array' and 'items' in schema:
                item_type = self._schema_to_type_hint(schema['items'], lang)
                base_type = f"[]{item_type}"
            
            if schema.get('nullable'):
                base_type = f"*{base_type}"
            
            return base_type
        
        return 'any'
    
    def _generate_interface_from_schema(self, name: str, schema: Dict[str, Any], lang: str, indent: int = 0) -> str:
        if schema.get('type') != 'object' or not schema.get('properties'):
            return ''
        
        indent_str = '  ' * indent
        
        if lang == 'typescript':
            lines = [f"{indent_str}interface {name} {{"]
            for prop_name, prop_schema in schema['properties'].items():
                prop_type = self._schema_to_type_hint(prop_schema, lang)
                optional = '?' if prop_schema.get('nullable') or prop_name not in schema.get('required', []) else ''
                lines.append(f"{indent_str}  {prop_name}{optional}: {prop_type};")
            lines.append(f"{indent_str}}}")
            return '\n'.join(lines)
        
        elif lang == 'python':
            lines = [f"{indent_str}class {name}:"]
            if not schema['properties']:
                lines.append(f"{indent_str}    pass")
            else:
                for prop_name, prop_schema in schema['properties'].items():
                    prop_type = self._schema_to_type_hint(prop_schema, lang)
                    lines.append(f"{indent_str}    {prop_name}: {prop_type}")
            return '\n'.join(lines)
        
        elif lang == 'go':
            lines = [f"{indent_str}type {name} struct {{"]
            for prop_name, prop_schema in schema['properties'].items():
                prop_type = self._schema_to_type_hint(prop_schema, lang)
                go_name = ''.join(word.capitalize() for word in prop_name.split('_'))
                lines.append(f'{indent_str}    {go_name} {prop_type} `json:"{prop_name}"`')
            lines.append(f"{indent_str}}}")
            return '\n'.join(lines)
        
        return ''