"""
Basic usage example for the API reverse engineering tool.

This example demonstrates how to use the main components programmatically.
"""

import json
import time
import requests
from pathlib import Path

# Import the main components
from src.capture import TrafficCapture
from src.analyzer import RequestAnalyzer
from src.generators import PythonGenerator, TypeScriptGenerator
from src.documentation import DocumentationGenerator


def create_sample_traffic():
    """Create sample API calls for demonstration."""
    from src.types import APICall, CapturedRequest, CapturedResponse
    
    calls = []
    
    # GET /users
    request1 = CapturedRequest(
        url="https://api.example.com/users",
        method="GET",
        headers={"Authorization": "Bearer abc123", "Content-Type": "application/json"},
        query_params={"limit": "10", "offset": "0"}
    )
    response1 = CapturedResponse(
        status_code=200,
        headers={"Content-Type": "application/json", "X-RateLimit-Remaining": "99"},
        body='{"users": [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}], "total": 2}'
    )
    calls.append(APICall(request1, response1, duration_ms=150))
    
    # GET /users/123
    request2 = CapturedRequest(
        url="https://api.example.com/users/123",
        method="GET",
        headers={"Authorization": "Bearer abc123", "Content-Type": "application/json"},
        query_params={"include": "posts"}
    )
    response2 = CapturedResponse(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body='{"id": 123, "name": "John Doe", "email": "john@example.com", "posts": []}'
    )
    calls.append(APICall(request2, response2, duration_ms=95))
    
    # POST /users
    request3 = CapturedRequest(
        url="https://api.example.com/users",
        method="POST",
        headers={"Authorization": "Bearer abc123", "Content-Type": "application/json"},
        query_params={},
        body='{"name": "New User", "email": "new@example.com", "age": 28}'
    )
    response3 = CapturedResponse(
        status_code=201,
        headers={"Content-Type": "application/json"},
        body='{"id": 124, "name": "New User", "email": "new@example.com", "age": 28}'
    )
    calls.append(APICall(request3, response3, duration_ms=200))
    
    # GET /users/123/posts
    request4 = CapturedRequest(
        url="https://api.example.com/users/123/posts",
        method="GET",
        headers={"Authorization": "Bearer abc123"},
        query_params={"limit": "5"}
    )
    response4 = CapturedResponse(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body='{"posts": [{"id": 1, "title": "Hello", "content": "World"}]}'
    )
    calls.append(APICall(request4, response4, duration_ms=120))
    
    return calls


def example_programmatic_usage():
    """Demonstrate programmatic usage of the tool."""
    print("=== API Reverse Engineering Tool - Basic Usage Example ===")
    print()
    
    # Step 1: Create sample traffic data
    print("1. Creating sample API traffic data...")
    api_calls = create_sample_traffic()
    print(f"   Created {len(api_calls)} sample API calls")
    print()
    
    # Step 2: Analyze the traffic
    print("2. Analyzing API traffic...")
    analyzer = RequestAnalyzer()
    api_spec = analyzer.analyze_calls(api_calls)
    
    print(f"   Base URL: {api_spec.base_url}")
    print(f"   Endpoints discovered: {len(api_spec.endpoints)}")
    print(f"   Authentication patterns: {len(api_spec.auth_patterns)}")
    
    # List endpoints
    for endpoint in api_spec.endpoints:
        print(f"   - {endpoint.method.value} {endpoint.path}")
    print()
    
    # Step 3: Generate Python SDK
    print("3. Generating Python SDK...")
    python_generator = PythonGenerator(api_spec)
    python_files = python_generator.generate("./output/python_sdk")
    print(f"   Generated {len(python_files)} Python files:")
    for file_path in python_files.keys():
        print(f"   - {file_path}")
    print()
    
    # Step 4: Generate TypeScript SDK
    print("4. Generating TypeScript SDK...")
    ts_generator = TypeScriptGenerator(api_spec)
    ts_files = ts_generator.generate("./output/typescript_sdk")
    print(f"   Generated {len(ts_files)} TypeScript files:")
    for file_path in ts_files.keys():
        print(f"   - {file_path}")
    print()
    
    # Step 5: Generate documentation
    print("5. Generating documentation...")
    doc_generator = DocumentationGenerator(api_spec)
    
    # Markdown documentation
    markdown_content = doc_generator.generate_markdown("./output/api_documentation.md")
    print(f"   Generated Markdown documentation ({len(markdown_content)} characters)")
    
    # OpenAPI specification
    openapi_spec = doc_generator.generate_openapi("./output/openapi.json")
    print(f"   Generated OpenAPI specification ({len(openapi_spec['paths'])} paths)")
    
    # Postman collection
    postman_collection = doc_generator.generate_postman("./output/postman_collection.json")
    print(f"   Generated Postman collection ({len(postman_collection['item'])} items)")
    print()
    
    # Step 6: Show API specification
    print("6. Generated API Specification:")
    print("   " + "="*50)
    spec_dict = api_spec.to_dict()
    print(f"   Title: {spec_dict['title']}")
    print(f"   Base URL: {spec_dict['base_url']}")
    print(f"   Version: {spec_dict['version']}")
    print()
    print("   Endpoints:")
    for endpoint in spec_dict['endpoints']:
        params_count = len(endpoint['parameters']) + len(endpoint['query_params'])
        print(f"   - {endpoint['method']} {endpoint['path']} ({params_count} params)")
    print()
    print("   Authentication:")
    for auth in spec_dict['auth_patterns']:
        print(f"   - {auth['type']}: {auth.get('header_name', 'N/A')}")
    print()
    
    print("Example completed successfully!")
    print("Check the ./output directory for generated files.")


def example_traffic_capture():
    """Demonstrate traffic capture capabilities."""
    print("=== Traffic Capture Example ===")
    print()
    print("This example shows how to capture live traffic.")
    print("Note: This requires running a separate API server to capture from.")
    print()
    
    # Create capture instance
    capture = TrafficCapture(
        port=8080,
        target_hosts={"localhost", "127.0.0.1"},
        output_file="./output/captured_traffic.json",
        verbose=True
    )
    
    # Add a callback to show progress
    def show_progress(api_call):
        print(f"Captured: {api_call.request.method} {api_call.request.url}")
    
    capture.add_callback(show_progress)
    
    print("Traffic capture setup complete.")
    print("To use this:")
    print("1. Start the capture: capture.start_capture()")
    print("2. Configure your app to use proxy at localhost:8080")
    print("3. Make API calls through the proxy")
    print("4. Stop capture: capture.stop_capture()")
    print("5. Save results: capture.save_to_file()")
    print()
    
    # For demo purposes, we'll just show the setup
    print("Demo: Showing capture configuration...")
    print(f"Proxy port: {capture.port}")
    print(f"Target hosts: {capture.target_hosts}")
    print(f"Output file: {capture.output_file}")
    print()


def example_live_api_testing():
    """Example of testing against a live API."""
    print("=== Live API Testing Example ===")
    print()
    print("This example shows how to test against the sample API server.")
    print("Make sure to run 'python examples/sample_api_server.py' first.")
    print()
    
    # Test if the sample API server is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        if response.status_code == 200:
            print("✓ Sample API server is running")
        else:
            print("✗ Sample API server returned unexpected status")
            return
    except requests.RequestException:
        print("✗ Sample API server is not running")
        print("  Please start it with: python examples/sample_api_server.py")
        return
    
    print()
    print("Making test API calls...")
    
    # Make some test calls
    base_url = "http://localhost:5000"
    headers = {
        "Authorization": "Bearer test-token-12345",
        "Content-Type": "application/json"
    }
    
    test_calls = [
        ("GET", "/health", None, None),
        ("GET", "/version", None, None),
        ("GET", "/users", {"limit": "5"}, None),
        ("GET", "/users/1", {"include": "posts"}, None),
        ("POST", "/users", None, {"name": "Test User", "email": "test@example.com"}),
        ("GET", "/posts", {"user_id": "1"}, None)
    ]
    
    captured_calls = []
    
    for method, path, params, data in test_calls:
        try:
            url = base_url + path
            
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=5)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=5)
            else:
                continue
                
            print(f"  {method} {path} -> {response.status_code}")
            
            # Convert to our APICall format for analysis
            from src.types import APICall, CapturedRequest, CapturedResponse
            
            request = CapturedRequest(
                url=response.url,
                method=method,
                headers=dict(headers),
                query_params=params or {},
                body=json.dumps(data) if data else None
            )
            
            captured_response = CapturedResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.text,
                content_type=response.headers.get('content-type', '')
            )
            
            captured_calls.append(APICall(request, captured_response))
            
        except requests.RequestException as e:
            print(f"  {method} {path} -> Error: {e}")
    
    print()
    print(f"Captured {len(captured_calls)} successful API calls")
    
    if captured_calls:
        print()
        print("Analyzing captured traffic...")
        
        analyzer = RequestAnalyzer()
        api_spec = analyzer.analyze_calls(captured_calls)
        
        print(f"API Analysis Results:")
        print(f"  Base URL: {api_spec.base_url}")
        print(f"  Endpoints: {len(api_spec.endpoints)}")
        print(f"  Auth patterns: {len(api_spec.auth_patterns)}")
        
        # Save the analysis results
        Path("./output").mkdir(exist_ok=True)
        with open("./output/live_api_spec.json", "w") as f:
            json.dump(api_spec.to_dict(), f, indent=2)
        print(f"  Saved API spec to: ./output/live_api_spec.json")


if __name__ == "__main__":
    # Create output directory
    Path("./output").mkdir(exist_ok=True)
    
    print("API Reverse Engineering Tool - Examples")
    print("======================================")
    print()
    
    # Run the examples
    try:
        example_programmatic_usage()
        print()
        print("-" * 60)
        print()
        example_traffic_capture()
        print()
        print("-" * 60)
        print()
        example_live_api_testing()
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()