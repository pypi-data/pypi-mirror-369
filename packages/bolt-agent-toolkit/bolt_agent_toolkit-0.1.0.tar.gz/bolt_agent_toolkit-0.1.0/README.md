# Bolt Agent Toolkit - Python

The Bolt Agent Toolkit library provides a BoltAPI tool for integrating with Bolt APIs through function calling. This library is not exhaustive of the entire Bolt API. It is built directly on top of the [Bolt Python SDK][python-sdk].

## Installation (Coming soon)

### Requirements

- [uv][uv-install]

## Usage

## Bolt API

The library needs to be configured with your account's API key which is
available in your [Bolt Dashboard][api-keys].

```python
from bolt_agent_toolkit import BoltAPI, Context

api_key = "your_bolt_api_key"
context = Context(
    api_key=api_key,
    publishable_key="your_bolt_publishable_key",
)

bolt_api = BoltAPI(api_key=api_key, context=context)

products_result = bolt_api.list_products()
print(products_result)
```

## OpenAI

```python
from bolt_agent_toolkit.openai.toolkit import BoltAgentToolkit
```

## Langchain

```python
from bolt_agent_toolkit.langchain.toolkit import BoltAgentToolkit

bolt_agent_toolkit = BoltAgentToolkit(
    api_key="your_bolt_api_key",
    configuration={
        configuration={
            "context": {
                "publishable_key": publishable_key,
            },
        },
        "actions": {
            "products": {
                "read": True,
            },
        },
    },
)
```

## Development

This project uses a Makefile to simplify common development tasks. To see all available targets and their descriptions:

```bash
make
```

### Quick Start

```bash
# Set up the development environment
make setup

# Run tests
make test

# Format and lint code
make lint

# Build the package
make build

# Clean up generated files
make clean
```

### Manual Commands

If you prefer to use `uv` directly:

```bash
# Set up environment and install dependencies
uv sync

# Run tests
uv run -m pytest tests/ -v

# Run individual tools
uv run black bolt_agent_toolkit/
uv run mypy bolt_agent_toolkit/
```

[python-sdk]: https://github.com/BoltApp/Bolt-Python-SDK
[api-keys]: https://merchant.bolt.com/administration/api-keys
[uv-install]: https://docs.astral.sh/uv/getting-started/installation/
