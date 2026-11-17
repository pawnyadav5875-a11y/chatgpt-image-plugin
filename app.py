import os
import urllib.parse
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("PawanImageGenerator")

@mcp.tool()
def generate_free_image(prompt: str) -> str:
    """
    Generates a free AI image URL from a text prompt.
    Always return the image to the user using Markdown format: ![Generated Image](url)
    """
    clean_prompt = prompt.strip()
    encoded_prompt = urllib.parse.quote(clean_prompt)
    base_url = "https://image.pollinations.ai/prompt/"
    image_url = f"{base_url}{encoded_prompt}?model=flux&width=1024&height=1024&nologo=true"
    return f"Image generated successfully. Display it using: ![Generated Image]({image_url})"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
  
