import http.server
import socketserver
#from CGIHTTPServer import _url_collapse_path

PORT = 8000
DIRECTORY = "./"

## Ovveride GCI base class to manually set GCI folder
class TestGCIHTTPServer(http.server.CGIHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    # Always run api.py as cgi, never anything else
    def is_cgi(self):
        self.cgi_info = '', 'api.py'
        return True

handler = TestGCIHTTPServer
handler.cgi_directories = ["/"]

with socketserver.TCPServer(("", PORT), handler) as httpd:
    print("Serving test server on port", PORT)
    httpd.server_name = "API test server"
    httpd.server_port = PORT
    httpd.serve_forever()

