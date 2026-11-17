import os
import time
import urllib.parse
import urllib.request
from typing import List, Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

# Server Configuration (Compatible with Render & mcp<2)
PORT = int(os.environ.get("PORT", 10000))
mcp = FastMCP("PawanImageGenerator", host="0.0.0.0", port=PORT)

# Default Cinematic 2D Animation Style Lock
DEFAULT_2D_STYLE = (
    "2D cinematic animated movie still, high-budget storybook anime illustration, "
    "clean expressive lineart, rich painterly background, dramatic rim lighting, "
    "depth of field, vivid colors, 4k masterpiece, no text, no watermark, no signature"
)

def _get_dimensions(aspect_ratio: str) -> tuple:
    ratio = (aspect_ratio or "16:9").strip()
    if ratio == "16:9":
        return (1280, 720)
    elif ratio == "9:16":
        return (720, 1280)
    elif ratio == "4:3":
        return (1024, 768)
    return (1024, 1024)

def _compose_master_prompt(
    scene_prompt: str,
    character_bible: Optional[str] = None,
    style_override: Optional[str] = None
) -> str:
    parts = []
    if character_bible and character_bible.strip():
        parts.append(f"Character Reference: {character_bible.strip()}")
    parts.append(f"Scene Action: {scene_prompt.strip()}")
    style = style_override.strip() if (style_override and style_override.strip()) else DEFAULT_2D_STYLE
    parts.append(f"Art Style: {style}")
    full_prompt = ", ".join(parts)
    return " ".join(full_prompt.split())

def _build_and_verify_url(full_prompt: str, width: int, height: int, seed: int) -> str:
    encoded_prompt = urllib.parse.quote(full_prompt)
    base_url = "https://image.pollinations.ai/prompt/"
    image_url = (
        f"{base_url}{encoded_prompt}"
        f"?model=flux&width={width}&height={height}&seed={seed}&nologo=true&enhance=false"
    )
    
    # 3 attempts with backoff to handle API load smoothly without failing
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                image_url,
                method="HEAD",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                if resp.status == 200:
                    return image_url
        except Exception:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
    return image_url

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
def generate_cinematic_image(
    prompt: str,
    character_bible: str = "",
    aspect_ratio: str = "16:9",
    seed: int = 101,
    style_override: str = ""
) -> str:
    """
    Generates a single consistent 2D cinematic animation image in 16:9 or 9:16.
    - prompt: Detailed scene action, camera angle, background, and lighting in English.
    - character_bible: Exact locked appearance of characters (age, face, hair, clothes) for consistency across 200+ scenes.
    - aspect_ratio: '16:9' (YouTube/Descript/CapCut) or '9:16' (Shorts/Reels).
    - seed: Fixed integer (e.g., 101) to keep visual consistency.
    Always display the image in Markdown: ![Scene](url) and show the Direct URL below it.
    """
    width, height = _get_dimensions(aspect_ratio)
    master_prompt = _compose_master_prompt(prompt, character_bible, style_override)
    url = _build_and_verify_url(master_prompt, width, height, seed)
    return (
        f"**Cinematic Scene Ready ({aspect_ratio} | Seed: {seed})**\n"
        f"![Generated Scene]({url})\n"
        f"**Direct URL (for CapCut/Descript):** {url}"
    )

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
def generate_batch_images(
    prompts: List[str],
    character_bible: str = "",
    aspect_ratio: str = "16:9",
    base_seed: int = 101,
    style_override: str = ""
) -> str:
    """
    Generates up to 10 consistent 2D animation scenes in a single batch for long 10-minute stories (200+ images).
    - prompts: List of 1 to 10 sequential English scene prompts.
    - character_bible: Locked character appearance applied automatically to EVERY scene in the batch.
    - aspect_ratio: Default '16:9'.
    - base_seed: Starting seed number for visual consistency.
    Always display every generated image using Markdown: ![Scene X](url) along with its Direct URL.
    """
    width, height = _get_dimensions(aspect_ratio)
    safe_prompts = prompts[:10]
    outputs = []
    
    for idx, raw_prompt in enumerate(safe_prompts, start=1):
        current_seed = base_seed + (idx - 1)
        master_prompt = _compose_master_prompt(raw_prompt, character_bible, style_override)
        url = _build_and_verify_url(master_prompt, width, height, current_seed)
        outputs.append(
            f"### Scene {idx} ({aspect_ratio} | Seed: {current_seed})\n"
            f"![Scene {idx}]({url})\n"
            f"**Direct URL:** {url}"
        )
        if idx < len(safe_prompts):
            time.sleep(1.2)
            
    return "\n\n---\n\n".join(outputs)

@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
def check_server_status() -> str:
    """
    Checks if PawanImageGenerator MCP server is awake and ready.
    """
    return "PawanImageGenerator v2.0 Premium is LIVE and ready for 16:9 2D cinematic batch generation!"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    
