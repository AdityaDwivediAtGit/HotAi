import http.server
import socketserver
import webbrowser
import os
import threading
import time

PORT = 8001
DIRECTORY = "ui"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

def start_server():
    try:
        with ThreadedTCPServer(("", PORT), Handler) as httpd:
            addr, port = httpd.server_address
            print(f"Serving at http://localhost:{port}")
            webbrowser.open(f"http://localhost:{port}/index.html")
            httpd.serve_forever()
    except OSError as e:
        print(f"Failed to bind port {PORT}: {e}")
        print("Make sure no other service is using port 8001, then restart run_ui.py.")

if __name__ == "__main__":
    print("Starting local server for HotAI UI...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server.")
