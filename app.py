#!/usr/bin/env python
"""
Wallpaper Switcher - Desktop Application Entry Point
Launches the FastAPI backend in a background thread and opens a native
Windows window via pywebview (no browser needed).
"""
import sys
import threading
import time
from pathlib import Path

import uvicorn
import webview


def get_static_dir():
    """Get the static files directory (works for dev and PyInstaller)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "static"
    return Path(__file__).parent / "static"


def start_server():
    """Start the FastAPI server in a background thread."""
    from server import app

    class NoSignalServer(uvicorn.Server):
        def install_signal_handlers(self):
            pass

    config = uvicorn.Config(app, host="127.0.0.1", port=8899, log_level="warning")
    server = NoSignalServer(config=config)
    server.run()


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
    webview.start(debug=False)


if __name__ == "__main__":
    main()
