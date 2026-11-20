import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

import httpx
from griptape_cloud_client.api.assets.create_asset import sync_detailed as create_asset
from griptape_cloud_client.api.assets.create_asset_url import sync_detailed as create_asset_url
from griptape_cloud_client.api.buckets.create_bucket import sync_detailed as create_bucket
from griptape_cloud_client.api.buckets.delete_bucket import sync_detailed as delete_bucket
from griptape_cloud_client.api.buckets.get_bucket import sync_detailed as get_bucket
from griptape_cloud_client.api.buckets.list_buckets import sync_detailed as list_buckets
from griptape_cloud_client.api.buckets.update_bucket import sync_detailed as update_bucket
from griptape_cloud_client.models.assert_url_operation import AssertUrlOperation
from griptape_cloud_client.models.create_asset_request_content import CreateAssetRequestContent
from griptape_cloud_client.models.create_asset_response_content import (
    CreateAssetResponseContent,
)
from griptape_cloud_client.models.create_asset_url_request_content import CreateAssetUrlRequestContent
from griptape_cloud_client.models.create_asset_url_response_content import CreateAssetUrlResponseContent
from griptape_cloud_client.models.create_bucket_request_content import CreateBucketRequestContent
from griptape_cloud_client.models.create_bucket_response_content import CreateBucketResponseContent
from griptape_cloud_client.models.get_bucket_response_content import GetBucketResponseContent
from griptape_cloud_client.models.list_buckets_response_content import ListBucketsResponseContent
from griptape_cloud_client.models.update_bucket_request_content import UpdateBucketRequestContent
from griptape_cloud_client.models.update_bucket_response_content import UpdateBucketResponseContent
from griptape_cloud_client.types import Response
from griptape_nodes.exe_types.core_types import NodeError

from griptape_cloud.node_errors import API_KEY_ENV_VAR, PROVIDER, api_error

if TYPE_CHECKING:
    from griptape_cloud_client.client import AuthenticatedClient

logger = logging.getLogger("griptape_nodes")

T = TypeVar("T")


class GriptapeCloudApiMixin:
    """Mixin class providing shared Griptape Cloud API functionality."""

    gtc_client: "AuthenticatedClient"

    def _call_api(
        self, endpoint: Callable[..., Response[Any]], expected_type: type[T], action: str, **kwargs: Any
    ) -> T:
        """Call an SDK endpoint and return its success model, or raise a NodeError.

        The SDK returns the success model for the expected status, a `ClientErrorResponseContent` or
        `ServiceErrorResponseContent` for a documented error, and `None` for any other status. The
        status code and request ID are only on the detailed response, so every call uses `sync_detailed`.
        The SDK parses the body of a status it has a model for, so a body it can't parse on one of those
        statuses raises the SDK's own `json.JSONDecodeError` or `TypeError` out of this method.

        Args:
            endpoint: A generated `sync_detailed` function.
            expected_type: The success model.
            action: What the call does, as a verb phrase such as "get bucket".
            **kwargs: The endpoint's arguments. The client is added here.
        """
        client = self.gtc_client
        try:
            response = endpoint(client=client, **kwargs)
        except httpx.TransportError as e:
            raise NodeError.from_request_exception(e, provider=PROVIDER, secret_name=API_KEY_ENV_VAR) from e

        if isinstance(response.parsed, expected_type):
            return response.parsed
        error = api_error(response, action)
        logger.error("Griptape Cloud request failed: %s", error)
        raise error

    def _list_buckets(self) -> ListBucketsResponseContent:
        return self._call_api(list_buckets, ListBucketsResponseContent, "list buckets", page=1, page_size=100)

    def _get_bucket(self, bucket_id: str) -> GetBucketResponseContent:
        return self._call_api(get_bucket, GetBucketResponseContent, "get bucket", bucket_id=bucket_id)

    def _create_bucket(self, name: str) -> CreateBucketResponseContent:
        return self._call_api(
            create_bucket, CreateBucketResponseContent, "create bucket", body=CreateBucketRequestContent(name=name)
        )

    def _update_bucket(self, bucket_id: str, name: str) -> UpdateBucketResponseContent:
        return self._call_api(
            update_bucket,
            UpdateBucketResponseContent,
            "update bucket",
            bucket_id=bucket_id,
            body=UpdateBucketRequestContent(name=name),
        )

    def _delete_bucket(self, bucket_id: str) -> None:
        delete_bucket(bucket_id=bucket_id, client=self.gtc_client)

    def _create_asset(
        self,
        asset_name: str,
        bucket_id: str,
    ) -> CreateAssetResponseContent:
        return self._call_api(
            create_asset,
            CreateAssetResponseContent,
            "create asset",
            bucket_id=bucket_id,
            body=CreateAssetRequestContent(name=asset_name),
        )

    def _create_asset_url(
        self, asset_name: str, bucket_id: str, operation: AssertUrlOperation = AssertUrlOperation.GET
    ) -> CreateAssetUrlResponseContent:
        return self._call_api(
            create_asset_url,
            CreateAssetUrlResponseContent,
            "create asset URL",
            bucket_id=bucket_id,
            name=asset_name,
            body=CreateAssetUrlRequestContent(operation=operation),
        )
