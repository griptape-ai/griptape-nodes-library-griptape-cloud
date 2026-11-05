"""Turns a Griptape Cloud API response into a NodeError.

A missing key, a refused key and a failed connection come from `NodeError.from_missing_secret`,
`from_http_response` and `from_request_exception`. This module adds the one thing they can't read:
Griptape Cloud sends its reasons as an `errors` list.
"""

import json
from types import SimpleNamespace
from typing import Any

from griptape_cloud_client.types import Response
from griptape_nodes.exe_types.core_types import NodeError

API_KEY_NAME = "GT_CLOUD_API_KEY"
API_KEY_URL = "https://cloud.griptape.ai/configuration/api-keys"
PROVIDER = "Griptape Cloud"

HTTP_UNAUTHORIZED = 401


def api_error(response: Response[Any], action: str) -> NodeError:
    """The error for a response the node can't use.

    Args:
        response: A `sync_detailed` response.
        action: What the call does, as a verb phrase such as "get bucket".
    """
    status = int(response.status_code)
    text = response.content.decode("utf-8", errors="replace")
    adapter = SimpleNamespace(status_code=status, headers=response.headers, text=text, json=lambda: _json(text))
    errors = (_json(text) or {}).get("errors")
    entries = [e for e in errors if isinstance(e, dict)] if isinstance(errors, list) else []
    code = next((e["code"] for e in entries if isinstance(e.get("code"), str)), None)
    error = NodeError.from_http_response(
        adapter,
        provider=PROVIDER,
        secret_name=API_KEY_NAME,
        key_refused=status == HTTP_UNAUTHORIZED,
        fields={"error_code": code} if code else None,
    )

    details = [e["detail"] for e in entries if isinstance(e.get("detail"), str) and e["detail"]]
    if status == HTTP_UNAUTHORIZED or not details:
        return error
    message = f"{PROVIDER} could not {action}: {' '.join(dict.fromkeys(details))}"
    return NodeError(message, fields=error.fields, response=error.response, links=error.links)


def _json(text: str) -> dict[str, Any] | None:
    try:
        body = json.loads(text)
    except ValueError:
        return None
    return body if isinstance(body, dict) else None
