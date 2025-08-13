# AI Spine Python SDK

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/ai-spine-sdk)](https://pypi.org/project/ai-spine-sdk/)

Python SDK for [AI Spine](https://dataframeai.com) - The Stripe for AI Agent Orchestration.

AI Spine provides a powerful platform for orchestrating AI agents and workflows, making it easy to build, deploy, and manage complex AI-powered applications.

## Features

- 🚀 **Simple Integration** - Get started with just a few lines of code
- 🔄 **Flow Execution** - Execute and monitor AI workflows
- 🤖 **Agent Management** - Create and manage AI agents
- ⚡ **Async Support** - Built-in polling and timeout handling
- 🛡️ **Robust Error Handling** - Comprehensive exception hierarchy
- 🔧 **Type Safety** - Full type hints for better IDE support
- 📊 **System Monitoring** - Health checks and metrics

## Installation

```bash
pip install ai-spine-sdk
```

For development dependencies:

```bash
pip install ai-spine-sdk[dev]
```

## Quick Start

```python
from ai_spine import AISpine

# Initialize the client
client = AISpine()

# Execute a flow and wait for completion
result = client.execute_and_wait(
    flow_id="sentiment-analysis",
    input_data={"text": "This product is amazing!"}
)

print(f"Result: {result['output_data']}")
```

## Configuration

### Client Initialization

```python
from ai_spine import AISpine

client = AISpine(
    api_key="your-api-key",  # Optional - currently not required
    base_url="https://custom-api.ai-spine.com",  # Optional
    timeout=30,  # Request timeout in seconds
    max_retries=3,  # Maximum retry attempts
    debug=True  # Enable debug logging
)
```

### Environment Variables

You can also configure the client using environment variables:

```bash
export AI_SPINE_API_KEY="your-api-key"
export AI_SPINE_BASE_URL="https://custom-api.ai-spine.com"
```

## API Reference

### Flow Execution

#### Execute Flow

```python
# Start a flow execution
execution = client.execute_flow(
    flow_id="credit-analysis",
    input_data={
        "customer_id": "CUST-001",
        "loan_amount": 50000
    },
    metadata={"source": "api"}  # Optional metadata
)

print(f"Execution ID: {execution['execution_id']}")
```

#### Get Execution Status

```python
# Check execution status
status = client.get_execution(execution_id="exec-123")
print(f"Status: {status['status']}")
```

#### Wait for Completion

```python
# Wait for execution to complete
result = client.wait_for_execution(
    execution_id="exec-123",
    timeout=300,  # Maximum wait time in seconds
    interval=2  # Polling interval in seconds
)
```

#### Execute and Wait (Convenience Method)

```python
# Execute and wait in one call
result = client.execute_and_wait(
    flow_id="sentiment-analysis",
    input_data={"text": "Great product!"},
    timeout=120
)
```

### Flow Management

```python
# List all flows
flows = client.list_flows()
for flow in flows:
    print(f"{flow['flow_id']}: {flow['name']}")

# Get flow details
flow = client.get_flow("sentiment-analysis")
print(f"Flow: {flow['name']} - {flow['description']}")
```

### Agent Management

```python
# List agents
agents = client.list_agents()

# Create an agent
agent = client.create_agent({
    "name": "Data Processor",
    "type": "processor",
    "configuration": {
        "model": "gpt-4",
        "temperature": 0.7
    }
})

# Delete an agent
success = client.delete_agent("agent-123")
```

### System Operations

```python
# Health check
health = client.health_check()
print(f"System status: {health['status']}")

# Get metrics
metrics = client.get_metrics()
print(f"Total executions: {metrics['executions_total']}")

# Get system status
status = client.get_status()
print(f"Uptime: {status['uptime']} seconds")
```

## Error Handling

The SDK provides a comprehensive exception hierarchy for robust error handling:

```python
from ai_spine import (
    AISpine,
    ValidationError,
    ExecutionError,
    TimeoutError,
    RateLimitError,
    AuthenticationError
)

client = AISpine()

try:
    result = client.execute_and_wait(
        flow_id="analysis",
        input_data={"data": "test"},
        timeout=60
    )
except ValidationError as e:
    print(f"Invalid input: {e}")
except ExecutionError as e:
    print(f"Execution failed: {e}")
    print(f"Execution ID: {e.execution_id}")
except TimeoutError as e:
    print(f"Execution timed out after {e.timeout} seconds")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

## Advanced Usage

### Batch Processing

Process multiple items efficiently:

```python
import concurrent.futures
from ai_spine import AISpine

def process_item(client, item):
    return client.execute_and_wait(
        flow_id="sentiment-analysis",
        input_data=item
    )

client = AISpine()
items = [
    {"text": "Great product!"},
    {"text": "Not satisfied"},
    {"text": "Average experience"}
]

# Parallel processing
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(lambda item: process_item(client, item), items))
```

### Context Manager

Use the client as a context manager for automatic cleanup:

```python
with AISpine() as client:
    result = client.execute_and_wait(
        flow_id="analysis",
        input_data={"data": "test"}
    )
    # Session automatically closed when exiting context
```

### Custom Retry Logic

Implement custom retry strategies:

```python
import time
from ai_spine import AISpine, AISpineError

def execute_with_retry(client, flow_id, input_data, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.execute_and_wait(flow_id, input_data)
        except AISpineError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise
```

## Data Models

The SDK includes data model classes for type-safe operations:

```python
from ai_spine.models import Flow, Execution, Agent

# Parse API responses into model objects
flow_data = client.get_flow("sentiment-analysis")
flow = Flow.from_dict(flow_data)

print(f"Flow: {flow.name}")
print(f"Created: {flow.created_at}")

# Check execution status
execution_data = client.get_execution("exec-123")
execution = Execution.from_dict(execution_data)

if execution.is_successful:
    print(f"Output: {execution.output_data}")
elif execution.is_failed:
    print(f"Error: {execution.error_message}")
```

## Examples

Check the `examples/` directory for complete examples:

- `basic_usage.py` - Simple usage patterns
- `error_handling.py` - Comprehensive error handling
- `batch_processing.py` - Batch and parallel processing

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Dataframe-Consulting/ai-spine-sdk-python.git
cd ai-spine-sdk-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_spine --cov-report=html

# Run specific test file
pytest tests/test_client.py -v
```

### Code Quality

```bash
# Format code
black ai_spine tests

# Lint code
flake8 ai_spine tests

# Type checking
mypy ai_spine
```

### Building and Publishing

```bash
# Build distribution
python -m build

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- **Documentation**: [https://dataframeai.com/docs](https://dataframeai.com/docs)
- **Issues**: [GitHub Issues](https://github.com/Dataframe-Consulting/ai-spine-sdk-python/issues)
- **Email**: support@dataframeai.com

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with ❤️ by the [Dataframe AI](https://dataframeai.com) team
- Inspired by the simplicity of Stripe's SDK design
- Thanks to all contributors and users

---

**Note**: This SDK is currently in beta. APIs may change in future versions. Please report any issues or feedback through GitHub Issues.