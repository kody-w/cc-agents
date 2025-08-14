#!/usr/bin/env python3
"""
API Reverse Engineer CLI
Automatically generates typed SDK clients from network traffic
"""

import argparse
import json
import sys
import os
from typing import Dict, Any
from traffic_parser import TrafficParser
from python_generator import PythonSDKGenerator
from typescript_generator import TypeScriptSDKGenerator
from go_generator import GoSDKGenerator


def main():
    parser = argparse.ArgumentParser(
        description='Generate SDK clients from API network traffic',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate SDKs from a HAR file
  %(prog)s --har api_traffic.har --name "MyAPI" --output ./sdks

  # Generate only Python SDK
  %(prog)s --har api_traffic.har --name "MyAPI" --languages python

  # Generate from JSON traffic data
  %(prog)s --json traffic.json --name "MyAPI" --base-url https://api.example.com

  # Capture live traffic (requires mitmproxy)
  %(prog)s --capture --port 8080 --name "MyAPI" --duration 60
        """
    )
    
    parser.add_argument(
        '--har',
        type=str,
        help='Path to HAR file containing API traffic'
    )
    
    parser.add_argument(
        '--json',
        type=str,
        help='Path to JSON file containing traffic data'
    )
    
    parser.add_argument(
        '--capture',
        action='store_true',
        help='Capture live traffic using mitmproxy (experimental)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Port for capturing live traffic (default: 8080)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Duration in seconds for live capture (default: 60)'
    )
    
    parser.add_argument(
        '--name',
        type=str,
        required=True,
        help='Name of the API for generated SDKs'
    )
    
    parser.add_argument(
        '--base-url',
        type=str,
        help='Override base URL for the API'
    )
    
    parser.add_argument(
        '--languages',
        nargs='+',
        choices=['python', 'typescript', 'go', 'all'],
        default=['all'],
        help='Languages to generate SDKs for (default: all)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='generated_sdks',
        help='Output directory for generated SDKs (default: generated_sdks)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    if not args.har and not args.json and not args.capture:
        parser.error('Please provide either --har, --json, or --capture option')
    
    traffic_parser = TrafficParser()
    endpoints = {}
    
    try:
        if args.har:
            if args.verbose:
                print(f"📝 Parsing HAR file: {args.har}")
            endpoints = traffic_parser.parse_har_file(args.har)
            
        elif args.json:
            if args.verbose:
                print(f"📝 Parsing JSON traffic file: {args.json}")
            with open(args.json, 'r') as f:
                traffic_data = json.load(f)
            endpoints = traffic_parser.parse_raw_traffic(traffic_data)
            
        elif args.capture:
            print(f"🔴 Live capture mode (experimental)")
            print(f"⚠️  This would require mitmproxy integration")
            print(f"💡 For now, please use HAR export from browser DevTools:")
            print(f"   1. Open DevTools Network tab")
            print(f"   2. Perform API calls")
            print(f"   3. Right-click and 'Save all as HAR'")
            print(f"   4. Run: {sys.argv[0]} --har <file.har> --name {args.name}")
            sys.exit(1)
        
        if not endpoints:
            print("❌ No API endpoints detected in the traffic")
            sys.exit(1)
        
        base_url = args.base_url or traffic_parser.base_url
        if not base_url:
            print("❌ Could not determine base URL. Please provide --base-url")
            sys.exit(1)
        
        print(f"\n✨ API Reverse Engineering Results")
        print(f"{'='*50}")
        print(f"📍 Base URL: {base_url}")
        print(f"🔍 Endpoints found: {len(endpoints)}")
        
        if args.verbose:
            print(f"\n📋 Detected Endpoints:")
            for endpoint_key, endpoint in endpoints.items():
                print(f"  • {endpoint.method:6} {endpoint.path_pattern}")
                if endpoint.path_params:
                    print(f"         Path params: {', '.join(endpoint.path_params)}")
                if endpoint.query_params:
                    print(f"         Query params: {', '.join(endpoint.query_params.keys())}")
        
        languages = args.languages
        if 'all' in languages:
            languages = ['python', 'typescript', 'go']
        
        print(f"\n🚀 Generating SDKs for: {', '.join(languages)}")
        print(f"{'='*50}")
        
        generated_files = []
        
        if 'python' in languages:
            print(f"🐍 Generating Python SDK...", end=' ')
            generator = PythonSDKGenerator(args.name, base_url, endpoints)
            output_file = generator.generate(f"{args.output}/python")
            generated_files.append(output_file)
            print(f"✅")
        
        if 'typescript' in languages:
            print(f"📘 Generating TypeScript SDK...", end=' ')
            generator = TypeScriptSDKGenerator(args.name, base_url, endpoints)
            output_file = generator.generate(f"{args.output}/typescript")
            generated_files.append(output_file)
            print(f"✅")
        
        if 'go' in languages:
            print(f"🐹 Generating Go SDK...", end=' ')
            generator = GoSDKGenerator(args.name, base_url, endpoints)
            output_file = generator.generate(f"{args.output}/go")
            generated_files.append(output_file)
            print(f"✅")
        
        print(f"\n🎉 SDK Generation Complete!")
        print(f"{'='*50}")
        print(f"📁 Generated files:")
        for file in generated_files:
            print(f"  • {file}")
        
        print(f"\n💡 Next steps:")
        print(f"  1. Review the generated SDKs in {args.output}/")
        print(f"  2. Test with your API endpoints")
        print(f"  3. Customize as needed")
        
        if 'python' in languages:
            print(f"\n🐍 Python SDK usage:")
            print(f"  cd {args.output}/python")
            print(f"  pip install -r requirements.txt")
            print(f"  # See README.md for usage examples")
        
        if 'typescript' in languages:
            print(f"\n📘 TypeScript SDK usage:")
            print(f"  cd {args.output}/typescript")
            print(f"  npm install")
            print(f"  npm run build")
            print(f"  # See README.md for usage examples")
        
        if 'go' in languages:
            print(f"\n🐹 Go SDK usage:")
            print(f"  cd {args.output}/go")
            print(f"  go mod tidy")
            print(f"  # See README.md for usage examples")
        
    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()