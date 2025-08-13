# Product Reader Example

This example shows how to use the Bolt Agent Toolkit with OpenAI to create an agent that can fetch product information from the Bolt API.

## Setup

1. Copy `.env.template` to `.env` and populate it with the relevant values.

```bash
OPENAI_API_KEY=your_openai_api_key
BOLT_API_KEY=your_bolt_api_key
BOLT_PUBLISHABLE_KEY=your_bolt_publishable_key
BOLT_BASE_URL=https://api.bolt.com
BOLT_TIMEOUT=30.0
BOLT_ENVIRONMENT=production
```

## Usage

```bash
python main.py
```
