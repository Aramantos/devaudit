"""
Tests for the dashboard's local-only guard (found 2026-10-18).

The dashboard has no authentication: it trusts that only the local user can
reach 127.0.0.1. Three browser-borne attacks break that trust, and each test
below was written RED against the unguarded server first:
- DNS rebinding: an attacker's domain re-resolves to 127.0.0.1, so its page
  is "same-origin" and CORS never applies. Defence: the Host header must
  name this machine.
- Cross-site requests that need no preflight (a form POST to /api/scan) and
  cross-site WebSocket hijacking (browsers apply no CORS to WebSockets, so
  any page could read the scan broadcasts). Defence: an Origin, when sent,
  must be local.
- Spec injection: /api/cleanup/* passed caller-supplied strings straight to
  pip/npm/docker, so "git+https://..." installed arbitrary code and
  "--index-url=..." rewired pip. Defence: strict name validation, refused
  before any subprocess runs.
"""
import subprocess

import pytest

pytest.importorskip("fastapi", reason="server extra not installed")
pytest.importorskip("httpx", reason="dev extra not installed")

import importlib

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

app_module = importlib.import_module("devaudit.server.app")

LOCAL = "http://127.0.0.1:8888"
EVIL = "https://evil.example"


@pytest.fixture
def client():
    return TestClient(app_module.app, base_url=LOCAL)


@pytest.fixture
def pip_calls(monkeypatch):
    """Record subprocess.run instead of running pip/npm/docker for real."""
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        return subprocess.CompletedProcess(argv, 0, stdout="ok", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


# --- Host header (DNS rebinding) -------------------------------------------

def test_foreign_host_header_is_refused(client):
    response = client.get("/api/health", headers={"host": "evil.example"})
    assert response.status_code == 400


def test_rebinding_host_with_local_port_is_refused(client):
    response = client.get("/api/health", headers={"host": "evil.example:8888"})
    assert response.status_code == 400


@pytest.mark.parametrize("host", ["127.0.0.1:8888", "localhost:8888", "[::1]:8888", "localhost"])
def test_local_host_headers_are_served(client, host):
    """Positive control: the guard must not lock the real user out."""
    response = client.get("/api/health", headers={"host": host})
    assert response.status_code == 200


# --- Origin on state-changing requests (CSRF) --------------------------------

def test_cross_origin_scan_trigger_is_refused(client):
    """/api/scan takes a query param, so a plain cross-site form POST reaches
    it without any CORS preflight."""
    response = client.post("/api/scan", headers={"origin": EVIL})
    assert response.status_code == 403


def test_null_origin_is_refused(client):
    """Sandboxed iframes and file:// pages send Origin: null."""
    response = client.post("/api/scan", headers={"origin": "null"})
    assert response.status_code == 403


def test_same_origin_scan_trigger_is_not_refused(client):
    """Positive control: the dashboard's own POST still gets through the
    guard (the scanner is uninitialised in tests, hence 500, never 403)."""
    response = client.post("/api/scan", headers={"origin": LOCAL})
    assert response.status_code != 403


def test_request_without_origin_is_not_refused(client):
    """Non-browser clients (curl, the tray widget) send no Origin."""
    response = client.post("/api/scan")
    assert response.status_code != 403


def test_cors_preflight_allows_the_real_serve_port(client):
    """The CORS list used to name 8080/3000 while `devaudit serve` binds 8888."""
    response = client.options(
        "/api/scan",
        headers={"origin": LOCAL, "access-control-request-method": "POST"},
    )
    assert response.headers.get("access-control-allow-origin") == LOCAL


def test_cors_preflight_from_foreign_origin_gets_no_grant(client):
    response = client.options(
        "/api/scan",
        headers={"origin": EVIL, "access-control-request-method": "POST"},
    )
    assert response.headers.get("access-control-allow-origin") is None


# --- WebSocket (cross-site WebSocket hijacking) ------------------------------
# Starlette's TestClient hard-codes "host: testserver" on WebSocket scopes, so
# each test sends a local Host: the refusal below must come from the ORIGIN
# check, not pass for the wrong reason on the Host check.

def test_cross_origin_websocket_is_refused(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws", headers={"host": "127.0.0.1:8888", "origin": EVIL}) as ws:
            ws.send_text("ping")
            ws.receive_text()


def test_rebinding_host_websocket_is_refused(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws", headers={"host": "evil.example:8888", "origin": "http://evil.example:8888"}) as ws:
            ws.send_text("ping")
            ws.receive_text()


def test_same_origin_websocket_is_served(client):
    with client.websocket_connect("/ws", headers={"host": "127.0.0.1:8888", "origin": LOCAL}) as ws:
        ws.send_text("ping")
        assert "ping" in ws.receive_text()


# --- Package / container spec injection --------------------------------------

@pytest.mark.parametrize("spec", [
    "git+https://evil.example/payload.git",
    "--index-url=https://evil.example/simple",
    "-r",
    "../local/path",
    "https://evil.example/pkg.tar.gz",
    "requests==2.0",
    "",
])
def test_python_upgrade_refuses_non_names(client, pip_calls, spec):
    response = client.post("/api/cleanup/python/upgrade", json=[spec])
    assert response.status_code == 400
    assert pip_calls == []


def test_python_upgrade_refuses_the_whole_batch_if_one_is_bad(client, pip_calls):
    response = client.post("/api/cleanup/python/upgrade",
                           json=["requests", "git+https://evil.example/x.git"])
    assert response.status_code == 400
    assert pip_calls == []


def test_python_upgrade_runs_pip_for_a_real_name(client, pip_calls):
    response = client.post("/api/cleanup/python/upgrade", json=["zope.interface"])
    assert response.status_code == 200
    assert pip_calls == [["pip", "install", "--upgrade", "zope.interface"]]


@pytest.mark.parametrize("spec", ["-y", "--requirement=x.txt", "git+https://evil.example/x"])
def test_python_uninstall_refuses_non_names(client, pip_calls, spec):
    response = client.post("/api/cleanup/python/uninstall", json=[spec])
    assert response.status_code == 400
    assert pip_calls == []


@pytest.mark.parametrize("spec", [
    "git+https://evil.example/x.git",
    "file:../payload",
    "github-user/repo",
    "--prefix=/tmp",
    "pkg@1.0.0",
])
def test_node_upgrade_refuses_non_names(client, pip_calls, spec):
    response = client.post("/api/cleanup/node/upgrade", json=[spec])
    assert response.status_code == 400
    assert pip_calls == []


def test_node_upgrade_runs_npm_for_a_scoped_name(client, pip_calls):
    response = client.post("/api/cleanup/node/upgrade", json=["@angular/cli"])
    assert response.status_code == 200
    assert pip_calls == [["npm", "install", "-g", "@angular/cli@latest"]]


@pytest.mark.parametrize("endpoint", [
    "/api/cleanup/docker/remove-containers",
    "/api/cleanup/docker/remove-images",
])
@pytest.mark.parametrize("ref", ["--all", "-f", "$(id)"])
def test_docker_removal_refuses_options(client, pip_calls, endpoint, ref):
    response = client.post(endpoint, json=[ref])
    assert response.status_code == 400
    assert pip_calls == []


def test_docker_image_removal_accepts_real_refs(client, pip_calls):
    refs = ["3f2a1b9c8d7e", "postgres:16-alpine", "ghcr.io/org/app@sha256:abc123"]
    response = client.post("/api/cleanup/docker/remove-images", json=refs)
    assert response.status_code == 200
    assert pip_calls == [["docker", "rmi", "-f", r] for r in refs]
