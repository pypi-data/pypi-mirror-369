from mcp.server.fastmcp import FastMCP
import asyncio

mcp = FastMCP("Greeter Server")

@mcp.tool()
async def greet(name:str) -> str:
    """Greet someone by name."""
    upper_name = name.upper()
    return f"Hello, {upper_name}!"

def main():
    mcp.run(transport='stdio')
