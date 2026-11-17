import os
import time
import urllib.parse
import urllib.request
from typing import List
from mcp.server.fastmcp import FastMCP

port = int(os.environ.get("PORT", 10000))
mcp = FastMCP("PawanImageGenerator", host="0.0.0.0", port=port)

def _build_and_verify_url(prompt: str, width: int, height: int, seed: int) -> str:
    clean_prompt = " ".join(prompt.strip().split())
    encoded_prompt = urllib.parse.quote(clean_prompt)
    base_url = "https://image.pollinations.ai/prompt/"
    image_url = (
        f"{base_url}{encoded_prompt}"
        f"?model=flux&width={width}&height={height}&seed={seed}&nologo=true&enhance=false"
    )
    
    for attempt in range(3):
        try:
            req = urllib.request.Request(image_url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25) as resp:
                if resp.status == 200:
                    return image_url
        except Exception:
            if attempt < 2:
                time.sleep(2)
    return image_url

def _get_dimensions(aspect_ratio: str) -> tuple:
    ratio = aspect_ratio.strip()
    if ratio == "16:9":
        return (1280, 720)
    elif ratio == "9:16":
        return (720, 1280)
    return (1024, 1024)

@mcp.tool()
def generate_cinematic_image(
    prompt: str,
    aspect_ratio: str = "16:9",
    seed: int = 42
) -> str:
    """
    Generates a single high-quality 2D cinematic image URL in 16:9, 9:16, or 1:1.
    Always display the image using Markdown: ![Scene](url) and also provide the raw direct download URL.
    """
    width, height = _get_dimensions(aspect_ratio)
    url = _build_and_verify_url(prompt, width, height, seed)
    return (
        f"Image Ready ({aspect_ratio}):\n"
        f"![Generated Scene]({url})\n"
        f"Direct URL: {url}"
    )

@mcp.tool()
def generate_batch_images(
    prompts: List[str],
    aspect_ratio: str = "16:9",
    base_seed: int = 42
) -> str:
    """
    Generates multiple 2D animation scene image URLs in one batch (recommended 5 to 10 prompts per call).
    """
    width, height = _get_dimensions(aspect_ratio)
    results = []
    for idx, p in enumerate(prompts[:10], start=1):
        scene_seed = base_seed + idx
        url = _build_and_verify_url(p, width, height, scene_seed)
        results.append(f"Scene {idx}:\n![Scene {idx}]({url})\nDirect URL: {url}")
    return "\n\n---\n\n".join(results)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    
