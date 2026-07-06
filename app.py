#!/usr/bin/env python
"""
Wallpaper Switcher - Desktop Application Entry Point
Launches FastAPI backend, opens native window via pywebview,
and runs a system-tray daemon. Close = minimize to tray.
"""
import os
import sys
import threading
import time
from pathlib import Path

import uvicorn
import webview


def get_static_dir():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "static"
    return Path(__file__).parent / "static"


def get_icon_path():
    """Get icon path for system tray (works for dev and PyInstaller)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "icon.ico"
    return Path(__file__).parent / "icon.ico"


def start_server():
    from server import app

    class NoSignalServer(uvicorn.Server):
        def install_signal_handlers(self):
            pass

    config = uvicorn.Config(app, host="127.0.0.1", port=8899, log_level="warning")
    server = NoSignalServer(config=config)
    server.run()


def create_tray_icon(window_ref):
    """Create Windows system tray icon. Runs in background thread."""
    import pystray
    from PIL import Image, ImageDraw, ImageFont

    # Generate tray icon image
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([4, 4, 60, 60], radius=14, fill=(108, 92, 231))
    draw.rounded_rectangle([6, 6, 58, 58], radius=12, fill=(90, 75, 210))
    # Draw "WS" text
    try:
        font = ImageFont.truetype("segoeui.ttf", 24)
    except Exception:
        font = ImageFont.load_default()
    draw.text((14, 16), "WS", fill="white", font=font)

    def on_show(icon, item):
        try:
            if window_ref[0] is not None:
                window_ref[0].show()
        except Exception:
            pass

    def on_exit(icon, item):
        icon.stop()
        os._exit(0)

    menu = pystray.Menu(
        pystray.MenuItem("显示窗口", on_show, default=True),
        pystray.MenuItem("退出", on_exit),
    )
    icon = pystray.Icon("WallpaperSwitcher", img, "Wallpaper Switcher", menu)
    icon.run()


def main():
    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Wait for server to be ready
    for _ in range(30):
        try:
            import urllib.request
            urllib.request.urlopen("http://127.0.0.1:8899/api/wallpaper/current", timeout=1)
            break
        except Exception:
            time.sleep(0.3)

    # Open native window
    window = webview.create_window(
        title="Wallpaper Switcher",
        url="http://127.0.0.1:8899",
        width=1200,
        height=800,
        min_size=(900, 600),
        resizable=True,
        text_select=True,
    )

    # Shared reference for tray thread to access window
    window_ref = [window]

    # Intercept close → minimize to tray
    window.events.closing += lambda: (window.hide(), False)[1]

    # Start system tray in background thread
    tray_thread = threading.Thread(target=create_tray_icon, args=(window_ref,), daemon=True)
    tray_thread.start()

    # Start webview (blocks main thread)
    webview.start(debug=False)


if __name__ == "__main__":
    main()
