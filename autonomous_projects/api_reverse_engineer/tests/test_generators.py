"""
Tests for SDK generators.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from src.generators import PythonGenerator, TypeScriptGenerator, JavaScriptGenerator
from src.types import APISpec, Endpoint, Parameter, HTTPMethod, ParameterType, AuthType, AuthPattern


class TestBaseGenerator(unittest.TestCase):
    """Test base generator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a sample API spec
        param = Parameter("id", ParameterType.STRING, required=True, description="User ID")
        endpoint = Endpoint(
            path="/users/{id}",
            method=HTTPMethod.GET,
            summary="Get user by ID",
            parameters=[param]
        )
        
        auth_pattern = AuthPattern(
            type=AuthType.BEARER_TOKEN,
            header_name="Authorization",
            token_prefix="Bearer"
        )
        
        self.api_spec = APISpec(
            base_url="https://api.example.com",
            title="Test API",
            description="A test API for unit testing",
            endpoints=[endpoint],
            auth_patterns=[auth_pattern]
        )
        
        # Create temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestPythonGenerator(TestBaseGenerator):
    """Test Python SDK generator."""
    
    def test_generate_files(self):
        """Test that all expected files are generated."""
        generator = PythonGenerator(self.api_spec)
        files = generator.generate(self.temp_dir)
        
        # Check that files were created
        expected_files = [
            "client.py",
            "types.py", 
            "exceptions.py",
            "__init__.py",
            "requirements.txt",
            "setup.py",
            "README.md"
        ]
        
        for expected_file in expected_files:
            file_path = Path(self.temp_dir) / expected_file
            self.assertTrue(file_path.exists(), f"File {expected_file} not created")
            self.assertIn(str(file_path), files, f"File {expected_file} not in returned files dict")
            
    def test_client_content(self):
        """Test client file content."""
        generator = PythonGenerator(self.api_spec)
        files = generator.generate(self.temp_dir)
        
        client_path = Path(self.temp_dir) / "client.py"
        with open(client_path, 'r') as f:
            content = f.read()
            
        # Check for key components
        self.assertIn("class TestAPIClient", content)
        self.assertIn("def __init__(", content)
        self.assertIn("def _make_request(", content)
        self.assertIn("def get_users_id(", content)  # Method for the endpoint
        self.assertIn("Bearer", content)  # Auth handling
        
    def test_method_name_generation(self):
        """Test method name generation."""
        generator = PythonGenerator(self.api_spec)
        endpoint = self.api_spec.endpoints[0]
        
        method_name = generator._get_method_name(endpoint)
        self.assertEqual(method_name, "get_users")
        
    def test_auth_initialization(self):
        """Test authentication initialization code."""
        generator = PythonGenerator(self.api_spec)
        
        auth_init = generator._generate_auth_init()
        self.assertEqual(auth_init, "token: str")
        
        auth_assignment = generator._generate_auth_assignment()
        self.assertEqual(auth_assignment, "self.token = token")
        
    def test_type_conversion(self):
        """Test type conversion to Python types."""
        generator = PythonGenerator(self.api_spec)
        
        self.assertEqual(generator._type_to_string(ParameterType.STRING, "python"), "str")
        self.assertEqual(generator._type_to_string(ParameterType.INTEGER, "python"), "int")
        self.assertEqual(generator._type_to_string(ParameterType.BOOLEAN, "python"), "bool")
        self.assertEqual(generator._type_to_string(ParameterType.ARRAY, "python"), "List[Any]")


class TestTypeScriptGenerator(TestBaseGenerator):
    """Test TypeScript SDK generator."""
    
    def test_generate_files(self):
        """Test that all expected files are generated."""
        generator = TypeScriptGenerator(self.api_spec)
        files = generator.generate(self.temp_dir)
        
        expected_files = [
            "client.ts",
            "types.ts",
            "index.ts", 
            "package.json",
            "tsconfig.json",
            "README.md"
        ]
        
        for expected_file in expected_files:
            file_path = Path(self.temp_dir) / expected_file
            self.assertTrue(file_path.exists(), f"File {expected_file} not created")
            
    def test_client_content(self):
        """Test client file content."""
        generator = TypeScriptGenerator(self.api_spec)
        files = generator.generate(self.temp_dir)
        
        client_path = Path(self.temp_dir) / "client.ts"
        with open(client_path, 'r') as f:
            content = f.read()
            
        # Check for key components
        self.assertIn("export class TestAPIClient", content)
        self.assertIn("constructor(config: ClientConfig)", content)
        self.assertIn("private async makeRequest", content)
        self.assertIn("async getUsersId(", content)  # Method for the endpoint
        
    def test_camel_case_conversion(self):
        """Test camelCase conversion."""
        generator = TypeScriptGenerator(self.api_spec)
        
        self.assertEqual(generator._camel_case("get_users"), "getUsers")
        self.assertEqual(generator._camel_case("create_user_profile"), "createUserProfile")
        self.assertEqual(generator._camel_case("delete"), "delete")
        
    def test_package_json_content(self):
        """Test package.json content."""
        generator = TypeScriptGenerator(self.api_spec)
        files = generator.generate(self.temp_dir)
        
        package_path = Path(self.temp_dir) / "package.json"
        with open(package_path, 'r') as f:
            content = f.read()
            
        # Check for key fields
        self.assertIn('"name":', content)
        self.assertIn('"typescript":', content)
        self.assertIn('"@types/node":', content)


class TestJavaScriptGenerator(TestBaseGenerator):
    """Test JavaScript SDK generator."""
    
    def test_generate_files(self):
        """Test that all expected files are generated."""
        generator = JavaScriptGenerator(self.api_spec)
        files = generator.generate(self.temp_dir)
        
        expected_files = [
            "client.js",
            "types.js",
            "index.js",
            "package.json", 
            "README.md"
        ]
        
        for expected_file in expected_files:
            file_path = Path(self.temp_dir) / expected_file
            self.assertTrue(file_path.exists(), f"File {expected_file} not created")
            
    def test_client_content(self):
        """Test client file content."""
        generator = JavaScriptGenerator(self.api_spec)
        files = generator.generate(self.temp_dir)
        
        client_path = Path(self.temp_dir) / "client.js"
        with open(client_path, 'r') as f:
            content = f.read()
            
        # Check for key components
        self.assertIn("class TestAPIClient", content)
        self.assertIn("constructor(config = {})", content)
        self.assertIn("async makeRequest(", content)
        self.assertIn("async getUsersId(", content)  # Method for the endpoint
        self.assertIn("module.exports", content)  # CommonJS export
        
    def test_jsdoc_type_conversion(self):
        """Test JSDoc type conversion."""
        generator = JavaScriptGenerator(self.api_spec)
        
        self.assertEqual(generator._type_to_jsdoc_type(ParameterType.STRING), "string")
        self.assertEqual(generator._type_to_jsdoc_type(ParameterType.INTEGER), "number")
        self.assertEqual(generator._type_to_jsdoc_type(ParameterType.BOOLEAN), "boolean")
        self.assertEqual(generator._type_to_jsdoc_type(ParameterType.ARRAY), "Array")
        self.assertEqual(generator._type_to_jsdoc_type(ParameterType.OBJECT), "Object")


class TestGeneratorComparison(TestBaseGenerator):
    """Test consistency across different generators."""
    
    def test_all_generators_produce_files(self):
        """Test that all generators produce output files."""
        generators = [
            PythonGenerator(self.api_spec),
            TypeScriptGenerator(self.api_spec),
            JavaScriptGenerator(self.api_spec)
        ]
        
        for i, generator in enumerate(generators):
            test_dir = Path(self.temp_dir) / f"test_{i}"
            test_dir.mkdir()
            
            files = generator.generate(str(test_dir))
            
            # Each generator should produce at least 3 files
            self.assertGreaterEqual(len(files), 3, 
                                  f"{generator.__class__.__name__} produced too few files")
            
            # All files should actually exist
            for file_path in files.keys():
                self.assertTrue(Path(file_path).exists(), 
                              f"File {file_path} was reported but doesn't exist")
                
    def test_consistent_method_naming(self):
        """Test that method naming is consistent across generators."""
        endpoint = Endpoint(
            path="/users/{id}/posts",
            method=HTTPMethod.GET,
            summary="Get user posts"
        )
        
        python_gen = PythonGenerator(self.api_spec)
        typescript_gen = TypeScriptGenerator(self.api_spec)
        javascript_gen = JavaScriptGenerator(self.api_spec)
        
        # Python uses snake_case
        python_method = python_gen._get_method_name(endpoint)
        self.assertIn("_", python_method)
        
        # TypeScript and JavaScript should use camelCase for the same endpoint
        typescript_method = typescript_gen._camel_case(typescript_gen._get_method_name(endpoint))
        javascript_method = javascript_gen._camel_case(javascript_gen._get_method_name(endpoint))
        
        # Convert python method to camelCase for comparison
        python_camel = typescript_gen._camel_case(python_method)
        
        self.assertEqual(typescript_method, javascript_method)
        self.assertEqual(python_camel, typescript_method)


if __name__ == '__main__':
    unittest.main()