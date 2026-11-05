import logging
from pathlib import Path
from typing import cast

import requests
from griptape_cloud_client.models.assert_url_operation import AssertUrlOperation
from griptape_cloud_client.models.bucket_detail import BucketDetail
from griptape_nodes.exe_types.core_types import NodeError, Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import ControlNode

from griptape_cloud.base.base_griptape_cloud_node import BaseGriptapeCloudNode

logger = logging.getLogger("griptape_nodes")


class UploadAsset(BaseGriptapeCloudNode, ControlNode):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.add_parameter(
            Parameter(
                name="bucket",
                input_types=["BucketDetail"],
                type="BucketDetail",
                output_type="BucketDetail",
                default_value=None,
                tooltip="The bucket to upload to. Defaults to the Griptape Cloud default bucket when not supplied.",
                allowed_modes={ParameterMode.INPUT, ParameterMode.OUTPUT},
            )
        )

        self.add_parameter(
            Parameter(
                name="file_path",
                input_types=["str"],
                type="str",
                output_type="str",
                default_value=None,
                ui_options={
                    "clickable_file_browser": True,
                    "expander": True,
                    "display_name": "Path to File",
                },
                tooltip="The file path of the asset to upload",
            )
        )

        self.add_parameter(
            Parameter(
                name="content_type",
                input_types=["str"],
                type="str",
                output_type="str",
                default_value="application/octet-stream",
                ui_options={
                    "display_name": "Content Type",
                },
                tooltip="The content type of the asset to upload",
            )
        )

        self.add_parameter(
            Parameter(
                name="asset_name",
                input_types=["str"],
                type="str",
                output_type="str",
                default_value=None,
                tooltip="The name of the asset",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY, ParameterMode.OUTPUT},
            )
        )

    def validate_before_node_run(self) -> list[Exception] | None:
        exceptions = super().validate_before_node_run() or []
        if exceptions:
            return exceptions

        if not self.get_parameter_value("asset_name"):
            exceptions.append(
                NodeError("No asset name is set. Enter one in 'asset_name'.", fields={"parameter": "asset_name"})
            )

        file_path = self.get_parameter_value("file_path")
        if not file_path:
            exceptions.append(
                NodeError("No file is selected. Choose one in 'Path to File'.", fields={"parameter": "file_path"})
            )
        elif not Path(file_path).exists():
            exceptions.append(
                NodeError(
                    f"The file '{file_path}' does not exist. Choose an existing file in 'Path to File'.",
                    fields={"parameter": "file_path"},
                )
            )

        return exceptions or None

    def _resolve_bucket(self) -> BucketDetail:
        """Returns the configured bucket, falling back to the default bucket."""
        bucket = cast("BucketDetail | None", self.get_parameter_value("bucket"))
        if bucket is not None:
            return bucket

        bucket_id = self._get_default_bucket_id()
        logger.info("No bucket supplied, uploading to default bucket %s", bucket_id)
        return BucketDetail.from_dict(self._get_bucket(bucket_id).to_dict())

    def _process(self) -> None:
        asset_name = self.get_parameter_value("asset_name")
        file_path = self.get_parameter_value("file_path")
        content_type = self.get_parameter_value("content_type")

        if asset_name and file_path:
            try:
                bucket = self._resolve_bucket()
                bucket_id = bucket.bucket_id
                self._create_asset(
                    asset_name=asset_name,
                    bucket_id=bucket_id,
                )
                upload_url_response = self._create_asset_url(asset_name, bucket_id, AssertUrlOperation.PUT)

                with Path(file_path).open("rb") as file:
                    headers = upload_url_response.headers.to_dict() or {}
                    headers["Content-Type"] = content_type
                    try:
                        upload_response = requests.put(upload_url_response.url, data=file, headers=headers, timeout=300)
                        upload_response.raise_for_status()
                    except requests.RequestException as e:
                        raise NodeError.from_request_exception(
                            e, provider="Griptape Cloud storage", key_refused=False
                        ) from e

                self.parameter_output_values["asset_name"] = asset_name
                self.parameter_output_values["bucket"] = bucket

                logger.info("Successfully uploaded asset %s to bucket %s", asset_name, bucket_id)

            except Exception as e:
                logger.error("Error uploading asset: %s", e)
                raise

    async def aprocess(self) -> None:
        self._process()
