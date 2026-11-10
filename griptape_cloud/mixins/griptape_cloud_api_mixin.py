import logging
import os
import time
from collections.abc import Callable, Generator
from typing import TYPE_CHECKING, Any, TypeVar

import httpx
from griptape_cloud_client.api.assets.create_asset import sync_detailed as create_asset
from griptape_cloud_client.api.assets.create_asset_url import sync_detailed as create_asset_url
from griptape_cloud_client.api.assistant_runs.create_assistant_run import sync_detailed as create_assistant_run
from griptape_cloud_client.api.assistant_runs.get_assistant_run import sync_detailed as get_assistant_run
from griptape_cloud_client.api.assistants.list_assistants import sync_detailed as list_assistants
from griptape_cloud_client.api.buckets.create_bucket import sync_detailed as create_bucket
from griptape_cloud_client.api.buckets.delete_bucket import sync_detailed as delete_bucket
from griptape_cloud_client.api.buckets.get_bucket import sync_detailed as get_bucket
from griptape_cloud_client.api.buckets.list_buckets import sync_detailed as list_buckets
from griptape_cloud_client.api.buckets.update_bucket import sync_detailed as update_bucket
from griptape_cloud_client.api.deployments.get_deployment import sync_detailed as get_deployment
from griptape_cloud_client.api.deployments.list_structure_deployments import sync_detailed as list_structure_deployments
from griptape_cloud_client.api.events.list_assistant_events import sync_detailed as list_assistant_events
from griptape_cloud_client.api.events.list_events import sync_detailed as list_events
from griptape_cloud_client.api.structure_runs.create_structure_run import sync_detailed as create_structure_run
from griptape_cloud_client.api.structure_runs.get_structure_run import sync_detailed as get_structure_run
from griptape_cloud_client.api.structures.list_structures import sync_detailed as list_structures
from griptape_cloud_client.models.assert_url_operation import AssertUrlOperation
from griptape_cloud_client.models.assistant_event_detail import AssistantEventDetail
from griptape_cloud_client.models.client_error_response_content import ClientErrorResponseContent
from griptape_cloud_client.models.create_asset_request_content import CreateAssetRequestContent
from griptape_cloud_client.models.create_asset_response_content import (
    CreateAssetResponseContent,
)
from griptape_cloud_client.models.create_asset_url_request_content import CreateAssetUrlRequestContent
from griptape_cloud_client.models.create_asset_url_response_content import CreateAssetUrlResponseContent
from griptape_cloud_client.models.create_assistant_run_request_content import (
    CreateAssistantRunRequestContent,
)
from griptape_cloud_client.models.create_assistant_run_response_content import (
    CreateAssistantRunResponseContent,
)
from griptape_cloud_client.models.create_bucket_request_content import CreateBucketRequestContent
from griptape_cloud_client.models.create_bucket_response_content import CreateBucketResponseContent
from griptape_cloud_client.models.create_structure_run_request_content import (
    CreateStructureRunRequestContent,
)
from griptape_cloud_client.models.create_structure_run_response_content import (
    CreateStructureRunResponseContent,
)
from griptape_cloud_client.models.deployment_status import DeploymentStatus
from griptape_cloud_client.models.event_detail import EventDetail
from griptape_cloud_client.models.get_assistant_run_response_content import (
    GetAssistantRunResponseContent,
)
from griptape_cloud_client.models.get_bucket_response_content import GetBucketResponseContent
from griptape_cloud_client.models.get_deployment_response_content import GetDeploymentResponseContent
from griptape_cloud_client.models.get_structure_run_response_content import (
    GetStructureRunResponseContent,
)
from griptape_cloud_client.models.list_assistant_events_response_content import (
    ListAssistantEventsResponseContent,
)
from griptape_cloud_client.models.list_assistants_response_content import ListAssistantsResponseContent
from griptape_cloud_client.models.list_buckets_response_content import ListBucketsResponseContent
from griptape_cloud_client.models.list_events_response_content import ListEventsResponseContent
from griptape_cloud_client.models.list_structure_deployments_response_content import (
    ListStructureDeploymentsResponseContent,
)
from griptape_cloud_client.models.list_structures_response_content import (
    ListStructuresResponseContent,
)
from griptape_cloud_client.models.service_error_response_content import ServiceErrorResponseContent
from griptape_cloud_client.models.structure_deployment_detail import StructureDeploymentDetail
from griptape_cloud_client.models.structure_run_status import StructureRunStatus
from griptape_cloud_client.models.update_bucket_request_content import UpdateBucketRequestContent
from griptape_cloud_client.models.update_bucket_response_content import UpdateBucketResponseContent
from griptape_cloud_client.types import UNSET, Response
from griptape_nodes.exe_types.core_types import NodeError

from griptape_cloud.node_errors import API_KEY_ENV_VAR, PROVIDER, api_error

if TYPE_CHECKING:
    from griptape_cloud_client.client import AuthenticatedClient

logger = logging.getLogger("griptape_nodes")

T = TypeVar("T")


class GriptapeCloudApiMixin:
    """Mixin class providing shared Griptape Cloud API functionality."""

    gtc_client: "AuthenticatedClient"

    @staticmethod
    def is_executing_in_structure_runtime() -> bool:
        """Check if the current process is running inside a Griptape Cloud worker."""
        return bool(os.environ.get("GT_CLOUD_STRUCTURE_RUN_ID"))

    def format_error_message_for_response(
        self, message: str, response: ClientErrorResponseContent | ServiceErrorResponseContent | Any
    ) -> str:
        if isinstance(response, (ClientErrorResponseContent, ServiceErrorResponseContent)) and response.errors:
            return f"{message} Errors: {response.errors}"
        return message

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

    def _get_deployment(self, deployment_id: str) -> GetDeploymentResponseContent:
        return self._call_api(
            get_deployment, GetDeploymentResponseContent, "get deployment", deployment_id=deployment_id
        )

    def _list_structure_deployments(
        self, structure_id: str, status: list[DeploymentStatus] | None = None
    ) -> ListStructureDeploymentsResponseContent:
        status_query = status or UNSET
        return self._call_api(
            list_structure_deployments,
            ListStructureDeploymentsResponseContent,
            "list structure deployments",
            structure_id=structure_id,
            status=status_query,
        )

    def _wait_for_structure_deployment(self, deployment_id: str, timeout: float = 60.0) -> GetDeploymentResponseContent:
        start_time = time.time()
        while True:
            response = self._get_deployment(deployment_id=deployment_id)
            # Check if deployment is in a terminal state
            if response.status in [DeploymentStatus.ERROR, DeploymentStatus.FAILED, DeploymentStatus.SUCCEEDED]:
                return response

            # Check timeout
            if time.time() - start_time > timeout:
                msg = (
                    f"The Griptape Cloud deployment did not finish within {timeout:g} seconds. "
                    "Check its status in Griptape Cloud and run the node again."
                )
                logger.error("Timeout waiting for deployment %s to reach terminal state", deployment_id)
                raise NodeError(msg, fields={"deployment_id": deployment_id, "status": str(response.status)})

            # Wait before next check
            time.sleep(1.0)

    def _wait_for_latest_structure_deployment(
        self, structure_id: str, timeout: float = 300.0
    ) -> GetDeploymentResponseContent:
        response = self._list_structure_deployments(structure_id=structure_id)
        latest_deployment = max(response.deployments, key=lambda d: d.created_at, default=None)
        if latest_deployment is None:
            msg = "The structure has no deployments. Deploy it in Griptape Cloud, then run the node again."
            logger.error("No deployments found for structure %s", structure_id)
            raise NodeError(msg, fields={"structure_id": structure_id})
        return self._wait_for_structure_deployment(latest_deployment.deployment_id, timeout=timeout)

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

    def _list_assistants(self) -> ListAssistantsResponseContent:
        return self._call_api(list_assistants, ListAssistantsResponseContent, "list assistants", page=1, page_size=100)

    def _get_assistant_run(self, assistant_run_id: str) -> GetAssistantRunResponseContent:
        return self._call_api(
            get_assistant_run, GetAssistantRunResponseContent, "get assistant run", assistant_run_id=assistant_run_id
        )

    def _create_assistant_run(self, assistant_id: str, args: list[str]) -> CreateAssistantRunResponseContent:
        return self._call_api(
            create_assistant_run,
            CreateAssistantRunResponseContent,
            "create assistant run",
            assistant_id=assistant_id,
            body=CreateAssistantRunRequestContent(args=args),
        )

    def _list_assistant_run_events(
        self, assistant_run_id: str, offset: float | None = None
    ) -> ListAssistantEventsResponseContent:
        return self._call_api(
            list_assistant_events,
            ListAssistantEventsResponseContent,
            "list assistant run events",
            assistant_run_id=assistant_run_id,
            offset=str(offset) if offset is not None else UNSET,
        )

    def _poll_assistant_run_events(self, assistant_run_id: str) -> Generator[list[AssistantEventDetail], None, None]:
        run_completed = False
        offset: float | None = None

        while not run_completed:
            list_events_response = self._list_assistant_run_events(assistant_run_id=assistant_run_id, offset=offset)
            offset = list_events_response.next_offset
            for event in list_events_response.events:
                if event.type_ == "FinishStructureRunEvent" and event.origin == "ASSISTANT":
                    run_completed = True
            yield list_events_response.events
            time.sleep(0.5)

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

    def _list_structures(self) -> ListStructuresResponseContent:
        return self._call_api(list_structures, ListStructuresResponseContent, "list structures", page=1, page_size=100)

    def _create_structure_run(self, structure_id: str, args: list[str]) -> CreateStructureRunResponseContent:
        return self._call_api(
            create_structure_run,
            CreateStructureRunResponseContent,
            "create structure run",
            structure_id=structure_id,
            body=CreateStructureRunRequestContent(args=args),
        )

    def _get_structure_run(self, structure_run_id: str) -> GetStructureRunResponseContent:
        return self._call_api(
            get_structure_run, GetStructureRunResponseContent, "get structure run", structure_run_id=structure_run_id
        )

    def _get_structure_run_bad_statuses(self) -> list[str]:
        return [StructureRunStatus.FAILED, StructureRunStatus.CANCELLED, StructureRunStatus.ERROR]

    def _list_structure_run_events(
        self, structure_run_id: str, offset: float | None = None
    ) -> ListEventsResponseContent:
        return self._call_api(
            list_events,
            ListEventsResponseContent,
            "list structure run events",
            structure_run_id=structure_run_id,
            offset=str(offset) if offset is not None else UNSET,
        )

    def _poll_structure_run_events(self, structure_run_id: str) -> Generator[list[EventDetail], None, None]:
        run_completed = False
        offset: float | None = None

        while not run_completed:
            list_events_response = self._list_structure_run_events(structure_run_id=structure_run_id, offset=offset)
            offset = list_events_response.next_offset
            for event in list_events_response.events:
                if event.type_ == "StructureRunCompleted" and event.origin == "SYSTEM":
                    run_completed = True
            yield list_events_response.events
            time.sleep(0.5)

    def _is_deployment_ready(self, deployment: GetDeploymentResponseContent | StructureDeploymentDetail) -> bool:
        return deployment.status == DeploymentStatus.SUCCEEDED
