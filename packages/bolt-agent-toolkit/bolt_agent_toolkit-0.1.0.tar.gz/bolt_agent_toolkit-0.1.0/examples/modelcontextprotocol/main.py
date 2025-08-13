#!/usr/bin/env python3
"""
Bolt Agent Toolkit MCP Example

A minimal example showing how to use BoltAgentToolkit with FastMCP.
"""

import asyncio
import os

from dotenv import load_dotenv

from bolt_agent_toolkit.configuration import Configuration, Context
from bolt_agent_toolkit.modelcontextprotocol.toolkit import BoltAgentToolkit

load_dotenv()


async def main():
    """Main function demonstrating BoltAgentToolkit MCP usage."""

    print("🚀 Bolt Agent Toolkit MCP Example")
    print("=" * 50)

    # Create configuration
    configuration = Configuration(
        context=Context(
            api_key=os.getenv("BOLT_API_KEY"),
            publishable_key=os.getenv("BOLT_PUBLISHABLE_KEY"),
            base_url=os.getenv("BOLT_BASE_URL", "https://api.bolt.com"),
            timeout=float(os.getenv("BOLT_TIMEOUT", "30.0")),
            environment=os.getenv("BOLT_ENVIRONMENT", "production"),
        ),
    )

    print("✅ Configuration created")

    # Create BoltAgentToolkit instance
    bolt_toolkit = BoltAgentToolkit(
        api_key=os.getenv("BOLT_API_KEY"),
        tools=[
            "products.read",
            "products.create",
            "subscriptions.read",
            "subscriptions.update",
            "subscriptions.delete",
            "plans.read",
        ],
        configuration=configuration,
    )

    print("✅ BoltAgentToolkit created")

    # List available tools
    print("\n🔧 Available Tools:")
    print("-" * 30)
    tools = await bolt_toolkit.get_tools()
    for _, tool in tools.items():
        print(f"• {tool.name}: {tool.description}")

    print(f"\n📊 Total tools: {len(tools)}")

    print("\n🎯 MCP Server Ready!")
    print("The BoltAgentToolkit is now ready to be used as an MCP server.")
    print("You can connect to it using any MCP client.")

    # Start the MCP server (this would normally run indefinitely)
    print("\n🚀 Starting MCP Server...")
    print("Press Ctrl+C to stop")

    try:
        await bolt_toolkit.run_http_async()
        # await bolt_toolkit.run()
    except KeyboardInterrupt:
        print("\n👋 MCP Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
