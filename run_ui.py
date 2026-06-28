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

def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        addr, port = httpd.server_address
        print(f"Serving at http://localhost:{port}")
        webbrowser.open(f"http://localhost:{port}/index.html")
        httpd.serve_forever()

if __name__ == "__main__":
    print("Starting local server for HotAI UI...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server.")
