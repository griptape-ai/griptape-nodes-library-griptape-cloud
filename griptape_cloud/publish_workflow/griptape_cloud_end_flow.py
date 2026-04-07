import asyncio
import logging
from pathlib import Path
from typing import Any

import httpx
from griptape_cloud_client.client import AuthenticatedClient
from griptape_cloud_client.models.assert_url_operation import AssertUrlOperation
from griptape_nodes.common.macro_parser import ParsedMacro
from griptape_nodes.exe_types.node_types import EndNode
from griptape_nodes.retained_mode.events.os_events import (
    GetFileInfoRequest,
    GetFileInfoResultSuccess,
)
from griptape_nodes.retained_mode.events.project_events import (
    GetCurrentProjectRequest,
    GetCurrentProjectResultSuccess,
    GetPathForMacroRequest,
    GetPathForMacroResultSuccess,
    GetSituationRequest,
    GetSituationResultSuccess,
)
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

from griptape_cloud.base.base_griptape_cloud_node import (
    API_KEY_ENV_VAR,
    DEFAULT_GRIPTAPE_CLOUD_ENDPOINT,
)
from griptape_cloud.mixins.griptape_cloud_api_mixin import GriptapeCloudApiMixin

logger = logging.getLogger("griptape_nodes")

METADATA_SITUATION_NAME = "save_griptape_nodes_metadata"


class GriptapeCloudEndFlow(EndNode, GriptapeCloudApiMixin):
    """End Flow node that uploads project output files to Griptape Cloud.

    This node extends the base EndNode to handle publishing workflow outputs.
    When parameters contain file paths that have corresponding metadata sidecar
    files (created by the project macro system), this node:
    1. Detects the file by checking for its metadata sidecar in the metadata directory
    2. Uploads the file to Griptape Cloud storage
    3. Generates a presigned URL for the uploaded file
    4. Substitutes the original file path with the presigned URL
    """

    def __init__(
        self,
        name: str,
        metadata: dict[Any, Any] | None = None,
    ) -> None:
        if metadata is None:
            metadata = {}
        metadata["showaddparameter"] = True
        super().__init__(name, metadata)

        # Set up the Griptape Cloud API client (from GriptapeCloudApiMixin)
        api_key = GriptapeNodes.SecretsManager().get_secret(API_KEY_ENV_VAR) or ""
        self.gtc_client = AuthenticatedClient(
            base_url=DEFAULT_GRIPTAPE_CLOUD_ENDPOINT,
            token=api_key,
            verify_ssl=False,
        )

    async def aprocess(self) -> None:
        """Process the End Flow node, uploading any output files to Griptape Cloud.

        This method processes all parameters to detect files with metadata sidecars,
        uploads them to Griptape Cloud, and replaces file paths with presigned URLs.
        """
        # Only upload assets when running inside a Griptape Cloud worker
        if self.is_executing_in_structure_runtime():
            await self._process_output_files()

        # Call parent class process() to handle normal End Flow logic
        super().process()

    async def _process_output_files(self) -> None:
        """Process all parameters to upload files that have metadata sidecars.

        This method:
        1. Resolves the metadata directory and project base directory
        2. Iterates through all parameters
        3. Detects files with metadata sidecars
        4. Uploads files to Griptape Cloud
        5. Substitutes file paths with presigned URLs
        """
        try:
            # Get bucket ID from secrets
            bucket_id = self._get_bucket_id()
            if not bucket_id:
                logger.warning("GT_CLOUD_BUCKET_ID not set, skipping file upload for End Flow")
                return

            # Resolve metadata directory and project base directory once
            metadata_dir = self._resolve_metadata_dir()
            if metadata_dir is None:
                logger.warning("Could not resolve metadata directory, skipping file upload")
                return

            project_base_dir = self._resolve_project_base_dir()
            if project_base_dir is None:
                logger.warning("Could not resolve project base directory, skipping file upload")
                return

            # Process all parameters that might contain file paths
            for param in self.parameters:
                try:
                    # Get the current parameter value
                    param_value = self.get_parameter_value(param.name)

                    # Process the parameter value to upload files and substitute URLs
                    updated_value = await self._process_parameter_value(
                        param_value, bucket_id, metadata_dir, project_base_dir
                    )

                    # If the value was updated, set it back to the parameter
                    if updated_value != param_value:
                        self.set_parameter_value(param.name, updated_value)
                        logger.info("Updated parameter '%s' with presigned URLs", param.name)

                except Exception as e:
                    # Log error but continue processing other parameters
                    logger.error("Error processing parameter '%s': %s", param.name, e)
                    continue

        except Exception as e:
            # Log error but don't fail the node - file upload is optional
            logger.error("Error processing output files for End Flow: %s", e)

    async def _process_parameter_value(
        self, value: Any, bucket_id: str, metadata_dir: Path, project_base_dir: Path
    ) -> Any:
        """Recursively process a parameter value to upload files and substitute URLs.

        This method handles different value types:
        - Strings: Check for metadata sidecar and upload if file exists
        - Dicts: Recursively process all values
        - Lists: Recursively process all items

        Args:
            value: The parameter value to process
            bucket_id: The Griptape Cloud bucket ID
            metadata_dir: The absolute path to the metadata sidecar directory
            project_base_dir: The absolute path to the project base directory

        Returns:
            The processed value with file paths replaced by presigned URLs
        """
        # Handle None values
        if value is None:
            return value

        # Handle dictionary values (e.g., ImageUrlArtifact with nested "value" field)
        if isinstance(value, dict):
            processed_dict = {}
            for key, val in value.items():
                processed_dict[key] = await self._process_parameter_value(
                    val, bucket_id, metadata_dir, project_base_dir
                )
            return processed_dict

        # Handle list values
        if isinstance(value, list):
            return await asyncio.gather(
                *[self._process_parameter_value(item, bucket_id, metadata_dir, project_base_dir) for item in value]
            )

        # Handle string values that might contain file paths
        if isinstance(value, str):
            return await self._process_string_value(value, bucket_id, metadata_dir, project_base_dir)

        # Handle objects with a string "value" attribute (e.g., ImageUrlArtifact, UrlArtifact)
        inner = getattr(value, "value", None)
        if isinstance(inner, str):
            updated_inner = await self._process_string_value(inner, bucket_id, metadata_dir, project_base_dir)
            if updated_inner != inner:
                value.value = updated_inner
            return value

        # Return other types unchanged
        return value

    async def _process_string_value(
        self, value: str, bucket_id: str, metadata_dir: Path, project_base_dir: Path
    ) -> str:
        """Process a string value: resolve as a macro path, check for a metadata sidecar, upload, and replace.

        Any string parameter value might be a macro path (e.g. ``{outputs}/file.jpg``
        or even a plain path). This method attempts to resolve it, then checks for
        a metadata sidecar to confirm the file was produced by the project macro
        system before uploading.

        Args:
            value: The string value to process
            bucket_id: The Griptape Cloud bucket ID
            metadata_dir: The absolute path to the metadata sidecar directory
            project_base_dir: The absolute path to the project base directory

        Returns:
            The original value if not a sidecar-tracked file, or the presigned URL if uploaded
        """
        try:
            # Attempt to resolve the value as a macro path
            file_path = self._resolve_macro_to_path(value)
            if file_path is None:
                return value
            logger.debug("Resolved macro '%s' to path: %s", value, file_path)

            # Verify the resolved path points to an existing file
            if not self._is_existing_file(file_path):
                logger.debug("Resolved path '%s' does not exist or is not a file", file_path)
                return value

            # Check for metadata sidecar to confirm this was produced by the macro system
            if not self._has_metadata_sidecar(file_path, metadata_dir, project_base_dir):
                logger.debug("No metadata sidecar found for '%s'", file_path)
                return value

            # File confirmed as macro output with sidecar — upload it
            presigned_url = await self._upload_file_and_get_url(file_path, bucket_id, project_base_dir)

        except Exception as e:
            logger.error("Error processing value '%s': %s", value, e)
            return value
        else:
            if presigned_url:
                logger.info("Uploaded file '%s' to Griptape Cloud", file_path)
                return presigned_url
            logger.warning("Failed to upload file '%s'", file_path)
            return value

    def _resolve_macro_to_path(self, macro_string: str) -> Path | None:
        """Resolve a macro string to an absolute file path.

        Uses ``GetPathForMacroRequest`` to resolve macro strings like
        ``{outputs}/file.jpg`` to absolute filesystem paths.

        Args:
            macro_string: The macro string to resolve

        Returns:
            The resolved absolute Path, or None if resolution fails.
        """
        try:
            parsed_macro = ParsedMacro(macro_string)
            result = GriptapeNodes.handle_request(GetPathForMacroRequest(parsed_macro=parsed_macro, variables={}))
            if not isinstance(result, GetPathForMacroResultSuccess):
                return None
        except Exception:
            return None
        else:
            return result.absolute_path

    def _is_existing_file(self, file_path: Path) -> bool:
        """Check if a path points to an existing file using the OS event system.

        Args:
            file_path: The absolute path to check.

        Returns:
            True if the path exists and is a file.
        """
        result = GriptapeNodes.handle_request(GetFileInfoRequest(path=str(file_path), workspace_only=False))
        if not isinstance(result, GetFileInfoResultSuccess) or result.file_entry is None:
            return False
        return not result.file_entry.is_dir

    def _get_metadata_dir_name(self) -> str | None:
        """Return the logical metadata directory name from the current project.

        Uses ``GetSituationRequest`` to look up the ``save_griptape_nodes_metadata``
        situation, then extracts the leading ``{directory}`` macro segment to
        determine the directory name used for metadata sidecars.

        Returns:
            The directory name (e.g. ``"griptape-nodes-metadata"``), or ``None``
            if the situation is not defined in the template.
        """
        result = GriptapeNodes.handle_request(GetSituationRequest(situation_name=METADATA_SITUATION_NAME))
        if not isinstance(result, GetSituationResultSuccess):
            return None

        macro = result.situation.macro
        # Extract the first {name} token from the macro string.
        if macro.startswith("{"):
            end = macro.index("}")
            return macro[1:end].split("?")[0]  # strip optional-format suffix

        return None

    def _resolve_metadata_dir(self) -> Path | None:
        """Resolve the metadata sidecar directory to an absolute path.

        Returns:
            The absolute path to the metadata directory, or None if resolution fails.
        """
        try:
            dir_name = self._get_metadata_dir_name()
            if dir_name is None:
                logger.debug("Metadata situation not defined in project template")
                return None

            parsed_macro = ParsedMacro(f"{{{dir_name}}}")
            request = GetPathForMacroRequest(parsed_macro=parsed_macro, variables={})
            result = GriptapeNodes.handle_request(request)

            if not isinstance(result, GetPathForMacroResultSuccess):
                logger.debug("Failed to resolve metadata directory: %s", result)
                return None
        except Exception as e:
            logger.error("Error resolving metadata directory: %s", e)
            return None
        else:
            return result.absolute_path

    def _resolve_project_base_dir(self) -> Path | None:
        """Get the current project's base directory.

        Returns:
            The absolute path to the project base directory, or None if not available.
        """
        try:
            result = GriptapeNodes.handle_request(GetCurrentProjectRequest())
            if not isinstance(result, GetCurrentProjectResultSuccess):
                logger.debug("Failed to get current project: %s", result)
                return None
        except Exception as e:
            logger.error("Error getting current project: %s", e)
            return None
        else:
            return result.project_info.project_base_dir

    def _has_metadata_sidecar(self, file_path: Path, metadata_dir: Path, project_base_dir: Path) -> bool:
        """Check if a file has a metadata sidecar, confirming it was produced by the macro system.

        Args:
            file_path: The absolute path to the file to check
            metadata_dir: The absolute path to the metadata sidecar directory
            project_base_dir: The absolute path to the project base directory

        Returns:
            True if the file has a metadata sidecar, False otherwise.
        """
        try:
            relative_path = file_path.relative_to(project_base_dir)
        except ValueError:
            # File is not inside the project directory
            return False

        sidecar_path = metadata_dir / f"{relative_path}.json"
        return sidecar_path.exists()

    async def _upload_file_and_get_url(self, file_path: Path, bucket_id: str, project_base_dir: Path) -> str | None:
        """Upload a file to Griptape Cloud and get a presigned URL.

        This method:
        1. Creates an asset in the bucket
        2. Gets a presigned upload URL
        3. Uploads the file content
        4. Generates a presigned download URL

        Args:
            file_path: The path to the file to upload
            bucket_id: The Griptape Cloud bucket ID
            project_base_dir: The absolute path to the project base directory

        Returns:
            The presigned download URL, or None if upload fails
        """
        try:
            # Read the file content
            with file_path.open("rb") as f:
                file_content = f.read()

            # Use the relative path as the asset name to avoid collisions
            try:
                relative_path = file_path.relative_to(project_base_dir)
                asset_name = str(relative_path)
            except ValueError:
                asset_name = file_path.name

            # Create the asset in Griptape Cloud
            await asyncio.to_thread(self._create_asset, asset_name=asset_name, bucket_id=bucket_id)

            # Get a presigned upload URL
            upload_response = await asyncio.to_thread(
                self._create_asset_url, asset_name=asset_name, bucket_id=bucket_id, operation=AssertUrlOperation.PUT
            )

            # Upload the file content using the presigned URL
            upload_url = upload_response.url
            upload_headers = upload_response.headers.to_dict()

            async with httpx.AsyncClient() as client:
                response = await client.put(upload_url, content=file_content, headers=upload_headers, timeout=60.0)
                response.raise_for_status()

            logger.debug("Successfully uploaded file '%s' to Griptape Cloud", file_path.name)

            # Generate a presigned download URL
            download_response = await asyncio.to_thread(
                self._create_asset_url, asset_name=asset_name, bucket_id=bucket_id, operation=AssertUrlOperation.GET
            )

        except Exception as e:
            logger.error("Failed to upload file '%s': %s", file_path, e)
            return None
        else:
            # Return the presigned download URL
            return download_response.url

    def _get_bucket_id(self) -> str | None:
        """Get the Griptape Cloud bucket ID from secrets.

        Tries GT_CLOUD_BUCKET_ID first, then falls back to GT_CLOUD_PUBLISH_BUCKET_ID.

        Returns:
            The bucket ID string, or None if not found
        """
        try:
            # Try GT_CLOUD_BUCKET_ID first
            bucket_id = GriptapeNodes.SecretsManager().get_secret("GT_CLOUD_BUCKET_ID")
            if bucket_id:
                return bucket_id

            # Fall back to GT_CLOUD_PUBLISH_BUCKET_ID
            return GriptapeNodes.SecretsManager().get_secret("GT_CLOUD_PUBLISH_BUCKET_ID")

        except Exception as e:
            logger.warning("Failed to get bucket ID from secrets: %s", e)
            return None

    @classmethod
    def get_default_node_parameter_names(cls) -> list[str]:
        """Get the names of the parameters configured on the node by default."""
        # Execution Status Component parameters
        params = ["was_successful", "result_details"]
        # Control parameters
        params.extend(["exec_in", "failed"])
        return params
