# Database MCP Server (by Legion AI)

A server that helps people access and query data in databases using the Legion Query Runner with integration of the Model Context Protocol (MCP) Python SDK.

# Start Generation Here
This tool is provided by [Legion AI](https://thelegionai.com/). To use the full-fledged and fully powered AI data analytics tool, please visit the site. Email us if there is one database you want us to support.
# End Generation Here

## Features

- Multi-database support - connect to multiple databases simultaneously
- Database access via Legion Query Runner
- Model Context Protocol (MCP) support for AI assistants
- Expose database operations as MCP resources, tools, and prompts
- Multiple deployment options (standalone MCP server, FastAPI integration)
- Query execution and result handling
- Flexible configuration via environment variables, command-line arguments, or MCP settings JSON
- User-driven database selection for multi-database setups

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

For single database configuration:
- **DB_TYPE**: The database type code (see table above)
- **DB_CONFIG**: A JSON configuration string for database connection

For multi-database configuration:
- **DB_CONFIGS**: A JSON array of database configurations, each containing:
  - **db_type**: The database type code
  - **configuration**: Database connection configuration
  - **description**: A human-readable description of the database

The configuration format varies by database type. See the [API documentation](https://theralabs.github.io/legion-database/docs/category/query-runners) for database-specific configuration details.

### Installation Methods

#### Option 1: Using UV (Recommended)

When using [`uv`](https://docs.astral.sh/uv/), no specific installation is needed. We will use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *database-mcp*.

**UV Configuration Example (Single Database):**

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

**UV Configuration Example (Multiple Databases):**

```json
{
    "mcpServers": {
      "database-mcp": {
        "command": "uvx",
        "args": [
          "database-mcp"
        ],
        "env": {
          "DB_CONFIGS": "[{\"db_type\":\"pg\",\"configuration\":{\"host\":\"localhost\",\"port\":5432,\"user\":\"user\",\"password\":\"pw\",\"dbname\":\"postgres\"},\"description\":\"PostgreSQL Database\"},{\"db_type\":\"mysql\",\"configuration\":{\"host\":\"localhost\",\"port\":3306,\"user\":\"root\",\"password\":\"pass\",\"database\":\"mysql\"},\"description\":\"MySQL Database\"}]"
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

**PIP Configuration Example (Single Database):**

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

### Production Mode

```bash
python mcp_server.py
```

### Configuration Methods

#### Environment Variables (Single Database)

```bash
export DB_TYPE="pg"  # or mysql, postgresql, etc.
export DB_CONFIG='{"host":"localhost","port":5432,"user":"username","password":"password","dbname":"database_name"}'
mcp dev mcp_server.py
```

#### Environment Variables (Multiple Databases)

```bash
export DB_CONFIGS='[{"db_type":"pg","configuration":{"host":"localhost","port":5432,"user":"username","password":"password","dbname":"database_name"},"description":"PostgreSQL Database"},{"db_type":"mysql","configuration":{"host":"localhost","port":3306,"user":"root","password":"pass","database":"mysql"},"description":"MySQL Database"}]'
mcp dev mcp_server.py
```

#### Command Line Arguments (Single Database)

```bash
python mcp_server.py --db-type pg --db-config '{"host":"localhost","port":5432,"user":"username","password":"password","dbname":"database_name"}'
```

#### Command Line Arguments (Multiple Databases)

```bash
python mcp_server.py --db-configs '[{"db_type":"pg","configuration":{"host":"localhost","port":5432,"user":"username","password":"password","dbname":"database_name"},"description":"PostgreSQL Database"},{"db_type":"mysql","configuration":{"host":"localhost","port":3306,"user":"root","password":"pass","database":"mysql"},"description":"MySQL Database"}]'
```

## Multi-Database Support

When connecting to multiple databases, you need to specify which database to use for each query:

1. Use the `list_databases` tool to see available databases with their indices
2. Use `get_database_info` to view schema details of databases
3. Use `find_table` to locate a table across all databases
4. Provide the `db_index` parameter to tools like `execute_query`, `get_table_columns`, etc.

The `select_database` prompt guides users through the database selection process.

## Exposed MCP Capabilities

### Resources

| Resource | Description |
|----------|-------------|
| `schema://all` | Get the schemas for all configured databases |

### Tools

| Tool | Description |
|------|-------------|
| `execute_query` | Execute a SQL query and return results as a markdown table |
| `execute_query_json` | Execute a SQL query and return results as JSON |
| `get_table_columns` | Get column names for a specific table |
| `get_table_types` | Get column types for a specific table |
| `get_query_history` | Get the recent query history |
| `list_databases` | List all available database connections |
| `get_database_info` | Get detailed information about a database |
| `find_table` | Find which database contains a specific table |

### Prompts

| Prompt | Description |
|--------|-------------|
| `sql_query` | Create an SQL query against the database |
| `explain_query` | Explain what a SQL query does |
| `optimize_query` | Optimize a SQL query for better performance |
| `select_database` | Help user select which database to use |

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