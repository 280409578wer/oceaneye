from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
BACKEND_ROOT = "http://127.0.0.1:8000"


class SpaRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIST), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_GET(self) -> None:
        if self.path.startswith("/api/"):
            self._proxy("GET")
            return
        requested = urlparse(self.path).path.lstrip("/")
        if requested and not (FRONTEND_DIST / requested).is_file():
            self.path = "/index.html"
        super().do_GET()

    def do_PUT(self) -> None:
        if self.path.startswith("/api/"):
            self._proxy("PUT")
            return
        self.send_error(405)

    def _proxy(self, method: str) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else None
        request = Request(
            f"{BACKEND_ROOT}{self.path}",
            data=body,
            method=method,
            headers={"Content-Type": self.headers.get("Content-Type", "application/json")},
        )
        try:
            with urlopen(request, timeout=15) as response:
                content = response.read()
                self.send_response(response.status)
                self.send_header("Content-Type", response.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
        except HTTPError as error:
            content = error.read()
            self.send_response(error.code)
            self.send_header("Content-Type", error.headers.get("Content-Type", "application/json"))
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except OSError:
            content = b'{"detail":"Backend is unavailable"}'
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    if not (FRONTEND_DIST / "index.html").exists():
        raise SystemExit("Frontend build is missing. Run setup.bat first.")
    server = ThreadingHTTPServer(("127.0.0.1", 5173), SpaRequestHandler)
    print("OceanEye frontend: http://127.0.0.1:5173")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
