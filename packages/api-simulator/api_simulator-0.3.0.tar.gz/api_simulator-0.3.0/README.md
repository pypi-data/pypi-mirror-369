# API Simulator

<div align="center">

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.3.0-orange)](https://github.com/yourusername/api-simulator)

**Multi-protocol API mocking made simple** • REST • GraphQL • WebSocket • UDP

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Examples](#examples) • [Contributing](#contributing)

</div>

---

## 🎯 Overview

API Simulator spins up lifelike backends from a single JSON configuration file. Perfect for frontend development, integration testing, and API prototyping without waiting for backend implementation.

### Key Features

- 🚀 **Zero dependencies** - Just Python and a JSON config
- 🔌 **Multi-protocol** - REST, GraphQL, WebSocket, and UDP from one server
- 📝 **Request-aware templating** - Dynamic responses based on headers, query params, and paths
- 🎭 **Realistic behavior** - Rules, delays, errors, and chaos testing
- 📊 **Streaming support** - SSE, NDJSON, and WebSocket broadcasts
- 🔒 **HTTPS/WSS ready** - Built-in TLS support
- 📖 **OpenAPI export** - Auto-generated documentation

## 🚀 Quick Start

### Installation

```bash
pip install -e .
```

### Basic Usage

1. **Create a config file** (`config.json`):

```json
{
  "rest": {
    "port": 3000,
    "path": "/api",
    "apis": [
      {
        "method": "GET",
        "path": "/users/{user_id}",
        "response": {
          "id": "{{ path('user_id') }}",
          "name": "Test User",
          "created": "{{ timestamp() }}"
        }
      }
    ]
  }
}
```

2. **Start the simulator**:

```bash
apisim run --config config.json
```

3. **Test your API**:

```bash
curl http://localhost:3000/api/users/123
```

## 📚 Documentation

### Table of Contents

- [CLI Commands](#cli-commands)
- [Configuration](#configuration)
- [Templating](#templating)
- [Protocols](#protocols)
  - [REST API](#rest-api)
  - [WebSocket](#websocket)
  - [GraphQL](#graphql)
  - [UDP Streaming](#udp-streaming)
- [Advanced Features](#advanced-features)

## 🛠️ CLI Commands

### Server Management

```bash
# Start server
apisim run --config config.json [options]
  --templates templates.json  # Template macros
  --seed 42                   # Deterministic randomness
  --log-level INFO           # Logging level
  --certfile cert.pem        # HTTPS/WSS certificate
  --keyfile key.pem          # HTTPS/WSS key

# Check running servers
apisim status

# Stop servers
apisim stop [--all]

# Validate configuration
apisim validate --config config.json

# Export OpenAPI spec
apisim openapi export --config config.json [--out openapi.json]
```

## ⚙️ Configuration

### REST API

```json
{
  "rest": {
    "port": 3000,
    "path": "/api/v1",
    "apis": [
      {
        "method": "GET",
        "path": "/products/{product_id}",
        "response": {...},      // JSON response
        "text": "plain text",   // Text response
        "file": "path/to/file", // File response
        "binary_b64": "...",    // Binary response
        "stream": {...},        // NDJSON streaming
        "sse": {...},          // Server-Sent Events
        "rules": {...}         // Conditional behavior
      }
    ]
  }
}
```

#### Streaming Responses

**Server-Sent Events (SSE)**:
```json
{
  "method": "GET",
  "path": "/events",
  "sse": {
    "interval": 1,
    "event": "update",
    "template": {"price": "{{ random_float(100,200,2) }}"},
    "count": 10  // null for infinite
  }
}
```

**NDJSON Streaming**:
```json
{
  "method": "GET",
  "path": "/stream",
  "stream": {
    "interval": 0.5,
    "template": {"seq": "{{ counter('seq') }}"},
    "content_type": "application/x-ndjson"
  }
}
```

### WebSocket

```json
{
  "websocket": {
    "port": 9080,
    "path": "/ws",
    "apis": [
      {
        "path": "/events",
        "response": {"type": "ack"},
        "broadcast": {
          "interval": 5,
          "response": {"event": "{{ counter('events') }}"}
        },
        "rules": {
          "message.action == 'subscribe'": {
            "response": {"subscribed": true}
          }
        }
      }
    ]
  }
}
```

### GraphQL

```json
{
  "graphql": {
    "port": 3000,
    "path": "/graphql",
    "queries": [
      {
        "operationName": "GetUser",
        "response": {"user": {"id": "123", "name": "Alice"}}
      }
    ],
    "mutations": [
      {
        "operationName": "CreateUser",
        "response": {"success": true, "id": "{{ uuid4() }}"}
      }
    ],
    "subscriptions": [
      {
        "operationName": "UserUpdates",
        "interval": 2,
        "response": {"user": {"updated": "{{ timestamp() }}"}}
      }
    ]
  }
}
```

### UDP Broadcasting

```json
{
  "udp": {
    "host": "127.0.0.1",
    "port": 5001,
    "apis": [
      {
        "name": "telemetry",
        "broadcast": {
          "interval": 1,
          "response": {"temp": "{{ random_float(20,30,1) }}"}
        }
      }
    ]
  }
}
```

## 🎨 Templating

### Built-in Functions

| Function | Description | Example |
|----------|-------------|---------|
| `{{ timestamp() }}` | ISO 8601 timestamp | `2024-01-15T10:30:00Z` |
| `{{ unix_timestamp() }}` | Unix timestamp | `1705315800` |
| `{{ uuid4() }}` | UUID v4 | `a3bb189e-8bf9-4c90-b8f0-d7d3e7e4d6c1` |
| `{{ random_int(min, max) }}` | Random integer | `{{ random_int(1, 100) }}` |
| `{{ random_float(min, max, decimals) }}` | Random float | `{{ random_float(0, 1, 2) }}` |
| `{{ counter(name, start, step) }}` | Auto-incrementing counter | `{{ counter('order', 1000, 1) }}` |
| `{{ choice([...]) }}` | Random selection | `{{ choice(['A', 'B', 'C']) }}` |

### Request-Aware Templates

Access request data in responses:

```json
{
  "response": {
    "path_param": "{{ path('user_id') }}",
    "query_param": "{{ query('search') }}",
    "header": "{{ header('Authorization') }}",
    "body_field": "{{ body('email') }}",
    "method": "{{ method() }}"
  }
}
```

### Custom Macros

Define reusable templates in `templates.json`:

```json
{
  "functions": {
    "order_id": "counter('order', 1000, 1)",
    "product": "choice(['Widget', 'Gadget', 'Tool'])",
    "price": "random_float(10.0, 100.0, 2)"
  }
}
```

## 🎯 Rules & Conditional Behavior

### Rule Conditions

- **Probability**: `"0.1"` (10% chance)
- **Path equality**: `"path.user_id == '123'"`
- **Query params**: `"query.debug == 'true'"`
- **Headers**: `"header.X-Test == 'yes'"`
- **Body fields**: `"body.amount > 100"`

### Actions

```json
{
  "rules": {
    "query.test == 'error'": {
      "status": 500,
      "response": {"error": "Test error"},
      "headers": {"X-Error": "true"}
    },
    "header.X-Slow == 'true'": {
      "delay": "2s"
    },
    "0.05": {
      "ignore": true  // 5% drop rate
    }
  }
}
```

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific protocols
pytest tests/test_protocols.py::TestRESTProtocol -v
pytest tests/test_e2e_protocols.py -v

# With coverage
pytest tests/ --cov=api_simulator
```

### Test Structure

```
tests/
├── test_cli.py           # CLI command tests
├── test_protocols.py     # Protocol unit tests
└── test_e2e_protocols.py # End-to-end with lifespan
```

## 📖 Examples

### Complete E-Commerce API

See [`examples/config.json`](examples/config.json) for a full example with:
- Product catalog with search
- Order streaming
- Real-time price updates (SSE)
- WebSocket order events
- GraphQL customer queries
- UDP inventory feeds

### Testing Different Protocols

After starting the server with `apisim run --config examples/config.json`:

**REST API Tests:**
```bash
# Basic GET endpoint
curl http://localhost:3000/api/v1/status

# Path parameters, query strings, and headers
curl "http://localhost:3000/api/v1/products/PROD-123?q=search" \
  -H "X-Session-Id: test-session"

# SSE streaming (real-time price updates)
curl -N http://localhost:3000/api/v1/prices/sse

# NDJSON streaming 
curl -N http://localhost:3000/api/v1/stream/orders
```

**GraphQL Tests:**
```bash
# Query
curl -X POST http://localhost:3000/graphql \
  -H "Content-Type: application/json" \
  -d '{"operationName":"GetCustomer"}'

# Mutation
curl -X POST http://localhost:3000/graphql \
  -H "Content-Type: application/json" \
  -d '{"operationName":"CreateOrder"}'

# List available operations
curl http://localhost:3000/openapi.json | jq '.paths."/graphql"'
```

**WebSocket Tests:**
```bash
# Using wscat (npm install -g wscat)
wscat -c ws://localhost:9080/realtime/events
> {"action":"subscribe"}

# Using Python
python3 -c "
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://localhost:9080/realtime/events') as ws:
        await ws.send(json.dumps({'action': 'subscribe'}))
        print(await ws.recv())
asyncio.run(test())
"

# GraphQL Subscriptions
python3 -c "
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://localhost:9080/realtime/graphql') as ws:
        await ws.send(json.dumps({'type': 'connection_init'}))
        print(await ws.recv())
        await ws.send(json.dumps({'id': '1', 'type': 'subscribe', 
                                 'payload': {'operationName': 'PriceUpdates'}}))
        print(await ws.recv())
asyncio.run(test())
"
```

**UDP Listener:**
```bash
python3 -c "
import socket, struct, msgpack
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', 5001))
print('Listening on 127.0.0.1:5001...')
while True:
    pkt, _ = s.recvfrom(65536)
    magic, ts, n = struct.unpack('>IIH', pkt[:10])
    print(f'Magic: 0x{magic:X}, Payload:', msgpack.unpackb(pkt[10:], raw=False))
"
```

## 🔌 API Documentation

When running, access auto-generated API docs at:

- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc
- **OpenAPI JSON**: http://localhost:3000/openapi.json

## 🐳 Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["apisim", "run", "--config", "/config/config.json"]
```

```bash
docker build -t api-simulator .
docker run -p 3000:3000 -p 9080:9080 \
  -v $(pwd)/examples:/config \
  api-simulator
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/api-simulator
cd api-simulator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install with dev dependencies
pip install -e ".[test]"

# Run tests
pytest tests/ -v

# Check code style
ruff check src/
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - REST/GraphQL server
- [websockets](https://websockets.readthedocs.io/) - WebSocket support
- [msgpack](https://msgpack.org/) - Binary serialization
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation

## 📮 Support

- 📧 Email: support@example.com
- 💬 Discord: [Join our server](https://discord.gg/example)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/api-simulator/issues)

---

<div align="center">
Made with ❤️ by the API Simulator Team
</div>