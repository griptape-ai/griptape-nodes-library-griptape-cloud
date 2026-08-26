import logging
from typing import TYPE_CHECKING, cast

from griptape_cloud_client.models.assert_url_operation import AssertUrlOperation
from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import ControlNode
from griptape_nodes.traits.options import Options

from griptape_cloud.base.base_griptape_cloud_node import BaseGriptapeCloudNode

if TYPE_CHECKING:
    from griptape_cloud_client.models.bucket_detail import BucketDetail

logger = logging.getLogger("griptape_nodes")


class CreateAssetUrl(BaseGriptapeCloudNode, ControlNode):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.add_parameter(
            Parameter(
                name="bucket",
                input_types=["BucketDetail"],
                type="BucketDetail",
                output_type="BucketDetail",
                default_value=None,
                tooltip="The bucket to create asset URL for",
                allowed_modes={ParameterMode.INPUT},
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

        self.add_parameter(
            Parameter(
                name="operation",
                input_types=["str"],
                type="str",
                output_type="str",
                default_value=AssertUrlOperation.GET.value,
                tooltip="The URL operation to perform",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
                traits={
                    Options(
                        choices=[op.value for op in AssertUrlOperation],
                    )
                },
            )
        )

        self.add_parameter(
            Parameter(
                name="asset_url",
                type="str",
                output_type="str",
                default_value=None,
                tooltip="The URL of the asset",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )

    def _process(self) -> None:
        bucket = cast("BucketDetail", self.get_parameter_value("bucket"))
        asset_name = self.get_parameter_value("asset_name")
        operation = self.get_parameter_value("operation")

        if bucket and asset_name:
            response = self._create_asset_url(asset_name, bucket.bucket_id, AssertUrlOperation(operation))
            self.set_parameter_value("asset_url", response.url)
            self.parameter_output_values["asset_url"] = response.url

    async def aprocess(self) -> None:
        self._process()
