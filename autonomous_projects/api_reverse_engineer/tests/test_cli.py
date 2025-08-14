"""
Tests for the CLI interface.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.cli import APIReverseEngineerCLI
from src.types import APISpec, Endpoint, HTTPMethod


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cli = APIReverseEngineerCLI()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_parser_creation(self):
        """Test argument parser creation."""
        parser = self.cli.create_parser()
        
        # Test that parser was created
        self.assertIsNotNone(parser)
        
        # Test help text generation (shouldn't raise an exception)
        try:
            parser.format_help()
        except Exception as e:
            self.fail(f"Parser help generation failed: {e}")
            
    def test_capture_command_args(self):
        """Test capture command argument parsing."""
        parser = self.cli.create_parser()
        
        # Test valid capture command
        args = parser.parse_args([
            'capture', 
            '--port', '8080',
            '--output', 'test.json',
            '--duration', '60'
        ])
        
        self.assertEqual(args.command, 'capture')
        self.assertEqual(args.port, 8080)
        self.assertEqual(args.output, 'test.json')
        self.assertEqual(args.duration, 60)
        
    def test_analyze_command_args(self):
        """Test analyze command argument parsing."""
        parser = self.cli.create_parser()
        
        args = parser.parse_args([
            'analyze',
            'input.json',
            '--output-dir', '/tmp/output',
            '--languages', 'python', 'typescript',
            '--api-title', 'My API'
        ])
        
        self.assertEqual(args.command, 'analyze')
        self.assertEqual(args.input_file, 'input.json')
        self.assertEqual(args.output_dir, '/tmp/output')
        self.assertEqual(args.languages, ['python', 'typescript'])
        self.assertEqual(args.api_title, 'My API')
        
    def test_generate_command_args(self):
        """Test generate command argument parsing."""
        parser = self.cli.create_parser()
        
        args = parser.parse_args([
            'generate',
            'api_spec.json',
            '--output-dir', '/tmp/sdk',
            '--language', 'python'
        ])
        
        self.assertEqual(args.command, 'generate')
        self.assertEqual(args.api_spec, 'api_spec.json')
        self.assertEqual(args.output_dir, '/tmp/sdk')
        self.assertEqual(args.language, 'python')
        
    def test_docs_command_args(self):
        """Test docs command argument parsing."""
        parser = self.cli.create_parser()
        
        args = parser.parse_args([
            'docs',
            'api_spec.json',
            '--format', 'openapi',
            '--output', 'openapi.json'
        ])
        
        self.assertEqual(args.command, 'docs')
        self.assertEqual(args.api_spec, 'api_spec.json')
        self.assertEqual(args.format, 'openapi')
        self.assertEqual(args.output, 'openapi.json')
        
    def test_workflow_command_args(self):
        """Test workflow command argument parsing."""
        parser = self.cli.create_parser()
        
        args = parser.parse_args([
            'workflow',
            '--port', '9090',
            '--duration', '120',
            '--output-dir', '/tmp/complete',
            '--languages', 'python', 'javascript',
            '--api-title', 'Complete API'
        ])
        
        self.assertEqual(args.command, 'workflow')
        self.assertEqual(args.port, 9090)
        self.assertEqual(args.duration, 120)
        self.assertEqual(args.output_dir, '/tmp/complete')
        self.assertEqual(args.languages, ['python', 'javascript'])
        self.assertEqual(args.api_title, 'Complete API')
        
    @patch('src.cli.DocumentationGenerator')
    def test_cmd_docs(self, mock_doc_gen):
        """Test docs command execution."""
        # Create a test API spec file
        api_spec_data = {
            "base_url": "https://api.example.com",
            "title": "Test API",
            "version": "1.0.0",
            "endpoints": []
        }
        
        spec_file = Path(self.temp_dir) / "api_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(api_spec_data, f)
            
        # Mock the documentation generator
        mock_generator = Mock()
        mock_doc_gen.return_value = mock_generator
        mock_generator.generate_markdown.return_value = "# Test API Documentation"
        
        # Create mock args
        args = Mock()
        args.api_spec = str(spec_file)
        args.format = 'markdown'
        args.output = None
        
        # Test the command
        with patch('builtins.print') as mock_print:
            self.cli.cmd_docs(args)
            mock_print.assert_called_once_with("# Test API Documentation")
            
    def test_generate_sdk_method(self):
        """Test SDK generation method."""
        # Create a simple API spec
        endpoint = Endpoint("/users", HTTPMethod.GET, summary="Get users")
        api_spec = APISpec(
            base_url="https://api.example.com",
            title="Test API",
            endpoints=[endpoint]
        )
        
        # Test Python generation
        with patch('src.cli.PythonGenerator') as mock_gen:
            mock_generator = Mock()
            mock_gen.return_value = mock_generator
            mock_generator.generate.return_value = {"client.py": "# Python client"}
            
            self.cli._generate_sdk(api_spec, 'python', self.temp_dir)
            
            mock_gen.assert_called_once_with(api_spec)
            mock_generator.generate.assert_called_once_with(self.temp_dir)
            
    def test_unsupported_language_error(self):
        """Test error handling for unsupported language."""
        endpoint = Endpoint("/users", HTTPMethod.GET)
        api_spec = APISpec(
            base_url="https://api.example.com", 
            title="Test API",
            endpoints=[endpoint]
        )
        
        with self.assertRaises(ValueError) as context:
            self.cli._generate_sdk(api_spec, 'unsupported_lang', self.temp_dir)
            
        self.assertIn("Unsupported language", str(context.exception))
        
    def test_no_command_shows_help(self):
        """Test that no command shows help."""
        with patch.object(self.cli, 'create_parser') as mock_parser:
            mock_parser_instance = Mock()
            mock_parser.return_value = mock_parser_instance
            mock_parser_instance.parse_args.return_value = Mock(command=None)
            
            self.cli.run([])
            
            mock_parser_instance.print_help.assert_called_once()
            
    @patch('src.cli.setup_logging')
    def test_verbose_logging_setup(self, mock_setup_logging):
        """Test verbose logging setup."""
        with patch.object(self.cli, 'cmd_capture'):
            args = Mock()
            args.command = 'capture'
            args.verbose = True
            
            with patch.object(self.cli, 'create_parser') as mock_parser:
                mock_parser.return_value.parse_args.return_value = args
                
                self.cli.run([])
                
                mock_setup_logging.assert_called_once_with(True)
                
    def test_keyboard_interrupt_handling(self):
        """Test keyboard interrupt handling."""
        with patch.object(self.cli, 'cmd_capture', side_effect=KeyboardInterrupt):
            with patch.object(self.cli, 'create_parser') as mock_parser:
                args = Mock()
                args.command = 'capture'
                args.verbose = False
                mock_parser.return_value.parse_args.return_value = args
                
                # Should not raise an exception
                self.cli.run([])
                
    def test_exception_handling_with_verbose(self):
        """Test exception handling with verbose mode."""
        with patch.object(self.cli, 'cmd_capture', side_effect=Exception("Test error")):
            with patch.object(self.cli, 'create_parser') as mock_parser:
                args = Mock()
                args.command = 'capture'
                args.verbose = True
                mock_parser.return_value.parse_args.return_value = args
                
                with patch('traceback.print_exc') as mock_traceback:
                    with self.assertRaises(SystemExit):
                        self.cli.run([])
                    mock_traceback.assert_called_once()
                    
    def test_exception_handling_without_verbose(self):
        """Test exception handling without verbose mode."""
        with patch.object(self.cli, 'cmd_capture', side_effect=Exception("Test error")):
            with patch.object(self.cli, 'create_parser') as mock_parser:
                args = Mock()
                args.command = 'capture'
                args.verbose = False
                mock_parser.return_value.parse_args.return_value = args
                
                with patch('traceback.print_exc') as mock_traceback:
                    with self.assertRaises(SystemExit):
                        self.cli.run([])
                    mock_traceback.assert_not_called()


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cli = APIReverseEngineerCLI()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_help_commands(self):
        """Test that help commands work for all subcommands."""
        parser = self.cli.create_parser()
        
        # Test main help
        try:
            parser.parse_args(['--help'])
        except SystemExit:
            pass  # Expected for help commands
            
        # Test subcommand help
        subcommands = ['capture', 'analyze', 'generate', 'docs', 'workflow']
        
        for subcmd in subcommands:
            try:
                parser.parse_args([subcmd, '--help'])
            except SystemExit:
                pass  # Expected for help commands
                
    def test_dict_to_api_spec_conversion(self):
        """Test conversion from dictionary to APISpec."""
        spec_data = {
            "base_url": "https://api.example.com",
            "title": "Test API",
            "version": "1.0.0",
            "description": "Test description",
            "endpoints": [
                {
                    "path": "/users",
                    "method": "GET",
                    "summary": "Get users"
                }
            ]
        }
        
        api_spec = self.cli._dict_to_api_spec(spec_data)
        
        self.assertEqual(api_spec.base_url, "https://api.example.com")
        self.assertEqual(api_spec.title, "Test API")
        self.assertEqual(api_spec.version, "1.0.0")
        self.assertEqual(len(api_spec.endpoints), 1)
        self.assertEqual(api_spec.endpoints[0].path, "/users")
        self.assertEqual(api_spec.endpoints[0].method, HTTPMethod.GET)


if __name__ == '__main__':
    unittest.main()