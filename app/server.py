import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            applicationInstanceName = os.environ.get("APP_NAME", "Unknown App Source")
            with open("index.html", "r", encoding="utf-8") as index_file:
                content = index_file.read()

            modified_content = content.format(APP_NAME=applicationInstanceName)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(modified_content.encode("utf-8"))
            
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"File not found")
            return
            
if __name__ == "__main__":
    applicationInstanceName = os.environ.get("APP_NAME", "Unknown App Source")
    
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"[{applicationInstanceName}] Server running on {server_address[0]}:{server_address[1]}")
    httpd.serve_forever()