"""
Tests for documentation generator.
"""

import unittest
import json
import tempfile
from pathlib import Path

from src.documentation import DocumentationGenerator
from src.types import (
    APISpec, Endpoint, Parameter, ResponseSchema, AuthPattern,
    HTTPMethod, ParameterType, AuthType
)


class TestDocumentationGenerator(unittest.TestCase):
    """Test documentation generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create comprehensive API spec for testing
        param = Parameter("id", ParameterType.STRING, required=True, description="User ID")
        query_param = Parameter("include", ParameterType.STRING, required=False, description="Fields to include")
        
        response_schema = ResponseSchema(
            status_code=200,
            content_type="application/json",
            schema={"type": "object", "properties": {"id": {"type": "string"}, "name": {"type": "string"}}},
            examples=[{"id": "123", "name": "John Doe"}]
        )
        
        endpoint = Endpoint(
            path="/users/{id}",
            method=HTTPMethod.GET,
            summary="Get user by ID",
            description="Retrieve a specific user by their unique identifier",
            parameters=[param],
            query_params=[query_param],
            responses=[response_schema],
            auth_required=True
        )
        
        auth_pattern = AuthPattern(
            type=AuthType.BEARER_TOKEN,
            header_name="Authorization",
            token_prefix="Bearer"
        )
        
        self.api_spec = APISpec(
            base_url="https://api.example.com",
            title="Test API",
            version="1.2.0",
            description="A comprehensive test API for documentation testing",
            endpoints=[endpoint],
            auth_patterns=[auth_pattern]
        )
        
        self.generator = DocumentationGenerator(self.api_spec)
        
    def test_generate_markdown(self):
        """Test Markdown documentation generation."""
        markdown = self.generator.generate_markdown()
        
        # Check basic structure
        self.assertIn("# Test API", markdown)
        self.assertIn("A comprehensive test API", markdown)
        self.assertIn("**Base URL:** `https://api.example.com`", markdown)
        self.assertIn("**Version:** 1.2.0", markdown)
        
        # Check sections
        self.assertIn("## Authentication", markdown)
        self.assertIn("## Endpoints", markdown)
        self.assertIn("## Examples", markdown)
        self.assertIn("## Error Handling", markdown)
        
        # Check endpoint documentation
        self.assertIn("🟢 GET", markdown)  # Method badge
        self.assertIn("`/users/{id}`", markdown)
        self.assertIn("Get user by ID", markdown)
        self.assertIn("🔒 **Authentication required**", markdown)
        
        # Check parameter table
        self.assertIn("| Name | Type | Location | Required | Description |", markdown)
        self.assertIn("| `id` | string | path | ✅ | User ID |", markdown)
        self.assertIn("| `include` | string | query | ❌ | Fields to include |", markdown)
        
    def test_generate_openapi(self):
        """Test OpenAPI 3.0 specification generation."""
        openapi_spec = self.generator.generate_openapi()
        
        # Check basic structure
        self.assertEqual(openapi_spec["openapi"], "3.0.0")
        self.assertEqual(openapi_spec["info"]["title"], "Test API")
        self.assertEqual(openapi_spec["info"]["version"], "1.2.0")
        
        # Check servers
        self.assertEqual(len(openapi_spec["servers"]), 1)
        self.assertEqual(openapi_spec["servers"][0]["url"], "https://api.example.com")
        
        # Check paths
        self.assertIn("/users/{id}", openapi_spec["paths"])
        path_spec = openapi_spec["paths"]["/users/{id}"]
        self.assertIn("get", path_spec)
        
        get_operation = path_spec["get"]
        self.assertEqual(get_operation["summary"], "Get user by ID")
        self.assertEqual(get_operation["description"], "Retrieve a specific user by their unique identifier")
        
        # Check parameters
        self.assertEqual(len(get_operation["parameters"]), 2)
        
        # Path parameter
        path_param = next(p for p in get_operation["parameters"] if p["in"] == "path")
        self.assertEqual(path_param["name"], "id")
        self.assertTrue(path_param["required"])
        
        # Query parameter
        query_param = next(p for p in get_operation["parameters"] if p["in"] == "query")
        self.assertEqual(query_param["name"], "include")
        self.assertFalse(query_param["required"])
        
        # Check responses
        self.assertIn("200", get_operation["responses"])
        
        # Check security schemes
        self.assertIn("securitySchemes", openapi_spec["components"])
        self.assertIn("bearerAuth", openapi_spec["components"]["securitySchemes"])
        
        # Check security on operation
        self.assertIn("security", get_operation)
        self.assertEqual(get_operation["security"], [{"bearerAuth": []}])
        
    def test_generate_postman_collection(self):
        """Test Postman collection generation."""
        collection = self.generator.generate_postman_collection()
        
        # Check basic structure
        self.assertIn("info", collection)
        self.assertEqual(collection["info"]["name"], "Test API")
        self.assertIn("schema", collection["info"])
        
        # Check variables
        self.assertIn("variable", collection)
        base_url_var = next(v for v in collection["variable"] if v["key"] == "baseUrl")
        self.assertEqual(base_url_var["value"], "https://api.example.com")
        
        # Check items (folders)
        self.assertIn("item", collection)
        self.assertTrue(len(collection["item"]) > 0)
        
        # Find the request item
        folder = collection["item"][0]
        self.assertIn("item", folder)
        
        request_item = folder["item"][0]
        self.assertIn("request", request_item)
        
        request = request_item["request"]
        self.assertEqual(request["method"], "GET")
        
        # Check URL structure
        self.assertIn("url", request)
        self.assertIn("{{baseUrl}}", request["url"]["raw"])
        
        # Check query parameters
        if "query" in request["url"]:
            query_params = request["url"]["query"]
            include_param = next(p for p in query_params if p["key"] == "include")
            self.assertEqual(include_param["description"], "Fields to include")
            
    def test_authentication_section_bearer_token(self):
        """Test Bearer token authentication documentation."""
        auth_content = self.generator._generate_authentication_section()
        
        self.assertIn("Bearer Token", auth_content)
        self.assertIn("Authorization: Bearer YOUR_TOKEN", auth_content)
        
    def test_authentication_section_api_key(self):
        """Test API key authentication documentation."""
        # Create API spec with API key auth
        auth_pattern = AuthPattern(
            type=AuthType.API_KEY,
            header_name="X-API-Key"
        )
        
        api_spec = APISpec(
            base_url="https://api.example.com",
            title="Test API",
            auth_patterns=[auth_pattern]
        )
        
        generator = DocumentationGenerator(api_spec)
        auth_content = generator._generate_authentication_section()
        
        self.assertIn("Api Key", auth_content)
        self.assertIn("X-API-Key: YOUR_API_KEY", auth_content)
        
    def test_method_badges(self):
        """Test HTTP method badge generation."""
        self.assertEqual(self.generator._get_method_badge("GET"), "🟢 GET")
        self.assertEqual(self.generator._get_method_badge("POST"), "🟡 POST")
        self.assertEqual(self.generator._get_method_badge("PUT"), "🔵 PUT")
        self.assertEqual(self.generator._get_method_badge("DELETE"), "🔴 DELETE")
        self.assertEqual(self.generator._get_method_badge("PATCH"), "🟠 PATCH")
        
    def test_status_descriptions(self):
        """Test HTTP status code descriptions."""
        self.assertEqual(self.generator._get_status_description(200), "OK")
        self.assertEqual(self.generator._get_status_description(201), "Created")
        self.assertEqual(self.generator._get_status_description(400), "Bad Request")
        self.assertEqual(self.generator._get_status_description(401), "Unauthorized")
        self.assertEqual(self.generator._get_status_description(404), "Not Found")
        self.assertEqual(self.generator._get_status_description(500), "Internal Server Error")
        self.assertEqual(self.generator._get_status_description(999), "Unknown")
        
    def test_curl_example_generation(self):
        """Test cURL example generation."""
        endpoint = self.api_spec.endpoints[0]
        curl_example = self.generator._generate_curl_example(endpoint)
        
        self.assertIn("curl -X GET", curl_example)
        self.assertIn("https://api.example.com/users/", curl_example)
        self.assertIn("Authorization: Bearer YOUR_TOKEN", curl_example)
        self.assertIn("Content-Type: application/json", curl_example)
        
    def test_python_example_generation(self):
        """Test Python example generation."""
        endpoint = self.api_spec.endpoints[0]
        python_example = self.generator._generate_python_example(endpoint)
        
        self.assertIn("import requests", python_example)
        self.assertIn("requests.get(", python_example)
        self.assertIn("Authorization", python_example)
        self.assertIn("Bearer YOUR_TOKEN", python_example)
        
    def test_javascript_example_generation(self):
        """Test JavaScript example generation."""
        endpoint = self.api_spec.endpoints[0]
        js_example = self.generator._generate_javascript_example(endpoint)
        
        self.assertIn("fetch(", js_example)
        self.assertIn("method: \"GET\"", js_example)
        self.assertIn("Authorization", js_example)
        self.assertIn("Bearer YOUR_TOKEN", js_example)
        
    def test_file_output(self):
        """Test file output functionality."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_file = f.name
            
        try:
            # Test markdown file output
            result = self.generator.generate_markdown(temp_file)
            
            # Check file was created
            self.assertTrue(Path(temp_file).exists())
            
            # Check content matches
            with open(temp_file, 'r') as f:
                file_content = f.read()
                
            self.assertEqual(result, file_content)
            self.assertIn("# Test API", file_content)
            
        finally:
            Path(temp_file).unlink(missing_ok=True)
            
    def test_complex_endpoint_documentation(self):
        """Test documentation generation for complex endpoints."""
        # Add a POST endpoint with request body
        post_endpoint = Endpoint(
            path="/users",
            method=HTTPMethod.POST,
            summary="Create user",
            description="Create a new user account",
            request_body={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "age": {"type": "integer"}
                }
            },
            responses=[
                ResponseSchema(
                    status_code=201,
                    content_type="application/json",
                    schema={"type": "object", "properties": {"id": {"type": "string"}}},
                    examples=[{"id": "new-user-123"}]
                ),
                ResponseSchema(
                    status_code=400,
                    content_type="application/json",
                    schema={"type": "object", "properties": {"error": {"type": "string"}}},
                    examples=[{"error": "Invalid input"}]
                )
            ]
        )
        
        # Create new API spec with the POST endpoint
        api_spec_with_post = APISpec(
            base_url="https://api.example.com",
            title="Extended Test API",
            endpoints=[post_endpoint],
            auth_patterns=self.api_spec.auth_patterns
        )
        
        generator = DocumentationGenerator(api_spec_with_post)
        markdown = generator.generate_markdown()
        
        # Check POST endpoint documentation
        self.assertIn("🟡 POST", markdown)
        self.assertIn("Create user", markdown)
        self.assertIn("**Request Body:**", markdown)
        self.assertIn("**201** - Created", markdown)
        self.assertIn("**400** - Bad Request", markdown)


if __name__ == '__main__':
    unittest.main()