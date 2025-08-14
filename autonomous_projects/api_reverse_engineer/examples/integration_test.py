"""
Integration test for the complete API reverse engineering workflow.

This test demonstrates the full end-to-end process:
1. Start a sample API server
2. Capture traffic
3. Analyze patterns
4. Generate SDKs
5. Generate documentation
6. Validate the generated output
"""

import os
import sys
import json
import time
import threading
import subprocess
import requests
import tempfile
import shutil
from pathlib import Path
from typing import List

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.capture import TrafficCapture
from src.analyzer import RequestAnalyzer
from src.generators import PythonGenerator, TypeScriptGenerator, JavaScriptGenerator
from src.documentation import DocumentationGenerator
from src.cli import APIReverseEngineerCLI


class IntegrationTest:
    """Integration test for the complete workflow."""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.api_server_process = None
        self.api_server_url = "http://localhost:5001"  # Different port to avoid conflicts
        self.proxy_port = 8081
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        
    def cleanup(self):
        """Clean up test resources."""
        if self.api_server_process:
            self.api_server_process.terminate()
            self.api_server_process.wait()
            
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def start_api_server(self) -> bool:
        """Start the sample API server."""
        try:
            # Get the path to the sample server
            server_path = Path(__file__).parent / "sample_api_server.py"
            
            # Start the server process
            env = os.environ.copy()
            env['FLASK_ENV'] = 'testing'
            
            self.api_server_process = subprocess.Popen([
                sys.executable, str(server_path)
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            for _ in range(10):  # Try for 10 seconds
                try:
                    response = requests.get(f"{self.api_server_url}/health", timeout=1)
                    if response.status_code == 200:
                        print("✓ API server started successfully")
                        return True
                except requests.RequestException:
                    time.sleep(1)
                    
            print("✗ Failed to start API server")
            return False
            
        except Exception as e:
            print(f"✗ Error starting API server: {e}")
            return False
            
    def make_test_requests_direct(self) -> List[dict]:
        """Make test requests directly to the API server."""
        headers = {
            "Authorization": "Bearer test-token-12345",
            "Content-Type": "application/json"
        }
        
        requests_made = []
        
        test_calls = [
            ("GET", "/health", None, None),
            ("GET", "/version", None, None),
            ("GET", "/users", {"limit": "3"}, None),
            ("GET", "/users/1", {"include": "posts"}, None),
            ("POST", "/users", None, {"name": "Integration Test User", "email": "test@integration.com"}),
            ("GET", "/posts", {"user_id": "1", "limit": "2"}, None),
            ("GET", "/users/1/posts", None, None)
        ]
        
        for method, path, params, data in test_calls:
            try:
                url = self.api_server_url + path
                
                if method == "GET":
                    response = requests.get(url, headers=headers, params=params, timeout=5)
                elif method == "POST":
                    response = requests.post(url, headers=headers, json=data, timeout=5)
                else:
                    continue
                    
                requests_made.append({
                    "method": method,
                    "url": response.url,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "request_headers": headers,
                    "params": params,
                    "data": data,
                    "response_body": response.text
                })
                
                print(f"  {method} {path} -> {response.status_code}")
                
            except requests.RequestException as e:
                print(f"  {method} {path} -> Error: {e}")
                
        return requests_made
        
    def convert_to_api_calls(self, requests_data: List[dict]):
        """Convert request data to APICall objects."""
        from src.types import APICall, CapturedRequest, CapturedResponse
        
        api_calls = []
        
        for req_data in requests_data:
            request = CapturedRequest(
                url=req_data["url"],
                method=req_data["method"],
                headers=req_data["request_headers"],
                query_params=req_data["params"] or {},
                body=json.dumps(req_data["data"]) if req_data["data"] else None
            )
            
            response = CapturedResponse(
                status_code=req_data["status_code"],
                headers=req_data["headers"],
                body=req_data["response_body"],
                content_type=req_data["headers"].get("content-type", "")
            )
            
            api_calls.append(APICall(request, response, duration_ms=100))
            
        return api_calls
        
    def test_traffic_analysis(self, api_calls):
        """Test traffic analysis functionality."""
        print("\n2. Testing traffic analysis...")
        
        analyzer = RequestAnalyzer()
        api_spec = analyzer.analyze_calls(api_calls)
        
        # Validate analysis results
        assert api_spec.base_url == self.api_server_url, f"Expected base URL {self.api_server_url}, got {api_spec.base_url}"
        assert len(api_spec.endpoints) > 0, "No endpoints detected"
        assert len(api_spec.auth_patterns) > 0, "No authentication patterns detected"
        
        print(f"  ✓ Detected {len(api_spec.endpoints)} endpoints")
        print(f"  ✓ Detected {len(api_spec.auth_patterns)} auth patterns")
        
        # Check for specific endpoints we expect
        endpoint_paths = [ep.path for ep in api_spec.endpoints]
        expected_paths = ["/health", "/users", "/users/{id}", "/posts"]
        
        for expected_path in expected_paths:
            if expected_path in endpoint_paths:
                print(f"  ✓ Found expected endpoint: {expected_path}")
            else:
                print(f"  ⚠ Missing expected endpoint: {expected_path}")
                
        return api_spec
        
    def test_sdk_generation(self, api_spec):
        """Test SDK generation for all supported languages."""
        print("\n3. Testing SDK generation...")
        
        languages = ["python", "typescript", "javascript"]
        generated_files = {}
        
        for language in languages:
            print(f"  Testing {language} SDK generation...")
            
            if language == "python":
                generator = PythonGenerator(api_spec)
            elif language == "typescript":
                generator = TypeScriptGenerator(api_spec)
            elif language == "javascript":
                generator = JavaScriptGenerator(api_spec)
            else:
                continue
                
            output_dir = Path(self.temp_dir) / f"sdk_{language}"
            files = generator.generate(str(output_dir))
            
            # Validate generated files
            assert len(files) > 0, f"No files generated for {language}"
            
            # Check that files actually exist
            for file_path in files.keys():
                assert Path(file_path).exists(), f"Generated file doesn't exist: {file_path}"
                
            print(f"  ✓ Generated {len(files)} {language} files")
            generated_files[language] = files
            
        return generated_files
        
    def test_documentation_generation(self, api_spec):
        """Test documentation generation."""
        print("\n4. Testing documentation generation...")
        
        doc_generator = DocumentationGenerator(api_spec)
        
        # Test Markdown generation
        markdown_file = Path(self.temp_dir) / "api_docs.md"
        markdown_content = doc_generator.generate_markdown(str(markdown_file))
        
        assert markdown_file.exists(), "Markdown file not created"
        assert len(markdown_content) > 0, "Empty markdown content"
        assert "# " in markdown_content, "No markdown headers found"
        print("  ✓ Generated Markdown documentation")
        
        # Test OpenAPI generation
        openapi_file = Path(self.temp_dir) / "openapi.json"
        openapi_spec = doc_generator.generate_openapi(str(openapi_file))
        
        assert openapi_file.exists(), "OpenAPI file not created"
        assert "openapi" in openapi_spec, "Invalid OpenAPI structure"
        assert "paths" in openapi_spec, "No paths in OpenAPI spec"
        print("  ✓ Generated OpenAPI specification")
        
        # Test Postman generation
        postman_file = Path(self.temp_dir) / "postman.json"
        postman_collection = doc_generator.generate_postman(str(postman_file))
        
        assert postman_file.exists(), "Postman file not created"
        assert "info" in postman_collection, "Invalid Postman structure"
        assert "item" in postman_collection, "No items in Postman collection"
        print("  ✓ Generated Postman collection")
        
        return {
            "markdown": markdown_content,
            "openapi": openapi_spec,
            "postman": postman_collection
        }
        
    def test_cli_interface(self, api_calls):
        """Test CLI interface functionality."""
        print("\n5. Testing CLI interface...")
        
        # Save API calls to a file for CLI testing
        traffic_file = Path(self.temp_dir) / "test_traffic.json"
        
        # Create traffic capture to save the data
        capture = TrafficCapture()
        capture.captured_calls = api_calls
        capture.save_to_file(str(traffic_file))
        
        assert traffic_file.exists(), "Traffic file not created"
        
        # Test CLI analyze command
        cli = APIReverseEngineerCLI()
        cli_output_dir = Path(self.temp_dir) / "cli_output"
        
        # Mock the arguments for the analyze command
        class MockArgs:
            input_file = str(traffic_file)
            output_dir = str(cli_output_dir)
            languages = ["python"]
            api_title = "CLI Test API"
            api_version = "1.0.0"
            
        mock_args = MockArgs()
        
        try:
            cli.cmd_analyze(mock_args)
            
            # Check that CLI generated files
            assert cli_output_dir.exists(), "CLI output directory not created"
            assert (cli_output_dir / "api_spec.json").exists(), "API spec not generated by CLI"
            assert (cli_output_dir / "README.md").exists(), "README not generated by CLI"
            
            print("  ✓ CLI analyze command works")
            
        except Exception as e:
            print(f"  ✗ CLI test failed: {e}")
            raise
            
    def validate_generated_content(self, generated_files, documentation):
        """Validate the quality of generated content."""
        print("\n6. Validating generated content...")
        
        # Check Python SDK content
        if "python" in generated_files:
            python_files = generated_files["python"]
            
            # Find client file
            client_files = [f for f in python_files.keys() if "client.py" in f]
            assert len(client_files) > 0, "No Python client file generated"
            
            client_path = client_files[0]
            with open(client_path, 'r') as f:
                client_content = f.read()
                
            # Validate client content
            assert "class " in client_content, "No class definition in Python client"
            assert "def __init__" in client_content, "No __init__ method in Python client"
            assert "requests" in client_content, "Python client doesn't use requests"
            
            print("  ✓ Python SDK content validated")
            
        # Check TypeScript SDK content
        if "typescript" in generated_files:
            ts_files = generated_files["typescript"]
            
            client_files = [f for f in ts_files.keys() if "client.ts" in f]
            assert len(client_files) > 0, "No TypeScript client file generated"
            
            client_path = client_files[0]
            with open(client_path, 'r') as f:
                client_content = f.read()
                
            # Validate client content
            assert "export class" in client_content, "No class export in TypeScript client"
            assert "async " in client_content, "No async methods in TypeScript client"
            assert "fetch" in client_content, "TypeScript client doesn't use fetch"
            
            print("  ✓ TypeScript SDK content validated")
            
        # Validate documentation content
        markdown = documentation["markdown"]
        assert "# " in markdown, "No title in markdown"
        assert "## " in markdown, "No sections in markdown"
        assert "GET" in markdown or "POST" in markdown, "No HTTP methods in markdown"
        
        openapi = documentation["openapi"]
        assert openapi["openapi"] == "3.0.0", "Invalid OpenAPI version"
        assert len(openapi["paths"]) > 0, "No paths in OpenAPI spec"
        
        postman = documentation["postman"]
        assert len(postman["item"]) > 0, "No items in Postman collection"
        
        print("  ✓ Documentation content validated")
        
    def run_full_test(self):
        """Run the complete integration test."""
        print("Starting Integration Test")
        print("=" * 50)
        
        try:
            # Step 1: Start API server and make requests
            print("1. Starting API server and making test requests...")
            if not self.start_api_server():
                raise Exception("Failed to start API server")
                
            # Make test requests
            requests_data = self.make_test_requests_direct()
            assert len(requests_data) > 0, "No requests were made"
            print(f"  ✓ Made {len(requests_data)} test requests")
            
            # Convert to API calls
            api_calls = self.convert_to_api_calls(requests_data)
            
            # Step 2: Test traffic analysis
            api_spec = self.test_traffic_analysis(api_calls)
            
            # Step 3: Test SDK generation
            generated_files = self.test_sdk_generation(api_spec)
            
            # Step 4: Test documentation generation
            documentation = self.test_documentation_generation(api_spec)
            
            # Step 5: Test CLI interface
            self.test_cli_interface(api_calls)
            
            # Step 6: Validate generated content
            self.validate_generated_content(generated_files, documentation)
            
            print("\n" + "=" * 50)
            print("✓ Integration test completed successfully!")
            print(f"  Temp directory: {self.temp_dir}")
            print(f"  Generated files: {sum(len(files) for files in generated_files.values())}")
            print(f"  Endpoints analyzed: {len(api_spec.endpoints)}")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Integration test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Run the integration test."""
    print("API Reverse Engineering Tool - Integration Test")
    print("This test validates the complete workflow from API capture to SDK generation.")
    print()
    
    # Check if Flask is available
    try:
        import flask
    except ImportError:
        print("✗ Flask is required for the integration test")
        print("  Install it with: pip install flask")
        return False
        
    # Run the integration test
    with IntegrationTest() as test:
        return test.run_full_test()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)