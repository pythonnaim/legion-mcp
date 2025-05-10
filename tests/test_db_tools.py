import pytest
import json
import sys
from unittest.mock import patch, MagicMock

# Create mocks for the MCP modules
class MockContext:
    def __init__(self):
        self.request_context = MagicMock()
        self.request_context.lifespan_context = MagicMock()

class MockFastMCP:
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', 'Mock MCP')
        self.lifespan = kwargs.get('lifespan', None)
        self.resources = {}
        self.tools = {}
        self.prompts = {}
    
    def resource(self, path):
        def decorator(func):
            self.resources[path] = func
            return func
        return decorator
    
    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator
    
    def prompt(self):
        def decorator(func):
            self.prompts[func.__name__] = func
            return func
        return decorator
    
    def run(self):
        pass

# Mock the QueryRunner class
class MockQueryRunner:
    def __init__(self, db_type, configuration):
        self.db_type = db_type
        self.configuration = configuration
    
    def get_schema(self):
        return []
    
    def test_connection(self):
        return True
    
    def run_query(self, query):
        return {
            'columns': [],
            'rows': []
        }
    
    def get_table_columns(self, table_name):
        return []
    
    def get_table_types(self, table_name):
        return {}

# Patch modules before imports
with patch.dict('sys.modules', {
    'mcp.server.fastmcp': MagicMock(FastMCP=MockFastMCP, Context=MockContext),
    'legion_query_runner': MagicMock(QueryRunner=MockQueryRunner)
}):
    from database_mcp.mcp_server import (
        DbConfig,
        get_database_schema_summary,
        list_databases,
        find_table,
        get_database_info
    )

# Define a simple DbConfig class for testing
@pytest.fixture
def db_config_class():
    """Create a DbConfig class for testing"""
    from dataclasses import dataclass
    from typing import Dict, Any, Optional, List
    
    @dataclass
    class DbConfig:
        id: str
        db_type: str
        configuration: Dict[str, Any]
        description: str
        schema: Optional[List[Dict[str, Any]]] = None
        query_runner: Optional[Any] = None
    
    return DbConfig

def test_get_database_schema_summary(monkeypatch):
    """Test get_database_schema_summary function"""
    # Create a mock DbConfig class and instance
    class MockDbConfig:
        def __init__(self, schema=None):
            self.schema = schema
    
    # Test with no schema
    db_config = MockDbConfig()
    summary = get_database_schema_summary(db_config)
    assert summary == "Schema information not available"
    
    # Test with empty tables
    db_config = MockDbConfig(schema=[])
    summary = get_database_schema_summary(db_config)
    assert summary == "No tables found in schema"
    
    # Test with tables
    schema = [
        {
            "name": "users",
            "columns": [
                {"name": "id"},
                {"name": "name"},
                {"name": "email"}
            ]
        },
        {
            "name": "orders",
            "columns": [
                {"name": "id"},
                {"name": "user_id"},
                {"name": "product_id"},
                {"name": "quantity"},
                {"name": "price"},
                {"name": "status"}
            ]
        }
    ]
    db_config = MockDbConfig(schema=schema)
    summary = get_database_schema_summary(db_config)
    assert "- users (id, name, email)" in summary
    assert "- orders (id, user_id, product_id, quantity, price, ...)" in summary

@pytest.fixture
def mock_ctx():
    """Create a mock context with lifespan_context for database tools"""
    mock_ctx = MockContext()
    mock_ctx.request_context.lifespan_context.db_configs = {}
    mock_ctx.request_context.lifespan_context.query_history = []
    return mock_ctx

def test_list_databases(db_config_class, mock_ctx):
    """Test list_databases tool"""
    # Create mock DbConfigs
    db_config1 = db_config_class(
        id="pg_db",
        db_type="pg",
        configuration={"host": "localhost"},
        description="PostgreSQL DB",
        schema=[{"name": "users"}, {"name": "products"}]
    )
    
    db_config2 = db_config_class(
        id="mysql_db",
        db_type="mysql",
        configuration={"host": "localhost"},
        description="MySQL DB",
        schema=[{"name": "customers"}, {"name": "orders"}, {"name": "items"}]
    )
    
    # Set up mock context
    mock_ctx.request_context.lifespan_context.db_configs = {
        "pg_db": db_config1,
        "mysql_db": db_config2
    }
    
    # Call the function
    output = list_databases(mock_ctx)
    
    # Verify output contains database info
    assert "ID: pg_db - PostgreSQL DB (Type: pg)" in output
    assert "ID: mysql_db - MySQL DB (Type: mysql)" in output

def test_list_databases_no_schema(db_config_class, mock_ctx):
    """Test list_databases tool with no schema information"""
    # Create mock DbConfigs
    db_config1 = db_config_class(
        id="pg_db",
        db_type="pg",
        configuration={"host": "localhost"},
        description="PostgreSQL DB"
    )
    
    # Set up mock context
    mock_ctx.request_context.lifespan_context.db_configs = {"pg_db": db_config1}
    
    # Call the function
    output = list_databases(mock_ctx)
    
    # Verify output contains database info without table count
    assert "ID: pg_db - PostgreSQL DB (Type: pg)" in output
    assert "tables" not in output

def test_find_table_found(db_config_class, mock_ctx):
    """Test find_table tool when table is found"""
    # Create schemas with tables
    schema1 = [
        {"name": "users"},
        {"name": "products"}
    ]
    
    schema2 = [
        {"name": "customers"},
        {"name": "orders"}
    ]
    
    # Create mock DbConfigs
    db_config1 = db_config_class(
        id="pg_db",
        db_type="pg",
        configuration={"host": "localhost"},
        description="PostgreSQL DB",
        schema=schema1
    )
    
    db_config2 = db_config_class(
        id="mysql_db",
        db_type="mysql",
        configuration={"host": "localhost"},
        description="MySQL DB",
        schema=schema2
    )
    
    # Set up mock context
    mock_ctx.request_context.lifespan_context.db_configs = {
        "pg_db": db_config1,
        "mysql_db": db_config2
    }
    
    # Call the function
    output = find_table("users", mock_ctx)
    
    # Verify output shows the table was found
    assert "Table 'users' was found in the following databases:" in output
    assert "Database ID: pg_db - PostgreSQL DB" in output

def test_find_table_not_found(db_config_class, mock_ctx):
    """Test find_table tool when table is not found"""
    # Create schema with tables
    schema = [
        {"name": "users"},
        {"name": "products"}
    ]
    
    # Create mock DbConfigs
    db_config1 = db_config_class(
        id="pg_db",
        db_type="pg",
        configuration={"host": "localhost"},
        description="PostgreSQL DB",
        schema=schema
    )
    
    # Set up mock context
    mock_ctx.request_context.lifespan_context.db_configs = {"pg_db": db_config1}
    
    # Call the function
    output = find_table("orders", mock_ctx)
    
    # Verify output shows the table was not found
    assert "Table 'orders' was not found in any database schema." in output

def test_get_database_info(db_config_class, mock_ctx):
    """Test get_database_info tool"""
    # Create schema with tables
    schema = [
        {
            "name": "users",
            "columns": [
                {"name": "id"},
                {"name": "name"},
                {"name": "email"}
            ]
        },
        {
            "name": "products",
            "columns": [
                {"name": "id"},
                {"name": "name"},
                {"name": "price"}
            ]
        }
    ]
    
    # Create mock DbConfigs
    db_config = db_config_class(
        id="pg_db",
        db_type="pg",
        configuration={"host": "localhost"},
        description="PostgreSQL DB",
        schema=schema
    )
    
    # Set up mock context
    mock_ctx.request_context.lifespan_context.db_configs = {"pg_db": db_config}
    
    # Call the function with specific db_id
    output = get_database_info(mock_ctx, db_id="pg_db")
    
    # Verify output contains database info and schema summary
    assert "Database ID: pg_db" in output
    assert "Description: PostgreSQL DB" in output
    assert "Type: pg" in output
    assert "- users (id, name, email)" in output
    assert "- products (id, name, price)" in output

def test_get_database_info_all(db_config_class, mock_ctx):
    """Test get_database_info tool for all databases"""
    # Create schemas
    schema1 = [
        {
            "name": "users",
            "columns": [{"name": "id"}, {"name": "name"}]
        }
    ]
    
    schema2 = [
        {
            "name": "orders",
            "columns": [{"name": "id"}, {"name": "user_id"}]
        }
    ]
    
    # Create mock DbConfigs
    db_config1 = db_config_class(
        id="pg_db",
        db_type="pg",
        configuration={"host": "localhost"},
        description="PostgreSQL DB",
        schema=schema1
    )
    
    db_config2 = db_config_class(
        id="mysql_db",
        db_type="mysql",
        configuration={"host": "localhost"},
        description="MySQL DB",
        schema=schema2
    )
    
    # Set up mock context
    mock_ctx.request_context.lifespan_context.db_configs = {
        "pg_db": db_config1,
        "mysql_db": db_config2
    }
    
    # Call the function without specifying a db_id
    output = get_database_info(mock_ctx)
    
    # Verify output contains information for all databases
    assert "Database ID: pg_db" in output
    assert "Database ID: mysql_db" in output
    assert "PostgreSQL DB" in output
    assert "MySQL DB" in output
    assert "- users (id, name)" in output
    assert "- orders (id, user_id)" in output 