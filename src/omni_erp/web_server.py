"""Local web server for OMNI ERP."""

from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from omni_erp.web_import import import_order_file
from omni_erp.web_state import read_state, write_state


class OmniWebHandler(SimpleHTTPRequestHandler):
    """Serve the web app and import uploaded order files."""

    project_root: Path

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/api/state":
            self._send_json(read_state(self.project_root))
            return
        super().do_GET()

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)
        if parsed_url.path != "/api/import/orders":
            self.send_error(404)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        content = self.rfile.read(content_length)
        file_name = self.headers.get("X-Filename", "orders.xlsx")
        platform_hint = parse_qs(parsed_url.query).get("platform", [""])[0]

        try:
            orders = import_order_file(file_name=file_name, content=content, platform_hint=platform_hint)
        except Exception as exc:  # pragma: no cover - returned to browser for usability
            self._send_json({"error": str(exc)}, status=400)
            return

        self._send_json({"orders": orders, "count": len(orders)})

    def do_PUT(self) -> None:
        parsed_url = urlparse(self.path)
        if parsed_url.path != "/api/state":
            self.send_error(404)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        content = self.rfile.read(content_length)
        try:
            state = json.loads(content.decode("utf-8"))
            state_path = write_state(self.project_root, state)
        except Exception as exc:  # pragma: no cover - returned to browser for usability
            self._send_json({"error": str(exc)}, status=400)
            return

        self._send_json({"saved": True, "path": str(state_path)})

    def _send_json(self, payload: dict[str, object], *, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(*, project_root: str | Path = ".", host: str = "127.0.0.1", port: int = 8765) -> None:
    root = Path(project_root).resolve()
    web_root = root / "web"

    def handler(*args, **kwargs):
        request_handler = OmniWebHandler(*args, directory=str(web_root), **kwargs)
        return request_handler

    OmniWebHandler.project_root = root
    server = ThreadingHTTPServer((host, port), handler)
    print(f"OMNI ERP web app: http://{host}:{port}")
    print(f"Data file: {root / 'data' / 'omni-data.json'}")
    server.serve_forever()
