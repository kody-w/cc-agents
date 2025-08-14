import json
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs
from collections import defaultdict
import hashlib


@dataclass
class APIEndpoint:
    method: str
    path_pattern: str
    path_params: Set[str] = field(default_factory=set)
    query_params: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, Any] = field(default_factory=dict)
    request_body_schema: Dict[str, Any] = field(default_factory=dict)
    response_schemas: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    

class TrafficParser:
    def __init__(self):
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.base_url = None
        
    def parse_har_file(self, har_file_path: str) -> Dict[str, APIEndpoint]:
        with open(har_file_path, 'r') as f:
            har_data = json.load(f)
        
        for entry in har_data['log']['entries']:
            self._process_entry(entry)
        
        return self.endpoints
    
    def parse_raw_traffic(self, traffic_data: List[Dict[str, Any]]) -> Dict[str, APIEndpoint]:
        for request_response in traffic_data:
            self._process_raw_request_response(request_response)
        
        return self.endpoints
    
    def _process_entry(self, entry: Dict[str, Any]):
        request = entry['request']
        response = entry['response']
        
        url = request['url']
        method = request['method']
        
        parsed_url = urlparse(url)
        if not self.base_url:
            self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        path_pattern, path_params = self._extract_path_pattern(path)
        
        endpoint_key = f"{method}:{path_pattern}"
        
        if endpoint_key not in self.endpoints:
            self.endpoints[endpoint_key] = APIEndpoint(
                method=method,
                path_pattern=path_pattern,
                path_params=path_params
            )
        
        endpoint = self.endpoints[endpoint_key]
        
        for param, values in query_params.items():
            if param not in endpoint.query_params:
                endpoint.query_params[param] = self._infer_type(values[0])
        
        headers = {h['name']: h['value'] for h in request.get('headers', [])}
        for header, value in headers.items():
            if header.lower() not in ['cookie', 'authorization', 'x-request-id']:
                if header not in endpoint.headers:
                    endpoint.headers[header] = self._infer_type(value)
        
        if request.get('postData'):
            body_text = request['postData'].get('text', '')
            if body_text:
                try:
                    body_data = json.loads(body_text)
                    self._merge_schema(endpoint.request_body_schema, self._extract_schema(body_data))
                except json.JSONDecodeError:
                    pass
        
        status = response['status']
        if response.get('content', {}).get('text'):
            try:
                response_data = json.loads(response['content']['text'])
                if status not in endpoint.response_schemas:
                    endpoint.response_schemas[status] = {}
                self._merge_schema(endpoint.response_schemas[status], self._extract_schema(response_data))
            except json.JSONDecodeError:
                pass
        
        endpoint.examples.append({
            'request': {
                'url': url,
                'method': method,
                'headers': headers,
                'body': request.get('postData', {}).get('text')
            },
            'response': {
                'status': status,
                'body': response.get('content', {}).get('text')
            }
        })
    
    def _extract_path_pattern(self, path: str) -> Tuple[str, Set[str]]:
        segments = path.split('/')
        pattern_segments = []
        path_params = set()
        
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        
        for segment in segments:
            if not segment:
                pattern_segments.append(segment)
                continue
            
            if segment.isdigit():
                param_name = 'id'
                pattern_segments.append(f'{{{param_name}}}')
                path_params.add(param_name)
            elif re.match(uuid_pattern, segment.lower()):
                param_name = 'uuid'
                pattern_segments.append(f'{{{param_name}}}')
                path_params.add(param_name)
            elif re.match(r'^[0-9a-f]{24}$', segment):
                param_name = 'objectId'
                pattern_segments.append(f'{{{param_name}}}')
                path_params.add(param_name)
            elif any(char.isdigit() for char in segment) and len(segment) > 5:
                param_name = self._generate_param_name(segments, segments.index(segment))
                pattern_segments.append(f'{{{param_name}}}')
                path_params.add(param_name)
            else:
                pattern_segments.append(segment)
        
        return '/'.join(pattern_segments), path_params
    
    def _generate_param_name(self, segments: List[str], index: int) -> str:
        if index > 0:
            prev_segment = segments[index - 1]
            if prev_segment and not prev_segment.startswith('{'):
                return f"{prev_segment}Id"
        if index < len(segments) - 1:
            next_segment = segments[index + 1]
            if next_segment and not next_segment.startswith('{'):
                return f"{next_segment}Id"
        return 'id'
    
    def _infer_type(self, value: Any) -> str:
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'number'
        elif isinstance(value, str):
            if value.lower() in ['true', 'false']:
                return 'boolean'
            try:
                int(value)
                return 'integer'
            except ValueError:
                try:
                    float(value)
                    return 'number'
                except ValueError:
                    return 'string'
        elif isinstance(value, list):
            return 'array'
        elif isinstance(value, dict):
            return 'object'
        else:
            return 'any'
    
    def _extract_schema(self, data: Any, depth: int = 0) -> Dict[str, Any]:
        if depth > 10:
            return {'type': 'any'}
        
        if data is None:
            return {'type': 'null', 'nullable': True}
        elif isinstance(data, bool):
            return {'type': 'boolean', 'example': data}
        elif isinstance(data, int):
            return {'type': 'integer', 'example': data}
        elif isinstance(data, float):
            return {'type': 'number', 'example': data}
        elif isinstance(data, str):
            schema = {'type': 'string', 'example': data[:100] if len(data) > 100 else data}
            if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', data):
                schema['format'] = 'date-time'
            elif re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data):
                schema['format'] = 'email'
            elif re.match(r'^https?://', data):
                schema['format'] = 'uri'
            return schema
        elif isinstance(data, list):
            if not data:
                return {'type': 'array', 'items': {'type': 'any'}}
            
            item_schemas = [self._extract_schema(item, depth + 1) for item in data[:10]]
            merged_schema = item_schemas[0] if item_schemas else {'type': 'any'}
            for schema in item_schemas[1:]:
                merged_schema = self._merge_schemas(merged_schema, schema)
            
            return {'type': 'array', 'items': merged_schema}
        elif isinstance(data, dict):
            properties = {}
            required = []
            
            for key, value in data.items():
                properties[key] = self._extract_schema(value, depth + 1)
                if value is not None:
                    required.append(key)
            
            return {
                'type': 'object',
                'properties': properties,
                'required': required
            }
        else:
            return {'type': 'any'}
    
    def _merge_schemas(self, schema1: Dict[str, Any], schema2: Dict[str, Any]) -> Dict[str, Any]:
        if schema1.get('type') != schema2.get('type'):
            return {'type': 'any'}
        
        merged = {'type': schema1['type']}
        
        if schema1['type'] == 'object':
            merged['properties'] = {}
            all_props = set(schema1.get('properties', {}).keys()) | set(schema2.get('properties', {}).keys())
            
            for prop in all_props:
                if prop in schema1.get('properties', {}) and prop in schema2.get('properties', {}):
                    merged['properties'][prop] = self._merge_schemas(
                        schema1['properties'][prop],
                        schema2['properties'][prop]
                    )
                elif prop in schema1.get('properties', {}):
                    merged['properties'][prop] = schema1['properties'][prop]
                    merged['properties'][prop]['nullable'] = True
                else:
                    merged['properties'][prop] = schema2['properties'][prop]
                    merged['properties'][prop]['nullable'] = True
            
            req1 = set(schema1.get('required', []))
            req2 = set(schema2.get('required', []))
            merged['required'] = list(req1 & req2)
        
        elif schema1['type'] == 'array':
            if 'items' in schema1 and 'items' in schema2:
                merged['items'] = self._merge_schemas(schema1['items'], schema2['items'])
            else:
                merged['items'] = schema1.get('items', {'type': 'any'})
        
        return merged
    
    def _merge_schema(self, target: Dict[str, Any], source: Dict[str, Any]):
        if not target:
            target.update(source)
        else:
            merged = self._merge_schemas(target, source)
            target.clear()
            target.update(merged)
    
    def _process_raw_request_response(self, data: Dict[str, Any]):
        request = data.get('request', {})
        response = data.get('response', {})
        
        url = request.get('url', '')
        method = request.get('method', 'GET')
        
        parsed_url = urlparse(url)
        if not self.base_url:
            self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        path_pattern, path_params = self._extract_path_pattern(path)
        
        endpoint_key = f"{method}:{path_pattern}"
        
        if endpoint_key not in self.endpoints:
            self.endpoints[endpoint_key] = APIEndpoint(
                method=method,
                path_pattern=path_pattern,
                path_params=path_params
            )
        
        endpoint = self.endpoints[endpoint_key]
        
        for param, values in query_params.items():
            if param not in endpoint.query_params:
                endpoint.query_params[param] = self._infer_type(values[0])
        
        headers = request.get('headers', {})
        for header, value in headers.items():
            if header.lower() not in ['cookie', 'authorization', 'x-request-id']:
                if header not in endpoint.headers:
                    endpoint.headers[header] = self._infer_type(value)
        
        if request.get('body'):
            try:
                body_data = json.loads(request['body']) if isinstance(request['body'], str) else request['body']
                self._merge_schema(endpoint.request_body_schema, self._extract_schema(body_data))
            except (json.JSONDecodeError, TypeError):
                pass
        
        status = response.get('status', 200)
        if response.get('body'):
            try:
                response_data = json.loads(response['body']) if isinstance(response['body'], str) else response['body']
                if status not in endpoint.response_schemas:
                    endpoint.response_schemas[status] = {}
                self._merge_schema(endpoint.response_schemas[status], self._extract_schema(response_data))
            except (json.JSONDecodeError, TypeError):
                pass
        
        endpoint.examples.append({
            'request': request,
            'response': response
        })