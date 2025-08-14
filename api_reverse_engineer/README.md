# API Reverse Engineering Tool 🔍

Automatically generate fully-typed SDK clients in Python, TypeScript, and Go from captured API network traffic. Simply record your API calls and get production-ready client libraries!

## Features ✨

- **Automatic Type Inference**: Analyzes request/response payloads to generate accurate type definitions
- **Multi-Language Support**: Generates SDKs for Python, TypeScript, and Go
- **Smart Endpoint Detection**: Groups similar API calls and identifies path parameters
- **HAR File Support**: Works with standard HAR exports from browser DevTools
- **Zero Configuration**: Just point it at your traffic and get working SDKs

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd api_reverse_engineer

# Install dependencies (Python 3.7+)
pip install -r requirements.txt
```

## Quick Start 🚀

### 1. Capture API Traffic

Open your browser's DevTools:
1. Go to Network tab
2. Perform the API operations you want to capture
3. Right-click → "Save all as HAR with content"
4. Save as `api_traffic.har`

### 2. Generate SDKs

```bash
python cli.py --har api_traffic.har --name "YourAPI"
```

### 3. Use Your Generated SDKs

**Python:**
```python
from your_api_client import YourAPIClient

client = YourAPIClient()
client.set_auth_token("your-token")
users = client.list_users(page=1, limit=10)
```

**TypeScript:**
```typescript
import { YourAPIClient } from './YourAPIClient';

const client = new YourAPIClient();
client.setAuthToken('your-token');
const users = await client.listUsers({ page: 1, limit: 10 });
```

**Go:**
```go
client := NewYourAPIClient("https://api.example.com")
client.SetAuthToken("your-token")
users, err := client.ListUsers()
```

## How It Works 🛠️

1. **Traffic Parsing**: Reads HAR files or JSON traffic data
2. **Pattern Detection**: Identifies API endpoints and extracts path parameters
3. **Type Inference**: Analyzes JSON payloads to determine data types
4. **Schema Merging**: Combines multiple requests to build complete type definitions
5. **Code Generation**: Creates idiomatic SDKs for each target language

## CLI Options

```bash
python cli.py [options]

Input Options:
  --har FILE           HAR file containing API traffic
  --json FILE          JSON file with traffic data
  --capture            Live capture mode (experimental)

Configuration:
  --name NAME          Name for the generated SDK (required)
  --base-url URL       Override the API base URL
  --languages LANGS    Languages to generate (python, typescript, go, all)
  --output DIR         Output directory (default: generated_sdks)
  --verbose            Enable verbose output

Examples:
  # Generate all SDKs from HAR file
  python cli.py --har traffic.har --name "MyAPI"
  
  # Generate only Python SDK
  python cli.py --har traffic.har --name "MyAPI" --languages python
  
  # Override base URL
  python cli.py --har traffic.har --name "MyAPI" --base-url https://api.prod.com
```

## Architecture

```
api_reverse_engineer/
├── traffic_parser.py      # Core parsing and type inference
├── sdk_generator.py       # Base SDK generation logic
├── python_generator.py    # Python-specific code generation
├── typescript_generator.py # TypeScript-specific generation
├── go_generator.py        # Go-specific generation
├── cli.py                # Command-line interface
└── generated_sdks/       # Output directory
    ├── python/
    ├── typescript/
    └── go/
```

## Type Inference Examples

The tool automatically infers types from JSON data:

- `"123"` → `integer`
- `"hello"` → `string`
- `"2024-01-15T10:30:00Z"` → `string` with `date-time` format
- `"user@example.com"` → `string` with `email` format
- `[1, 2, 3]` → `array` of `integer`
- UUID patterns → Recognized as path parameters

## Advanced Features

### Path Parameter Detection
- Numeric IDs: `/users/123` → `/users/{id}`
- UUIDs: `/posts/550e8400-e29b-41d4-a716-446655440000` → `/posts/{uuid}`
- MongoDB ObjectIds: `/items/507f1f77bcf86cd799439011` → `/items/{objectId}`

### Schema Merging
Multiple requests to the same endpoint are analyzed to build comprehensive type definitions, marking optional fields appropriately.

### Smart Method Naming
- `GET /users` → `list_users()`
- `GET /users/123` → `get_user(id)`
- `POST /users` → `create_user(data)`
- `PUT /users/123` → `update_user(id, data)`
- `DELETE /users/123` → `delete_user(id)`

## Limitations

- Requires at least one successful request/response for each endpoint
- Authentication tokens are not automatically extracted
- WebSocket and GraphQL APIs are not yet supported
- Binary payloads are not analyzed

## Contributing

Contributions are welcome! Areas for improvement:
- Live traffic capture via mitmproxy
- Additional language targets (Java, C#, Ruby)
- GraphQL support
- OpenAPI spec generation
- Better handling of nested resources

## License

MIT