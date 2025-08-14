#!/usr/bin/env python3
"""
Simple Bolt Agent Toolkit with LangChain Example

A minimal example showing how to use BoltAgentToolkit with Ollama.
"""

import os

from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from bolt_agent_toolkit.langchain.toolkit import BoltAgentToolkit

load_dotenv()


def main():
    """Run the Bolt Agent Toolkit example with LangChain."""

    llm = ChatOpenAI(
        model="gpt-4o",
    )

    api_key = os.getenv("BOLT_API_KEY")
    publishable_key = os.getenv("BOLT_PUBLISHABLE_KEY")
    base_url = os.getenv("BOLT_BASE_URL", "https://api.bolt.com")
    timeout = float(os.getenv("BOLT_TIMEOUT", "30.0"))
    environment = os.getenv("BOLT_ENVIRONMENT", "production")

    bolt_agent_toolkit = BoltAgentToolkit(
        api_key=api_key,
        configuration={
            "context": {
                "publishable_key": publishable_key,
                "base_url": base_url,
                "timeout": timeout,
                "environment": environment,
            },
            "actions": {
                "products": {
                    "read": True,
                    "create": True,
                },
                "subscriptions": {
                    "read": True,
                },
                "plans": {
                    "read": True,
                },
            }
        },
    )

    tools = []
    tools.extend(bolt_agent_toolkit.get_tools())

    langgraph_agent_executor = create_react_agent(llm, tools)

    input_state = {
        "messages": """
            List the names of all the products in alphabetical order as a list.
        """,
    }

    output_state = langgraph_agent_executor.invoke(input_state)

    print(output_state["messages"][-1].content)


if __name__ == "__main__":
    main()
