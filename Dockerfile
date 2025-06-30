FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for database clients
RUN apt-get update && apt-get install -y --no-install-recommends \
    # MySQL dependencies
    default-libmysqlclient-dev \
    pkg-config \
    # PostgreSQL dependencies
    libpq-dev \
    # MSSQL dependencies
    freetds-dev \
    freetds-bin \
    # General build tools
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files
COPY . /app

# Install the project dependencies
RUN pip install --no-cache-dir .

# The database connection parameters should be provided at runtime
# Example environment variables (these will be overridden at runtime)
ENV DB_TYPE="pg"
ENV DB_CONFIG='{"host":"localhost","port":5432,"user":"username","password":"password","dbname":"database_name"}'

# Expose the default MCP server port
EXPOSE 8080

# Set the entrypoint command to run the MCP server
ENTRYPOINT ["database-mcp"] 
