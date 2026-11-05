"""Tests for the NodeErrors Griptape Cloud failures turn into.

The API tests run the generated SDK client against a local HTTP server, so each error comes from the
SDK's own parsing and not from a hand-built response.
"""

# ruff: noqa: D103, PLR2004

import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, ClassVar

import pytest
import requests
from griptape_cloud_client.client import AuthenticatedClient
from griptape_nodes.exe_types.core_types import NodeError
from griptape_nodes.exe_types.node_types import BaseNode
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

from griptape_cloud.base.base_griptape_cloud_node import BaseGriptapeCloudNode
from griptape_cloud.mixins.griptape_cloud_api_mixin import GriptapeCloudApiMixin
from griptape_cloud.node_errors import API_KEY_NAME, API_KEYS_URL, upload_error

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
    assert str(error) == (
        f"Griptape Cloud refused {API_KEY_NAME}. Update the key in Settings → API Keys & Secrets, "
        "then run the node again."
    )
    assert error.fields == {"status_code": 401, "request_id": "req-123", "error_code": "token_not_valid"}
    assert error.response == TOKEN_NOT_VALID
    assert [(link.label, link.url) for link in error.links] == [
        ("Update the API key", f"#settings-secrets?filter={API_KEY_NAME}"),
        ("Get a Griptape Cloud API key", API_KEYS_URL),
    ]


def test_not_found_names_the_action_and_the_reason(server: HTTPServer) -> None:
    _reply(404, {"type": "client_error", "errors": [{"code": "not_found", "detail": "Not found.", "attr": None}]})
    with pytest.raises(NodeError) as exc:
        _api(server)._get_bucket("b-1")

    assert str(exc.value) == "Griptape Cloud could not get bucket: Not found."
    assert exc.value.fields["status_code"] == 404
    assert exc.value.links == []


def test_validation_error_names_the_field(server: HTTPServer) -> None:
    _reply(
        422,
        {"type": "client_error", "errors": [{"code": "required", "detail": "This field is required.", "attr": "name"}]},
    )
    with pytest.raises(NodeError, match=r"could not list buckets: name: This field is required\."):
        _api(server)._list_buckets()


def test_status_the_sdk_does_not_parse_keeps_its_code(server: HTTPServer) -> None:
    """The SDK returns None for a status it has no model for, so the status code must come from elsewhere."""
    _reply(502, b"<html>Bad gateway</html>")
    with pytest.raises(NodeError) as exc:
        _api(server)._list_buckets()

    assert str(exc.value) == "Griptape Cloud could not list buckets. It answered with HTTP 502."
    assert exc.value.fields["status_code"] == 502
    assert exc.value.response == {"text": "<html>Bad gateway</html>"}


def test_rate_limit_says_to_wait(server: HTTPServer) -> None:
    _reply(429, {"type": "client_error", "errors": []})
    with pytest.raises(NodeError, match="rate-limiting"):
        _api(server)._list_buckets()


def test_connection_failure_is_plain() -> None:
    api = _Api("http://127.0.0.1:1")
    with pytest.raises(NodeError, match="Could not reach Griptape Cloud") as exc:
        api._list_buckets()

    assert "ConnectError" not in str(exc.value)


def test_success_returns_the_model(server: HTTPServer) -> None:
    _reply(200, {"buckets": [], "pagination": {"page_number": 1, "page_size": 100, "total_count": 0, "total_pages": 0}})
    assert _api(server)._list_buckets().buckets == []


def test_upload_rejection_does_not_blame_the_api_key() -> None:
    response = requests.Response()
    response.status_code = 403
    response._content = b"<Error><Code>AccessDenied</Code></Error>"
    response.headers["x-amz-request-id"] = "amz-1"
    error = upload_error(requests.HTTPError(response=response))

    assert "HTTP 403" in str(error)
    assert error.links == []
    assert error.fields == {"status_code": 403, "request_id": "amz-1"}
    assert error.response == {"text": "<Error><Code>AccessDenied</Code></Error>"}


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
    assert str(error).startswith(f"{API_KEY_NAME} is not set.")
    assert error.links[0].url == f"#settings-secrets?filter={API_KEY_NAME}"
