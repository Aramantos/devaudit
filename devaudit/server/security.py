"""
Local-only request guard and input validation for the dashboard server.

The dashboard has no authentication: it is a tool for the person sitting at
this machine, bound to 127.0.0.1. These checks are what stop a web page that
person happens to have open from driving it:

- The Host header must name this machine. This defeats DNS rebinding, where
  an attacker's domain re-resolves to 127.0.0.1 and its page becomes
  "same-origin", so CORS never applies.
- A state-changing request or a WebSocket handshake that carries an Origin
  must come from a local origin. Browsers send cross-site form POSTs without
  a CORS preflight and apply no CORS to WebSockets at all, so without this
  any page could trigger scans or read the scan broadcasts.
- Package and container names are validated before they reach pip, npm or
  docker, so a request can never smuggle in a URL, a path or an option.
"""

import os
import re
from typing import Iterable, List, Optional, Set
from urllib.parse import urlsplit

from fastapi.responses import JSONResponse
from starlette.websockets import WebSocketClose

LOCAL_HOSTNAMES = frozenset({"localhost", "127.0.0.1", "::1"})

# Matches what CORS should grant: the same local hosts, any port.
LOCAL_ORIGIN_REGEX = r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$"

UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})

_extra_hostnames: Set[str] = set()


def allow_hostname(hostname: str) -> None:
    """Trust one more hostname (the specific address `serve --host` bound to)."""
    _extra_hostnames.add(hostname.strip().lower())


def allowed_hostnames() -> Set[str]:
    """Local names, the bound address, and DEVAUDIT_ALLOWED_HOSTS (comma list)."""
    from_env = os.getenv("DEVAUDIT_ALLOWED_HOSTS", "")
    extra = {h.strip().lower() for h in from_env.split(",") if h.strip()}
    return set(LOCAL_HOSTNAMES) | _extra_hostnames | extra


def _hostname_of_host_header(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("["):  # [::1]:8888
        return value[1:value.find("]")] if "]" in value else ""
    if value.count(":") == 1:  # name:port
        return value.split(":", 1)[0]
    return value


def host_is_allowed(host_header: Optional[str]) -> bool:
    if not host_header:
        return False
    return _hostname_of_host_header(host_header) in allowed_hostnames()


def origin_is_allowed(origin: Optional[str]) -> bool:
    """True only for an http(s) origin naming an allowed host ("null" is not)."""
    if not origin:
        return False
    try:
        parts = urlsplit(origin)
    except ValueError:
        return False
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return False
    return parts.hostname.lower() in allowed_hostnames()


class LocalOnlyGuard:
    """Pure ASGI middleware applying the Host and Origin rules above."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        headers = {}
        for key, value in scope.get("headers", []):
            headers.setdefault(key.decode("latin-1").lower(), value.decode("latin-1"))

        if not host_is_allowed(headers.get("host")):
            await self._refuse(scope, receive, send, 400, "Invalid host header")
            return

        checks_origin = scope["type"] == "websocket" or scope.get("method") in UNSAFE_METHODS
        origin = headers.get("origin")
        # No Origin = not a browser (curl, the tray widget); browsers always send one here.
        if checks_origin and origin is not None and not origin_is_allowed(origin):
            await self._refuse(scope, receive, send, 403, "Cross-origin request refused")
            return

        await self.app(scope, receive, send)

    @staticmethod
    async def _refuse(scope, receive, send, status_code: int, message: str):
        if scope["type"] == "websocket":
            await WebSocketClose(code=1008)(scope, receive, send)
            return
        response = JSONResponse({"status": "error", "message": message}, status_code=status_code)
        await response(scope, receive, send)


# --- names handed to pip / npm / docker --------------------------------------

# PEP 508 project name: alphanumeric at both ends, . _ - inside. No versions,
# extras, URLs, paths or options.
_PYTHON_NAME = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")

# npm package name, optionally scoped. No ':' (git+https:, file:), no bare
# "user/repo" (npm reads that as a GitHub shorthand), no leading '-', '.', '_'.
_NPM_NAME = re.compile(r"^(?:@[a-z0-9][a-z0-9._~-]*/)?[a-z0-9][a-z0-9._~-]*$", re.IGNORECASE)

# Docker container id/name or image reference (repo/name:tag, name@sha256:...).
_DOCKER_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/@-]*$")


def _invalid(names: Iterable[str], pattern, max_len: int) -> List[str]:
    return [n for n in names if not isinstance(n, str) or len(n) > max_len or not pattern.match(n)]


def invalid_python_names(names: Iterable[str]) -> List[str]:
    return _invalid(names, _PYTHON_NAME, 200)


def invalid_npm_names(names: Iterable[str]) -> List[str]:
    return _invalid(names, _NPM_NAME, 214)


def invalid_docker_refs(refs: Iterable[str]) -> List[str]:
    return _invalid(refs, _DOCKER_REF, 255)


def refuse_invalid(kind: str, invalid: List[str]) -> JSONResponse:
    """Refuse the whole batch: nothing runs if any entry is not a plain name."""
    return JSONResponse({
        "status": "error",
        "message": f"Refused: not a valid {kind}. Nothing was run.",
        "invalid": invalid,
    }, status_code=400)
