from mcp.server.fastmcp import FastMCP
import asyncio

mcp = FastMCP("Greeter Server")

@mcp.tool()
async def greet(name:str) -> str:
    """Greet someone by name."""
    return f"Hello, {name.upper()}!"

def main():
    mcp.run(transport='stdio')
