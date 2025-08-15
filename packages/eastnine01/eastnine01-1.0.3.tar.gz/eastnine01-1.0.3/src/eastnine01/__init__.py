from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="eastnine01")

@mcp.tool()
def echo (message: str) -> str:
    """
    입력받은 메시지를 그대로 반환하는 도구 입니다. 
    """
    return message + " 라는 메시지가 입력 되었습니다"

def main():
    mcp.run(transport="stdio")

    