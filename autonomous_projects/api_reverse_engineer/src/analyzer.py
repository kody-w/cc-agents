"""
Request/Response analyzer for pattern detection and type inference.
"""

import json
import re
from typing import Dict, List, Any, Optional, Set, Union
from urllib.parse import urlparse, parse_qs
from collections import defaultdict, Counter
import statistics
import logging

from .types import (
    APICall, APISpec, Endpoint, Parameter, ResponseSchema, 
    HTTPMethod, ParameterType, AuthType, AuthPattern, RateLimit
)


class TypeInferencer:
    """Infer types from JSON values."""
    
    @staticmethod
    def infer_type(value: Any) -> ParameterType:
        """Infer the parameter type from a value."""
        if value is None:
            return ParameterType.NULL
        elif isinstance(value, bool):
            return ParameterType.BOOLEAN
        elif isinstance(value, int):
            return ParameterType.INTEGER
        elif isinstance(value, float):
            return ParameterType.FLOAT
        elif isinstance(value, str):
            return ParameterType.STRING
        elif isinstance(value, list):
            return ParameterType.ARRAY
        elif isinstance(value, dict):
            return ParameterType.OBJECT
        else:
            return ParameterType.STRING
            
    @staticmethod
    def infer_schema(data: Any) -> Dict[str, Any]:
        """Infer a JSON schema from data."""
        if data is None:
            return {"type": "null"}
        elif isinstance(data, bool):
            return {"type": "boolean"}
        elif isinstance(data, int):
            return {"type": "integer"}
        elif isinstance(data, float):
            return {"type": "number"}
        elif isinstance(data, str):
            return {"type": "string"}
        elif isinstance(data, list):
            if not data:
                return {"type": "array", "items": {}}
            # Infer type from first item (could be improved)
            item_schema = TypeInferencer.infer_schema(data[0])
            return {"type": "array", "items": item_schema}
        elif isinstance(data, dict):
            properties = {}
            for key, value in data.items():
                properties[key] = TypeInferencer.infer_schema(value)
            return {"type": "object", "properties": properties}
        else:
            return {"type": "string"}


class PatternDetector:
    """Detect patterns in API calls."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def detect_path_patterns(self, calls: List[APICall]) -> Dict[str, List[str]]:
        """Detect path patterns and group similar endpoints."""
        path_groups = defaultdict(list)
        
        for call in calls:
            parsed_url = urlparse(call.request.url)
            path = parsed_url.path
            
            # Normalize path by replacing numeric IDs with placeholders
            normalized_path = self._normalize_path(path)
            path_groups[normalized_path].append(path)
            
        return dict(path_groups)
        
    def _normalize_path(self, path: str) -> str:
        """Normalize a path by replacing IDs with placeholders."""
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        
        # Replace UUIDs
        uuid_pattern = r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        path = re.sub(uuid_pattern, '/{id}', path, flags=re.IGNORECASE)
        
        # Replace other common ID patterns
        path = re.sub(r'/[a-zA-Z0-9_-]{20,}', '/{id}', path)
        
        return path
        
    def detect_auth_patterns(self, calls: List[APICall]) -> List[AuthPattern]:
        """Detect authentication patterns from captured calls."""
        auth_patterns = []
        
        # Track potential auth headers and tokens
        auth_headers = defaultdict(set)
        bearer_tokens = set()
        api_keys = set()
        
        for call in calls:
            headers = call.request.headers
            
            # Check for common auth headers
            for header, value in headers.items():
                header_lower = header.lower()
                
                if header_lower == 'authorization':
                    if value.startswith('Bearer '):
                        bearer_tokens.add(value[7:])
                    elif value.startswith('Basic '):
                        auth_patterns.append(AuthPattern(
                            type=AuthType.BASIC_AUTH,
                            header_name='Authorization',
                            token_prefix='Basic'
                        ))
                elif header_lower in ['x-api-key', 'apikey', 'api-key']:
                    api_keys.add(value)
                    auth_headers[header].add(value)
                elif 'token' in header_lower or 'auth' in header_lower:
                    auth_headers[header].add(value)
                    
        # Create auth patterns
        if bearer_tokens:
            auth_patterns.append(AuthPattern(
                type=AuthType.BEARER_TOKEN,
                header_name='Authorization',
                token_prefix='Bearer',
                examples=list(bearer_tokens)[:3]  # Keep only first 3 examples
            ))
            
        if api_keys:
            for header, values in auth_headers.items():
                if any(key in api_keys for key in values):
                    auth_patterns.append(AuthPattern(
                        type=AuthType.API_KEY,
                        header_name=header,
                        examples=list(values)[:3]
                    ))
                    
        return auth_patterns
        
    def detect_rate_limits(self, calls: List[APICall]) -> Optional[RateLimit]:
        """Detect rate limiting from response headers."""
        rate_limit_headers = {}
        
        for call in calls:
            headers = call.response.headers
            
            for header, value in headers.items():
                header_lower = header.lower()
                
                if 'rate-limit' in header_lower or 'ratelimit' in header_lower:
                    rate_limit_headers[header] = value
                elif header_lower in ['x-ratelimit-remaining', 'x-ratelimit-limit']:
                    rate_limit_headers[header] = value
                    
        if rate_limit_headers:
            return RateLimit(headers=rate_limit_headers)
            
        return None


class RequestAnalyzer:
    """Main analyzer for API requests and responses."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.type_inferencer = TypeInferencer()
        self.pattern_detector = PatternDetector()
        
    def analyze_calls(self, calls: List[APICall]) -> APISpec:
        """Analyze a list of API calls and generate an API specification."""
        if not calls:
            raise ValueError("No API calls to analyze")
            
        self.logger.info(f"Analyzing {len(calls)} API calls")
        
        # Group calls by endpoint
        endpoint_groups = self._group_by_endpoint(calls)
        
        # Analyze each endpoint
        endpoints = []
        for endpoint_key, endpoint_calls in endpoint_groups.items():
            endpoint = self._analyze_endpoint(endpoint_key, endpoint_calls)
            endpoints.append(endpoint)
            
        # Detect global patterns
        auth_patterns = self.pattern_detector.detect_auth_patterns(calls)
        rate_limits = self.pattern_detector.detect_rate_limits(calls)
        
        # Determine base URL
        base_url = self._determine_base_url(calls)
        
        # Create API spec
        api_spec = APISpec(
            base_url=base_url,
            title="Generated API",
            endpoints=endpoints,
            auth_patterns=auth_patterns,
            rate_limits=rate_limits
        )
        
        self.logger.info(f"Generated API spec with {len(endpoints)} endpoints")
        return api_spec
        
    def _group_by_endpoint(self, calls: List[APICall]) -> Dict[str, List[APICall]]:
        """Group API calls by endpoint (method + normalized path)."""
        groups = defaultdict(list)
        
        for call in calls:
            parsed_url = urlparse(call.request.url)
            path = parsed_url.path
            method = call.request.method
            
            # Normalize path
            normalized_path = self.pattern_detector._normalize_path(path)
            endpoint_key = f"{method} {normalized_path}"
            
            groups[endpoint_key].append(call)
            
        return dict(groups)
        
    def _analyze_endpoint(self, endpoint_key: str, calls: List[APICall]) -> Endpoint:
        """Analyze a single endpoint from multiple calls."""
        method_str, path = endpoint_key.split(' ', 1)
        method = HTTPMethod(method_str)
        
        # Analyze parameters
        path_params = self._analyze_path_parameters(path, calls)
        query_params = self._analyze_query_parameters(calls)
        headers = self._analyze_headers(calls)
        
        # Analyze request body
        request_body = self._analyze_request_body(calls)
        
        # Analyze responses
        responses = self._analyze_responses(calls)
        
        # Detect auth requirement
        auth_required = self._detect_auth_requirement(calls)
        
        # Generate summary and description
        summary = self._generate_summary(method, path, calls)
        
        return Endpoint(
            path=path,
            method=method,
            summary=summary,
            parameters=path_params,
            query_params=query_params,
            headers=headers,
            request_body=request_body,
            responses=responses,
            auth_required=auth_required
        )
        
    def _analyze_path_parameters(self, path: str, calls: List[APICall]) -> List[Parameter]:
        """Analyze path parameters from the endpoint path."""
        parameters = []
        
        # Find {id} placeholders in path
        param_matches = re.findall(r'\{(\w+)\}', path)
        
        for param_name in param_matches:
            # For now, assume all path params are strings
            # Could be improved by analyzing actual values
            parameter = Parameter(
                name=param_name,
                type=ParameterType.STRING,
                required=True,
                description=f"Path parameter: {param_name}"
            )
            parameters.append(parameter)
            
        return parameters
        
    def _analyze_query_parameters(self, calls: List[APICall]) -> List[Parameter]:
        """Analyze query parameters from API calls."""
        param_stats = defaultdict(lambda: {
            'values': [],
            'types': Counter(),
            'required': 0,
            'total': 0
        })
        
        for call in calls:
            query_params = call.request.query_params
            
            # Track which params appear in this call
            call_params = set(query_params.keys())
            
            # Update stats for all parameters we've seen
            for param_name in param_stats:
                param_stats[param_name]['total'] += 1
                if param_name in call_params:
                    param_stats[param_name]['required'] += 1
                    
            # Add new parameters from this call
            for param_name, value in query_params.items():
                stats = param_stats[param_name]
                stats['values'].append(value)
                stats['types'][self.type_inferencer.infer_type(value)] += 1
                stats['total'] += 1
                stats['required'] += 1
                
        # Convert stats to parameters
        parameters = []
        for param_name, stats in param_stats.items():
            # Determine most common type
            most_common_type = stats['types'].most_common(1)[0][0]
            
            # Determine if required (appears in > 50% of calls)
            required = stats['required'] / len(calls) > 0.5
            
            # Get example value
            example = stats['values'][0] if stats['values'] else None
            
            parameter = Parameter(
                name=param_name,
                type=most_common_type,
                required=required,
                example=example,
                description=f"Query parameter: {param_name}"
            )
            parameters.append(parameter)
            
        return parameters
        
    def _analyze_headers(self, calls: List[APICall]) -> List[Parameter]:
        """Analyze common headers that might be required."""
        header_stats = defaultdict(lambda: {'count': 0, 'values': set()})
        
        for call in calls:
            for header, value in call.request.headers.items():
                # Skip standard HTTP headers
                if header.lower() in ['host', 'user-agent', 'accept', 'content-length']:
                    continue
                    
                header_stats[header]['count'] += 1
                header_stats[header]['values'].add(value)
                
        # Only include headers that appear in most calls
        parameters = []
        for header, stats in header_stats.items():
            if stats['count'] / len(calls) > 0.8:  # Appears in 80% of calls
                parameter = Parameter(
                    name=header,
                    type=ParameterType.STRING,
                    required=True,
                    description=f"Required header: {header}"
                )
                parameters.append(parameter)
                
        return parameters
        
    def _analyze_request_body(self, calls: List[APICall]) -> Optional[Dict[str, Any]]:
        """Analyze request body structure."""
        bodies = []
        
        for call in calls:
            if call.request.body:
                try:
                    # Try to parse as JSON
                    body_data = json.loads(call.request.body)
                    bodies.append(body_data)
                except json.JSONDecodeError:
                    # Handle non-JSON bodies
                    continue
                    
        if not bodies:
            return None
            
        # Infer schema from first body (could be improved)
        return self.type_inferencer.infer_schema(bodies[0])
        
    def _analyze_responses(self, calls: List[APICall]) -> List[ResponseSchema]:
        """Analyze response structures."""
        response_groups = defaultdict(list)
        
        # Group by status code and content type
        for call in calls:
            key = (call.response.status_code, call.response.content_type or 'unknown')
            response_groups[key].append(call.response)
            
        responses = []
        for (status_code, content_type), response_list in response_groups.items():
            # Analyze response bodies
            schema = None
            examples = []
            
            for response in response_list:
                if response.body:
                    try:
                        body_data = json.loads(response.body)
                        examples.append(body_data)
                        if schema is None:
                            schema = self.type_inferencer.infer_schema(body_data)
                    except json.JSONDecodeError:
                        continue
                        
            response_schema = ResponseSchema(
                status_code=status_code,
                content_type=content_type,
                schema=schema or {},
                examples=examples[:3]  # Keep only first 3 examples
            )
            responses.append(response_schema)
            
        return responses
        
    def _detect_auth_requirement(self, calls: List[APICall]) -> bool:
        """Detect if authentication is required for this endpoint."""
        auth_headers = ['authorization', 'x-api-key', 'apikey', 'api-key']
        
        for call in calls:
            headers = {k.lower(): v for k, v in call.request.headers.items()}
            if any(auth_header in headers for auth_header in auth_headers):
                return True
                
        return False
        
    def _generate_summary(self, method: HTTPMethod, path: str, calls: List[APICall]) -> str:
        """Generate a summary for the endpoint."""
        operation_map = {
            HTTPMethod.GET: "Get",
            HTTPMethod.POST: "Create",
            HTTPMethod.PUT: "Update",
            HTTPMethod.DELETE: "Delete",
            HTTPMethod.PATCH: "Partially update"
        }
        
        operation = operation_map.get(method, method.value)
        
        # Extract resource name from path
        path_parts = [part for part in path.split('/') if part and part != '{id}']
        resource = path_parts[-1] if path_parts else "resource"
        
        return f"{operation} {resource}"
        
    def _determine_base_url(self, calls: List[APICall]) -> str:
        """Determine the base URL from captured calls."""
        if not calls:
            return "https://api.example.com"
            
        # Use the first call to determine base URL
        first_url = calls[0].request.url
        parsed = urlparse(first_url)
        
        return f"{parsed.scheme}://{parsed.netloc}"