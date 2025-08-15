from mcp.server import FastMCP

mcp = FastMCP(name="eastnine_demo1")

@mcp.tool()
def add(a,b) -> int:
    """
    a 와 b 를 입력 받아서 두개의 값을 더하는 툴이다 

    Args:
        변수는 int 형식으로 a와 b 를 입력 받는다.

    Return:
        a + b 의 값을 반환한다.
    """
    try:
        a = int(a)  
        b = int(b)
        return a + b
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    mcp.run(transport="stdio")