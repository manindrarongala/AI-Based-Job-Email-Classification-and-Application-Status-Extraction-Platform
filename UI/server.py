#!/usr/bin/env python3
"""
Simple HTTP server to serve the UI files.
Run: python server.py
Then open: http://localhost:8080
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 8080
UI_DIR = Path(__file__).parent.absolute()

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for API communication
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(UI_DIR)
    
    print(f"🚀 Starting UI server...")
    print(f"📂 Serving files from: {UI_DIR}")
    print(f"🌐 Open http://localhost:{PORT}")
    print(f"💡 Make sure backend is running on http://localhost:8000")
    print(f"⚡ Press Ctrl+C to stop\n")
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"✅ Server running on http://localhost:{PORT}\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")
