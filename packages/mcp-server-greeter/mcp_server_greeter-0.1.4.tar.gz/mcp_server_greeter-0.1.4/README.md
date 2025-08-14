# MCP Server Greeter

A minimal [Model Context Protocol](https://modelcontextprotocol.io) server that exposes one tool: `greet(name)`.

## 🚀 Usage

Run without installing permanently:
```bash
uvx mcp-server-greeter
```

Or install and run:
```bash
pip install mcp-server-greeter
mcp-server-greeter
```

The server will start and wait for MCP clients (like `McpWorkbench`) to connect.

## 🛠 Tool List
- **greet(name: str)** → Returns `"Hello, <name>!"`

## 📦 Installation from source
```bash
git clone https://github.com/Adonpm/mcp-server-greeter
cd mcp-server-greeter
pip install .
```

## 📜 License
This project is licensed under the MIT License.
