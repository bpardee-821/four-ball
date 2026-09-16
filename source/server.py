"""Run with Python 3.10+: python3 server.py. No third-party packages required."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from store import Problem, Store

ROOT = Path(__file__).resolve().parent


def make_server(host, port, database):
    store = Store(database)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Link tokens must not appear in request logs.

        def send(self, status, data, content_type='application/json'):
            body = json.dumps(data).encode() if content_type == 'application/json' else data
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlsplit(self.path).path
            try:
                if path.startswith('/api/view/'):
                    return self.send(200, store.view(path.removeprefix('/api/view/')))
                assets = {'/app.js': ('app.js', 'text/javascript'),
                          '/style.css': ('style.css', 'text/css'),
                          '/review.html': ('review.html', 'text/html; charset=utf-8')}
                if path in assets:
                    file, kind = assets[path]
                    return self.send(200, (ROOT / 'static' / file).read_bytes(), kind)
                if path == '/' or path.startswith(('/invite/', '/round/')):
                    return self.send(200, (ROOT / 'static/index.html').read_bytes(), 'text/html; charset=utf-8')
                raise Problem(404, 'Page not found.')
            except Problem as error:
                self.send(error.status, {'error': error.message})

        def do_POST(self):
            try:
                size = int(self.headers.get('Content-Length', 0))
                if size < 0 or size > 2048:
                    raise Problem(413, 'Request is too large.')
                payload = json.loads(self.rfile.read(size) or b'{}')
                if not isinstance(payload, dict):
                    raise Problem(400, 'Expected a JSON object.')
                path = urlsplit(self.path).path
                if path == '/api/demos':
                    return self.send(201, store.create(payload.get('scenario', 'priority')))
                if path.startswith('/api/confirm/'):
                    return self.send(200, store.confirm(path.removeprefix('/api/confirm/')))
                raise Problem(404, 'Action not found.')
            except (ValueError, UnicodeError):
                self.send(400, {'error': 'Invalid request.'})
            except Problem as error:
                self.send(error.status, {'error': error.message})

    return ThreadingHTTPServer((host, port), Handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--database', default=str(ROOT / 'demo.sqlite3'))
    args = parser.parse_args()
    server = make_server(args.host, args.port, args.database)
    print(f'Four-Ball demo: http://{args.host}:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
