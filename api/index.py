import os
import sys
import json
import traceback
from pathlib import Path

_curr = Path(__file__).resolve().parent
_root = _curr.parent

for p in [str(_curr), str(_root), os.getcwd(), "/var/task/api", "/var/task"]:
    if p not in sys.path:
        sys.path.insert(0, p)

_import_error = None
_import_traceback = None
_real_app = None

try:
    from backend.app.main import app as _real_app
except Exception as e:
    _import_error = str(e)
    _import_traceback = traceback.format_exc()
    print(f"CRITICAL: Failed to import backend.app.main: {e}\n{_import_traceback}")


async def app(scope, receive, send):
    """ASGI application entrypoint for Vercel Serverless Functions."""
    if _real_app is not None:
        return await _real_app(scope, receive, send)

    if scope.get("type") == "http":
        body = json.dumps({
            "error": "Backend Import Failure",
            "detail": _import_error,
            "traceback": _import_traceback,
            "sys_path": sys.path,
            "cwd": os.getcwd()
        }).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": 500,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("utf-8")),
                (b"access-control-allow-origin", b"*"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
