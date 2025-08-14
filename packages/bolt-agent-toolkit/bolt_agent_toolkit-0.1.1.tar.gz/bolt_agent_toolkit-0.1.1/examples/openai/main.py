"""
Example usage of Bolt Agent Toolkit with OpenAI.
"""

import os

from agents import Agent, Runner
from dotenv import load_dotenv

from bolt_agent_toolkit.openai.toolkit import BoltAgentToolkit

load_dotenv()

api_key = os.getenv("BOLT_API_KEY")
publishable_key = os.getenv("BOLT_PUBLISHABLE_KEY")
base_url = os.getenv("BOLT_BASE_URL", "https://api.bolt.com")
timeout = float(os.getenv("BOLT_TIMEOUT", "30.0"))
environment = os.getenv("BOLT_ENVIRONMENT", "production")

bolt_agent_toolkit = BoltAgentToolkit(
    api_key=api_key,
    configuration={
        "context": {
            "api_key": api_key,
            "publishable_key": publishable_key,
            "base_url": base_url,
            "timeout": timeout,
            "environment": environment,
        },
        "actions": {
            "products": {
                "read": True
            }
        },
    },
)

agent = Agent(
    name="Product Reader",
    instructions="""
    You are an expert at using the Bolt API to fetch product information.
    """,
    tools=bolt_agent_toolkit.get_tools(),
)


def main():
    result = Runner.run_sync(agent, "Get all product names")
    # result = Runner.run_sync(agent, """
    #     Call the trial method with the following product information:
    #     brand as elixir, name as "potion1", description as "1st potion formula", sku as "i-50012", unit_price as 100, merchant_product_id as "mp-1234567890", merchant_variant_id as "mv-1234567890", plans as [plan1, plan2], images as ["image1", "image2"]
    # """)
    print(result.final_output)


if __name__ == "__main__":
    main()
