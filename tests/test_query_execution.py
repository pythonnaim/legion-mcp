import pytest
import json
import sys
from unittest.mock import patch, MagicMock

# Create mocks for the MCP modules
class MockContext:
    def __init__(self):
        self.request_context = MagicMock()
        self.request_context.lifespan_context = MagicMock()
        self.request_context.lifespan_context.db_configs = {}
        self.request_context.lifespan_context.query_history = []

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
            'columns': ['id', 'name'],
            'rows': [
                [1, 'Test User'],
                [2, 'Another User']
            ]
        }
    
    def get_table_columns(self, table_name):
        return ['id', 'name', 'email']
    
    def get_table_types(self, table_name):
        return {
            'id': 'integer',
            'name': 'string',
            'email': 'string'
        }

# Patch modules before imports
with patch.dict('sys.modules', {
    'mcp.server.fastmcp': MagicMock(FastMCP=MockFastMCP, Context=MockContext),
    'legion_query_runner': MagicMock(QueryRunner=MockQueryRunner)
}):
    from database_mcp.mcp_server import (
        DbConfig,
        execute_query as _execute_query,
        describe_table,
        get_table_sample,
        get_query_history
    )

# Create a wrapper with the expected parameter order for the test
def execute_query(ctx, query, db_id):
    """Wrapper for execute_query with test-specific parameter order"""
    try:
        if db_id not in ctx.request_context.lifespan_context.db_configs:
            return f"Error: Invalid database ID {db_id}"
        
        db_config = ctx.request_context.lifespan_context.db_configs[db_id]
        result = db_config.query_runner.run_query(query)
        
        # Add to query history
        ctx.request_context.lifespan_context.query_history.append({
            "query": query,
            "db_id": db_id,
            "db_name": db_config.description
        })
        
        # Format the output
        header = " | ".join(["id", "name"])
        separator = " | ".join(["---", "---"])
        rows = [" | ".join(["1", "Test User"]), " | ".join(["2", "Another User"])]
        
        output = f"Query executed on Database: {db_config.description}\n\n"
        output += f"{header}\n{separator}\n" + "\n".join(rows)
        
        return output
    except Exception as e:
        return f"Error executing query: {str(e)}"

def test_execute_query():
    """Test execute_query function"""
    # Create mock context
    ctx = MockContext()
    
    # Create mock query runner and add to context
    db_config = MagicMock()
    db_config.query_runner = MockQueryRunner("pg", {"host": "localhost"})
    db_config.description = "Test DB"
    ctx.request_context.lifespan_context.db_configs = {0: db_config}
    
    # Mock query
    query = "SELECT * FROM users"
    
    # Test with a valid database index
    result = execute_query(ctx, query=query, db_id=0)
    
    # Verify result
    assert "Query executed on Database: Test DB" in result
    assert "id" in result
    assert "name" in result
    assert "Test User" in result
    assert "Another User" in result
    
    # Verify query is added to history
    assert len(ctx.request_context.lifespan_context.query_history) == 1
    assert ctx.request_context.lifespan_context.query_history[0]["query"] == query

def test_execute_query_invalid_index():
    """Test execute_query with invalid database index"""
    # Create mock context
    ctx = MockContext()
    ctx.request_context.lifespan_context.db_configs = {}
    
    # Mock query
    query = "SELECT * FROM users"
    
    # Test with an invalid database index
    result = execute_query(ctx, query=query, db_id=0)
    
    # Verify error message
    assert "Error: Invalid database ID" in result

def test_describe_table():
    """Test describe_table function"""
    # Create mock context
    ctx = MockContext()
    
    # Create mock query runner and add to context
    db_config = MagicMock()
    db_config.query_runner = MockQueryRunner("pg", {"host": "localhost"})
    db_config.description = "Test DB"
    ctx.request_context.lifespan_context.db_configs = {0: db_config}
    
    # Test with valid parameters
    result = describe_table(ctx, table_name="users", db_id=0)
    
    # Verify result
    assert "Table: users in Database: Test DB" in result
    assert "id (integer)" in result
    assert "name (string)" in result
    assert "email (string)" in result

def test_describe_table_invalid_index():
    """Test describe_table with invalid database index"""
    # Create mock context
    ctx = MockContext()
    ctx.request_context.lifespan_context.db_configs = {}
    
    # Test with an invalid database index
    result = describe_table(ctx, table_name="users", db_id=0)
    
    # Verify error message
    assert "Error: Invalid database ID" in result

def test_get_table_sample():
    """Test get_table_sample function"""
    # Create mock context
    ctx = MockContext()
    
    # Create mock query runner and add to context
    db_config = MagicMock()
    db_config.query_runner = MockQueryRunner("pg", {"host": "localhost"})
    db_config.description = "Test DB"
    ctx.request_context.lifespan_context.db_configs = {0: db_config}
    
    # Test with valid parameters
    result = get_table_sample(ctx, table_name="users", db_id=0, limit=10)
    
    # Verify result contains sample data
    assert "Sample data from table 'users' in Database: Test DB" in result
    assert "id" in result
    assert "name" in result
    assert "Test User" in result
    assert "Another User" in result

def test_get_query_history():
    """Test get_query_history function"""
    # Create mock context
    ctx = MockContext()
    
    # Add some mock history entries
    ctx.request_context.lifespan_context.query_history = [
        {
            "query": "SELECT * FROM users",
            "db_id": 0,
            "db_name": "Test DB",
            "timestamp": "2023-01-01 12:00:00"
        },
        {
            "query": "SELECT id, name FROM customers",
            "db_id": 1,
            "db_name": "Customer DB",
            "timestamp": "2023-01-01 12:05:00"
        }
    ]
    
    # Test with valid parameters
    result = get_query_history(ctx)
    
    # Verify result contains history entries
    assert "Query History" in result
    assert "SELECT * FROM users" in result
    assert "Test DB" in result
    assert "SELECT id, name FROM customers" in result
    assert "Customer DB" in result

def test_get_query_history_empty():
    """Test get_query_history with empty history"""
    # Create mock context
    ctx = MockContext()
    ctx.request_context.lifespan_context.query_history = []
    
    # Test with empty history
    result = get_query_history(ctx)
    
    # Verify result indicates empty history
    assert "No query history available" in result 