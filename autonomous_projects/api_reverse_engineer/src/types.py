"""
Type definitions for the API reverse engineering tool.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum
import json


class HTTPMethod(Enum):
    """Supported HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthType(Enum):
    """Detected authentication types."""
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    OAUTH = "oauth"
    CUSTOM_HEADER = "custom_header"


class ParameterType(Enum):
    """Parameter types for API endpoints."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"


@dataclass
class Parameter:
    """Represents an API parameter."""
    name: str
    type: ParameterType
    required: bool = False
    description: Optional[str] = None
    example: Optional[Any] = None
    enum_values: Optional[List[Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None


@dataclass
class ResponseSchema:
    """Represents a response schema."""
    status_code: int
    content_type: str
    schema: Dict[str, Any]
    examples: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RateLimit:
    """Rate limiting information."""
    requests_per_minute: Optional[int] = None
    requests_per_hour: Optional[int] = None
    requests_per_day: Optional[int] = None
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class AuthPattern:
    """Authentication pattern information."""
    type: AuthType
    header_name: Optional[str] = None
    parameter_name: Optional[str] = None
    token_prefix: Optional[str] = None
    examples: List[str] = field(default_factory=list)


@dataclass
class Endpoint:
    """Represents an API endpoint."""
    path: str
    method: HTTPMethod
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: List[Parameter] = field(default_factory=list)
    query_params: List[Parameter] = field(default_factory=list)
    headers: List[Parameter] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: List[ResponseSchema] = field(default_factory=list)
    auth_required: bool = False
    rate_limit: Optional[RateLimit] = None
    examples: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class APISpec:
    """Complete API specification."""
    base_url: str
    title: str = "Generated API"
    version: str = "1.0.0"
    description: str = "API specification generated from network traffic"
    endpoints: List[Endpoint] = field(default_factory=list)
    auth_patterns: List[AuthPattern] = field(default_factory=list)
    global_headers: Dict[str, str] = field(default_factory=dict)
    rate_limits: Optional[RateLimit] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "base_url": self.base_url,
            "title": self.title,
            "version": self.version,
            "description": self.description,
            "endpoints": [
                {
                    "path": ep.path,
                    "method": ep.method.value,
                    "summary": ep.summary,
                    "description": ep.description,
                    "parameters": [
                        {
                            "name": p.name,
                            "type": p.type.value,
                            "required": p.required,
                            "description": p.description,
                            "example": p.example
                        } for p in ep.parameters
                    ],
                    "query_params": [
                        {
                            "name": p.name,
                            "type": p.type.value,
                            "required": p.required,
                            "description": p.description,
                            "example": p.example
                        } for p in ep.query_params
                    ],
                    "responses": [
                        {
                            "status_code": r.status_code,
                            "content_type": r.content_type,
                            "schema": r.schema
                        } for r in ep.responses
                    ]
                } for ep in self.endpoints
            ],
            "auth_patterns": [
                {
                    "type": auth.type.value,
                    "header_name": auth.header_name,
                    "parameter_name": auth.parameter_name,
                    "token_prefix": auth.token_prefix
                } for auth in self.auth_patterns
            ]
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class CapturedRequest:
    """Represents a captured HTTP request."""
    url: str
    method: str
    headers: Dict[str, str]
    query_params: Dict[str, Any]
    body: Optional[str] = None
    timestamp: Optional[float] = None


@dataclass
class CapturedResponse:
    """Represents a captured HTTP response."""
    status_code: int
    headers: Dict[str, str]
    body: Optional[str] = None
    content_type: Optional[str] = None
    timestamp: Optional[float] = None


@dataclass
class APICall:
    """Represents a complete API call (request + response)."""
    request: CapturedRequest
    response: CapturedResponse
    duration_ms: Optional[float] = None