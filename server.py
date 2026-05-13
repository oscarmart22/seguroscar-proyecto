"""HTTP server with Range request support for video seeking.
Binds to both IPv4 and IPv6 to handle all localhost configurations.
"""
import os
import sys
import mimetypes
import socket
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler


class RangeHTTPRequestHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)

        if os.path.isdir(path):
            return super().send_head()

        if not os.path.isfile(path):
            self.send_error(404, "File not found")
            return None

        file_size = os.path.getsize(path)
        ctype, _ = mimetypes.guess_type(path)
        if ctype is None:
            ctype = 'application/octet-stream'

        range_header = self.headers.get('Range')

        if range_header and range_header.startswith('bytes='):
            range_spec = range_header[6:].strip()
            parts = range_spec.split('-')
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
            end = min(end, file_size - 1)
            length = end - start + 1

            f = open(path, 'rb')
            f.seek(start)

            self.send_response(206)
            self.send_header('Content-type', ctype)
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Content-Range', 'bytes %d-%d/%d' % (start, end, file_size))
            self.send_header('Content-Length', str(length))
            self.end_headers()
            return LimitedFile(f, length)
        else:
            f = open(path, 'rb')
            self.send_response(200)
            self.send_header('Content-type', ctype)
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Content-Length', str(file_size))
            self.end_headers()
            return f


class LimitedFile:
    def __init__(self, f, limit):
        self.f = f
        self.remaining = limit

    def read(self, n=-1):
        if self.remaining <= 0:
            return b''
        if n < 0 or n > self.remaining:
            n = self.remaining
        data = self.f.read(n)
        self.remaining -= len(data)
        return data

    def close(self):
        self.f.close()


class HTTPServerV6(HTTPServer):
    address_family = socket.AF_INET6


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))

    # Start IPv4 server
    server4 = HTTPServer(('0.0.0.0', port), RangeHTTPRequestHandler)
    t4 = threading.Thread(target=server4.serve_forever, daemon=True)
    t4.start()
    print(f'IPv4 server running on 0.0.0.0:{port}', flush=True)

    # Start IPv6 server on a different port or same port
    try:
        server6 = HTTPServerV6(('::', port + 1), RangeHTTPRequestHandler)
        t6 = threading.Thread(target=server6.serve_forever, daemon=True)
        t6.start()
        print(f'IPv6 server running on [::]:{port + 1}', flush=True)
    except OSError:
        pass

    print(f'\nOpen http://127.0.0.1:{port} in your browser', flush=True)

    try:
        while True:
            t4.join(1)
            if not t4.is_alive():
                break
    except KeyboardInterrupt:
        print("\nCerrando servidor...")
        server4.shutdown()
        if 'server6' in locals():
            server6.shutdown()
