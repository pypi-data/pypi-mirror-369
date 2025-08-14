#server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo")

#add an addition tool
@mcp.tool()
def add(a:int,b:int) -> int:
    """add two numbers"""
    return a + b + 100

#add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name:str) -> str:
    """get a personalized greeting"""
    return f"hello,{name}!"

def main() -> None:
    mcp.run(transport='stdio')
