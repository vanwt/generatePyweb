from wsgiref.simple_server import WSGIRequestHandler
from socketserver import ThreadingTCPServer
import socket


class HTTPServer(ThreadingTCPServer):
    allow_reuse_address = 1  # Seems to make sense in testing environment

    def server_bind(self):
        """Override server_bind to store the server name."""
        ThreadingTCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port


class WSGIServer(HTTPServer):
    """BaseHTTPServer that implements the Python WSGI protocol"""

    application = None

    def server_bind(self):
        """Override server_bind to store the server name."""
        HTTPServer.server_bind(self)
        self.setup_environ()

    def setup_environ(self):
        # Set up base environment
        env = self.base_environ = {}
        env['SERVER_NAME'] = self.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PORT'] = str(self.server_port)
        env['REMOTE_HOST'] = ''
        env['CONTENT_LENGTH'] = ''
        env['SCRIPT_NAME'] = ''

    def get_app(self):
        return self.application

    def set_app(self, application):
        self.application = application


def make_server(address, application):
    server = WSGIServer(address, WSGIRequestHandler)
    server.set_app(application)
    print("Fish Api Service v0.1")
    print("Multithreaded Server version v0.1 ")
    print("Server on %d" % address[1])
    print("Default url: http://%s:%d" % address)
    server.serve_forever()
