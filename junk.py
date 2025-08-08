from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import time

class TimeServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Format: ISO 8601 string
        fake_time = datetime.now().isoformat()
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(fake_time.encode())

def run(server_class=HTTPServer, handler_class=TimeServer, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting HTTP time server on port {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
