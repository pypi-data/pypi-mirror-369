import httpx
from mcp.server.fastmcp import FastMCP, Image as MCPImage
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO

mcp = FastMCP("Image-MCP")

def is_url(path: str) -> bool:
    return urlparse(path).scheme in ["http", "https"]

@mcp.tool(
    name="load_image",
    description="Load an image from a path or HTTP/HTTPS URL"
)
async def load_image(path: str) -> MCPImage:
    if is_url(path):
        response = httpx.get(path)
        image = Image.open(BytesIO(response.content))
    else:
        image = Image.open(path)

    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return MCPImage(data=buffered.getvalue(), format="jpeg")

def main():
    mcp.run()

if __name__ == "__main__":
    main()
