# Database MCP Server (by Legion AI)

A server that helps people access and query data in databases using the Legion Query Runner with integration of the Model Context Protocol (MCP) Python SDK.

## Features

- Database access via Legion Query Runner
- Model Context Protocol (MCP) support for AI assistants
- Expose database operations as MCP resources, tools, and prompts
- Multiple deployment options (standalone MCP server, FastAPI integration)
- Query execution and result handling
- Flexible configuration via environment variables, command-line arguments, or MCP settings JSON

## Supported Databases

PostgreSQL
Redshift
CockroachDB
MySQL
RDS MySQL
Microsoft SQL Server
Big Query
Oracle DB
SQLite


## What is MCP?

The Model Context Protocol (MCP) is a specification for maintaining context in AI applications. This server uses the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) to:

- Expose database operations as tools for AI assistants
- Provide database schemas and metadata as resources
- Generate useful prompts for database operations
- Enable stateful interactions with databases

## Installation

### Using UV (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *database-mcp*.

### Using PIP

Alternatively you can install `database-mcp` via pip:

```bash
pip install database-mcp
```

```json

### UV Configuration
{
    "mcpServers": {
      "database-mcp": {
        "command": "uvx",
        "args": [
          "database-mcp"
        ],
        "env": {
          "DB_TYPE": "pg",
          "DB_CONFIG": "{\"host\":\"localhost\",\"port\":5432,\"user\":\"user\",\"password\":\"pw\",\"dbname\":\"dbname\"}"
        },
        "disabled": true,
        "autoApprove": []
      }
    }
}
```

### Pip Configuration


```json
{
"mcpServers": {
  "database": {
    "command": "python",
    "args": [
      "-m", "database_mcp", 
      "--repository", "path/to/git/repo"
    ],
    "env": {
        "DB_TYPE": "pg",
        "DB_CONFIG": "{\"host\":\"localhost\",\"port\":5432,\"user\":\"user\",\"password\":\"pw\",\"dbname\":\"dbname\"}"
    },
  }
}
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
rm -rf dist/ build/ *.egg-info/ && python -m build
python -m build
python -m twine upload dist/*
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

This repository is licensed under GPL