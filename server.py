import os
import sys
import ctypes
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional

import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Wallpaper Switcher")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Windows Wallpaper API ===
SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x0001
SPIF_SENDCHANGE = 0x0002
SPI_GETDESKWALLPAPER = 0x0073

WALLPAPER_DIR = Path(tempfile.gettempdir()) / "wallpaper_switcher"
WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".tif"}


def set_wallpaper(image_path: str) -> bool:
    """Set Windows desktop wallpaper using Win32 API."""
    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, str(image_path), SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    return result != 0


def get_current_wallpaper() -> Optional[str]:
    """Get current wallpaper path."""
    buffer = ctypes.create_unicode_buffer(1024)
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_GETDESKWALLPAPER, 1024, buffer, 0
    )
    path = buffer.value
    return path if path else None


# === Pydantic Models ===
class URLRequest(BaseModel):
    url: str


class SetWallpaperRequest(BaseModel):
    path: str


class GitHubRequest(BaseModel):
    repo_url: str
    path: str = ""
    branch: str = "main"


# === Routes ===

@app.get("/api/wallpaper/current")
async def current_wallpaper():
    path = get_current_wallpaper()
    return {"path": path}


@app.post("/api/wallpaper/local")
async def set_local_wallpaper(file: UploadFile = File(...)):
    """Upload and set a local image as wallpaper."""
    ext = Path(file.filename).suffix.lower()
    if ext not in IMAGE_EXTENSIONS:
        raise HTTPException(400, f"Unsupported image format: {ext}")

    dest = WALLPAPER_DIR / f"local_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
    with open(dest, "wb") as f:
        f.write(await file.read())

    if set_wallpaper(str(dest)):
        return {"success": True, "path": str(dest)}
    raise HTTPException(500, "Failed to set wallpaper")


@app.post("/api/wallpaper/url")
async def set_url_wallpaper(req: URLRequest):
    """Download an image from a URL (direct link or API) and set as wallpaper."""
    import re

    async def download_image(dl_url: str) -> bytes:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            r = await client.get(dl_url)
            r.raise_for_status()
            return r.content, r.headers.get("content-type", "")

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}) as client:
            resp = await client.get(req.url)
            resp.raise_for_status()
    except Exception as e:
        raise HTTPException(400, f"Failed to fetch URL: {str(e)}")

    content_type = resp.headers.get("content-type", "")
    image_data = None
    final_content_type = ""

    # Case 1: Response is already an image
    ext_map = {
        "image/jpeg": ".jpg", "image/png": ".png", "image/bmp": ".bmp",
        "image/gif": ".gif", "image/webp": ".webp",
    }
    is_image = any(m in content_type for m in ext_map)
    if is_image:
        image_data = resp.content
        final_content_type = content_type

    # Case 2: Response is JSON (API) - try to extract image URL
    if image_data is None:
        try:
            import json
            data = resp.json() if hasattr(resp, "json") else json.loads(resp.text)

            # Flatten and search for a URL that looks like an image
            def find_image_url(obj, depth=0):
                if depth > 5:
                    return None
                if isinstance(obj, str):
                    if re.search(r"\.(jpg|jpeg|png|bmp|gif|webp)(\?|$)", obj, re.I):
                        return obj
                elif isinstance(obj, dict):
                    for key in ("url", "src", "image_url", "download_url", "raw", "full",
                                 "regular", "large", "original", "path", "link"):
                        if key in obj:
                            result = find_image_url(obj[key], depth + 1)
                            if result:
                                return result
                    for val in obj.values():
                        result = find_image_url(val, depth + 1)
                        if result:
                            return result
                elif isinstance(obj, list):
                    for item in obj[:5]:
                        result = find_image_url(item, depth + 1)
                        if result:
                            return result
                return None

            img_url = find_image_url(data)
            if img_url:
                image_data, final_content_type = await download_image(img_url)
            else:
                raise HTTPException(400, "Could not find an image URL in the API response")
        except (ValueError, TypeError):
            raise HTTPException(400, "Response is not an image and not valid JSON")

    # Determine file extension
    ext = ".jpg"
    for mime, e in ext_map.items():
        if mime in final_content_type:
            ext = e
            break
    if ext == ".jpg" and image_data[:4] == bytes([0x89, 0x50, 0x4E, 0x47]):
        ext = ".png"
    elif ext == ".jpg" and image_data[:6] in (b"GIF87a", b"GIF89a"):
        ext = ".gif"

    dest = WALLPAPER_DIR / f"url_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
    with open(dest, "wb") as f:
        f.write(image_data)

    if set_wallpaper(str(dest)):
        return {"success": True, "path": str(dest)}
    raise HTTPException(500, "Failed to set wallpaper")

@app.post("/api/wallpaper/github")
async def set_github_wallpaper(req: GitHubRequest):
    """Browse GitHub repo for images or set a specific image."""
    # Parse GitHub repo URL
    url = req.repo_url.rstrip("/")
    parts = url.replace("https://github.com/", "").strip("/").split("/")
    if len(parts) < 2:
        raise HTTPException(400, "Invalid GitHub URL")

    owner, repo = parts[0], parts[1]

    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{req.path}"
    params = {"ref": req.branch}

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(api_url, params=params, headers={"Accept": "application/vnd.github.v3+json"})
        if resp.status_code != 200:
            raise HTTPException(400, f"GitHub API error: {resp.status_code}")

        data = resp.json()

    if isinstance(data, list):
        # Directory listing
        items = []
        for item in data:
            if item["type"] == "dir":
                items.append({"type": "dir", "name": item["name"], "path": item["path"]})
            elif item["type"] == "file":
                ext = Path(item["name"]).suffix.lower()
                if ext in IMAGE_EXTENSIONS:
                    items.append({
                        "type": "file",
                        "name": item["name"],
                        "path": item["path"],
                        "download_url": item["download_url"],
                        "size": item.get("size", 0),
                    })
        return {"items": items, "path": req.path}
    elif isinstance(data, dict) and "download_url" in data:
        # Single file - download and set as wallpaper
        dl_url = data["download_url"]
        if not dl_url:
            raise HTTPException(400, "No download URL available")

        dl_resp = await httpx.AsyncClient(timeout=60.0).get(dl_url)
        dl_resp.raise_for_status()

        ext = Path(data["name"]).suffix.lower()
        dest = WALLPAPER_DIR / f"github_{data['name']}"
        with open(dest, "wb") as f:
            f.write(dl_resp.content)

        if set_wallpaper(str(dest)):
            return {"success": True, "path": str(dest)}
        raise HTTPException(500, "Failed to set wallpaper")
    else:
        raise HTTPException(400, "Unexpected GitHub API response")


@app.get("/api/history")
async def get_history():
    """List previously downloaded wallpapers."""
    files = sorted(WALLPAPER_DIR.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
    return {
        "wallpapers": [
            {"name": f.name, "path": str(f), "size": f.stat().st_size}
            for f in files if f.is_file()
        ]
    }


@app.post("/api/wallpaper/set")
async def set_existing_wallpaper(req: SetWallpaperRequest):
    """Set wallpaper from history."""
    path = req.path
    if not os.path.isfile(path):
        raise HTTPException(404, "File not found")
    if set_wallpaper(path):
        return {"success": True}
    raise HTTPException(500, "Failed to set wallpaper")


@app.delete("/api/wallpaper/{filename}")
async def delete_wallpaper(filename: str):
    """Delete a downloaded wallpaper."""
    path = (WALLPAPER_DIR / filename).resolve()
    if not str(path).startswith(str(WALLPAPER_DIR.resolve())):
        raise HTTPException(403, "Access denied")
    if not path.exists():
        raise HTTPException(404, "File not found")
    path.unlink()
    return {"success": True}

@app.get("/api/current-wallpaper-image")
async def current_wallpaper_image():
    path = get_current_wallpaper()
    if not path or not os.path.isfile(path):
        raise HTTPException(404, "No wallpaper found")
    return FileResponse(path)


@app.get("/api/wallpaper-image")
async def wallpaper_image(path: str):
    resolved = Path(path).resolve()
    if not str(resolved).startswith(str(WALLPAPER_DIR.resolve())):
        raise HTTPException(403, "Access denied")
    if not resolved.is_file():
        raise HTTPException(404, "File not found")
    return FileResponse(str(resolved))


# === Serve Vue Frontend ===
# PyInstaller compatible path
def get_static_dir():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "static"
    return Path(__file__).parent / "static"


@app.get("/")
async def index():
    return FileResponse(get_static_dir() / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8899)


