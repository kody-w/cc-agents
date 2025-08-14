"""
Tests for type definitions.
"""

import unittest
import json
from src.types import (
    APISpec, Endpoint, Parameter, ResponseSchema, AuthPattern,
    HTTPMethod, ParameterType, AuthType, CapturedRequest, 
    CapturedResponse, APICall
)


class TestTypes(unittest.TestCase):
    """Test type definitions and serialization."""
    
    def test_parameter_creation(self):
        """Test Parameter creation and properties."""
        param = Parameter(
            name="user_id",
            type=ParameterType.INTEGER,
            required=True,
            description="User ID",
            example=123
        )
        
        self.assertEqual(param.name, "user_id")
        self.assertEqual(param.type, ParameterType.INTEGER)
        self.assertTrue(param.required)
        self.assertEqual(param.description, "User ID")
        self.assertEqual(param.example, 123)
        
    def test_endpoint_creation(self):
        """Test Endpoint creation with parameters."""
        param = Parameter("id", ParameterType.STRING, required=True)
        endpoint = Endpoint(
            path="/users/{id}",
            method=HTTPMethod.GET,
            summary="Get user by ID",
            parameters=[param]
        )
        
        self.assertEqual(endpoint.path, "/users/{id}")
        self.assertEqual(endpoint.method, HTTPMethod.GET)
        self.assertEqual(endpoint.summary, "Get user by ID")
        self.assertEqual(len(endpoint.parameters), 1)
        self.assertEqual(endpoint.parameters[0].name, "id")
        
    def test_api_spec_serialization(self):
        """Test APISpec to_dict and to_json methods."""
        param = Parameter("id", ParameterType.STRING, required=True)
        endpoint = Endpoint("/users/{id}", HTTPMethod.GET, parameters=[param])
        
        api_spec = APISpec(
            base_url="https://api.example.com",
            title="Test API",
            endpoints=[endpoint]
        )
        
        # Test to_dict
        spec_dict = api_spec.to_dict()
        self.assertIsInstance(spec_dict, dict)
        self.assertEqual(spec_dict["base_url"], "https://api.example.com")
        self.assertEqual(spec_dict["title"], "Test API")
        self.assertEqual(len(spec_dict["endpoints"]), 1)
        
        # Test to_json
        spec_json = api_spec.to_json()
        self.assertIsInstance(spec_json, str)
        
        # Test that JSON is valid
        parsed_json = json.loads(spec_json)
        self.assertEqual(parsed_json["base_url"], "https://api.example.com")
        
    def test_api_call_creation(self):
        """Test APICall creation with request and response."""
        request = CapturedRequest(
            url="https://api.example.com/users/123",
            method="GET",
            headers={"Authorization": "Bearer token"},
            query_params={"include": "profile"}
        )
        
        response = CapturedResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body='{"id": 123, "name": "John Doe"}',
            content_type="application/json"
        )
        
        api_call = APICall(
            request=request,
            response=response,
            duration_ms=150.5
        )
        
        self.assertEqual(api_call.request.url, "https://api.example.com/users/123")
        self.assertEqual(api_call.response.status_code, 200)
        self.assertEqual(api_call.duration_ms, 150.5)
        
    def test_auth_pattern_creation(self):
        """Test AuthPattern creation."""
        auth_pattern = AuthPattern(
            type=AuthType.BEARER_TOKEN,
            header_name="Authorization",
            token_prefix="Bearer",
            examples=["Bearer abc123"]
        )
        
        self.assertEqual(auth_pattern.type, AuthType.BEARER_TOKEN)
        self.assertEqual(auth_pattern.header_name, "Authorization")
        self.assertEqual(auth_pattern.token_prefix, "Bearer")
        self.assertEqual(len(auth_pattern.examples), 1)
        
    def test_response_schema_creation(self):
        """Test ResponseSchema creation."""
        schema = ResponseSchema(
            status_code=200,
            content_type="application/json",
            schema={"type": "object", "properties": {"id": {"type": "integer"}}},
            examples=[{"id": 123}]
        )
        
        self.assertEqual(schema.status_code, 200)
        self.assertEqual(schema.content_type, "application/json")
        self.assertIsInstance(schema.schema, dict)
        self.assertEqual(len(schema.examples), 1)


if __name__ == '__main__':
    unittest.main()