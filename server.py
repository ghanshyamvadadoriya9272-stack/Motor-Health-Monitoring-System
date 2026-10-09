"""
Local HTTP Server for Motor Health Monitoring System Web Dashboard
Includes automatic port detection, socket reuse, and graceful fallback.
"""

import http.server
import socketserver
import webbrowser
import os
import sys

DEFAULT_PORT = 8080

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def find_available_server(start_port=DEFAULT_PORT, max_tries=10):
    for port in range(start_port, start_port + max_tries):
        try:
            httpd = ReusableTCPServer(("", port), NoCacheHandler)
            return httpd, port
        except OSError:
            continue
    return None, None

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    httpd, port = find_available_server(DEFAULT_PORT)
    if not httpd:
        print("[ERROR] Could not find an available port between 8080 and 8090.")
        print("Please terminate any process occupying the ports and try again.")
        sys.exit(1)

    url = f"http://localhost:{port}"
    print("=" * 65)
    print(" ⚡ MOTOR HEALTH MONITORING SYSTEM - WEB DASHBOARD")
    print(" Milestone 3 Submission (Roll: 240280109042)")
    print("=" * 65)
    print(f" Status: Server running actively")
    print(f" URL:    {url}")
    print(" Press Ctrl+C in this terminal to stop the server.")
    print("=" * 65)

    if "--no-browser" not in sys.argv:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped gracefully.")
    finally:
        httpd.server_close()

if __name__ == '__main__':
    main()
