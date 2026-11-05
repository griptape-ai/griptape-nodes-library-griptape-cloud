"""Builds NodeError for Griptape Cloud failures.

The engine shows a NodeError's message, `fields`, `response` and `links` in the editor's error panel.
These helpers turn a Griptape Cloud API response, a failed connection, or a missing API key into one.
"""

import json
from typing import Any
from urllib.parse import quote

import httpx
import requests
from griptape_nodes.exe_types.core_types import NodeError, NodeErrorLink

API_KEY_NAME = "GT_CLOUD_API_KEY"
API_KEYS_URL = "https://cloud.griptape.ai/configuration/api-keys"

HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_TOO_MANY_REQUESTS = 429

# The longest start of a non-JSON body kept in `response`.
MAX_TEXT_CHARS = 2000

FieldValue = str | int | float | bool


def secret_link(secret_name: str, label: str) -> NodeErrorLink:
    """A link that opens Settings -> API Keys & Secrets filtered to one secret."""
    return NodeErrorLink(label=label, url=f"#settings-secrets?filter={quote(secret_name)}")


def missing_api_key_error() -> NodeError:
    """The error for a Griptape Cloud API key that is not set."""
    return NodeError(
        f"{API_KEY_NAME} is not set. Add it in Settings → API Keys & Secrets, then run the node again.",
        links=[
            secret_link(API_KEY_NAME, "Add the API key"),
            NodeErrorLink(label="Get a Griptape Cloud API key", url=API_KEYS_URL),
        ],
    )


def connection_error(exc: httpx.TransportError) -> NodeError:
    """The error for a request that never got an answer from Griptape Cloud."""
    if isinstance(exc, httpx.TimeoutException):
        return NodeError("Griptape Cloud did not answer in time. Run the node again.")
    return NodeError("Could not reach Griptape Cloud. Check your internet connection and run the node again.")


def _json_object(content: bytes) -> dict[str, Any] | None:
    try:
        body = json.loads(content)
    except ValueError:
        return None
    return body if isinstance(body, dict) else None


def _error_entries(body: dict[str, Any] | None) -> list[dict[str, Any]]:
    """The `errors` list Griptape Cloud sends, keeping only the entries that are objects."""
    errors = body.get("errors") if body else None
    if not isinstance(errors, list):
        return []
    return [entry for entry in errors if isinstance(entry, dict)]


def _reason(entries: list[dict[str, Any]]) -> str:
    """Join each error's `detail`, prefixed with the field it names when there is one."""
    reasons = []
    for entry in entries:
        detail = entry.get("detail")
        if not isinstance(detail, str) or not detail:
            continue
        attr = entry.get("attr")
        reasons.append(f"{attr}: {detail}" if isinstance(attr, str) and attr and attr != "detail" else detail)
    return " ".join(dict.fromkeys(reasons))


def api_error(*, status_code: int, content: bytes, headers: Any, action: str) -> NodeError:
    """The error for a Griptape Cloud response the node can't use.

    Args:
        status_code: The HTTP status.
        content: The raw response body.
        headers: The response headers, read only for the request ID.
        action: What the node was doing, as a verb phrase such as "get bucket".
    """
    body = _json_object(content)
    entries = _error_entries(body)
    reason = _reason(entries)

    fields: dict[str, FieldValue] = {"status_code": status_code}
    request_id = headers.get("x-request-id") if headers is not None else None
    if request_id:
        fields["request_id"] = request_id
    error_code = next((e["code"] for e in entries if isinstance(e.get("code"), str)), None)
    if error_code:
        fields["error_code"] = error_code

    response: dict[str, Any] | None = body
    if response is None and content:
        response = {"text": content.decode("utf-8", errors="replace")[:MAX_TEXT_CHARS]}

    links: list[NodeErrorLink] = []
    if status_code in {HTTP_UNAUTHORIZED, HTTP_FORBIDDEN}:
        message = f"Griptape Cloud refused {API_KEY_NAME}. Update the key in Settings → API Keys & Secrets, then run the node again."
        links = [
            secret_link(API_KEY_NAME, "Update the API key"),
            NodeErrorLink(label="Get a Griptape Cloud API key", url=API_KEYS_URL),
        ]
    elif status_code == HTTP_TOO_MANY_REQUESTS:
        message = "Griptape Cloud is rate-limiting requests. Wait a minute and run the node again."
    elif reason:
        message = f"Griptape Cloud could not {action}: {reason}"
    else:
        message = f"Griptape Cloud could not {action}. It answered with HTTP {status_code}."

    return NodeError(message, fields=fields, response=response, links=links)


def upload_error(exc: requests.RequestException) -> NodeError:
    """The error for a failed upload to the presigned storage URL Griptape Cloud issued.

    The storage service answers 403 for an expired or invalid URL, which says nothing about the API
    key, so this never links to the secret.
    """
    response = exc.response
    if response is None:
        if isinstance(exc, requests.Timeout):
            return NodeError("The upload to Griptape Cloud storage timed out. Run the node again.")
        return NodeError(
            "Could not reach Griptape Cloud storage to upload the file. Check your internet connection and run the "
            "node again."
        )

    fields: dict[str, FieldValue] = {"status_code": response.status_code}
    request_id = response.headers.get("x-amz-request-id") or response.headers.get("x-request-id")
    if request_id:
        fields["request_id"] = request_id
    body = response.text[:MAX_TEXT_CHARS] if response.text else None
    return NodeError(
        f"Griptape Cloud storage rejected the upload with HTTP {response.status_code}. Run the node again.",
        fields=fields,
        response={"text": body} if body else None,
    )
