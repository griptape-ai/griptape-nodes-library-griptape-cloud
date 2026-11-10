"""Tests for the NodeErrors Griptape Cloud failures turn into.

The API tests run the generated SDK client against a local HTTP server, so each error comes from the
SDK's own parsing and not from a hand-built response.
"""

# ruff: noqa: D103, PLR2004

import importlib.util
import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, ClassVar

import pytest
from griptape_cloud_client.client import AuthenticatedClient
from griptape_nodes.exe_types.core_types import NodeError
from griptape_nodes.exe_types.node_types import BaseNode
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

from griptape_cloud import node_errors
from griptape_cloud.base.base_griptape_cloud_node import BaseGriptapeCloudNode
from griptape_cloud.mixins.griptape_cloud_api_mixin import GriptapeCloudApiMixin
from griptape_cloud.node_errors import API_KEY_ENV_VAR

TOKEN_NOT_VALID = {
    "type": "client_error",
    "errors": [
        {"code": "token_not_valid", "detail": "Given token not valid for any token type", "attr": "detail"},
        {"code": "token_not_valid", "detail": "Token is invalid", "attr": "messages.0.message"},
    ],
}


class _Handler(BaseHTTPRequestHandler):
    reply: ClassVar[dict[str, Any]] = {}

    def do_GET(self) -> None:
        body = self.reply["body"]
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(self.reply["status"])
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("x-request-id", "req-123")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args: Any) -> None:
        pass


@pytest.fixture
def server() -> Iterator[HTTPServer]:
    httpd = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield httpd
    httpd.shutdown()
    thread.join()


class _Api(GriptapeCloudApiMixin):
    def __init__(self, base_url: str) -> None:
        self.gtc_client = AuthenticatedClient(base_url=base_url, token="bad-token")  # noqa: S106


def _api(server: HTTPServer) -> _Api:
    return _Api(f"http://127.0.0.1:{server.server_port}")


def _reply(status: int, body: Any) -> None:
    _Handler.reply = {"status": status, "body": body}


def test_refused_key_links_to_the_secret(server: HTTPServer) -> None:
    _reply(401, TOKEN_NOT_VALID)
    with pytest.raises(NodeError) as exc:
        _api(server)._list_buckets()

    error = exc.value
    assert str(error).startswith("Griptape Cloud refused the API key.")
    assert error.fields == {"status_code": 401, "request_id": "req-123", "error_code": "token_not_valid"}
    assert error.response == TOKEN_NOT_VALID
    assert [(link.label, link.url) for link in error.links] == [
        ("Update the API key", f"#settings-secrets?filter={API_KEY_ENV_VAR}"),
    ]


def test_not_found_names_the_action_and_the_reason(server: HTTPServer) -> None:
    _reply(404, {"type": "client_error", "errors": [{"code": "not_found", "detail": "Not found.", "attr": None}]})
    with pytest.raises(NodeError) as exc:
        _api(server)._get_bucket("b-1")

    assert str(exc.value) == "Griptape Cloud could not get bucket: Not found."
    assert exc.value.fields["status_code"] == 404
    assert exc.value.fields["error_code"] == "not_found"
    assert exc.value.links == []


BAD_BODIES = pytest.mark.parametrize("body", [b"<html>Bad gateway</html>", b"", [1, 2]], ids=["html", "empty", "list"])


@BAD_BODIES
@pytest.mark.parametrize("status", [429, 502, 503, 504])
def test_an_unmodelled_status_keeps_its_code_whatever_the_body(server: HTTPServer, status: int, body: Any) -> None:
    """The SDK does not read the body of a status it has no model for, so the status reaches the error."""
    _reply(status, body)
    with pytest.raises(NodeError) as exc:
        _api(server)._list_buckets()

    assert exc.value.fields["status_code"] == status


@BAD_BODIES
@pytest.mark.parametrize("status", [200, 401, 404, 500])
def test_a_modelled_status_with_a_body_the_sdk_cannot_parse_is_a_node_error(
    server: HTTPServer, status: int, body: Any
) -> None:
    """The SDK raises from its own parser here. The error has no status, because it never returned the response."""
    _reply(status, body)
    with pytest.raises(NodeError, match="could not read") as exc:
        _api(server)._list_buckets()

    assert isinstance(exc.value.__cause__, (ValueError, KeyError, TypeError, AttributeError))


def test_forbidden_is_not_a_refused_key(server: HTTPServer) -> None:
    _reply(
        403, {"type": "client_error", "errors": [{"code": "permission_denied", "detail": "No access.", "attr": None}]}
    )
    with pytest.raises(NodeError) as exc:
        _api(server)._get_bucket("b-1")

    assert str(exc.value) == "Griptape Cloud could not get bucket: No access."
    assert exc.value.links == []


def test_connection_failure_is_plain() -> None:
    api = _Api("http://127.0.0.1:1")
    with pytest.raises(NodeError, match="Could not reach Griptape Cloud") as exc:
        api._list_buckets()

    assert "ConnectError" not in str(exc.value)


def test_missing_key_is_the_only_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """With no key, nothing else is listed, and the error links to the secret."""
    monkeypatch.setattr(
        type(GriptapeNodes.SecretsManager()), "get_secret", lambda *_args, **_kwargs: None, raising=True
    )
    node = object.__new__(BaseGriptapeCloudNode)

    def _fail(_self: BaseNode) -> list[Exception]:
        msg = "validation must stop at the key"
        raise AssertionError(msg)

    monkeypatch.setattr(BaseNode, "validate_before_node_run", _fail)
    errors = node.validate_before_node_run()

    assert errors is not None
    assert len(errors) == 1
    error = errors[0]
    assert isinstance(error, NodeError)
    assert str(error).startswith(f"{API_KEY_ENV_VAR} is not set.")
    assert error.links[0].url == f"#settings-secrets?filter={API_KEY_ENV_VAR}"


def test_node_files_load_the_way_the_engine_loads_them(monkeypatch: pytest.MonkeyPatch) -> None:
    """The engine loads each node file on its own, with the manifest's folder on sys.path."""
    root = Path(__file__).parents[2]
    manifest = json.loads((root / "griptape_nodes_library.json").read_text())
    monkeypatch.syspath_prepend(str(root))
    for node in manifest["nodes"]:
        path = root / node["file_path"]
        spec = importlib.util.spec_from_file_location(f"engine_style_{path.stem}", path)
        assert spec is not None
        assert spec.loader is not None
        spec.loader.exec_module(importlib.util.module_from_spec(spec))


def test_a_local_error_before_the_request_is_not_blamed_on_griptape_cloud(server: HTTPServer) -> None:
    api = _api(server)

    def endpoint(**_kwargs: Any) -> None:
        msg = "unexpected keyword argument"
        raise TypeError(msg)

    with pytest.raises(TypeError, match="unexpected keyword argument"):
        api._call_api(endpoint, object, "list buckets")


def _node_with_key(monkeypatch: pytest.MonkeyPatch, server: HTTPServer) -> BaseGriptapeCloudNode:
    """A node whose default-bucket lookup goes to the local server through the engine's own reader."""
    secrets = {API_KEY_ENV_VAR: "bad-token"}
    monkeypatch.setattr(
        type(GriptapeNodes.SecretsManager()), "get_secret", lambda _self, name, **_kw: secrets.get(name), raising=True
    )
    node = object.__new__(BaseGriptapeCloudNode)
    node.base_url = f"http://127.0.0.1:{server.server_port}"
    return node


def test_default_bucket_401_keeps_the_key_link(server: HTTPServer, monkeypatch: pytest.MonkeyPatch) -> None:
    _reply(401, TOKEN_NOT_VALID)
    with pytest.raises(NodeError) as exc:
        _node_with_key(monkeypatch, server)._get_default_bucket_id()

    assert str(exc.value).startswith("Griptape Cloud refused the API key.")
    assert [link.url for link in exc.value.links] == [f"#settings-secrets?filter={API_KEY_ENV_VAR}"]
    assert exc.value.fields["error_code"] == "token_not_valid"


def test_default_bucket_403_shows_clouds_reason_and_no_key_link(
    server: HTTPServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    _reply(
        403, {"type": "client_error", "errors": [{"code": "permission_denied", "detail": "No access.", "attr": None}]}
    )
    with pytest.raises(NodeError) as exc:
        _node_with_key(monkeypatch, server)._get_default_bucket_id()

    assert str(exc.value) == "Griptape Cloud could not read your default bucket: No access."
    assert exc.value.links == []
    assert exc.value.fields["status_code"] == 403


def test_key_page_link_follows_the_configured_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GT_CLOUD_BASE_URL", "https://cloud.example.test")
    reloaded = importlib.reload(node_errors)
    try:
        assert reloaded.API_KEY_URL == "https://cloud.example.test/configuration/api-keys"
    finally:
        monkeypatch.undo()
        importlib.reload(node_errors)
