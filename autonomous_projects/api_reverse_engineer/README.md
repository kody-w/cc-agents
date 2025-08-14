# Automated API Reverse Engineering Tool

A comprehensive tool for capturing API traffic and automatically generating fully-typed client libraries in multiple programming languages with complete documentation.

## 🚀 Features

- **Traffic Capture**: Intercept HTTP(S) requests using mitmproxy
- **Pattern Analysis**: Automatically detect API patterns, authentication methods, and rate limiting
- **Type Inference**: Infer types from API responses and generate proper schemas
- **Multi-language SDK Generation**: Generate SDKs for Python, TypeScript, and JavaScript
- **Documentation Generation**: Create Markdown docs, OpenAPI specs, and Postman collections
- **CLI Interface**: Complete command-line interface for all operations
- **Production Ready**: Comprehensive error handling, logging, and testing

## 📁 Project Structure

```
api_reverse_engineer/
├── src/                          # Main source code
│   ├── capture.py                # Traffic capture using mitmproxy
│   ├── analyzer.py               # Request/response analysis
│   ├── types.py                  # Type definitions
│   ├── cli.py                    # Command-line interface
│   ├── documentation.py          # Documentation generation
│   ├── exceptions.py             # Custom exceptions
│   ├── generators/               # SDK generators
│   │   ├── base_generator.py     # Base generator class
│   │   ├── python_generator.py   # Python SDK generator
│   │   ├── typescript_generator.py # TypeScript SDK generator
│   │   └── javascript_generator.py # JavaScript SDK generator
│   └── __init__.py
├── tests/                        # Unit tests
│   ├── test_types.py
│   ├── test_analyzer.py
│   ├── test_generators.py
│   ├── test_documentation.py
│   └── test_cli.py
├── examples/                     # Examples and integration tests
│   ├── sample_api_server.py      # Sample Flask API for testing
│   ├── basic_usage.py            # Basic usage examples
│   └── integration_test.py       # Full integration test
├── docs/                         # Documentation
├── requirements.txt              # Python dependencies
├── run_tests.py                  # Test runner
└── README.md                     # This file
```

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd api_reverse_engineer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python run_tests.py
   ```

## 🔧 Quick Start

### Command Line Usage

#### 1. Complete Workflow (Recommended)
```bash
# Capture traffic, analyze, and generate everything
python -m src.cli workflow \
    --port 8080 \
    --duration 300 \
    --output-dir ./output \
    --languages python typescript \
    --api-title "My API"
```

#### 2. Step-by-Step Process

**Capture Traffic:**
```bash
python -m src.cli capture \
    --port 8080 \
    --output captured_traffic.json \
    --duration 60
```

**Analyze and Generate:**
```bash
python -m src.cli analyze \
    captured_traffic.json \
    --output-dir ./sdks \
    --languages python typescript javascript
```

**Generate Documentation:**
```bash
python -m src.cli docs api_spec.json \
    --format markdown \
    --output api_documentation.md
```

### Programmatic Usage

```python
from src.capture import TrafficCapture
from src.analyzer import RequestAnalyzer
from src.generators import PythonGenerator
from src.documentation import DocumentationGenerator

# 1. Capture traffic
capture = TrafficCapture(port=8080)
capture.start_capture()
# ... make API calls through proxy ...
capture.stop_capture()

# 2. Analyze traffic
analyzer = RequestAnalyzer()
api_spec = analyzer.analyze_calls(capture.captured_calls)

# 3. Generate SDK
generator = PythonGenerator(api_spec)
files = generator.generate("./python_sdk")

# 4. Generate documentation
doc_gen = DocumentationGenerator(api_spec)
markdown = doc_gen.generate_markdown("./api_docs.md")
```

## 📋 Usage Examples

### Example 1: Analyze a REST API

1. **Start the sample API server:**
   ```bash
   python examples/sample_api_server.py
   ```

2. **Run the complete workflow:**
   ```bash
   python -m src.cli workflow \
       --port 8080 \
       --duration 60 \
       --output-dir ./my_api_analysis \
       --languages python typescript
   ```

3. **Configure your application to use proxy:**
   - Set HTTP proxy to `localhost:8080`
   - Make API calls normally
   - The tool will capture and analyze all traffic

### Example 2: Analyze Existing Traffic

```bash
# If you have captured traffic in a JSON file
python -m src.cli analyze existing_traffic.json \
    --output-dir ./analysis_results \
    --api-title "Existing API" \
    --languages python javascript
```

### Example 3: Generate Documentation Only

```bash
python -m src.cli docs api_specification.json \
    --format openapi \
    --output openapi_spec.json
```

## 🎯 Key Capabilities

### Traffic Analysis
- **Authentication Detection**: Automatically detects Bearer tokens, API keys, Basic auth
- **Rate Limiting**: Identifies rate limit headers and patterns
- **Parameter Analysis**: Infers required vs optional parameters
- **Type Inference**: Determines parameter and response types from actual data
- **Path Normalization**: Groups similar endpoints (e.g., `/users/123` and `/users/456`)

### SDK Generation
- **Python**: Full typing support with dataclasses and type hints
- **TypeScript**: Complete type definitions and interfaces
- **JavaScript**: JSDoc annotations and modern async/await syntax
- **Features**: Error handling, authentication, request/response typing

### Documentation
- **Markdown**: Human-readable API documentation with examples
- **OpenAPI 3.0**: Machine-readable API specification
- **Postman**: Collection for API testing and exploration
- **Examples**: cURL, Python, JavaScript examples for each endpoint

## 🧪 Testing

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Types
```bash
# Unit tests only
python -m unittest discover tests

# Integration test
python examples/integration_test.py

# Basic usage example
python examples/basic_usage.py
```

## 🔧 Configuration

### Traffic Capture Options
- **Port**: Proxy server port (default: 8080)
- **Target Hosts**: Specific hosts to capture (default: all)
- **Output Format**: JSON file format for captured data
- **Filters**: Include/exclude specific paths or methods

### Analysis Options
- **Type Inference**: Automatic type detection from JSON responses
- **Pattern Detection**: Group similar endpoints and detect patterns
- **Authentication**: Detect and categorize auth methods
- **Rate Limiting**: Extract rate limit information from headers

### Generation Options
- **Languages**: Choose from Python, TypeScript, JavaScript
- **Templates**: Customizable code generation templates
- **Naming**: Configurable naming conventions
- **Documentation**: Include examples and comprehensive docs

## 🐛 Troubleshooting

### Common Issues

**1. Proxy Connection Issues**
```bash
# Check if port is available
netstat -ln | grep :8080

# Try different port
python -m src.cli capture --port 8081 --output traffic.json
```

**2. SSL/TLS Issues**
```bash
# Install mitmproxy certificate
~/.mitmproxy/mitmproxy-ca-cert.pem
```

**3. No Traffic Captured**
- Ensure your application is configured to use the proxy
- Check firewall settings
- Verify the target hosts filter

**4. Analysis Errors**
```bash
# Run with verbose logging
python -m src.cli analyze traffic.json --output-dir ./output -v
```

### Debug Mode
```bash
# Enable verbose logging for all commands
python -m src.cli --verbose <command>
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes and add tests**
4. **Run the test suite**: `python run_tests.py`
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests in watch mode
python run_tests.py

# Run linting
flake8 src tests examples
```

## 📊 Generated Output Examples

### Generated Python SDK
```python
from api_client import MyAPIClient

client = MyAPIClient(token="your-bearer-token")
users = client.get_users(limit=10, offset=0)
user = client.get_users_id("123", include="posts")
```

### Generated TypeScript SDK
```typescript
import { MyAPIClient } from './client';

const client = new MyAPIClient({ token: 'your-bearer-token' });
const users = await client.getUsers({ limit: 10, offset: 0 });
const user = await client.getUsersId('123', { include: 'posts' });
```

### Generated Documentation
- **Markdown**: Complete API documentation with examples
- **OpenAPI**: Industry-standard API specification
- **Postman**: Ready-to-use collection for testing

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **mitmproxy**: For excellent HTTP(S) traffic interception
- **requests**: For reliable HTTP client functionality
- **Flask**: For the sample API server in examples

## 📈 Roadmap

- [ ] Support for GraphQL APIs
- [ ] WebSocket traffic capture
- [ ] Additional language generators (Go, Rust, Java)
- [ ] Advanced authentication patterns (OAuth2, JWT)
- [ ] API versioning detection
- [ ] Performance metrics and optimization suggestions
- [ ] Integration with CI/CD pipelines
- [ ] Real-time traffic analysis dashboard

---

**Built with ❤️ by Claude Code Agent**

For questions, issues, or contributions, please open an issue on GitHub.
