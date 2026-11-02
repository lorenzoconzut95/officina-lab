from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class OfficinaHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(
                b"<h1>Officina Lab</h1><p>Server v0.1 is running.</p>"
            )

        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            response = {
                "status": "ok"
            }

            self.wfile.write(
                json.dumps(response).encode()
            )

        elif self.path == "/api/info":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            response = {
                "project": "Officina Lab",
                "version": "0.1",
                "status": "building"
            }

            self.wfile.write(
                json.dumps(response).encode()
            )

        else:
            self.send_response(404)
            self.end_headers()


server = HTTPServer(("localhost", 8000), OfficinaHandler)

print("Officina Server running on http://localhost:8000")

server.serve_forever()