"""
Tests for the request analyzer.
"""

import unittest
import json
from src.analyzer import RequestAnalyzer, TypeInferencer, PatternDetector
from src.types import (
    APICall, CapturedRequest, CapturedResponse, 
    HTTPMethod, ParameterType, AuthType
)


class TestTypeInferencer(unittest.TestCase):
    """Test type inference functionality."""
    
    def setUp(self):
        self.inferencer = TypeInferencer()
        
    def test_infer_basic_types(self):
        """Test inference of basic Python types."""
        self.assertEqual(self.inferencer.infer_type(None), ParameterType.NULL)
        self.assertEqual(self.inferencer.infer_type(True), ParameterType.BOOLEAN)
        self.assertEqual(self.inferencer.infer_type(42), ParameterType.INTEGER)
        self.assertEqual(self.inferencer.infer_type(3.14), ParameterType.FLOAT)
        self.assertEqual(self.inferencer.infer_type("hello"), ParameterType.STRING)
        self.assertEqual(self.inferencer.infer_type([1, 2, 3]), ParameterType.ARRAY)
        self.assertEqual(self.inferencer.infer_type({"key": "value"}), ParameterType.OBJECT)
        
    def test_infer_schema(self):
        """Test JSON schema inference."""
        # Test simple object
        data = {"name": "John", "age": 30, "active": True}
        schema = self.inferencer.infer_schema(data)
        
        self.assertEqual(schema["type"], "object")
        self.assertIn("properties", schema)
        self.assertEqual(schema["properties"]["name"]["type"], "string")
        self.assertEqual(schema["properties"]["age"]["type"], "integer")
        self.assertEqual(schema["properties"]["active"]["type"], "boolean")
        
        # Test array
        data = [{"id": 1}, {"id": 2}]
        schema = self.inferencer.infer_schema(data)
        
        self.assertEqual(schema["type"], "array")
        self.assertEqual(schema["items"]["type"], "object")
        
    def test_empty_collections(self):
        """Test schema inference for empty collections."""
        # Empty array
        schema = self.inferencer.infer_schema([])
        self.assertEqual(schema["type"], "array")
        self.assertEqual(schema["items"], {})
        
        # Empty object
        schema = self.inferencer.infer_schema({})
        self.assertEqual(schema["type"], "object")
        self.assertEqual(schema["properties"], {})


class TestPatternDetector(unittest.TestCase):
    """Test pattern detection functionality."""
    
    def setUp(self):
        self.detector = PatternDetector()
        
    def test_normalize_path(self):
        """Test path normalization."""
        # Test numeric ID replacement
        self.assertEqual(
            self.detector._normalize_path("/users/123/posts"),
            "/users/{id}/posts"
        )
        
        # Test UUID replacement
        self.assertEqual(
            self.detector._normalize_path("/users/550e8400-e29b-41d4-a716-446655440000"),
            "/users/{id}"
        )
        
        # Test multiple IDs
        self.assertEqual(
            self.detector._normalize_path("/users/123/posts/456"),
            "/users/{id}/posts/{id}"
        )
        
    def test_detect_auth_patterns(self):
        """Test authentication pattern detection."""
        # Create mock API calls with different auth patterns
        calls = []
        
        # Bearer token
        request1 = CapturedRequest(
            url="https://api.example.com/users",
            method="GET",
            headers={"Authorization": "Bearer abc123"},
            query_params={}
        )
        response1 = CapturedResponse(200, {}, '{"users": []}')
        calls.append(APICall(request1, response1))
        
        # API key
        request2 = CapturedRequest(
            url="https://api.example.com/data",
            method="GET",
            headers={"X-API-Key": "secret123"},
            query_params={}
        )
        response2 = CapturedResponse(200, {}, '{"data": []}')
        calls.append(APICall(request2, response2))
        
        patterns = self.detector.detect_auth_patterns(calls)
        
        # Should detect both patterns
        self.assertEqual(len(patterns), 2)
        
        # Check for bearer token pattern
        bearer_patterns = [p for p in patterns if p.type == AuthType.BEARER_TOKEN]
        self.assertEqual(len(bearer_patterns), 1)
        self.assertEqual(bearer_patterns[0].header_name, "Authorization")
        
        # Check for API key pattern
        api_key_patterns = [p for p in patterns if p.type == AuthType.API_KEY]
        self.assertEqual(len(api_key_patterns), 1)
        self.assertEqual(api_key_patterns[0].header_name, "X-API-Key")
        
    def test_detect_rate_limits(self):
        """Test rate limit detection."""
        calls = []
        
        request = CapturedRequest(
            url="https://api.example.com/data",
            method="GET",
            headers={},
            query_params={}
        )
        response = CapturedResponse(
            200, 
            {"X-RateLimit-Remaining": "99", "X-RateLimit-Limit": "100"}, 
            '{"data": []}'
        )
        calls.append(APICall(request, response))
        
        rate_limit = self.detector.detect_rate_limits(calls)
        
        self.assertIsNotNone(rate_limit)
        self.assertIn("X-RateLimit-Remaining", rate_limit.headers)
        self.assertIn("X-RateLimit-Limit", rate_limit.headers)


class TestRequestAnalyzer(unittest.TestCase):
    """Test the main request analyzer."""
    
    def setUp(self):
        self.analyzer = RequestAnalyzer()
        
    def create_sample_calls(self):
        """Create sample API calls for testing."""
        calls = []
        
        # GET /users
        request1 = CapturedRequest(
            url="https://api.example.com/users",
            method="GET",
            headers={"Authorization": "Bearer token123"},
            query_params={"limit": "10", "offset": "0"}
        )
        response1 = CapturedResponse(
            200,
            {"Content-Type": "application/json"},
            '{"users": [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]}'
        )
        calls.append(APICall(request1, response1))
        
        # GET /users/123
        request2 = CapturedRequest(
            url="https://api.example.com/users/123",
            method="GET",
            headers={"Authorization": "Bearer token123"},
            query_params={}
        )
        response2 = CapturedResponse(
            200,
            {"Content-Type": "application/json"},
            '{"id": 123, "name": "John Doe", "email": "john@example.com"}'
        )
        calls.append(APICall(request2, response2))
        
        # POST /users
        request3 = CapturedRequest(
            url="https://api.example.com/users",
            method="POST",
            headers={"Authorization": "Bearer token123", "Content-Type": "application/json"},
            query_params={},
            body='{"name": "New User", "email": "new@example.com"}'
        )
        response3 = CapturedResponse(
            201,
            {"Content-Type": "application/json"},
            '{"id": 124, "name": "New User", "email": "new@example.com"}'
        )
        calls.append(APICall(request3, response3))
        
        return calls
        
    def test_group_by_endpoint(self):
        """Test endpoint grouping."""
        calls = self.create_sample_calls()
        groups = self.analyzer._group_by_endpoint(calls)
        
        # Should have 3 different endpoints
        self.assertEqual(len(groups), 3)
        
        # Check endpoint keys
        keys = set(groups.keys())
        self.assertIn("GET /users", keys)
        self.assertIn("GET /users/{id}", keys)
        self.assertIn("POST /users", keys)
        
    def test_analyze_calls(self):
        """Test full call analysis."""
        calls = self.create_sample_calls()
        api_spec = self.analyzer.analyze_calls(calls)
        
        # Check basic properties
        self.assertEqual(api_spec.base_url, "https://api.example.com")
        self.assertEqual(len(api_spec.endpoints), 3)
        
        # Check authentication patterns
        self.assertEqual(len(api_spec.auth_patterns), 1)
        self.assertEqual(api_spec.auth_patterns[0].type, AuthType.BEARER_TOKEN)
        
        # Check endpoints
        endpoint_paths = [ep.path for ep in api_spec.endpoints]
        self.assertIn("/users", endpoint_paths)
        self.assertIn("/users/{id}", endpoint_paths)
        
        # Check methods
        get_endpoints = [ep for ep in api_spec.endpoints if ep.method == HTTPMethod.GET]
        post_endpoints = [ep for ep in api_spec.endpoints if ep.method == HTTPMethod.POST]
        
        self.assertEqual(len(get_endpoints), 2)
        self.assertEqual(len(post_endpoints), 1)
        
    def test_analyze_query_parameters(self):
        """Test query parameter analysis."""
        calls = self.create_sample_calls()
        
        # Get the GET /users calls
        get_users_calls = [call for call in calls if call.request.url.endswith("/users") and call.request.method == "GET"]
        
        params = self.analyzer._analyze_query_parameters(get_users_calls)
        
        # Should detect limit and offset parameters
        param_names = [p.name for p in params]
        self.assertIn("limit", param_names)
        self.assertIn("offset", param_names)
        
        # Check parameter properties
        limit_param = next(p for p in params if p.name == "limit")
        self.assertEqual(limit_param.type, ParameterType.STRING)
        self.assertEqual(limit_param.example, "10")
        
    def test_analyze_request_body(self):
        """Test request body analysis."""
        calls = self.create_sample_calls()
        
        # Get POST calls
        post_calls = [call for call in calls if call.request.method == "POST"]
        
        body_schema = self.analyzer._analyze_request_body(post_calls)
        
        self.assertIsNotNone(body_schema)
        self.assertEqual(body_schema["type"], "object")
        self.assertIn("properties", body_schema)
        self.assertIn("name", body_schema["properties"])
        self.assertIn("email", body_schema["properties"])
        
    def test_empty_calls_raises_error(self):
        """Test that empty calls list raises ValueError."""
        with self.assertRaises(ValueError):
            self.analyzer.analyze_calls([])


if __name__ == '__main__':
    unittest.main()