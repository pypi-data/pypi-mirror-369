from mcp.server import Server
import asyncio

server = Server(name="Greeter Server")

async def greet(name:str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

async def main():
    # Register the tool explicitly
    server.register_tool(
        name="greet",
        description="Say hello to someone",
        handler=greet
    )

    # Run the server
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
