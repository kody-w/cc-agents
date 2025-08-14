"""
Command-line interface for the API reverse engineering tool.
"""

import argparse
import json
import sys
import time
import logging
from pathlib import Path
from typing import Optional, List

from .capture import TrafficCapture
from .analyzer import RequestAnalyzer
from .generators import PythonGenerator, TypeScriptGenerator, JavaScriptGenerator
from .documentation import DocumentationGenerator
from .types import APISpec


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


class APIReverseEngineerCLI:
    """Command-line interface for API reverse engineering."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            description="Automated API Reverse Engineering Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Start capturing traffic on port 8080
  python -m src.cli capture --port 8080 --output traffic.json
  
  # Analyze captured traffic and generate SDKs
  python -m src.cli analyze traffic.json --output-dir ./sdks
  
  # Generate documentation from API spec
  python -m src.cli docs api_spec.json --format markdown --output api_docs.md
  
  # Complete workflow: capture -> analyze -> generate
  python -m src.cli workflow --port 8080 --duration 300 --output-dir ./output
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Capture command
        capture_parser = subparsers.add_parser('capture', help='Capture API traffic')
        self._add_capture_args(capture_parser)
        
        # Analyze command
        analyze_parser = subparsers.add_parser('analyze', help='Analyze captured traffic')
        self._add_analyze_args(analyze_parser)
        
        # Generate command
        generate_parser = subparsers.add_parser('generate', help='Generate SDK from API spec')
        self._add_generate_args(generate_parser)
        
        # Documentation command
        docs_parser = subparsers.add_parser('docs', help='Generate documentation')
        self._add_docs_args(docs_parser)
        
        # Complete workflow command
        workflow_parser = subparsers.add_parser('workflow', help='Complete capture and analysis workflow')
        self._add_workflow_args(workflow_parser)
        
        # Global options
        parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
        
        return parser
        
    def _add_capture_args(self, parser: argparse.ArgumentParser):
        """Add arguments for capture command."""
        parser.add_argument('--port', type=int, default=8080, help='Proxy server port (default: 8080)')
        parser.add_argument('--hosts', nargs='*', help='Target hostnames to capture (captures all if not specified)')
        parser.add_argument('--output', '-o', required=True, help='Output file for captured traffic')
        parser.add_argument('--duration', type=int, help='Capture duration in seconds (runs indefinitely if not specified)')
        
    def _add_analyze_args(self, parser: argparse.ArgumentParser):
        """Add arguments for analyze command."""
        parser.add_argument('input_file', help='Captured traffic JSON file')
        parser.add_argument('--output-dir', '-o', required=True, help='Output directory for generated files')
        parser.add_argument('--languages', nargs='*', choices=['python', 'typescript', 'javascript'], 
                          default=['python'], help='Programming languages to generate SDKs for')
        parser.add_argument('--api-title', help='API title (auto-detected if not specified)')
        parser.add_argument('--api-version', default='1.0.0', help='API version (default: 1.0.0)')
        
    def _add_generate_args(self, parser: argparse.ArgumentParser):
        """Add arguments for generate command."""
        parser.add_argument('api_spec', help='API specification JSON file')
        parser.add_argument('--output-dir', '-o', required=True, help='Output directory for generated SDK')
        parser.add_argument('--language', choices=['python', 'typescript', 'javascript'], 
                          required=True, help='Programming language for SDK generation')
        
    def _add_docs_args(self, parser: argparse.ArgumentParser):
        """Add arguments for docs command."""
        parser.add_argument('api_spec', help='API specification JSON file')
        parser.add_argument('--format', choices=['markdown', 'openapi', 'postman'], 
                          default='markdown', help='Documentation format')
        parser.add_argument('--output', '-o', help='Output file (prints to stdout if not specified)')
        
    def _add_workflow_args(self, parser: argparse.ArgumentParser):
        """Add arguments for workflow command."""
        parser.add_argument('--port', type=int, default=8080, help='Proxy server port (default: 8080)')
        parser.add_argument('--hosts', nargs='*', help='Target hostnames to capture')
        parser.add_argument('--duration', type=int, default=300, help='Capture duration in seconds (default: 300)')
        parser.add_argument('--output-dir', '-o', required=True, help='Output directory for all generated files')
        parser.add_argument('--languages', nargs='*', choices=['python', 'typescript', 'javascript'], 
                          default=['python', 'typescript'], help='Programming languages to generate SDKs for')
        parser.add_argument('--api-title', help='API title')
        
    def run(self, args: Optional[List[str]] = None):
        """Run the CLI with provided arguments."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            return
            
        setup_logging(parsed_args.verbose)
        
        try:
            if parsed_args.command == 'capture':
                self.cmd_capture(parsed_args)
            elif parsed_args.command == 'analyze':
                self.cmd_analyze(parsed_args)
            elif parsed_args.command == 'generate':
                self.cmd_generate(parsed_args)
            elif parsed_args.command == 'docs':
                self.cmd_docs(parsed_args)
            elif parsed_args.command == 'workflow':
                self.cmd_workflow(parsed_args)
        except KeyboardInterrupt:
            self.logger.info("Operation cancelled by user")
        except Exception as e:
            self.logger.error(f"Error: {e}")
            if parsed_args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
            
    def cmd_capture(self, args):
        """Handle capture command."""
        self.logger.info(f"Starting traffic capture on port {args.port}")
        
        # Create traffic capture instance
        target_hosts = set(args.hosts) if args.hosts else None
        capture = TrafficCapture(
            port=args.port,
            target_hosts=target_hosts,
            output_file=args.output,
            verbose=args.verbose
        )
        
        # Add callback to show progress
        call_count = 0
        def progress_callback(api_call):
            nonlocal call_count
            call_count += 1
            if call_count % 10 == 0:
                self.logger.info(f"Captured {call_count} API calls")
                
        capture.add_callback(progress_callback)
        
        # Start capture
        if not capture.start_capture(background=False if args.duration else True):
            self.logger.error("Failed to start traffic capture")
            return
            
        try:
            if args.duration:
                self.logger.info(f"Capturing for {args.duration} seconds...")
                time.sleep(args.duration)
            else:
                self.logger.info("Capturing traffic... Press Ctrl+C to stop")
                while capture.is_running:
                    time.sleep(1)
        finally:
            capture.stop_capture()
            capture.save_to_file()
            
        self.logger.info(f"Captured {len(capture.captured_calls)} API calls to {args.output}")
        
    def cmd_analyze(self, args):
        """Handle analyze command."""
        self.logger.info(f"Analyzing traffic from {args.input_file}")
        
        # Load captured traffic
        capture = TrafficCapture()
        capture.load_from_file(args.input_file)
        
        if not capture.captured_calls:
            self.logger.error("No API calls found in input file")
            return
            
        # Analyze traffic
        analyzer = RequestAnalyzer()
        api_spec = analyzer.analyze_calls(capture.captured_calls)
        
        # Update API spec with user-provided values
        if args.api_title:
            api_spec.title = args.api_title
        api_spec.version = args.api_version
        
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save API specification
        spec_file = output_dir / "api_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(api_spec.to_dict(), f, indent=2)
        self.logger.info(f"Saved API specification to {spec_file}")
        
        # Generate SDKs for requested languages
        for language in args.languages:
            self.logger.info(f"Generating {language} SDK...")
            self._generate_sdk(api_spec, language, str(output_dir / language))
            
        # Generate documentation
        self.logger.info("Generating documentation...")
        doc_generator = DocumentationGenerator(api_spec)
        
        # Markdown documentation
        markdown_file = output_dir / "README.md"
        doc_generator.generate_markdown(str(markdown_file))
        self.logger.info(f"Generated Markdown documentation: {markdown_file}")
        
        # OpenAPI specification
        openapi_file = output_dir / "openapi.json"
        doc_generator.generate_openapi(str(openapi_file))
        self.logger.info(f"Generated OpenAPI specification: {openapi_file}")
        
        # Postman collection
        postman_file = output_dir / "postman_collection.json"
        doc_generator.generate_postman(str(postman_file))
        self.logger.info(f"Generated Postman collection: {postman_file}")
        
        self.logger.info(f"Analysis complete! Generated files in {output_dir}")
        
    def cmd_generate(self, args):
        """Handle generate command."""
        self.logger.info(f"Generating {args.language} SDK from {args.api_spec}")
        
        # Load API specification
        with open(args.api_spec, 'r') as f:
            spec_data = json.load(f)
            
        # Convert to APISpec object
        api_spec = self._dict_to_api_spec(spec_data)
        
        # Generate SDK
        self._generate_sdk(api_spec, args.language, args.output_dir)
        
        self.logger.info(f"Generated {args.language} SDK in {args.output_dir}")
        
    def cmd_docs(self, args):
        """Handle docs command."""
        self.logger.info(f"Generating {args.format} documentation from {args.api_spec}")
        
        # Load API specification
        with open(args.api_spec, 'r') as f:
            spec_data = json.load(f)
            
        api_spec = self._dict_to_api_spec(spec_data)
        doc_generator = DocumentationGenerator(api_spec)
        
        if args.format == 'markdown':
            content = doc_generator.generate_markdown(args.output)
        elif args.format == 'openapi':
            content = json.dumps(doc_generator.generate_openapi(args.output), indent=2)
        elif args.format == 'postman':
            content = json.dumps(doc_generator.generate_postman(args.output), indent=2)
            
        if not args.output:
            print(content)
        else:
            self.logger.info(f"Generated {args.format} documentation: {args.output}")
            
    def cmd_workflow(self, args):
        """Handle complete workflow command."""
        self.logger.info("Starting complete API reverse engineering workflow")
        
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Capture traffic
        self.logger.info("Step 1: Capturing API traffic...")
        traffic_file = output_dir / "captured_traffic.json"
        
        target_hosts = set(args.hosts) if args.hosts else None
        capture = TrafficCapture(
            port=args.port,
            target_hosts=target_hosts,
            output_file=str(traffic_file),
            verbose=args.verbose
        )
        
        if not capture.start_capture(background=True):
            self.logger.error("Failed to start traffic capture")
            return
            
        try:
            self.logger.info(f"Capturing for {args.duration} seconds... Configure your application to use proxy at localhost:{args.port}")
            time.sleep(args.duration)
        finally:
            capture.stop_capture()
            capture.save_to_file()
            
        if not capture.captured_calls:
            self.logger.error("No API calls were captured. Make sure your application is configured to use the proxy.")
            return
            
        self.logger.info(f"Captured {len(capture.captured_calls)} API calls")
        
        # Step 2: Analyze traffic
        self.logger.info("Step 2: Analyzing captured traffic...")
        analyzer = RequestAnalyzer()
        api_spec = analyzer.analyze_calls(capture.captured_calls)
        
        if args.api_title:
            api_spec.title = args.api_title
            
        # Save API specification
        spec_file = output_dir / "api_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(api_spec.to_dict(), f, indent=2)
            
        # Step 3: Generate SDKs
        self.logger.info("Step 3: Generating SDKs...")
        for language in args.languages:
            self.logger.info(f"Generating {language} SDK...")
            self._generate_sdk(api_spec, language, str(output_dir / f"sdk_{language}"))
            
        # Step 4: Generate documentation
        self.logger.info("Step 4: Generating documentation...")
        doc_generator = DocumentationGenerator(api_spec)
        
        doc_generator.generate_markdown(str(output_dir / "README.md"))
        doc_generator.generate_openapi(str(output_dir / "openapi.json"))
        doc_generator.generate_postman(str(output_dir / "postman_collection.json"))
        
        self.logger.info(f"""
Workflow complete! Generated files:
- API Specification: {spec_file}
- Documentation: {output_dir / 'README.md'}
- OpenAPI Spec: {output_dir / 'openapi.json'}
- Postman Collection: {output_dir / 'postman_collection.json'}
- SDKs: {', '.join([str(output_dir / f'sdk_{lang}') for lang in args.languages])}

Summary:
- Endpoints discovered: {len(api_spec.endpoints)}
- Authentication methods: {len(api_spec.auth_patterns)}
- Languages generated: {', '.join(args.languages)}
        """)
        
    def _generate_sdk(self, api_spec: APISpec, language: str, output_dir: str):
        """Generate SDK for a specific language."""
        generators = {
            'python': PythonGenerator,
            'typescript': TypeScriptGenerator,
            'javascript': JavaScriptGenerator
        }
        
        generator_class = generators.get(language)
        if not generator_class:
            raise ValueError(f"Unsupported language: {language}")
            
        generator = generator_class(api_spec)
        files = generator.generate(output_dir)
        
        self.logger.info(f"Generated {len(files)} files for {language} SDK")
        
    def _dict_to_api_spec(self, data: dict) -> APISpec:
        """Convert dictionary to APISpec object."""
        # This is a simplified conversion - in a full implementation,
        # you'd need to properly reconstruct all the nested objects
        from .types import APISpec, Endpoint, HTTPMethod
        
        api_spec = APISpec(
            base_url=data.get('base_url', ''),
            title=data.get('title', 'Generated API'),
            version=data.get('version', '1.0.0'),
            description=data.get('description', '')
        )
        
        # Convert endpoints (simplified)
        for ep_data in data.get('endpoints', []):
            endpoint = Endpoint(
                path=ep_data['path'],
                method=HTTPMethod(ep_data['method']),
                summary=ep_data.get('summary'),
                description=ep_data.get('description')
            )
            api_spec.endpoints.append(endpoint)
            
        return api_spec


def main():
    """Main entry point for the CLI."""
    cli = APIReverseEngineerCLI()
    cli.run()


if __name__ == '__main__':
    main()