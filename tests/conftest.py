import pytest
import sys
from unittest.mock import MagicMock

# Mock the MCP modules to avoid importing actual server
class MockFastMCP:
    def __init__(self, *args, **kwargs):
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

# Mock Context class
class MockContext:
    def __init__(self):
        self.request_context = MagicMock()
        self.request_context.lifespan_context = MagicMock()

# Create a fixture to mock the MCP server
@pytest.fixture(autouse=True)
def mock_mcp_server(monkeypatch):
    """Mock the MCP server to avoid initialization issues during testing"""
    mcp_mock = MockFastMCP()
    
    # Add mock to sys.modules
    mock_module = MagicMock()
    mock_module.FastMCP = MockFastMCP
    mock_module.Context = MockContext
    monkeypatch.setitem(sys.modules, 'mcp.server.fastmcp', mock_module)
    monkeypatch.setitem(sys.modules, 'mcp.server.fastmcp.server', mock_module)
    
    # Mock legion_query_runner module if not found
    if 'legion_query_runner' not in sys.modules:
        mock_legion = MagicMock()
        mock_legion.QueryRunner = MagicMock
        monkeypatch.setitem(sys.modules, 'legion_query_runner', mock_legion)
        
    return mcp_mock 