# server.py
from mcp.server.fastmcp import FastMCP
# create an MCP server
mcp = FastMCP("Demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a greeting for a given name"""
    return f"Hello, {name}!"

def main() -> None:
    mcp.run(transport="stdio")
