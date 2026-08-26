import logging
import os

from griptape_cloud_client.client import AuthenticatedClient
from griptape_nodes.drivers.storage.griptape_cloud_storage_driver import GriptapeCloudStorageDriver
from griptape_nodes.exe_types.node_types import BaseNode
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

from griptape_cloud.mixins.griptape_cloud_api_mixin import GriptapeCloudApiMixin

DEFAULT_GRIPTAPE_CLOUD_URL = os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")
API_KEY_ENV_VAR = "GT_CLOUD_API_KEY"
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
        self.gtc_client = AuthenticatedClient(
            base_url=self.base_url,
            token=self._get_gt_cloud_api_key(),
            verify_ssl=False,
        )

    def validate_before_workflow_run(self) -> list[Exception] | None:
        exceptions = []

        try:
            self._get_gt_cloud_api_key()
        except Exception as e:
            exceptions.append(e)

        return exceptions or None

    def _get_gt_cloud_api_key(self) -> str:
        if (api_key := GriptapeNodes.SecretsManager().get_secret(API_KEY_ENV_VAR)) is None:
            msg = f"{API_KEY_ENV_VAR} not found by Griptape Secrets Manager"
            raise KeyError(msg)
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
        bucket_id = GriptapeCloudStorageDriver.get_default_bucket_id(
            base_url=self.base_url, api_key=self._get_gt_cloud_api_key()
        )
        if not bucket_id:
            msg = (
                f"No default Griptape Cloud Bucket available. Set the {BUCKET_ID_ENV_VAR} secret or configure the "
                "Node with a Bucket."
            )
            raise ValueError(msg)
        return bucket_id
