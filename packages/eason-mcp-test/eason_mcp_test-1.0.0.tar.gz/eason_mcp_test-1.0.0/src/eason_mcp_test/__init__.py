"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

# %%
from mcp.server.fastmcp import FastMCP
from typing import List, Union

# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(numbers: Union[int, List[int]]) -> int:
    """Sum numbers.

    支持传入单个整数，或 `List[int]`。当为列表时，对列表中所有数字求和。
    """

    def sum_numbers(value: Union[int, List[int]]) -> int:
        if isinstance(value, list):
            return sum(value)
        return int(value)

    return sum_numbers(numbers)


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."


# if __name__ == "__main__":
#     mcp.run(transport="sse")


def main() -> None:
    print("Hello from eason-mcp-test!")
    mcp.run(transport="stdio")
