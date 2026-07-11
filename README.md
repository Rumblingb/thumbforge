# 🖼️ ThumbForge MCP

> Your AI agent's image processing toolkit. Resize, thumbnail, format conversion. Zero API keys. Uses Pillow.

[![MCP Server](https://img.shields.io/badge/MCP-Server-blue)](https://smithery.ai/servers/Rumblingb/thumbforge)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Pro](https://img.shields.io/badge/Pro-%249%2Fmo-blueviolet)](https://buy.stripe.com/your_link_here)

**4 pure-Python image processing tools. Zero API keys. Freemium with 50 free calls. $9/mo Pro unlimited.**

---

## 🎯 Why ThumbForge?

AI agents need to manipulate images: create thumbnails, resize, convert formats, and get image info. Instead of installing Pillow and writing boilerplate in every agent, ThumbForge MCP gives you **4 battle-tested, production-ready image tools** in a single MCP server.

Every tool is:
- **Built with Pillow** — reliable image processing
- **Read-only, idempotent** — safe for any agent to call
- **Error-as-result** — never throws exceptions, always returns structured JSON
- **Rate-limited** — free tier with clear upgrade path

---

## 🛠️ Tools

| Tool | Description | Example Use Case |
|------|-------------|------------------|
| `thumbnail_generate` | Generate a thumbnail from image data | Create preview images, avatars |
| `resize_image` | Resize image to exact dimensions | Fit images to specific dimensions |
| `convert_format` | Convert image to another format (JPEG, PNG, WEBP, AVIF, etc.) | Optimize for web, reduce file size |
| `image_info` | Get basic info about an image (size, mode, format) | Validate image properties, debug |

---

## 📦 Installation

### Smithery (Recommended)
```bash
npx smithery install thumbforge --client claude
```

### Manual (Python)
```bash
git clone https://github.com/Rumblingb/thumbforge.git
cd thumbforge
pip install -r requirements.txt
python3 server.py
```

### Claude Desktop Config
```json
{
  "mcpServers": {
    "thumbforge": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "/path/to/thumbforge"
    }
  }
}
```

---

## 💰 Pricing

| Tier | Price | Limits |
|------|-------|--------|
| **Free** | $0 | 50 calls per server start |
| **Pro** | $9/mo | Unlimited calls |

**[Upgrade to Pro →](https://buy.stripe.com/your_link_here)**

Pro users get:
- Unlimited calls across all 4 tools
- Priority support via GitHub Issues
- Access to new tools before free tier

---

## 🧪 Usage Examples

### Generate a thumbnail
```json
{
  "tool": "thumbnail_generate",
  "image": "/9j/4AAQSkZJRgABAQAAAQABAAD...", // base64 encoded image
  "width": 128,
  "height": 128,
  "format": "PNG"
}
```
→ Returns base64-encoded thumbnail

### Resize image
```json
{
  "tool": "resize_image",
  "image": "/9j/4AAQSkZJRgABAQAAAQABAAD...",
  "width": 800,
  "height": 600,
  "format": "JPEG"
}
```
→ Returns base64-encoded resized image

### Convert to WebP
```json
{
  "tool": "convert_format",
  "image": "/9j/4AAQSkZJRgABAQAAAQABAAD...",
  "format": "WEBP"
}
```
→ Returns base64-encoded WebP image

### Get image info
```json
{
  "tool": "image_info",
  "image": "/9j/4AAQSkZJRgABAQAAAQABAAD..."
}
```
→ Returns `{ "status": "success", "format": "JPEG", "width": 1920, "height": 1080, "mode": "RGB" }`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         MCP Client (Claude, etc.)    │
└────────────┬────────────────────────┘
             │ JSON-RPC over stdio
┌────────────▼────────────────────────┐
│         ThumbForge MCP Server         │
│                                       │
│  ┌──────────┐  ┌───────────┐         │
│  │ Rate Lim  │  │  Tool     │         │
│  │ (free 50) │  │  Registry │         │
│  └──────────┘  └─────┬─────┘         │
│                      │               │
│   ┌──────────────────┼──────────┐    │
│   │                  │          │    │
│  Thumb│Resize│Convert│Info│ ...  │    │
│       │    │     │    │      │      │
└──────┴──────┴─────┴────┴──────┴──────┘
     All tools: Pillow for image processing
```

---

## 🔄 Error Handling

All tools return errors INSIDE the response (never throw exceptions):
```json
{
  "status": "error",
  "isError": true,
  "error": "Invalid image data",
}
```

Rate limit exceeded:
```json
{
  "error": "Free tier limit (50 calls). Upgrade to Pro ($9/mo unlimited).",
  "isError": true,
  "next_steps": [
    "Buy Pro: https://buy.stripe.com/your_link_here",
    "Restart server to reset counter",
    "Use --pro-key PROL_AGENTPAY_DEMO for testing"
  ],
  "calls_used": 50,
  "limit": 50
}
```

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

## 🚀 Part of the AgentPay Labs ecosystem

[More MCP Servers](https://rumblingb.github.io/mcp-directory/)

[![smithery badge](https://smithery.ai/badge/Rumblingb/thumbforge)](https://smithery.ai/servers/Rumblingb/thumbforge)