# /// script
# dependencies = []
#
# [tool.griptape-nodes]
# name = "griptape_cloud_published_workflow_template_1"
# schema_version = "0.20.0"
# engine_version_created_with = "0.98.0"
# node_libraries_referenced = [["Griptape Cloud Library", "0.72.0"], ["Griptape Nodes Library", "0.84.0"]]
# node_types_used = [["Griptape Cloud Library", "CreateAssetUrl"], ["Griptape Cloud Library", "GriptapeCloudEndFlow"], ["Griptape Cloud Library", "GriptapeCloudStartFlow"], ["Griptape Cloud Library", "UploadAsset"], ["Griptape Nodes Library", "Agent"], ["Griptape Nodes Library", "LoadImage"], ["Griptape Nodes Library", "MergeTexts"], ["Griptape Nodes Library", "Note"], ["Griptape Nodes Library", "ResolveMacroPath"], ["Griptape Nodes Library", "SeedreamImageGeneration"]]
# description = "Example image generation workflow that can be published to Griptape Cloud."
# image = "https://raw.githubusercontent.com/griptape-ai/griptape-nodes-library-griptape-cloud/main/workflows/templates/thumbnail_griptape_cloud_published_workflow_template.webp"
# is_griptape_provided = true
# is_template = true
# is_internal = false
# creation_date = 2026-08-25T22:24:14.812297Z
# last_modified_date = 2026-08-25T23:42:10.176740Z
# workflow_shape = "{\"inputs\":{\"Griptape Cloud Start Flow\":{\"exec_out\":{\"name\":\"exec_out\",\"tooltip\":\"Connection to the next node in the execution chain\",\"type\":\"parametercontroltype\",\"input_types\":[\"parametercontroltype\"],\"output_type\":\"parametercontroltype\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":false,\"mode_allowed_property\":false,\"mode_allowed_output\":true,\"ui_options\":{\"parameter_render_location\":\"top\",\"display_name\":\"Flow Out\"},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":null},\"structure_id\":{\"name\":\"structure_id\",\"tooltip\":\"The structure ID of the published workflow\",\"type\":\"str\",\"input_types\":[\"str\"],\"output_type\":\"str\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":false,\"mode_allowed_property\":true,\"mode_allowed_output\":true,\"ui_options\":{\"button_label\":\"\",\"variant\":\"secondary\",\"size\":\"default\",\"state\":\"normal\",\"full_width\":false,\"button_icon\":\"link\",\"iconPosition\":\"left\",\"tooltip\":\"View Structure in Griptape Cloud\",\"hide\":true},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":\"Structure Config\"},\"structure_name\":{\"name\":\"structure_name\",\"tooltip\":\"The name for the Griptape Cloud Structure.\",\"type\":\"str\",\"input_types\":[\"str\"],\"output_type\":\"str\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":false,\"mode_allowed_property\":true,\"mode_allowed_output\":true,\"ui_options\":{},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":\"Structure Config\"},\"structure_description\":{\"name\":\"structure_description\",\"tooltip\":\"The description for the Griptape Cloud Structure.\",\"type\":\"str\",\"input_types\":[\"str\"],\"output_type\":\"str\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":false,\"mode_allowed_property\":true,\"mode_allowed_output\":true,\"ui_options\":{},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":\"Structure Config\"},\"enable_webhook_integration\":{\"name\":\"enable_webhook_integration\",\"tooltip\":\"Whether to enable a webhook integration for the Structure.\",\"type\":\"bool\",\"input_types\":[\"bool\"],\"output_type\":\"bool\",\"default_value\":false,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":false,\"mode_allowed_property\":true,\"mode_allowed_output\":true,\"ui_options\":{},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":null},\"webhook_url\":{\"name\":\"webhook_url\",\"tooltip\":\"The webhook URL for the published workflow\",\"type\":\"str\",\"input_types\":[\"str\"],\"output_type\":\"str\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":false,\"mode_allowed_property\":true,\"mode_allowed_output\":false,\"ui_options\":{\"button_label\":\"\",\"variant\":\"secondary\",\"size\":\"default\",\"state\":\"normal\",\"full_width\":false,\"button_icon\":\"webhook\",\"iconPosition\":\"left\",\"tooltip\":\"Get Webhook URL\",\"placeholder_text\":\"Click button to retrieve webhook URL after publishing\",\"hide\":true},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":null},\"integration_id\":{\"name\":\"integration_id\",\"tooltip\":\"The integration ID of the published workflow\",\"type\":\"str\",\"input_types\":[\"str\"],\"output_type\":\"str\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":false,\"mode_allowed_property\":true,\"mode_allowed_output\":true,\"ui_options\":{\"button_label\":\"\",\"variant\":\"secondary\",\"size\":\"default\",\"state\":\"normal\",\"full_width\":false,\"button_icon\":\"link\",\"iconPosition\":\"left\",\"tooltip\":\"View Integration in Griptape Cloud\",\"hide\":true},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":null},\"payload\":{\"name\":\"payload\",\"tooltip\":\"The payload for the webhook integration.\",\"type\":\"json\",\"input_types\":[\"json\",\"str\",\"dict\"],\"output_type\":\"json\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":false,\"mode_allowed_property\":true,\"mode_allowed_output\":true,\"ui_options\":{\"display_name\":\"Webhook Payload\",\"hide\":true},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":null},\"query_params\":{\"name\":\"query_params\",\"tooltip\":\"The query parameters for the webhook integration.\",\"type\":\"json\",\"input_types\":[\"json\",\"str\",\"dict\"],\"output_type\":\"json\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":false,\"mode_allowed_property\":true,\"mode_allowed_output\":true,\"ui_options\":{\"display_name\":\"Webhook Query Params\",\"hide\":true},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":null},\"headers\":{\"name\":\"headers\",\"tooltip\":\"The headers for the webhook integration.\",\"type\":\"json\",\"input_types\":[\"json\",\"str\",\"dict\"],\"output_type\":\"json\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":false,\"mode_allowed_property\":true,\"mode_allowed_output\":true,\"ui_options\":{\"display_name\":\"Webhook Headers\",\"hide\":true},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":null},\"custom_install_script_path\":{\"name\":\"custom_install_script_path\",\"tooltip\":\"Path to a .sh file whose contents will be appended to the pre-build install script before publishing.\",\"type\":\"str\",\"input_types\":[\"str\"],\"output_type\":\"str\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":false,\"mode_allowed_property\":true,\"mode_allowed_output\":false,\"ui_options\":{},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":null},\"gpu\":{\"name\":\"gpu\",\"tooltip\":\"Enable GPU support for the published structure.\",\"type\":\"bool\",\"input_types\":[\"bool\"],\"output_type\":\"bool\",\"default_value\":false,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":false,\"mode_allowed_property\":true,\"mode_allowed_output\":false,\"ui_options\":{},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":null},\"prompt\":{\"name\":\"prompt\",\"tooltip\":\"New parameter\",\"type\":\"str\",\"input_types\":[\"any\"],\"output_type\":\"str\",\"default_value\":\"\",\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":true,\"mode_allowed_property\":true,\"mode_allowed_output\":true,\"ui_options\":{\"placeholder_text\":\"Input 2\",\"hide_label\":false,\"hide_property\":false,\"is_custom\":true,\"is_user_added\":true},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":\"\",\"parent_element_name\":null}}},\"outputs\":{\"Griptape Cloud End Flow\":{\"exec_in\":{\"name\":\"exec_in\",\"tooltip\":\"Control path when the flow completed successfully\",\"type\":\"parametercontroltype\",\"input_types\":[\"parametercontroltype\"],\"output_type\":\"parametercontroltype\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":true,\"mode_allowed_property\":false,\"mode_allowed_output\":false,\"ui_options\":{\"parameter_render_location\":\"top\",\"display_name\":\"Succeeded\"},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":null},\"failed\":{\"name\":\"failed\",\"tooltip\":\"Control path when the flow failed\",\"type\":\"parametercontroltype\",\"input_types\":[\"parametercontroltype\"],\"output_type\":\"parametercontroltype\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":true,\"mode_allowed_property\":false,\"mode_allowed_output\":false,\"ui_options\":{\"parameter_render_location\":\"top\",\"display_name\":\"Failed\"},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":null},\"was_successful\":{\"name\":\"was_successful\",\"tooltip\":\"Indicates whether it completed without errors.\",\"type\":\"bool\",\"input_types\":[\"bool\"],\"output_type\":\"bool\",\"default_value\":false,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":false,\"mode_allowed_property\":true,\"mode_allowed_output\":false,\"ui_options\":{},\"settable\":false,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":\"Status\"},\"result_details\":{\"name\":\"result_details\",\"tooltip\":\"Details about the operation result\",\"type\":\"str\",\"input_types\":[\"str\"],\"output_type\":\"str\",\"default_value\":null,\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":true,\"mode_allowed_property\":false,\"mode_allowed_output\":false,\"ui_options\":{\"multiline\":true,\"placeholder_text\":\"Details about the completion or failure will be shown here.\"},\"settable\":false,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":null,\"parent_element_name\":\"Status\"},\"image_prompt\":{\"name\":\"image_prompt\",\"tooltip\":\"New parameter\",\"type\":\"str\",\"input_types\":[\"any\"],\"output_type\":\"str\",\"default_value\":\"\",\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":true,\"mode_allowed_property\":true,\"mode_allowed_output\":true,\"ui_options\":{\"multiline\":true,\"placeholder_text\":\"Agent response\",\"markdown\":false,\"hide_label\":false,\"hide_property\":false,\"is_custom\":true,\"is_user_added\":true},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":\"\",\"parent_element_name\":null},\"image_url\":{\"name\":\"image_url\",\"tooltip\":\"New parameter\",\"type\":\"ImageUrlArtifact\",\"input_types\":[\"any\"],\"output_type\":\"ImageUrlArtifact\",\"default_value\":\"\",\"tooltip_as_input\":null,\"tooltip_as_property\":null,\"tooltip_as_output\":null,\"mode_allowed_input\":true,\"mode_allowed_property\":true,\"mode_allowed_output\":true,\"ui_options\":{\"pulse_on_run\":true,\"hide\":false,\"clickable_file_browser\":true,\"hide_label\":false,\"hide_property\":false,\"is_custom\":true,\"is_user_added\":true},\"settable\":true,\"is_user_defined\":true,\"private\":false,\"parent_container_name\":\"\",\"parent_element_name\":null}}}}"
#
# ///

import argparse
import asyncio
import json
import logging
import pickle
from griptape_nodes.bootstrap.workflow_executors.local_workflow_executor import LocalWorkflowExecutor
from griptape_nodes.bootstrap.workflow_executors.workflow_executor import WorkflowExecutor
from griptape_nodes.node_library.library_registry import IconVariant, NodeDeprecationMetadata, NodeMetadata
from griptape_nodes.retained_mode.events.connection_events import CreateConnectionRequest
from griptape_nodes.retained_mode.events.flow_events import (
    CreateFlowRequest,
    GetTopLevelFlowRequest,
    GetTopLevelFlowResultSuccess,
)
from griptape_nodes.retained_mode.events.library_events import RegisterLibraryFromFileRequest
from griptape_nodes.retained_mode.events.node_events import CreateNodeRequest
from griptape_nodes.retained_mode.events.parameter_events import (
    AddParameterToNodeRequest,
    AlterParameterDetailsRequest,
    AlterParameterGroupDetailsRequest,
    SetParameterValueRequest,
)
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes
from typing import Any


async def build_workflow() -> None:
    await GriptapeNodes.ahandle_request(
        RegisterLibraryFromFileRequest(library_name="Griptape Cloud Library", perform_discovery_if_not_found=True)
    )
    await GriptapeNodes.ahandle_request(
        RegisterLibraryFromFileRequest(library_name="Griptape Nodes Library", perform_discovery_if_not_found=True)
    )
    context_manager = GriptapeNodes.ContextManager()
    if not context_manager.has_current_workflow():
        context_manager.push_workflow(file_path=__file__)
    # 1. We've collated all of the unique parameter values into a dictionary so that we do not have to duplicate them.
    #    This minimizes the size of the code, especially for large objects like serialized image files.
    # 2. We're using a prefix so that it's clear which Flow these values are associated with.
    # 3. The values are serialized using pickle, which is a binary format. This makes them harder to read, but makes
    #    them consistently save and load. It allows us to serialize complex objects like custom classes, which otherwise
    #    would be difficult to serialize.
    top_level_unique_values_dict = {
        "7f429b4b-a0d4-4046-bde7-b0d673c7d30d": pickle.loads(
            b"\x80\x04\x95]\x00\x00\x00\x00\x00\x00\x00\x8cYTake the following input prompt, and use it to create a detailed image generation prompt:\x94."
        ),
        "c6c589ed-5086-4858-98dc-64ab0c92e7da": pickle.loads(
            b"\x80\x04\x95\x0e\x00\x00\x00\x00\x00\x00\x00\x8c\nskateboard\x94."
        ),
        "5a5674aa-cde1-4c7a-97cd-d25be76e20c7": pickle.loads(
            b"\x80\x04\x95\x08\x00\x00\x00\x00\x00\x00\x00\x8c\x04\\n\\n\x94."
        ),
        "29dcd471-b9e3-4b81-876c-39e49d3a27ed": pickle.loads(b"\x80\x04\x89."),
        "2af9b91b-c2e3-4e3b-aff0-4f9061237bdb": pickle.loads(
            b"\x80\x04\x95i\x00\x00\x00\x00\x00\x00\x00\x8ceTake the following input prompt, and use it to create a detailed image generation prompt:\n\nskateboard\x94."
        ),
        "ecf109ac-a570-463e-beb1-9710a626c525": pickle.loads(
            b"\x80\x04\x95\xe4\x00\x00\x00\x00\x00\x00\x00\x8c\xe0The Griptape Cloud Start Flow node here exposes the input parameters that can be supplied for the workflow. \n\nA Start Flow node is a required node to have before publishing, and should be placed at the beginning of the flow.\x94."
        ),
        "2508ed38-fbef-48b7-a5c6-51ca76ae6fdd": pickle.loads(
            b"\x80\x04\x95\xc7\x00\x00\x00\x00\x00\x00\x00\x8c\xc3This section of the workflow is just an example. This logic will be bundled up as a result of publishing, like a black box. The Start Flow inputs will be exposed, as well as the End Flow outputs.\x94."
        ),
        "547b4beb-ec23-4672-b042-261f34281f06": pickle.loads(
            b"\x80\x04\x95g\x00\x00\x00\x00\x00\x00\x00\x8ccThe End Flow node here exposes the outputs for this workflow. It is a required node for publishing.\x94."
        ),
        "80fb6416-dc1b-40c0-9d08-0b24ed47ff9c": pickle.loads(
            b"\x80\x04\x95a\x00\x00\x00\x00\x00\x00\x00\x8c]To publish this workflow, click the top right rocket icon, and choose Griptape Cloud Library!\x94."
        ),
        "bc00a77c-f581-4e20-a5a7-910dbecaa3e8": pickle.loads(
            b"\x80\x04\x95\x04\x00\x00\x00\x00\x00\x00\x00\x8c\x00\x94."
        ),
        "2e3acfc4-6e98-4f95-b684-ea7ae855b3a4": pickle.loads(
            b"\x80\x04\x95\r\x00\x00\x00\x00\x00\x00\x00\x8c\timage/png\x94."
        ),
        "357ce777-3aba-461a-955d-269b80db3348": pickle.loads(
            b"\x80\x04\x95\n\x00\x00\x00\x00\x00\x00\x00\x8c\x06output\x94."
        ),
        "65876e0a-ed3d-452b-b63e-9877c20188c5": pickle.loads(
            b"\x80\x04\x95\x07\x00\x00\x00\x00\x00\x00\x00\x8c\x03GET\x94."
        ),
        "55c58576-ff56-42f6-a52d-ed8b5b52c8e4": pickle.loads(
            b"\x80\x04\x95\x12\x00\x00\x00\x00\x00\x00\x00\x8c\x0egriptape_cloud\x94."
        ),
        "f324a9ad-0757-47d2-aef6-74c6c301cafc": pickle.loads(
            b"\x80\x04\x95\x13\x00\x00\x00\x00\x00\x00\x00\x8c\x0fclaude-sonnet-5\x94."
        ),
        "c5b25a14-a4f7-472d-bd15-0a1750c7c339": pickle.loads(b"\x80\x04}\x94."),
        "a739cd2b-f2df-4150-8a47-6485cf4f2dd0": pickle.loads(b"\x80\x04]\x94."),
        "f9d4b69a-4736-4c74-8b93-1577fbd25172": pickle.loads(b"\x80\x04]\x94."),
        "858ccee2-eb49-47c4-afe7-22569f790ca7": pickle.loads(b"\x80\x04\x95\x04\x00\x00\x00\x00\x00\x00\x00MX\x02."),
        "b7eafdb5-6536-43a0-bbdc-96f32394f9e3": pickle.loads(
            b"\x80\x04\x95\x17\x00\x00\x00\x00\x00\x00\x00\x8c\x13seedream-5-0-260128\x94."
        ),
        "dfa4b251-d641-4ae5-b095-b30c25058968": pickle.loads(b"\x80\x04]\x94."),
        "cff4b4c4-b419-430f-ae1a-3a1df3ed2150": pickle.loads(
            b"\x80\x04\x95\x06\x00\x00\x00\x00\x00\x00\x00\x8c\x022K\x94."
        ),
        "e6397bc7-a0c6-4c2c-83d1-6b28ecef54e9": pickle.loads(b"\x80\x04K\n."),
        "03aa97ad-7e4e-4018-8605-d44bb06fc271": pickle.loads(
            b"\x80\x04\x95\x08\x00\x00\x00\x00\x00\x00\x00\x8c\x04jpeg\x94."
        ),
        "6831ce54-81c2-467d-906d-b1f6282aa431": pickle.loads(
            b"\x80\x04\x95\x0c\x00\x00\x00\x00\x00\x00\x00\x8c\x08standard\x94."
        ),
        "a28f3e34-3a68-442c-9590-766bd6207c28": pickle.loads(
            b"\x80\x04\x95\x16\x00\x00\x00\x00\x00\x00\x00\x8c\x12seedream_image.jpg\x94."
        ),
        "6f11612a-7207-41ce-a37c-647ea34a7af1": pickle.loads(
            b"\x80\x04\x95\x08\x00\x00\x00\x00\x00\x00\x00\x8c\x04none\x94."
        ),
        "6bd0efeb-a456-496b-9bc4-8c7298e64d5f": pickle.loads(
            b"\x80\x04\x95\x0c\x00\x00\x00\x00\x00\x00\x00\x8c\x08mask.png\x94."
        ),
    }
    # Create the Flow, then do work within it as context.
    flow0_name = (
        await GriptapeNodes.ahandle_request(
            CreateFlowRequest(parent_flow_name=None, flow_name="ControlFlow_1", set_as_new_context=False, metadata={})
        )
    ).flow_name
    with GriptapeNodes.ContextManager().flow(flow0_name):
        node0_name = (
            await GriptapeNodes.ahandle_request(
                CreateNodeRequest(
                    node_type="MergeTexts",
                    specific_library_name="Griptape Nodes Library",
                    node_name="Merge Texts",
                    metadata={
                        "position": {"x": 550, "y": 932},
                        "tempId": "placing-1767980369997-kufb8",
                        "library_node_metadata": {
                            "category": "text",
                            "description": "MergeTexts node",
                            "display_name": "Merge Texts",
                            "tags": ["text", "combine"],
                            "icon": "merge",
                            "color": None,
                            "group": "merge",
                            "deprecation": None,
                            "is_node_group": None,
                            "declarations": [],
                        },
                        "library": "Griptape Nodes Library",
                        "node_type": "MergeTexts",
                        "showaddparameter": False,
                        "size": {"width": 607, "height": 846},
                        "category": "text",
                    },
                    initial_setup=True,
                )
            )
        ).node_name
        node1_name = (
            await GriptapeNodes.ahandle_request(
                CreateNodeRequest(
                    node_type="Note",
                    specific_library_name="Griptape Nodes Library",
                    node_name="Workflow Start",
                    metadata={
                        "position": {"x": -223.91570464903003, "y": 489.38316050831463},
                        "tempId": "placing-1759960199321-1cotty",
                        "library_node_metadata": {
                            "category": "misc",
                            "description": "Create a note node to provide helpful context in your workflow",
                            "display_name": "Note",
                            "tags": ["workflow", "annotation", "note"],
                            "icon": "notepad-text",
                            "color": None,
                            "group": "create",
                            "deprecation": None,
                            "is_node_group": None,
                            "declarations": [],
                        },
                        "library": "Griptape Nodes Library",
                        "node_type": "Note",
                        "showaddparameter": False,
                        "category": "misc",
                        "size": {"width": 600, "height": 356},
                    },
                    resolution="resolved",
                    initial_setup=True,
                )
            )
        ).node_name
        node2_name = (
            await GriptapeNodes.ahandle_request(
                CreateNodeRequest(
                    node_type="Note",
                    specific_library_name="Griptape Nodes Library",
                    node_name="Workflow Body",
                    metadata={
                        "position": {"x": 550, "y": 483.3831605083146},
                        "tempId": "placing-1759960275375-u04md",
                        "library_node_metadata": {
                            "category": "misc",
                            "description": "Create a note node to provide helpful context in your workflow",
                            "display_name": "Note",
                            "tags": ["workflow", "annotation", "note"],
                            "icon": "notepad-text",
                            "color": None,
                            "group": "create",
                            "deprecation": None,
                            "is_node_group": None,
                            "declarations": [],
                            "resolved_model_usage": [],
                        },
                        "library": "Griptape Nodes Library",
                        "node_type": "Note",
                        "showaddparameter": False,
                        "size": {"width": 4820, "height": 361},
                        "category": "misc",
                    },
                    resolution="resolved",
                    initial_setup=True,
                )
            )
        ).node_name
        node3_name = (
            await GriptapeNodes.ahandle_request(
                CreateNodeRequest(
                    node_type="Note",
                    specific_library_name="Griptape Nodes Library",
                    node_name="Workflow Output",
                    metadata={
                        "position": {"x": 5434.097631760926, "y": 502.38316050831463},
                        "tempId": "placing-1759960354172-8aukc",
                        "library_node_metadata": {
                            "category": "misc",
                            "description": "Create a note node to provide helpful context in your workflow",
                            "display_name": "Note",
                            "tags": ["workflow", "annotation", "note"],
                            "icon": "notepad-text",
                            "color": None,
                            "group": "create",
                            "deprecation": None,
                            "is_node_group": None,
                            "declarations": [],
                            "resolved_model_usage": [],
                        },
                        "library": "Griptape Nodes Library",
                        "node_type": "Note",
                        "showaddparameter": False,
                        "category": "misc",
                        "size": {"width": 600, "height": 334},
                    },
                    resolution="resolved",
                    initial_setup=True,
                )
            )
        ).node_name
        node4_name = (
            await GriptapeNodes.ahandle_request(
                CreateNodeRequest(
                    node_type="Note",
                    specific_library_name="Griptape Nodes Library",
                    node_name="Publishing",
                    metadata={
                        "position": {"x": 5434.097631760926, "y": 113.81610428702987},
                        "tempId": "placing-1759960393090-qtlpje",
                        "library_node_metadata": {
                            "category": "misc",
                            "description": "Create a note node to provide helpful context in your workflow",
                            "display_name": "Note",
                            "tags": ["workflow", "annotation", "note"],
                            "icon": "notepad-text",
                            "color": None,
                            "group": "create",
                            "deprecation": None,
                            "is_node_group": None,
                            "declarations": [],
                            "resolved_model_usage": [],
                        },
                        "library": "Griptape Nodes Library",
                        "node_type": "Note",
                        "showaddparameter": False,
                        "size": {"width": 600, "height": 319},
                        "category": "misc",
                    },
                    resolution="resolved",
                    initial_setup=True,
                )
            )
        ).node_name
        node5_name = (
            await GriptapeNodes.ahandle_request(
                CreateNodeRequest(
                    node_type="ResolveMacroPath",
                    specific_library_name="Griptape Nodes Library",
                    node_name="Resolve Macro Path",
                    metadata={
                        "position": {"x": 2690.0779239468116, "y": 932},
                        "tempId": "placing-1787699704094-ukbw9",
                        "library_node_metadata": {
                            "category": "files",
                            "description": "Resolve a macro path to an absolute filesystem path (e.g. {inputs}/file.txt → /home/user/project/inputs/file.txt).",
                            "display_name": "Resolve Macro Path",
                            "tags": ["file", "macro", "path"],
                            "icon": "FolderSearch",
                            "color": None,
                            "group": None,
                            "deprecation": None,
                            "is_node_group": None,
                            "declarations": [],
                        },
                        "library": "Griptape Nodes Library",
                        "node_type": "ResolveMacroPath",
                        "showaddparameter": False,
                        "size": {"width": 600, "height": 823},
                    },
                    initial_setup=True,
                )
            )
        ).node_name
        node6_name = (
            await GriptapeNodes.ahandle_request(
                CreateNodeRequest(
                    node_type="UploadAsset",
                    specific_library_name="Griptape Cloud Library",
                    node_name="Upload Asset",
                    metadata={
                        "position": {"x": 3436.2860826566475, "y": 932},
                        "tempId": "placing-1787700497439-8ui59",
                        "library_node_metadata": {
                            "category": "griptape_cloud/assets",
                            "description": "Griptape Node that uploads an asset to a specific bucket.",
                            "display_name": "Upload Asset",
                            "tags": None,
                            "icon": None,
                            "color": None,
                            "group": None,
                            "deprecation": None,
                            "is_node_group": None,
                            "declarations": [],
                        },
                        "library": "Griptape Cloud Library",
                        "node_type": "UploadAsset",
                        "showaddparameter": False,
                        "size": {"width": 601, "height": 808},
                    },
                    initial_setup=True,
                )
            )
        ).node_name
        node7_name = (
            await GriptapeNodes.ahandle_request(
                CreateNodeRequest(
                    node_type="CreateAssetUrl",
                    specific_library_name="Griptape Cloud Library",
                    node_name="Create Asset URL",
                    metadata={
                        "position": {"x": 4113.853045824894, "y": 932},
                        "tempId": "placing-1787700536387-v9hoi",
                        "library_node_metadata": {
                            "category": "griptape_cloud/assets",
                            "description": "Griptape Node that creates a URL for uploading or downloading an asset.",
                            "display_name": "Create Asset URL",
                            "tags": None,
                            "icon": None,
                            "color": None,
                            "group": None,
                            "deprecation": None,
                            "is_node_group": None,
                            "declarations": [],
                        },
                        "library": "Griptape Cloud Library",
                        "node_type": "CreateAssetUrl",
                        "showaddparameter": False,
                        "size": {"width": 600, "height": 802},
                    },
                    initial_setup=True,
                )
            )
        ).node_name
        node8_name = (
            await GriptapeNodes.ahandle_request(
                CreateNodeRequest(
                    node_type="Agent",
                    specific_library_name="Griptape Nodes Library",
                    node_name="Agent",
                    metadata={
                        "library_node_metadata": {
                            "category": "agents",
                            "description": "Creates an AI agent with conversation memory and the ability to use tools",
                            "display_name": "Agent",
                            "tags": ["agent", "ai", "llm", "conversation", "memory"],
                            "icon": None,
                            "color": None,
                            "group": "create",
                            "deprecation": None,
                            "is_node_group": None,
                            "declarations": [
                                {
                                    "type": "model_usage",
                                    "model_ids": [
                                        "gtc_claude_sonnet_5",
                                        "gtc_claude_opus_5",
                                        "gtc_claude_haiku_4_5",
                                        "gtc_gemini_3_6_flash",
                                        "gtc_gemini_3_5_flash",
                                        "gtc_gemini_3_5_flash_lite",
                                        "gtc_gemini_3_1_pro",
                                        "gtc_gemini_3_1_flash_lite",
                                        "gtc_gemini_3_flash",
                                        "gtc_gemini_2_5_pro",
                                        "gtc_gemini_2_5_flash",
                                        "gtc_gemini_2_5_flash_lite",
                                        "gtc_gpt_5_2",
                                        "gtc_gpt_5_2_chat",
                                        "gtc_gpt_5_1",
                                        "gtc_gpt_5",
                                        "gtc_gpt_5_mini",
                                        "gtc_gpt_5_nano",
                                        "gtc_gpt_4_1",
                                        "gtc_gpt_4_1_mini",
                                        "gtc_gpt_4_1_nano",
                                        "gtc_gpt_4o",
                                        "gtc_o4_mini",
                                        "gtc_o3",
                                        "gtc_o3_mini",
                                        "gtc_o1",
                                        "gtc_deepseek_v3",
                                        "gtc_deepseek_r1",
                                        "gtc_llama_3_3_70b",
                                        "gtc_llama_3_1_70b",
                                    ],
                                }
                            ],
                        },
                        "library": "Griptape Nodes Library",
                        "node_type": "Agent",
                        "position": {"x": 1234.0721897946703, "y": 932},
                        "size": {"width": 600, "height": 841},
                    },
                    initial_setup=True,
                )
            )
        ).node_name
        node9_name = (
            await GriptapeNodes.ahandle_request(
                CreateNodeRequest(
                    node_type="SeedreamImageGeneration",
                    specific_library_name="Griptape Nodes Library",
                    node_name="Seedream Image Generation",
                    metadata={
                        "library_node_metadata": {
                            "category": "image",
                            "description": "Generate images using Seedream models via Griptape model proxy",
                            "display_name": "Seedream Image Generation",
                            "tags": ["image", "generation", "ai", "api", "seedream"],
                            "icon": "Sparkles",
                            "color": None,
                            "group": "create",
                            "deprecation": None,
                            "is_node_group": None,
                            "declarations": [
                                {
                                    "type": "model_usage",
                                    "model_ids": ["gtc_seedream_5_0_pro", "gtc_seedream_5_0_lite", "gtc_seedream_4_5"],
                                }
                            ],
                        },
                        "library": "Griptape Nodes Library",
                        "node_type": "SeedreamImageGeneration",
                        "position": {"x": 1905.8443362551295, "y": 932},
                        "size": {"width": 600, "height": 840},
                    },
                    initial_setup=True,
                )
            )
        ).node_name
        with GriptapeNodes.ContextManager().node(node9_name):
            await GriptapeNodes.ahandle_request(
                AlterParameterDetailsRequest(
                    parameter_name="size",
                    ui_options={
                        "simple_dropdown": [
                            "2K",
                            "3K",
                            "4K",
                            "2048x2048",
                            "2304x1728",
                            "1728x2304",
                            "2848x1600",
                            "1600x2848",
                            "2496x1664",
                            "1664x2496",
                            "3136x1344",
                            "3072x3072",
                            "3456x2592",
                            "2592x3456",
                            "4096x2304",
                            "2304x4096",
                            "2496x3744",
                            "3744x2496",
                            "4704x2016",
                            "4096x4096",
                            "3520x4704",
                            "4704x3520",
                            "5504x3040",
                            "3040x5504",
                            "3328x4992",
                            "4992x3328",
                            "6240x2656",
                        ],
                        "show_search": True,
                        "search_filter": "",
                        "hide_label": False,
                        "hide_property": False,
                    },
                    initial_setup=True,
                )
            )
            await GriptapeNodes.ahandle_request(
                AlterParameterDetailsRequest(
                    parameter_name="output_format",
                    ui_options={
                        "simple_dropdown": ["jpeg", "png"],
                        "show_search": True,
                        "search_filter": "",
                        "hide": False,
                        "hide_label": False,
                        "hide_property": False,
                    },
                    initial_setup=True,
                )
            )
            await GriptapeNodes.ahandle_request(
                AlterParameterDetailsRequest(
                    parameter_name="optimize_prompt_mode",
                    ui_options={
                        "simple_dropdown": ["standard"],
                        "show_search": True,
                        "search_filter": "",
                        "hide": False,
                        "hide_label": False,
                        "hide_property": False,
                    },
                    initial_setup=True,
                )
            )
        node10_name = (
            await GriptapeNodes.ahandle_request(
                CreateNodeRequest(
                    node_type="GriptapeCloudStartFlow",
                    specific_library_name="Griptape Cloud Library",
                    node_name="Griptape Cloud Start Flow",
                    metadata={
                        "library_node_metadata": {
                            "category": "griptape_cloud/published_workflows",
                            "description": "Node that defines the start of a workflow and passes parameters for a flow on Griptape Cloud.",
                            "display_name": "Griptape Cloud Start Flow",
                            "tags": None,
                            "icon": None,
                            "color": None,
                            "group": None,
                            "deprecation": None,
                            "is_node_group": None,
                            "declarations": [],
                        },
                        "library": "Griptape Cloud Library",
                        "node_type": "GriptapeCloudStartFlow",
                        "showaddparameter": True,
                        "position": {"x": -223.91570464903003, "y": 932},
                        "size": {"width": 617, "height": 832},
                    },
                    initial_setup=True,
                )
            )
        ).node_name
        with GriptapeNodes.ContextManager().node(node10_name):
            await GriptapeNodes.ahandle_request(
                AddParameterToNodeRequest(
                    parameter_name="prompt",
                    default_value="",
                    tooltip="New parameter",
                    type="str",
                    input_types=["any"],
                    output_type="str",
                    ui_options={
                        "placeholder_text": "Input 2",
                        "hide_label": False,
                        "hide_property": False,
                        "is_custom": True,
                        "is_user_added": True,
                    },
                    parent_container_name="",
                    initial_setup=True,
                )
            )
            await GriptapeNodes.ahandle_request(
                AlterParameterGroupDetailsRequest(
                    group_name="Structure Config", ui_options={"hide": False, "collapsed": True}, initial_setup=True
                )
            )
        node11_name = (
            await GriptapeNodes.ahandle_request(
                CreateNodeRequest(
                    node_type="GriptapeCloudEndFlow",
                    specific_library_name="Griptape Cloud Library",
                    node_name="Griptape Cloud End Flow",
                    metadata={
                        "position": {"x": 5434.097631760926, "y": 932},
                        "tempId": "placing-1787701239022-oxfl5",
                        "library_node_metadata": {
                            "category": "griptape_cloud/published_workflows",
                            "description": "Node that defines the end of a workflow and passes parameters for a flow on Griptape Cloud.",
                            "display_name": "Griptape Cloud End Flow",
                            "tags": None,
                            "icon": None,
                            "color": None,
                            "group": None,
                            "deprecation": None,
                            "is_node_group": None,
                            "declarations": [],
                            "resolved_model_usage": [],
                        },
                        "library": "Griptape Cloud Library",
                        "node_type": "GriptapeCloudEndFlow",
                        "showaddparameter": True,
                        "size": {"width": 600, "height": 813},
                    },
                    initial_setup=True,
                )
            )
        ).node_name
        with GriptapeNodes.ContextManager().node(node11_name):
            await GriptapeNodes.ahandle_request(
                AddParameterToNodeRequest(
                    parameter_name="image_prompt",
                    default_value="",
                    tooltip="New parameter",
                    type="str",
                    input_types=["any"],
                    output_type="str",
                    ui_options={
                        "multiline": True,
                        "placeholder_text": "Agent response",
                        "markdown": False,
                        "hide_label": False,
                        "hide_property": False,
                        "is_custom": True,
                        "is_user_added": True,
                    },
                    parent_container_name="",
                    initial_setup=True,
                )
            )
            await GriptapeNodes.ahandle_request(
                AddParameterToNodeRequest(
                    parameter_name="image_url",
                    default_value="",
                    tooltip="New parameter",
                    type="ImageUrlArtifact",
                    input_types=["any"],
                    output_type="ImageUrlArtifact",
                    ui_options={
                        "pulse_on_run": True,
                        "hide": False,
                        "clickable_file_browser": True,
                        "hide_label": False,
                        "hide_property": False,
                        "is_custom": True,
                        "is_user_added": True,
                    },
                    parent_container_name="",
                    initial_setup=True,
                )
            )
        node12_name = (
            await GriptapeNodes.ahandle_request(
                CreateNodeRequest(
                    node_type="LoadImage",
                    specific_library_name="Griptape Nodes Library",
                    node_name="Load Image",
                    metadata={
                        "position": {"x": 4772.7813914999, "y": 932},
                        "tempId": "placing-1787701296591-hjdubr",
                        "library_node_metadata": {
                            "category": "image",
                            "description": "Loads an image from disk",
                            "display_name": "Load Image",
                            "tags": ["image", "file", "load"],
                            "icon": "image-up",
                            "color": None,
                            "group": "Input/Output",
                            "deprecation": None,
                            "is_node_group": None,
                            "declarations": [],
                            "resolved_model_usage": [],
                        },
                        "library": "Griptape Nodes Library",
                        "node_type": "LoadImage",
                        "showaddparameter": False,
                        "size": {"width": 607, "height": 797},
                    },
                    initial_setup=True,
                )
            )
        ).node_name
        with GriptapeNodes.ContextManager().node(node12_name):
            await GriptapeNodes.ahandle_request(
                AlterParameterDetailsRequest(parameter_name="image", settable=False, initial_setup=True)
            )
            await GriptapeNodes.ahandle_request(
                AlterParameterDetailsRequest(parameter_name="path", settable=False, initial_setup=True)
            )
        await GriptapeNodes.ahandle_request(
            CreateConnectionRequest(
                source_node_name=node5_name,
                source_parameter_name="resolved_path",
                target_node_name=node6_name,
                target_parameter_name="file_path",
                initial_setup=True,
            )
        )
        await GriptapeNodes.ahandle_request(
            CreateConnectionRequest(
                source_node_name=node6_name,
                source_parameter_name="bucket",
                target_node_name=node7_name,
                target_parameter_name="bucket",
                initial_setup=True,
            )
        )
        await GriptapeNodes.ahandle_request(
            CreateConnectionRequest(
                source_node_name=node6_name,
                source_parameter_name="asset_name",
                target_node_name=node7_name,
                target_parameter_name="asset_name",
                initial_setup=True,
            )
        )
        await GriptapeNodes.ahandle_request(
            CreateConnectionRequest(
                source_node_name=node0_name,
                source_parameter_name="output",
                target_node_name=node8_name,
                target_parameter_name="prompt",
                initial_setup=True,
            )
        )
        await GriptapeNodes.ahandle_request(
            CreateConnectionRequest(
                source_node_name=node8_name,
                source_parameter_name="output",
                target_node_name=node9_name,
                target_parameter_name="prompt",
                initial_setup=True,
            )
        )
        await GriptapeNodes.ahandle_request(
            CreateConnectionRequest(
                source_node_name=node9_name,
                source_parameter_name="image_url",
                target_node_name=node5_name,
                target_parameter_name="path",
                initial_setup=True,
            )
        )
        await GriptapeNodes.ahandle_request(
            CreateConnectionRequest(
                source_node_name=node10_name,
                source_parameter_name="prompt",
                target_node_name=node0_name,
                target_parameter_name="input_2",
                initial_setup=True,
            )
        )
        await GriptapeNodes.ahandle_request(
            CreateConnectionRequest(
                source_node_name=node8_name,
                source_parameter_name="output",
                target_node_name=node11_name,
                target_parameter_name="image_prompt",
                initial_setup=True,
            )
        )
        await GriptapeNodes.ahandle_request(
            CreateConnectionRequest(
                source_node_name=node7_name,
                source_parameter_name="asset_url",
                target_node_name=node12_name,
                target_parameter_name="image",
                initial_setup=True,
            )
        )
        await GriptapeNodes.ahandle_request(
            CreateConnectionRequest(
                source_node_name=node12_name,
                source_parameter_name="image",
                target_node_name=node11_name,
                target_parameter_name="image_url",
                initial_setup=True,
            )
        )
        with GriptapeNodes.ContextManager().node(node0_name):
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="input_1",
                    node_name=node0_name,
                    value=top_level_unique_values_dict["7f429b4b-a0d4-4046-bde7-b0d673c7d30d"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="input_2",
                    node_name=node0_name,
                    value=top_level_unique_values_dict["c6c589ed-5086-4858-98dc-64ab0c92e7da"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="merge_string",
                    node_name=node0_name,
                    value=top_level_unique_values_dict["5a5674aa-cde1-4c7a-97cd-d25be76e20c7"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="whitespace",
                    node_name=node0_name,
                    value=top_level_unique_values_dict["29dcd471-b9e3-4b81-876c-39e49d3a27ed"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="output",
                    node_name=node0_name,
                    value=top_level_unique_values_dict["2af9b91b-c2e3-4e3b-aff0-4f9061237bdb"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="output",
                    node_name=node0_name,
                    value=top_level_unique_values_dict["2af9b91b-c2e3-4e3b-aff0-4f9061237bdb"],
                    initial_setup=True,
                    is_output=True,
                )
            )
        with GriptapeNodes.ContextManager().node(node1_name):
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="note",
                    node_name=node1_name,
                    value=top_level_unique_values_dict["ecf109ac-a570-463e-beb1-9710a626c525"],
                    initial_setup=True,
                    is_output=False,
                )
            )
        with GriptapeNodes.ContextManager().node(node2_name):
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="note",
                    node_name=node2_name,
                    value=top_level_unique_values_dict["2508ed38-fbef-48b7-a5c6-51ca76ae6fdd"],
                    initial_setup=True,
                    is_output=False,
                )
            )
        with GriptapeNodes.ContextManager().node(node3_name):
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="note",
                    node_name=node3_name,
                    value=top_level_unique_values_dict["547b4beb-ec23-4672-b042-261f34281f06"],
                    initial_setup=True,
                    is_output=False,
                )
            )
        with GriptapeNodes.ContextManager().node(node4_name):
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="note",
                    node_name=node4_name,
                    value=top_level_unique_values_dict["80fb6416-dc1b-40c0-9d08-0b24ed47ff9c"],
                    initial_setup=True,
                    is_output=False,
                )
            )
        with GriptapeNodes.ContextManager().node(node5_name):
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="path",
                    node_name=node5_name,
                    value=top_level_unique_values_dict["bc00a77c-f581-4e20-a5a7-910dbecaa3e8"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="resolved_path",
                    node_name=node5_name,
                    value=top_level_unique_values_dict["bc00a77c-f581-4e20-a5a7-910dbecaa3e8"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="was_successful",
                    node_name=node5_name,
                    value=top_level_unique_values_dict["29dcd471-b9e3-4b81-876c-39e49d3a27ed"],
                    initial_setup=True,
                    is_output=False,
                )
            )
        with GriptapeNodes.ContextManager().node(node6_name):
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="file_path",
                    node_name=node6_name,
                    value=top_level_unique_values_dict["bc00a77c-f581-4e20-a5a7-910dbecaa3e8"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="content_type",
                    node_name=node6_name,
                    value=top_level_unique_values_dict["2e3acfc4-6e98-4f95-b684-ea7ae855b3a4"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="asset_name",
                    node_name=node6_name,
                    value=top_level_unique_values_dict["357ce777-3aba-461a-955d-269b80db3348"],
                    initial_setup=True,
                    is_output=False,
                )
            )
        with GriptapeNodes.ContextManager().node(node7_name):
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="asset_name",
                    node_name=node7_name,
                    value=top_level_unique_values_dict["357ce777-3aba-461a-955d-269b80db3348"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="operation",
                    node_name=node7_name,
                    value=top_level_unique_values_dict["65876e0a-ed3d-452b-b63e-9877c20188c5"],
                    initial_setup=True,
                    is_output=False,
                )
            )
        with GriptapeNodes.ContextManager().node(node8_name):
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="model_provider",
                    node_name=node8_name,
                    value=top_level_unique_values_dict["55c58576-ff56-42f6-a52d-ed8b5b52c8e4"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="model",
                    node_name=node8_name,
                    value=top_level_unique_values_dict["f324a9ad-0757-47d2-aef6-74c6c301cafc"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="agent_memory",
                    node_name=node8_name,
                    value=top_level_unique_values_dict["c5b25a14-a4f7-472d-bd15-0a1750c7c339"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="prompt",
                    node_name=node8_name,
                    value=top_level_unique_values_dict["2af9b91b-c2e3-4e3b-aff0-4f9061237bdb"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="additional_context",
                    node_name=node8_name,
                    value=top_level_unique_values_dict["bc00a77c-f581-4e20-a5a7-910dbecaa3e8"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="tools",
                    node_name=node8_name,
                    value=top_level_unique_values_dict["a739cd2b-f2df-4150-8a47-6485cf4f2dd0"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="rulesets",
                    node_name=node8_name,
                    value=top_level_unique_values_dict["f9d4b69a-4736-4c74-8b93-1577fbd25172"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="output",
                    node_name=node8_name,
                    value=top_level_unique_values_dict["bc00a77c-f581-4e20-a5a7-910dbecaa3e8"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="include_details",
                    node_name=node8_name,
                    value=top_level_unique_values_dict["29dcd471-b9e3-4b81-876c-39e49d3a27ed"],
                    initial_setup=True,
                    is_output=False,
                )
            )
        with GriptapeNodes.ContextManager().node(node9_name):
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="api_key_provider",
                    node_name=node9_name,
                    value=top_level_unique_values_dict["29dcd471-b9e3-4b81-876c-39e49d3a27ed"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="timeout",
                    node_name=node9_name,
                    value=top_level_unique_values_dict["858ccee2-eb49-47c4-afe7-22569f790ca7"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="model",
                    node_name=node9_name,
                    value=top_level_unique_values_dict["b7eafdb5-6536-43a0-bbdc-96f32394f9e3"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="prompt",
                    node_name=node9_name,
                    value=top_level_unique_values_dict["bc00a77c-f581-4e20-a5a7-910dbecaa3e8"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="images",
                    node_name=node9_name,
                    value=top_level_unique_values_dict["dfa4b251-d641-4ae5-b095-b30c25058968"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="size",
                    node_name=node9_name,
                    value=top_level_unique_values_dict["cff4b4c4-b419-430f-ae1a-3a1df3ed2150"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="max_images",
                    node_name=node9_name,
                    value=top_level_unique_values_dict["e6397bc7-a0c6-4c2c-83d1-6b28ecef54e9"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="output_format",
                    node_name=node9_name,
                    value=top_level_unique_values_dict["03aa97ad-7e4e-4018-8605-d44bb06fc271"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="optimize_prompt_mode",
                    node_name=node9_name,
                    value=top_level_unique_values_dict["6831ce54-81c2-467d-906d-b1f6282aa431"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="output_file",
                    node_name=node9_name,
                    value=top_level_unique_values_dict["a28f3e34-3a68-442c-9590-766bd6207c28"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="was_successful",
                    node_name=node9_name,
                    value=top_level_unique_values_dict["29dcd471-b9e3-4b81-876c-39e49d3a27ed"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="generation_id",
                    node_name=node9_name,
                    value=top_level_unique_values_dict["bc00a77c-f581-4e20-a5a7-910dbecaa3e8"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="generation_status",
                    node_name=node9_name,
                    value=top_level_unique_values_dict["bc00a77c-f581-4e20-a5a7-910dbecaa3e8"],
                    initial_setup=True,
                    is_output=False,
                )
            )
        with GriptapeNodes.ContextManager().node(node10_name):
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="enable_webhook_integration",
                    node_name=node10_name,
                    value=top_level_unique_values_dict["29dcd471-b9e3-4b81-876c-39e49d3a27ed"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="gpu",
                    node_name=node10_name,
                    value=top_level_unique_values_dict["29dcd471-b9e3-4b81-876c-39e49d3a27ed"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="prompt",
                    node_name=node10_name,
                    value=top_level_unique_values_dict["c6c589ed-5086-4858-98dc-64ab0c92e7da"],
                    initial_setup=True,
                    is_output=False,
                )
            )
        with GriptapeNodes.ContextManager().node(node11_name):
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="was_successful",
                    node_name=node11_name,
                    value=top_level_unique_values_dict["29dcd471-b9e3-4b81-876c-39e49d3a27ed"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="image_prompt",
                    node_name=node11_name,
                    value=top_level_unique_values_dict["bc00a77c-f581-4e20-a5a7-910dbecaa3e8"],
                    initial_setup=True,
                    is_output=False,
                )
            )
        with GriptapeNodes.ContextManager().node(node12_name):
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="path",
                    node_name=node12_name,
                    value=top_level_unique_values_dict["bc00a77c-f581-4e20-a5a7-910dbecaa3e8"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="path",
                    node_name=node12_name,
                    value=top_level_unique_values_dict["bc00a77c-f581-4e20-a5a7-910dbecaa3e8"],
                    initial_setup=True,
                    is_output=True,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="mask_channel",
                    node_name=node12_name,
                    value=top_level_unique_values_dict["6f11612a-7207-41ce-a37c-647ea34a7af1"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="was_successful",
                    node_name=node12_name,
                    value=top_level_unique_values_dict["29dcd471-b9e3-4b81-876c-39e49d3a27ed"],
                    initial_setup=True,
                    is_output=False,
                )
            )
            await GriptapeNodes.ahandle_request(
                SetParameterValueRequest(
                    parameter_name="mask_output_file",
                    node_name=node12_name,
                    value=top_level_unique_values_dict["6bd0efeb-a456-496b-9bc4-8c7298e64d5f"],
                    initial_setup=True,
                    is_output=False,
                )
            )


async def _ensure_workflow_context():
    context_manager = GriptapeNodes.ContextManager()
    if not context_manager.has_current_flow():
        top_level_flow_request = GetTopLevelFlowRequest()
        top_level_flow_result = await GriptapeNodes.ahandle_request(top_level_flow_request)
        if (
            isinstance(top_level_flow_result, GetTopLevelFlowResultSuccess)
            and top_level_flow_result.flow_name is not None
        ):
            flow_manager = GriptapeNodes.FlowManager()
            flow_obj = flow_manager.get_flow_by_name(top_level_flow_result.flow_name)
            context_manager.push_flow(flow_obj)


def execute_workflow(input: dict, *, workflow_executor: WorkflowExecutor | None = None, **kwargs: Any) -> dict | None:
    return asyncio.run(aexecute_workflow(input=input, workflow_executor=workflow_executor, **kwargs))


async def aexecute_workflow(
    input: dict, *, workflow_executor: WorkflowExecutor | None = None, **kwargs: Any
) -> dict | None:
    await build_workflow()
    await _ensure_workflow_context()
    if workflow_executor is None:
        kwargs.setdefault("pickle_control_flow_result", False)
        workflow_executor = LocalWorkflowExecutor(skip_library_loading=True, workflows_to_register=[__file__], **kwargs)
    async with workflow_executor as executor:
        await executor.arun(flow_input=input, **kwargs)
    return executor.output


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    LocalWorkflowExecutor.add_cli_arguments(parser, pickle_control_flow_result_default=False)
    parser.add_argument(
        "--json-input",
        default=None,
        help="JSON string containing parameter values. Takes precedence over individual parameter arguments if provided.",
    )
    parser.add_argument(
        "--exec_out", dest="exec_out", default=None, help="Connection to the next node in the execution chain"
    )
    parser.add_argument(
        "--structure_id", dest="structure_id", default=None, help="The structure ID of the published workflow"
    )
    parser.add_argument(
        "--structure_name", dest="structure_name", default=None, help="The name for the Griptape Cloud Structure."
    )
    parser.add_argument(
        "--structure_description",
        dest="structure_description",
        default=None,
        help="The description for the Griptape Cloud Structure.",
    )
    parser.add_argument(
        "--enable_webhook_integration",
        dest="enable_webhook_integration",
        default=None,
        help="Whether to enable a webhook integration for the Structure.",
    )
    parser.add_argument(
        "--webhook_url", dest="webhook_url", default=None, help="The webhook URL for the published workflow"
    )
    parser.add_argument(
        "--integration_id", dest="integration_id", default=None, help="The integration ID of the published workflow"
    )
    parser.add_argument("--payload", dest="payload", default=None, help="The payload for the webhook integration.")
    parser.add_argument(
        "--query_params", dest="query_params", default=None, help="The query parameters for the webhook integration."
    )
    parser.add_argument("--headers", dest="headers", default=None, help="The headers for the webhook integration.")
    parser.add_argument(
        "--custom_install_script_path",
        dest="custom_install_script_path",
        default=None,
        help="Path to a .sh file whose contents will be appended to the pre-build install script before publishing.",
    )
    parser.add_argument("--gpu", dest="gpu", default=None, help="Enable GPU support for the published structure.")
    parser.add_argument("--prompt", dest="prompt", default=None, help="New parameter")
    args = parser.parse_args()
    flow_input = {}
    if args.json_input is not None:
        flow_input = json.loads(args.json_input)
    if args.json_input is None:
        if "Griptape Cloud Start Flow" not in flow_input:
            flow_input["Griptape Cloud Start Flow"] = {}
        if args.exec_out is not None:
            flow_input["Griptape Cloud Start Flow"]["exec_out"] = args.exec_out
        if args.structure_id is not None:
            flow_input["Griptape Cloud Start Flow"]["structure_id"] = args.structure_id
        if args.structure_name is not None:
            flow_input["Griptape Cloud Start Flow"]["structure_name"] = args.structure_name
        if args.structure_description is not None:
            flow_input["Griptape Cloud Start Flow"]["structure_description"] = args.structure_description
        if args.enable_webhook_integration is not None:
            flow_input["Griptape Cloud Start Flow"]["enable_webhook_integration"] = args.enable_webhook_integration
        if args.webhook_url is not None:
            flow_input["Griptape Cloud Start Flow"]["webhook_url"] = args.webhook_url
        if args.integration_id is not None:
            flow_input["Griptape Cloud Start Flow"]["integration_id"] = args.integration_id
        if args.payload is not None:
            flow_input["Griptape Cloud Start Flow"]["payload"] = args.payload
        if args.query_params is not None:
            flow_input["Griptape Cloud Start Flow"]["query_params"] = args.query_params
        if args.headers is not None:
            flow_input["Griptape Cloud Start Flow"]["headers"] = args.headers
        if args.custom_install_script_path is not None:
            flow_input["Griptape Cloud Start Flow"]["custom_install_script_path"] = args.custom_install_script_path
        if args.gpu is not None:
            flow_input["Griptape Cloud Start Flow"]["gpu"] = args.gpu
        if args.prompt is not None:
            flow_input["Griptape Cloud Start Flow"]["prompt"] = args.prompt
    executor = LocalWorkflowExecutor.from_cli_args(args, skip_library_loading=True, workflows_to_register=[__file__])
    workflow_output = execute_workflow(input=flow_input, workflow_executor=executor)
    print(workflow_output)
