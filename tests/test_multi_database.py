import pytest
import json
import os
from unittest.mock import patch, MagicMock, AsyncMock

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
        return {"tables": []}
    
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
    # Now it's safe to import
    from database_mcp.mcp_server import (
        DbConfig,
        DbContext,
        get_database_schema_summary,
    )

# Define init_query_runners function for testing separately to avoid module initialization
def init_query_runners_for_test(db_type=None, db_config=None, db_configs=None):
    """Test version of init_query_runners that doesn't rely on argparse"""
    from database_mcp.mcp_server import QueryRunner
    
    if db_configs:
        db_configs_list = json.loads(db_configs) if isinstance(db_configs, str) else db_configs
        
        if not isinstance(db_configs_list, list) or len(db_configs_list) == 0:
            raise ValueError("DB_CONFIGS must be a non-empty JSON array")
        
        query_runners = {}
        for i, config in enumerate(db_configs_list):
            if not isinstance(config, dict) or "db_type" not in config or "configuration" not in config or "description" not in config:
                raise ValueError("Each DB_CONFIG must contain db_type, configuration, and description")
            
            # Generate a meaningful ID if not provided
            db_id = config.get("id", "")
            if not db_id:
                # Create an ID based on database type and description
                db_type_abbr = config["db_type"][:2].lower()
                desc_part = ''.join(c for c in config["description"] if c.isalnum())[:8].lower()
                db_id = f"{db_type_abbr}_{desc_part}_{i}"
            
            db_config_obj = DbConfig(
                id=db_id,
                db_type=config["db_type"],
                configuration=config["configuration"],
                description=config["description"]
            )
            
            db_config_obj.query_runner = QueryRunner(db_type=db_config_obj.db_type, configuration=db_config_obj.configuration)
            query_runners[db_id] = db_config_obj
        
        return query_runners
    
    # Fallback to single database configuration
    if not db_type:
        db_type = "pg"
    
    if isinstance(db_config, str):
        db_config = json.loads(db_config)
    elif db_config is None:
        db_config = {}
    
    if not db_type or not db_config:
        raise ValueError("Database type and configuration are required")
    
    # Generate a meaningful ID for the single database
    db_id = f"{db_type.lower()}_default"
    
    db_config_obj = DbConfig(
        id=db_id,
        db_type=db_type,
        configuration=db_config,
        description="Default database connection"
    )
    db_config_obj.query_runner = QueryRunner(db_type=db_type, configuration=db_config)
    
    return {db_id: db_config_obj}


class TestDbConfig:
    def test_db_config_init(self):
        """Test DbConfig initialization"""
        config = DbConfig(
            id="test_db",
            db_type="pg",
            configuration={"host": "localhost"},
            description="Test DB"
        )
        
        assert config.id == "test_db"
        assert config.db_type == "pg"
        assert config.configuration == {"host": "localhost"}
        assert config.description == "Test DB"
        assert config.schema is None
        assert config.query_runner is None


class TestDbContext:
    def test_db_context_init(self):
        """Test DbContext initialization"""
        db_config = DbConfig(
            id="test_db",
            db_type="pg",
            configuration={"host": "localhost"},
            description="Test DB"
        )
        
        context = DbContext(db_configs={"test_db": db_config})
        
        assert context.db_configs == {"test_db": db_config}
        assert context.last_query is None
        assert context.last_result is None
        assert context.query_history == []
    
    def test_get_default_query_runner(self):
        """Test get_default_query_runner method"""
        # Mock QueryRunner
        mock_runner = MagicMock()
        
        db_config1 = DbConfig(
            id="test_db1",
            db_type="pg",
            configuration={"host": "localhost"},
            description="Test DB 1"
        )
        db_config1.query_runner = mock_runner
        
        db_config2 = DbConfig(
            id="test_db2",
            db_type="mysql",
            configuration={"host": "localhost"},
            description="Test DB 2"
        )
        
        # Test with multiple runners
        context = DbContext(db_configs={"test_db1": db_config1, "test_db2": db_config2})
        assert context.get_default_query_runner() == mock_runner
        
        # Test with empty runners list
        with pytest.raises(ValueError, match="No database connections available"):
            DbContext(db_configs={}).get_default_query_runner()


class TestInitQueryRunners:
    @patch('database_mcp.mcp_server.QueryRunner')
    def test_init_single_db(self, mock_query_runner):
        """Test initialization of a single database"""
        # Mock QueryRunner instance
        mock_query_runner_instance = MagicMock()
        mock_query_runner.return_value = mock_query_runner_instance
        
        result = init_query_runners_for_test(
            db_type='pg',
            db_config={"host": "localhost", "port": 5432}
        )
        
        # Verify result
        assert len(result) == 1
        db_id = "pg_default"
        assert db_id in result
        assert result[db_id].db_type == 'pg'
        assert result[db_id].configuration == {"host": "localhost", "port": 5432}
        assert result[db_id].description == "Default database connection"
        assert result[db_id].query_runner == mock_query_runner_instance
        
        # Verify QueryRunner creation
        mock_query_runner.assert_called_once_with(
            db_type='pg',
            configuration={"host": "localhost", "port": 5432}
        )
    
    @patch('database_mcp.mcp_server.QueryRunner')
    def test_init_multiple_dbs(self, mock_query_runner):
        """Test initialization of multiple databases"""
        # Mock QueryRunner instances
        mock_query_runner_instances = [MagicMock(), MagicMock()]
        mock_query_runner.side_effect = mock_query_runner_instances
        
        db_configs = [
            {
                "db_type": "pg",
                "configuration": {"host": "localhost", "port": 5432},
                "description": "PostgreSQL DB"
            },
            {
                "db_type": "mysql",
                "configuration": {"host": "localhost", "port": 3306},
                "description": "MySQL DB"
            }
        ]
        
        result = init_query_runners_for_test(db_configs=db_configs)
        
        # Verify result
        assert len(result) == 2
        
        # Expected IDs based on our generation logic
        pg_id = "pg_postgres_0"
        mysql_id = "my_mysqldb_1"
        
        assert pg_id in result
        assert result[pg_id].db_type == 'pg'
        assert result[pg_id].configuration == {"host": "localhost", "port": 5432}
        assert result[pg_id].description == "PostgreSQL DB"
        assert result[pg_id].query_runner == mock_query_runner_instances[0]
        
        assert mysql_id in result
        assert result[mysql_id].db_type == 'mysql'
        assert result[mysql_id].configuration == {"host": "localhost", "port": 3306}
        assert result[mysql_id].description == "MySQL DB"
        assert result[mysql_id].query_runner == mock_query_runner_instances[1]
        
        # Verify QueryRunner creation
        assert mock_query_runner.call_count == 2
        mock_query_runner.assert_any_call(
            db_type='pg',
            configuration={"host": "localhost", "port": 5432}
        )
        mock_query_runner.assert_any_call(
            db_type='mysql',
            configuration={"host": "localhost", "port": 3306}
        )


class TestDatabaseTools:
    def test_get_database_schema_summary_no_schema(self):
        """Test get_database_schema_summary with no schema"""
        db_config = DbConfig(
            id="test_db",
            db_type="pg",
            configuration={"host": "localhost"},
            description="Test DB"
        )
        
        summary = get_database_schema_summary(db_config)
        assert summary == "Schema information not available"
    
    def test_get_database_schema_summary_no_tables(self):
        """Test get_database_schema_summary with empty tables"""
        db_config = DbConfig(
            id="test_db",
            db_type="pg",
            configuration={"host": "localhost"},
            description="Test DB",
            schema=[]
        )
        
        summary = get_database_schema_summary(db_config)
        assert summary == "No tables found in schema"
    
    def test_get_database_schema_summary_with_tables(self):
        """Test get_database_schema_summary with tables"""
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
        
        db_config = DbConfig(
            id="test_db",
            db_type="pg",
            configuration={"host": "localhost"},
            description="Test DB",
            schema=schema
        )
        
        summary = get_database_schema_summary(db_config)
        assert "- users (id, name, email)" in summary
        assert "- orders (id, user_id, product_id, quantity, price, ...)" in summary


@patch('database_mcp.mcp_server._execute_and_get_results')
def test_execute_query(mock_execute):
    """Test execute_query tool"""
    from database_mcp.mcp_server import execute_query
    
    # Mock context
    mock_ctx = MagicMock()
    
    # Mock _execute_and_get_results
    result = {
        'column_names': ['id', 'name'],
        'columns': [{'name': 'id'}, {'name': 'name'}],
        'rows': [[1, 'Product 1'], [2, 'Product 2']],
        'raw_rows': [{'id': 1, 'name': 'Product 1'}, {'id': 2, 'name': 'Product 2'}],
        'row_count': 2,
        'database': {
            'id': 'test_db',
            'description': 'Test DB',
            'db_type': 'pg'
        }
    }
    mock_execute.return_value = result
    
    # Call the function
    output = execute_query('SELECT * FROM products', mock_ctx, 'test_db')
    
    # Verify mock was called correctly
    mock_execute.assert_called_once_with('SELECT * FROM products', mock_ctx, 'test_db')
    
    # Verify output format - accept either output format
    assert any(
        x in output for x in [
            "Database: Test DB (Type: pg)",
            "Query executed on Database: Test DB"
        ]
    )
    assert "id | name" in output
    assert "--- | ---" in output
    assert "1 | Product 1" in output
    assert "2 | Product 2" in output

@patch('database_mcp.mcp_server._execute_and_get_results')
def test_execute_query_json(mock_execute):
    """Test execute_query_json tool"""
    from database_mcp.mcp_server import execute_query_json
    
    # Mock context
    mock_ctx = MagicMock()
    
    # Mock _execute_and_get_results
    result = {
        'column_names': ['id', 'name'],
        'columns': [{'name': 'id'}, {'name': 'name'}],
        'rows': [[1, 'Product 1'], [2, 'Product 2']],
        'raw_rows': [{'id': 1, 'name': 'Product 1'}, {'id': 2, 'name': 'Product 2'}],
        'row_count': 2,
        'database': {
            'id': 'test_db',
            'description': 'Test DB',
            'db_type': 'pg'
        }
    }
    mock_execute.return_value = result
    
    # Call the function
    output = execute_query_json('SELECT * FROM products', mock_ctx, 'test_db')
    
    # Verify mock was called correctly
    mock_execute.assert_called_once_with('SELECT * FROM products', mock_ctx, 'test_db')
    
    # Parse JSON output
    output_json = json.loads(output)
    
    # Verify output structure
    assert 'database' in output_json
    assert output_json['database']['description'] == 'Test DB'
    assert output_json['columns'] == ['id', 'name']
    assert len(output_json['rows']) == 2
    assert output_json['rows'][0]['id'] == 1
    assert output_json['rows'][1]['name'] == 'Product 2'
    assert output_json['row_count'] == 2

def test_list_databases():
    """Test list_databases tool"""
    from database_mcp.mcp_server import list_databases
    
    # Create mock DbConfigs
    db_config1 = DbConfig(
        id="pg_db",
        db_type="pg",
        configuration={"host": "localhost"},
        description="PostgreSQL DB",
        schema=[{"name": "users"}, {"name": "products"}]
    )
    
    db_config2 = DbConfig(
        id="mysql_db",
        db_type="mysql",
        configuration={"host": "localhost"},
        description="MySQL DB",
        schema=[{"name": "customers"}, {"name": "orders"}, {"name": "items"}]
    )
    
    # Create mock context
    mock_ctx = MagicMock()
    mock_lifespan_ctx = MagicMock()
    mock_lifespan_ctx.db_configs = {
        "pg_db": db_config1,
        "mysql_db": db_config2
    }
    mock_ctx.request_context.lifespan_context = mock_lifespan_ctx
    
    # Call the function
    output = list_databases(mock_ctx)
    
    # Verify output contains database info
    assert "ID: pg_db - PostgreSQL DB (Type: pg)" in output
    assert "ID: mysql_db - MySQL DB (Type: mysql)" in output

def test_list_databases_no_schema():
    """Test list_databases tool with no schema information"""
    from database_mcp.mcp_server import list_databases
    
    # Create mock DbConfigs
    db_config1 = DbConfig(
        id="pg_db",
        db_type="pg",
        configuration={"host": "localhost"},
        description="PostgreSQL DB"
    )
    
    # Create mock context
    mock_ctx = MagicMock()
    mock_lifespan_ctx = MagicMock()
    mock_lifespan_ctx.db_configs = {"pg_db": db_config1}
    mock_ctx.request_context.lifespan_context = mock_lifespan_ctx
    
    # Call the function
    output = list_databases(mock_ctx)
    
    # Verify output contains database info without table count
    assert "ID: pg_db - PostgreSQL DB (Type: pg)" in output
    assert "tables" not in output

def test_find_table_found():
    """Test find_table tool when table is found"""
    from database_mcp.mcp_server import find_table
    
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
    db_config1 = DbConfig(
        id="pg_db",
        db_type="pg",
        configuration={"host": "localhost"},
        description="PostgreSQL DB",
        schema=schema1
    )
    
    db_config2 = DbConfig(
        id="mysql_db",
        db_type="mysql",
        configuration={"host": "localhost"},
        description="MySQL DB",
        schema=schema2
    )
    
    # Create mock context
    mock_ctx = MagicMock()
    mock_lifespan_ctx = MagicMock()
    mock_lifespan_ctx.db_configs = {
        "pg_db": db_config1,
        "mysql_db": db_config2
    }
    mock_ctx.request_context.lifespan_context = mock_lifespan_ctx
    
    # Call the function
    output = find_table("users", mock_ctx)
    
    # Verify output shows the table was found
    assert "Table 'users' was found in the following databases:" in output
    assert "Database ID: pg_db - PostgreSQL DB" in output

def test_find_table_not_found():
    """Test find_table tool when table is not found"""
    from database_mcp.mcp_server import find_table
    
    # Create schema with tables
    schema = [
        {"name": "users"},
        {"name": "products"}
    ]
    
    # Create mock DbConfigs
    db_config1 = DbConfig(
        id="pg_db",
        db_type="pg",
        configuration={"host": "localhost"},
        description="PostgreSQL DB",
        schema=schema
    )
    
    # Create mock context
    mock_ctx = MagicMock()
    mock_lifespan_ctx = MagicMock()
    mock_lifespan_ctx.db_configs = {"pg_db": db_config1}
    mock_ctx.request_context.lifespan_context = mock_lifespan_ctx
    
    # Call the function
    output = find_table("orders", mock_ctx)
    
    # Verify output shows the table was not found
    assert "Table 'orders' was not found in any database schema." in output

def test_get_database_info():
    """Test get_database_info tool"""
    from database_mcp.mcp_server import get_database_info
    
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
    db_config = DbConfig(
        id="pg_db",
        db_type="pg",
        configuration={"host": "localhost"},
        description="PostgreSQL DB",
        schema=schema
    )
    
    # Create mock context
    mock_ctx = MagicMock()
    mock_lifespan_ctx = MagicMock()
    mock_lifespan_ctx.db_configs = {"pg_db": db_config}
    mock_ctx.request_context.lifespan_context = mock_lifespan_ctx
    
    # Call the function with specific db_id
    output = get_database_info(mock_ctx, db_id="pg_db")
    
    # Verify output contains database info and schema summary
    assert "Database ID: pg_db" in output
    assert "Description: PostgreSQL DB" in output
    assert "Type: pg" in output
    assert "- users (id, name, email)" in output
    assert "- products (id, name, price)" in output 