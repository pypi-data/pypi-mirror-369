try:
    from .server import app
except ImportError:
    from server import app

if __name__ == "__main__":
    print("Starting MCP server...")
    app.run(transport="stdio")
    print("MCP server started")