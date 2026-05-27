from http.server import SimpleHTTPRequestHandler, HTTPServer
import os

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = "<h1>Hello from test-app!</h1>"
            self.wfile.write(message.encode('utf-8'))
        elif self.path == '/healthz':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            super().do_GET()

def run(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, MyHandler)
    print(f"Starting test-app server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()