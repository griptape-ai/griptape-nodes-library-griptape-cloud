import asyncio
import logging
import re
from pathlib import Path
from typing import Any

import httpx
from griptape_cloud_client.models.assert_url_operation import AssertUrlOperation
from griptape_nodes.common.macro_parser import MacroSyntaxError, ParsedMacro
from griptape_nodes.exe_types.node_types import EndNode
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

from griptape_cloud.base.base_griptape_cloud_node import BaseGriptapeCloudNode

logger = logging.getLogger("griptape_nodes")


class GriptapeCloudEndFlow(EndNode, BaseGriptapeCloudNode):
    """End Flow node that uploads project output files to Griptape Cloud.

    This node extends the base EndNode to handle publishing workflow outputs.
    When parameters contain macro strings (e.g., {outputs}/file.jpg), this node:
    1. Resolves the macro to the actual file path using ProjectManager
    2. Uploads the file to Griptape Cloud storage
    3. Generates a presigned URL for the uploaded file
    4. Substitutes the original macro string with the presigned URL
    """

    def __init__(
        self,
        name: str,
        metadata: dict[Any, Any] | None = None,
    ) -> None:
        if metadata is None:
            metadata = {}
        metadata["showaddparameter"] = True
        # Initialize both parent classes
        EndNode.__init__(self, name, metadata)
        BaseGriptapeCloudNode.__init__(self, name, metadata=metadata)

    async def aprocess(self) -> None:
        """Process the End Flow node, uploading any output files to Griptape Cloud.

        This method processes all parameters to detect macro strings, uploads referenced
        files to Griptape Cloud, and replaces the macro strings with presigned URLs.
        """
        # First, process any file uploads before calling parent process()
        await self._process_output_files()

        # Call parent class process() to handle normal End Flow logic
        super().process()

    async def _process_output_files(self) -> None:
        """Process all parameters to upload files referenced by macro strings.

        This method:
        1. Iterates through all parameters
        2. Detects macro strings in parameter values
        3. Resolves macros to file paths
        4. Uploads files to Griptape Cloud
        5. Substitutes macro strings with presigned URLs
        """
        try:
            # Get bucket ID from secrets
            bucket_id = self._get_bucket_id()
            if not bucket_id:
                logger.warning("GT_CLOUD_BUCKET_ID not set, skipping file upload for End Flow")
                return

            # Process all parameters that might contain macro strings
            for param in self.parameters:
                try:
                    # Get the current parameter value
                    param_value = self.get_parameter_value(param.name)

                    # Process the parameter value to upload files and substitute URLs
                    updated_value = await self._process_parameter_value(param_value, bucket_id)

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

    async def _process_parameter_value(self, value: Any, bucket_id: str) -> Any:
        """Recursively process a parameter value to upload files and substitute URLs.

        This method handles different value types:
        - Strings: Check for macro strings and upload if file exists
        - Dicts: Recursively process all values
        - Lists: Recursively process all items

        Args:
            value: The parameter value to process
            bucket_id: The Griptape Cloud bucket ID

        Returns:
            The processed value with macro strings replaced by presigned URLs
        """
        # Handle None values
        if value is None:
            return value

        # Handle dictionary values (e.g., ImageUrlArtifact with nested "value" field)
        if isinstance(value, dict):
            processed_dict = {}
            for key, val in value.items():
                processed_dict[key] = await self._process_parameter_value(val, bucket_id)
            return processed_dict

        # Handle list values
        if isinstance(value, list):
            return await asyncio.gather(
                *[self._process_parameter_value(item, bucket_id) for item in value]
            )

        # Handle string values that might contain macro strings
        if isinstance(value, str):
            return await self._process_string_value(value, bucket_id)

        # Return other types unchanged
        return value

    async def _process_string_value(self, value: str, bucket_id: str) -> str:
        """Process a string value to detect and replace macro strings with presigned URLs.

        Args:
            value: The string value that might contain a macro string
            bucket_id: The Griptape Cloud bucket ID

        Returns:
            The original value if no macro found, or the presigned URL if file was uploaded
        """
        # Check if the string contains a macro pattern (e.g., {outputs}/file.jpg)
        # Macro pattern: starts with {variable_name} followed by optional path
        macro_pattern = r"^(\{[^}]+\})(.*)$"
        match = re.match(macro_pattern, value)

        if not match:
            # Not a macro string, return unchanged
            return value

        try:
            # Attempt to resolve the macro to an actual file path
            file_path = self._resolve_macro_to_path(value)

            if file_path is None or not file_path.exists():
                # Macro resolved but file doesn't exist, return original value
                logger.debug("Macro '%s' resolved but file does not exist at: %s", value, file_path)
                return value

            # File exists! Upload it to Griptape Cloud
            presigned_url = await self._upload_file_and_get_url(file_path, bucket_id)

        except Exception as e:
            # Log error but return original value
            logger.error("Error processing macro string '%s': %s", value, e)
            return value
        else:
            if presigned_url:
                logger.info("Uploaded file '%s' from macro '%s' to Griptape Cloud", file_path, value)
                return presigned_url
            logger.warning("Failed to upload file '%s' from macro '%s'", file_path, value)
            return value

    def _resolve_macro_to_path(self, macro_string: str) -> Path | None:
        """Resolve a macro string to an actual file path using ProjectManager.

        Uses the ProjectManager to resolve macro strings like {outputs}/file.jpg
        to actual file system paths.

        Args:
            macro_string: The macro string to resolve (e.g., "{outputs}/file.jpg")

        Returns:
            The resolved Path object, or None if resolution fails
        """
        try:
            # Parse the macro string to validate syntax
            parsed_macro = ParsedMacro(macro_string)

            # Import here to avoid circular dependencies
            from griptape_nodes.retained_mode.events.project_events import GetPathForMacroRequest

            # Use ProjectManager to resolve the macro to an absolute path
            request = GetPathForMacroRequest(
                parsed_macro=parsed_macro,
                variables={},  # No additional variables needed for output macros
            )

            result = GriptapeNodes.handle_request(request)

            # Check if resolution was successful
            if result.failed():
                logger.debug("Failed to resolve macro '%s': %s", macro_string, result.result_details)
                return None

            # Return the absolute path from the result
            # The result object contains the resolved path
            # Type ignore needed due to ResultPayload not exposing attributes in type hints
            return Path(result.payload) if result.payload else None  # type: ignore[attr-defined]

        except MacroSyntaxError as e:
            # Not a valid macro syntax
            logger.debug("Invalid macro syntax for '%s': %s", macro_string, e)
            return None
        except Exception as e:
            logger.error("Error resolving macro '%s': %s", macro_string, e)
            return None

    async def _upload_file_and_get_url(self, file_path: Path, bucket_id: str) -> str | None:
        """Upload a file to Griptape Cloud and get a presigned URL.

        This method follows the same pattern as GriptapeCloudStorageDriver:
        1. Create an asset in the bucket
        2. Get a presigned upload URL
        3. Upload the file content
        4. Generate a presigned download URL

        Args:
            file_path: The path to the file to upload
            bucket_id: The Griptape Cloud bucket ID

        Returns:
            The presigned download URL, or None if upload fails
        """
        try:
            # Read the file content
            with file_path.open("rb") as f:
                file_content = f.read()

            # Use the file name as the asset name in the bucket
            asset_name = file_path.name

            # Create the asset in Griptape Cloud
            # Uses the _create_asset method from BaseGriptapeCloudNode's GriptapeCloudApiMixin
            self._create_asset(asset_name=asset_name, bucket_id=bucket_id)

            # Get a presigned upload URL
            # Uses the _create_asset_url method from GriptapeCloudApiMixin
            upload_response = self._create_asset_url(
                asset_name=asset_name, bucket_id=bucket_id, operation=AssertUrlOperation.PUT
            )

            # Upload the file content using the presigned URL
            upload_url = upload_response.url
            upload_headers = upload_response.headers.to_dict() if hasattr(upload_response.headers, "to_dict") else {}

            async with httpx.AsyncClient() as client:
                response = await client.put(upload_url, content=file_content, headers=upload_headers, timeout=60.0)
                response.raise_for_status()

            logger.debug("Successfully uploaded file '%s' to Griptape Cloud", file_path.name)

            # Generate a presigned download URL
            # Uses the _create_asset_url method from GriptapeCloudApiMixin
            download_response = self._create_asset_url(
                asset_name=asset_name, bucket_id=bucket_id, operation=AssertUrlOperation.GET
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
