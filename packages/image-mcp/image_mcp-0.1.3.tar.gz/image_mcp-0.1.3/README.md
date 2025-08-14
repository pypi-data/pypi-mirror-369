# Image-MCP

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-light.svg)](https://cursor.com/en/install-mcp?name=image_loader&config=eyJjb21tYW5kIjoidXZ4IGltYWdlLW1jcEBsYXRlc3QifQ%3D%3D)

This is a simple MCP server that loads images from a local path or HTTP/HTTPS URL. This enables AI (e.g. your cursor agent) to load and analyze images. Click the above button to install, or add the following snippet to your `mcp.json`:

```json
{
  "image_loader": {
    "command": "uvx",
    "args": ["image-mcp@latest"]
  }
}
```
