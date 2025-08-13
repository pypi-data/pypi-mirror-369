# SpiderFoot MCP Server

A Model Context Protocol (MCP) server that provides SpiderFoot OSINT automation capabilities to AI assistants and other MCP clients.

## Installation

```bash
pip install spiderfoot-mcp
```

## Configuration

Set the following environment variables or create a `.env` file:

```bash
SPIDERFOOT_URL=http://localhost:5001
SPIDERFOOT_USERNAME=admin
SPIDERFOOT_PASSWORD=your_password
```

## Usage

### As MCP Server

Start the MCP server:

```bash
spiderfoot-mcp
```

The server will expose SpiderFoot functionality as MCP tools that can be used by AI assistants.

### Available Tools

The MCP server provides the following tools:

- `start_scan`: Start a new SpiderFoot scan
- `get_scan_status`: Get the current status of a scan
- `list_scans`: List all scans on the server
- `stop_scan`: Stop a running scan
- `delete_scan`: Delete a scan and its data
- `get_scan_results`: Get results from a scan
- `get_scan_summary`: Get a summary of scan results
- `wait_for_scan_completion`: Wait for a scan to complete
- `export_scan_results`: Export scan results in various formats
- `get_available_modules`: Get list of available SpiderFoot modules
- `search_scan_results`: Search across scan results
- `get_scan_log`: Get log entries for a scan
- `get_active_scans_summary`: Get summary of tracked scans
- `ping`: Test connectivity to SpiderFoot server

### MCP Client Configuration

To use this server with Claude Desktop or other MCP clients, add the following to your MCP configuration:

```json
{
  "mcpServers": {
    "spiderfoot": {
      "command": "spiderfoot-mcp",
      "env": {
        "SPIDERFOOT_URL": "http://localhost:5001",
        "SPIDERFOOT_USERNAME": "admin",
        "SPIDERFOOT_PASSWORD": "your_password"
      }
    }
  }
}
```

## Requirements

- Python 3.8+
- spiderfoot-client>=1.0.0
- fastmcp>=2.10.0
- python-dotenv>=1.0.0
- A running SpiderFoot instance

## Dependencies

This package depends on the `spiderfoot-client` package, which provides the underlying SpiderFoot API client functionality.

## License

MIT License