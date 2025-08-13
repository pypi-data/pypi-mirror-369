# Coplay MCP Server

A Model Context Protocol (MCP) server for Coplay, providing Unity Editor integration capabilities through MCP tools.

## Features

- **Unity Project Discovery**: Automatically discover running Unity Editor instances and their project roots
- **Unity Editor State**: Retrieve current Unity Editor state and scene hierarchy information
- **Script Execution**: Execute arbitrary C# scripts within the Unity Editor
- **Log Management**: Access and filter Unity console logs
- **GameObject Hierarchy**: List and filter GameObjects in the scene hierarchy
- **Task Creation**: Create new Coplay tasks directly from MCP clients

## Usage

### As an MCP server

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "coplay-testpypi": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "uvx",
      "args": [
        "coplay-mcp-server@latest"
      ]
    }
  }
}
```

## Available Tools

- `set_unity_project_root` - Set the Unity project root path
- `list_unity_project_roots` - Discover all running Unity Editor instances
- `execute_script` - Execute C# scripts in Unity Editor
- `get_unity_logs` - Retrieve Unity console logs with filtering
- `get_unity_editor_state` - Get current Unity Editor state
- `list_game_objects_in_hierarchy` - List GameObjects with filtering options
- `create_coplay_task` - Create new Coplay tasks

## Development

To launch the server in development mode:

```bash
uv run mcp dev coplay_mcp_server/server.py
```

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Unity Editor with Coplay plugin installed

### Project Structure

- `coplay_mcp_server/server.py` - Main MCP server implementation
- `coplay_mcp_server/unity_client.py` - Unity RPC client for communication
- `coplay_mcp_server/process_discovery.py` - Process discovery utilities
- `pyproject.toml` - Project configuration and dependencies

## License

MIT License - see LICENSE file for details.
