#!/usr/bin/env python3
"""
ThumbForge MCP Server — Image resize, thumbnail, format conversion for AI agents.
Zero API keys. Uses Pillow for image processing. Freemium: 50 free calls, $9/mo unlimited.
Built for AgentPay Labs — one new product every day.
"""

import sys
import json
import asyncio
import io
import base64
from typing import Any, Dict

try:
    from PIL import Image
except ImportError:
    Image = None

# ── Rate limiting ───────────────────────────────────────────────────────────
FREE_LIMIT = 50
PRO_KEYS = {"PROL_AGENTPAY_DEMO": "demo"}
STRIPE_LINK = "https://buy.stripe.com/your_link_here"  # Update after Stripe product creation

PRO_KEY = None
for i, arg in enumerate(sys.argv):
    if arg == "--pro-key" and i + 1 < len(sys.argv):
        PRO_KEY = sys.argv[i + 1]
IS_PRO = PRO_KEY in PRO_KEYS
call_counter = 0


def check_rate_limit():
    if IS_PRO:
        return None
    global call_counter
    call_counter += 1
    if call_counter > FREE_LIMIT:
        return {
            "error": f"Free tier limit ({FREE_LIMIT} calls). Upgrade to Pro ($9/mo unlimited).",
            "isError": True,
            "next_steps": [
                f"Buy Pro: {STRIPE_LINK}",
                "Restart server to reset counter",
                "Use --pro-key PROL_AGENTPAY_DEMO for testing",
            ],
            "calls_used": call_counter,
            "limit": FREE_LIMIT,
        }
    return None


# ── Tool implementations ────────────────────────────────────────────────────
def _validate_image(data: bytes) -> Image.Image:
    if Image is None:
        raise RuntimeError("Pillow not installed. Run: pip install pillow")
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
        return img
    except Exception as e:
        raise ValueError(f"Invalid image data: {e}")


def _image_to_bytes(img: Image.Image, format: str = "PNG") -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def thumbnail_generate(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a thumbnail from image data.
    Expects: image (base64), width, height, optional format (default PNG).
    Returns: base64-encoded thumbnail.
    """
    try:
        img_b64 = params.get("image")
        if not img_b64:
            return {"error": "Missing 'image' parameter (base64 encoded).", "isError": True}
        width = int(params.get("width", 128))
        height = int(params.get("height", 128))
        fmt = params.get("format", "PNG").upper()
        img_data = base64.b64decode(img_b64)
        img = _validate_image(img_data)
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
        out_bytes = _image_to_bytes(img, fmt)
        out_b64 = base64.b64encode(out_bytes).decode("utf-8")
        return {
            "status": "success",
            "format": fmt,
            "width": width,
            "height": height,
            "thumbnail_base64": out_b64,
        }
    except Exception as e:
        return {"error": str(e), "isError": True}


def resize_image(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resize image to exact dimensions (may distort).
    Expects: image (base64), width, height, optional format.
    """
    try:
        img_b64 = params.get("image")
        if not img_b64:
            return {"error": "Missing 'image' parameter (base64 encoded).", "isError": True}
        width = int(params.get("width"))
        height = int(params.get("height"))
        fmt = params.get("format", "PNG").upper()
        img_data = base64.b64decode(img_b64)
        img = _validate_image(img_data)
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        out_bytes = _image_to_bytes(img, fmt)
        out_b64 = base64.b64encode(out_bytes).decode("utf-8")
        return {
            "status": "success",
            "format": fmt,
            "width": width,
            "height": height,
            "image_base64": out_b64,
        }
    except Exception as e:
        return {"error": str(e), "isError": True}


def convert_format(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert image to another format.
    Expects: image (base64), format (e.g., JPEG, PNG, WEBP, AVIF).
    """
    try:
        img_b64 = params.get("image")
        if not img_b64:
            return {"error": "Missing 'image' parameter (base64 encoded).", "isError": True}
        fmt = params.get("format", "PNG").upper()
        if fmt not in ["JPEG", "PNG", "WEBP", "AVIF", "TIFF", "BMP", "GIF"]:
            return {"error": f"Unsupported format: {fmt}", "isError": True}
        img_data = base64.b64decode(img_b64)
        img = _validate_image(img_data)
        # Handle mode conversions for certain formats
        if fmt == "JPEG":
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
        elif fmt in ["PNG", "WEBP"] and img.mode == "P":
            img = img.convert("RGBA")
        out_bytes = _image_to_bytes(img, fmt)
        out_b64 = base64.b64encode(out_bytes).decode("utf-8")
        return {
            "status": "success",
            "format": fmt,
            "image_base64": out_b64,
        }
    except Exception as e:
        return {"error": str(e), "isError": True}


def image_info(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get basic info about an image: size, mode, format.
    Expects: image (base64).
    """
    try:
        img_b64 = params.get("image")
        if not img_b64:
            return {"error": "Missing 'image' parameter (base64 encoded).", "isError": True}
        img_data = base64.b64decode(img_b64)
        img = _validate_image(img_data)
        return {
            "status": "success",
            "format": img.format,
            "mode": img.mode,
            "width": img.width,
            "height": img.height,
        }
    except Exception as e:
        return {"error": str(e), "isError": True}


# Map tool names to functions
TOOLS = {
    "thumbnail_generate": thumbnail_generate,
    "resize_image": resize_image,
    "convert_format": convert_format,
    "image_info": image_info,
}


# ── MCP Server (Direct stdio) ───────────────────────────────────────────────
async def main():
    """MCP stdio main loop."""
    tier = "PRO (unlimited)" if IS_PRO else f"FREE ({FREE_LIMIT} calls)"
    print(f"ThumbForge MCP v1.0.0 — {tier}", file=sys.stderr)
    print(f"Pro upgrade: {STRIPE_LINK}", file=sys.stderr)

    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    loop = asyncio.get_event_loop()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    writer_transport, writer_protocol = await loop.connect_write_pipe(
        lambda: asyncio.Protocol(), sys.stdout
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, loop)

    buffer = ""
    request_id = 0

    while True:
        # Read line-by-line for simplicity (JSON-RPC over stdio uses newline-delimited messages)
        data = await reader.readuntil(b"\n")
        if not data:
            break
        buffer += data.decode("utf-8")
        if not buffer.endswith("\n"):
            continue  # incomplete message
        try:
            request = json.loads(buffer.strip())
        except json.JSONDecodeError:
            # Invalid JSON, ignore and reset buffer
            buffer = ""
            continue
        buffer = ""

        # JSON-RPC 2.0 handling
        method = request.get("method")
        msg_id = request.get("id")
        params = request.get("params", {})

        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "thumbforge", "version": "1.0.0"},
            }
            response = {"jsonrpc": "2.0", "id": msg_id, "result": result}
            writer.write(json.dumps(response).encode() + b"\n")
            await writer.drain()
            continue

        if method == "notifications/initialized":
            # Notification, no response needed
            continue

        if method == "tools/list":
            tool_defs = []
            for name, func in TOOLS.items():
                # Derive simple schema; for brevity we use a placeholder
                tool_defs.append(
                    {
                        "name": name,
                        "description": func.__doc__.strip() if func.__doc__ else "",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                        },
                    }
                )
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": tool_defs},
            }
            writer.write(json.dumps(response).encode() + b"\n")
            await writer.drain()
            continue

        if method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            if tool_name not in TOOLS:
                error = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
                }
                writer.write(json.dumps(error).encode() + b"\n")
                await writer.drain()
                continue

            # Rate limit check
            limit_check = check_rate_limit()
            if limit_check:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(limit_check)}]},
                }
                writer.write(json.dumps(error_response).encode() + b"\n")
                await writer.drain()
                continue

            try:
                result = TOOLS[tool_name](tool_args)
            except Exception as e:
                result = {"status": "error", "isError": True, "error": str(e)}

            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
            }
            writer.write(json.dumps(response).encode() + b"\n")
            await writer.drain()
            continue

        # Unknown method
        error = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
        writer.write(json.dumps(error).encode() + b"\n")
        await writer.drain()


if __name__ == "__main__":
    asyncio.run(main())