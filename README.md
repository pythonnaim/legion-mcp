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

| Database | DB_TYPE code |
|----------|--------------|
| PostgreSQL | pg |
| Redshift | redshift |
| CockroachDB | cockroach |
| MySQL | mysql |
| RDS MySQL | rds_mysql |
| Microsoft SQL Server | mssql |
| Big Query | bigquery |
| Oracle DB | oracle |
| SQLite | sqlite |

We use Legion Query Runner library as connectors. You can find more info on their [api doc](https://theralabs.github.io/legion-database/docs/category/query-runners).

## What is MCP?

The Model Context Protocol (MCP) is a specification for maintaining context in AI applications. This server uses the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) to:

- Expose database operations as tools for AI assistants
- Provide database schemas and metadata as resources
- Generate useful prompts for database operations
- Enable stateful interactions with databases

## Installation & Configuration

### Required Parameters

Two parameters are required for all installation methods:

- **DB_TYPE**: The database type code (see table above)
- **DB_CONFIG**: A JSON configuration string for database connection

The DB_CONFIG format varies by database type. See the [API documentation](https://theralabs.github.io/legion-database/docs/category/query-runners) for database-specific configuration details.

### Installation Methods

#### Option 1: Using UV (Recommended)

When using [`uv`](https://docs.astral.sh/uv/), no specific installation is needed. We will use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *database-mcp*.

**UV Configuration Example:**

```json





REPLACE DB_TYPE and DB_CONFIG with your connection info.
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

#### Option 2: Using PIP

Install via pip:

```bash
pip install database-mcp
```

**PIP Configuration Example:**

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
      }
    }
  }
}
```

## Running the Server

### Development Mode

```bash
mcp dev mcp_server.py
```

### Production Mode

```bash
python mcp_server.py
```

### Configuration Methods

#### Environment Variables

```bash
export DB_TYPE="pg"  # or mysql, postgresql, etc.
export DB_CONFIG='{"host":"localhost","port":5432,"user":"username","password":"password","dbname":"database_name"}'
mcp dev mcp_server.py
```

#### Command Line Arguments

```bash
python mcp_server.py --db-type pg --db-config '{"host":"localhost","port":5432,"user":"username","password":"password","dbname":"database_name"}'
```

Or with UV:

```bash
uv mcp_server.py --db-type pg --db-config '{"host":"localhost","port":5432,"user":"username","password":"password","dbname":"database_name"}'
```

## Exposed MCP Capabilities

### Resources

| Resource | Description |
|----------|-------------|
| `schema://all` | Get the complete database schema |

### Tools

| Tool | Description |
|------|-------------|
| `execute_query` | Execute a SQL query and return results as a markdown table |
| `execute_query_json` | Execute a SQL query and return results as JSON |
| `get_table_columns` | Get column names for a specific table |
| `get_table_types` | Get column types for a specific table |
| `get_query_history` | Get the recent query history |

### Prompts

| Prompt | Description |
|--------|-------------|
| `sql_query` | Create an SQL query against the database |
| `explain_query` | Explain what a SQL query does |
| `optimize_query` | Optimize a SQL query for better performance |

## Development

### Testing

```bash
uv pip install -e ".[dev]"
pytest
```

### Publishing

```bash
rm -rf dist/ build/ *.egg-info/ && python -m build
python -m build
python -m twine upload dist/*
```

## License

This repository is licensed under GPL