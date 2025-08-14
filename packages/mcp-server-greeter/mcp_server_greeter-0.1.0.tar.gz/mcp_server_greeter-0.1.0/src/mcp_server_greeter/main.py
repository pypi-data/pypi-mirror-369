from mcp.server import Server
import asyncio

server = Server(name="Greeter Server")

@server.tool()
async def greet(name:str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

def main():
    """Entry point for the MCP server."""
    asyncio.run(server.run())
    