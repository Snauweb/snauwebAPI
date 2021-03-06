import http.server
import socketserver
import sys

PORT = 8000
DIRECTORY = "./"

## Ovveride GCI base class to manually set GCI folder
class TestGCIHTTPServer(http.server.CGIHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
      

    def do_DELETE(self):
        self.do_POST()

    def do_PUT(self):
        self.do_POST()

handler = TestGCIHTTPServer
handler.cgi_directories += ["/snauwebAPI"]

with socketserver.TCPServer(("", PORT), handler) as httpd:
    print("Serving test server on port", PORT)
    httpd.server_name = "API test server"
    httpd.server_port = PORT
    httpd.serve_forever()

