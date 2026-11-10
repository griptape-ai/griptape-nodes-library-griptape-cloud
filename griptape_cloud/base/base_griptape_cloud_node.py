import logging

from griptape_cloud_client.client import AuthenticatedClient
from griptape_nodes.drivers.storage.griptape_cloud_storage_driver import GriptapeCloudStorageDriver
from griptape_nodes.exe_types.core_types import NodeError
from griptape_nodes.exe_types.node_types import BaseNode
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

from griptape_cloud.mixins.griptape_cloud_api_mixin import GriptapeCloudApiMixin
from griptape_cloud.node_errors import (
    API_KEY_ENV_VAR,
    API_KEY_URL,
    DEFAULT_GRIPTAPE_CLOUD_URL,
    PROVIDER,
    api_error,
)

BUCKET_ID_ENV_VAR = "GT_CLOUD_BUCKET_ID"
SERVICE = "Griptape"

logger = logging.getLogger("griptape_nodes")


class BaseGriptapeCloudNode(BaseNode, GriptapeCloudApiMixin):
    def __init__(self, name: str | None = None, **kwargs) -> None:
        # Handle name as either positional or keyword argument
        if name is not None:
            kwargs["name"] = name
        super().__init__(**kwargs)
        self.base_url = DEFAULT_GRIPTAPE_CLOUD_URL
        self._gtc_client: AuthenticatedClient | None = None
        self._gtc_client_token: str | None = None

    @property
    def gtc_client(self) -> AuthenticatedClient:  # pyright: ignore[reportIncompatibleVariableOverride]
        """The API client, built from the key as it is now.

        The key is read when the client is first needed, not when the node is created. A node created
        before the key was added can then still run, and a missing key is reported when the node runs.
        """
        token = self._get_gt_cloud_api_key()
        if self._gtc_client is None or token != self._gtc_client_token:
            self._gtc_client = AuthenticatedClient(base_url=self.base_url, token=token)
            self._gtc_client_token = token
        return self._gtc_client

    def validate_before_node_run(self) -> list[Exception] | None:
        """Report a missing API key first and on its own, so nothing else hides it."""
        try:
            self._get_gt_cloud_api_key()
        except NodeError as e:
            return [e]
        return super().validate_before_node_run()

    def _get_gt_cloud_api_key(self) -> str:
        api_key = GriptapeNodes.SecretsManager().get_secret(API_KEY_ENV_VAR, should_error_on_not_found=False)
        if not api_key:
            raise NodeError.from_missing_secret(API_KEY_ENV_VAR, key_url=API_KEY_URL)
        return api_key

    def _get_default_bucket_id(self) -> str:
        """Returns the bucket to use when a Node is not configured with an explicit one.

        Prefers the GT_CLOUD_BUCKET_ID secret, which is the bucket the engine stores assets in, so
        that uploads land alongside the rest of the workspace's assets. Falls back to the
        organization's default bucket, which is guaranteed to exist and cannot be deleted.
        """
        bucket_id = GriptapeNodes.SecretsManager().get_secret(BUCKET_ID_ENV_VAR, should_error_on_not_found=False)
        if bucket_id:
            return bucket_id

        # The generated client cannot parse the organizations response, so use the engine's
        # reader, which pulls default_bucket_id off the raw payload.
        try:
            bucket_id = GriptapeCloudStorageDriver.get_default_bucket_id(
                base_url=self.base_url, api_key=self._get_gt_cloud_api_key()
            )
        except NodeError:
            raise
        except Exception as e:
            # The engine wraps a failed request in a RuntimeError with the response on the cause. A body it
            # can't read raises a ValueError or AttributeError, and a failed connection its own error.
            cause = e.__cause__ if isinstance(e.__cause__, Exception) else e
            response = getattr(cause, "response", None)
            if response is not None:
                raise api_error(response, "read your default bucket") from e
            if isinstance(cause, ValueError | KeyError | TypeError | AttributeError):
                raise api_error(None, "read your default bucket") from e
            raise NodeError.from_request_exception(cause, provider=PROVIDER, secret_name=API_KEY_ENV_VAR) from e
        if not bucket_id:
            msg = (
                "Your Griptape Cloud account has no default bucket. Connect a bucket to 'Bucket', "
                f"or set the {BUCKET_ID_ENV_VAR} secret."
            )
            raise NodeError(msg)
        return bucket_id
