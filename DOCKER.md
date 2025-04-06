# Docker Guide for Database MCP Server

This document provides instructions for building and running the Database MCP Server using Docker.

## Building the Docker Image

To build the Docker image:

```bash
docker build -t database-mcp .
```

## Running the Docker Container

Run the container with your database configuration:

```bash
docker run -p 5678:5678 \
  -e DB_TYPE="pg" \
  -e DB_CONFIG='{"host":"your-db-host","port":5432,"user":"your-username","password":"your-password","dbname":"your-database"}' \
  database-mcp
```

Replace the values in the `DB_CONFIG` with your actual database connection details.

## Environment Variables

- **DB_TYPE**: Database type code (e.g., "pg" for PostgreSQL, "mysql" for MySQL)
- **DB_CONFIG**: JSON string with database connection parameters

See the main README for a complete list of supported database types and their configuration formats.

## Using with MCP Configuration

In your MCP configuration:

```json
{
  "mcpServers": {
    "database": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-p", "5678:5678",
        "-e", "DB_TYPE=pg",
        "-e", "DB_CONFIG={\"host\":\"localhost\",\"port\":5432,\"user\":\"username\",\"password\":\"password\",\"dbname\":\"database_name\"}",
        "database-mcp"
      ]
    }
  }
}
```

## Using Custom Port

To use a custom port:

```bash
docker run -p 8080:5678 \
  -e DB_TYPE="pg" \
  -e DB_CONFIG='{"host":"your-db-host","port":5432,"user":"your-username","password":"your-password","dbname":"your-database"}' \
  database-mcp
```

In this example, the MCP server will be accessible on port 8080 on your host machine, while it continues to use the default port 5678 internally. 