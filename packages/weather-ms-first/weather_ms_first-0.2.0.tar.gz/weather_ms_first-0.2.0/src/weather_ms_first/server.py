from mcp.server.fastmcp import FastMCP

app = FastMCP("Math")

@app.tool()
def add(a: int, b: int) -> int:
    """
    Add two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of the two numbers.
    """
    return a + b

@app.tool()
def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The product of the two numbers.
    """
    return a * b


def main():
    print("Starting MCP server...")
    app.run(transport="stdio")
    print("MCP server started")
