# Legion MCP (Model Context Protocol) Server

A server that helps people access and query data in databases using the Legion Query Runner with integration of the Model Context Protocol (MCP) Python SDK.

## Features

- Database access via Legion Query Runner
- Model Context Protocol (MCP) support for AI assistants
- Expose database operations as MCP resources, tools, and prompts
- Multiple deployment options (standalone MCP server, FastAPI integration)
- Query execution and result handling
- Flexible configuration via environment variables, command-line arguments, or MCP settings JSON

## What is MCP?

The Model Context Protocol (MCP) is a specification for maintaining context in AI applications. This server uses the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) to:

- Expose database operations as tools for AI assistants
- Provide database schemas and metadata as resources
- Generate useful prompts for database operations
- Enable stateful interactions with databases

## Setup with uv

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Installation

1. Install uv:
```bash
pip install uv
```

2. Create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# OR
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
uv pip install -e .
```

### Development

To run the server in development mode:
```bash
mcp dev mcp_server.py
```

For production mode:
```bash
python mcp_server.py
```

### Testing

Run tests with:
```bash
uv pip install -e ".[dev]"
pytest
```

### Publish

```bash
uv build
```


```bash
rm -rf dist/ build/ *.egg-info/ && python -m build
python -m build
python -m twine upload dist/*
```
## Standalone FastMCP Server

The simplest approach using the high-level FastMCP API:

```bash
python mcp_server.py
```

This runs a standalone MCP server using the FastMCP class, which provides:
- Easy setup with decorators for resources, tools, and prompts
- Automatic context management
- Lifecycle management via lifespan


## MCP Development

For development with the MCP Inspector tool:

```bash
mcp dev mcp_server.py
```

## MCP Configuration

### Environment Variables

When running with the MCP CLI, you can configure the database connection using environment variables:

```bash
export DB_TYPE="pg"  # or mysql, postgresql, etc.
export DB_CONFIG='{"host":"localhost","port":5432,"user":"username","password":"password","dbname":"database_name"}'
mcp dev mcp_server.py
```

### Command Line Arguments

For direct execution, use command line arguments:

```bash
python mcp_server.py --db-type pg --db-config '{"host":"localhost","port":5432,"user":"username","password":"password","dbname":"database_name"}'
```

or

```bash
uv mcp_server.py --db-type pg --db-config '{"host":"localhost","port":5432,"user":"username","password":"password","dbname":"database_name"}'
```

### MCP Settings JSON

To integrate with AI assistants like Claude, you can configure the MCP server in the settings JSON:

```json
{
  "legion_mcp": {
    "command": "uv",
    "args": [
      "--directory",
      "/path/to/legion-mcp",
      "run",
      "mcp_server.py"
    ],
    "env": {
      "DB_TYPE": "pg",
      "DB_CONFIG": "{\"host\":\"localhost\",\"port\":5432,\"user\":\"username\",\"password\":\"password\",\"dbname\":\"database_name\"}"
    },
    "disabled": false,
    "autoApprove": []
  }
}
```

This configuration:
- Specifies the command to run the server (`uv run mcp_server.py`)
- Sets the working directory (`/path/to/legion-mcp`)
- Provides database connection details via environment variables
- Controls whether the MCP is enabled or disabled
- Can specify actions to auto-approve without user confirmation

Place this configuration in your editor's MCP settings file to enable database access for your AI assistant.

## Exposed MCP Capabilities

### Resources

- `schema://all` - Get the complete database schema

### Tools

- `execute_query` - Execute a SQL query and return results as a markdown table
- `execute_query_json` - Execute a SQL query and return results as JSON
- `get_table_columns` - Get column names for a specific table
- `get_table_types` - Get column types for a specific table
- `get_query_history` - Get the recent query history

### Prompts

- `sql_query` - Create an SQL query against the database
- `explain_query` - Explain what a SQL query does
- `optimize_query` - Optimize a SQL query for better performance

## Development

Run tests:
```bash
pytest
```

## License

This repository is licensed under CC BY-NC-SA 4.0

## Running as an Installed Library

When installed as a library, there are multiple ways to run the database-mcp server:

### 1. Using the Entry Point

If the package is properly installed, you can use the generated entry point:

```bash
database-mcp --db-type pg --db-config '{"host":"localhost","port":5432,"user":"username","password":"password","dbname":"database_name"}'
```

### 2. Using the Python Module Directly

You can also run the module directly:

```bash
python -m database_mcp.mcp_server --db-type pg --db-config '{"host":"localhost","port":5432,"user":"username","password":"password","dbname":"database_name"}'
```

### 3. Importing in Your Code

You can import and use the main function in your own Python code:

```python
from database_mcp import main

# Run the MCP server
main()
```

### 4. For Development

During development, you can use the provided wrapper script:

```bash
./run-database-mcp.py --db-type pg --db-config '{"host":"localhost","port":5432,"user":"username","password":"password","dbname":"database_name"}'
```

This ensures the module is properly found regardless of your Python path configuration.