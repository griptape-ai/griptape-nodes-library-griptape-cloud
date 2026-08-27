"""WorkflowBuilder for generating a Griptape Nodes workflow that can invoke a published workflow in the form of a Griptape Cloud structure.

This module provides simple script generation for creating workflows that follow the pattern:
StartNode -> PublishedWorkflow -> EndNode

The generated workflows can execute published structures in Griptape Cloud using the
PublishedWorkflow node which handles parameter mapping automatically.
"""

import logging
import os
import subprocess
import sys
import uuid
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

from griptape_cloud_client.models.update_structure_response_content import UpdateStructureResponseContent
from griptape_nodes.retained_mode.events.node_events import SerializeNodeToCommandsResultSuccess
from griptape_nodes.retained_mode.events.parameter_events import AddParameterToNodeRequest
from griptape_nodes.retained_mode.events.project_events import (
    GetCurrentProjectRequest,
    GetCurrentProjectResultSuccess,
)
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

from griptape_cloud.publish_workflow.griptape_cloud_published_workflow import GriptapeCloudPublishedWorkflow
from griptape_cloud.publish_workflow.griptape_cloud_start_flow import GriptapeCloudStartFlow

logger = logging.getLogger("griptape_nodes")

# Prefix the generated script prints the saved workflow path with, so that the parent process
# learns where the workflow actually landed instead of guessing at the path.
SAVED_WORKFLOW_PATH_PREFIX = "GRIPTAPE_CLOUD_EXECUTOR_WORKFLOW_PATH="


@dataclass
class GriptapeCloudWebhookIntegration:
    integration_id: str
    webhook_url: str


@dataclass
class GriptapeCloudWorkflowBuilderInput:
    workflow_name: str
    workflow_shape: dict[str, Any]
    executor_workflow_name: str
    structure: UpdateStructureResponseContent
    webhook_integration: GriptapeCloudWebhookIntegration | None = None
    libraries: list[str] = field(default_factory=list)
    pickle_control_flow_result: bool = False
    griptape_cloud_start_flow_input: dict[str, Any] = field(default_factory=dict)
    griptape_cloud_start_flow_node_commands: SerializeNodeToCommandsResultSuccess | None = None
    unique_parameter_uuid_to_values: dict = field(default_factory=dict)


class GriptapeCloudWorkflowBuilder:
    """Builder class for generating executor workflows using simple script generation."""

    def __init__(
        self,
        workflow_builder_input: GriptapeCloudWorkflowBuilderInput,
    ) -> None:
        """Initialize the WorkflowBuilder.

        Args:
            workflow_builder_input: Configuration input for the workflow builder
        """
        self.workflow_builder_input = workflow_builder_input

    def generate_executor_workflow(self) -> Path:
        """Generate an executor workflow that can invoke the published structure."""
        project_file_path = self._get_current_project_file_path()

        # Generate a simple workflow creation script using PublishedWorkflow node
        workflow_script = self._build_simple_workflow_script(project_file_path)

        # Execute the script in a subprocess to create the workflow
        executor_workflow_path = self._execute_workflow_script(workflow_script)

        # Verify the workflow was created successfully
        if executor_workflow_path is None:
            executor_workflow_path = self._default_executor_workflow_path()
        if not executor_workflow_path.exists():
            error_msg = (
                f"Executor workflow {self.workflow_builder_input.executor_workflow_name} was not created successfully. "
                f"Expected it at {executor_workflow_path}."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # The engine re-registers the published workflow by file name against the workspace root,
        # so a workflow saved anywhere else will not be found again.
        workspace_path = GriptapeNodes.ConfigManager().workspace_path
        if executor_workflow_path.parent.resolve() != workspace_path:
            logger.warning(
                "Executor workflow was saved to %s, outside the workspace directory %s. It may not be registered.",
                executor_workflow_path,
                workspace_path,
            )

        return executor_workflow_path

    def _default_executor_workflow_path(self) -> Path:
        """Path the executor workflow is expected at when the subprocess did not report one."""
        return GriptapeNodes.ConfigManager().workspace_path / (
            self.workflow_builder_input.executor_workflow_name + ".py"
        )

    def _get_current_project_file_path(self) -> Path | None:
        """Get the file path of the project active in this engine, if it has one.

        The subprocess needs the same project as its parent so that the workspace directory
        and the `save_workflow` situation resolve identically in both processes. Without it the
        subprocess falls back to user-level config and saves the executor workflow somewhere
        the parent is not looking for it.
        """
        current_project_result = GriptapeNodes.handle_request(GetCurrentProjectRequest())
        if not isinstance(current_project_result, GetCurrentProjectResultSuccess):
            logger.warning(
                "Could not retrieve the current project: %s. The executor workflow will be generated without one.",
                current_project_result,
            )
            return None

        project_file_path = current_project_result.project_info.project_file_path
        if project_file_path is None:
            logger.debug("The current project is not backed by a file on disk; none will be passed to the subprocess.")
        return project_file_path

    def _build_library_registration_script(self, libraries: list[str]) -> str:
        """Build a script to register libraries for the workflow.

        Args:
            libraries: List of library paths to register

        Returns:
            Complete Python script as string
        """
        if not libraries:
            return ""

        # Build the library registration script
        script = ""

        for i, lib in enumerate(libraries):
            if lib.endswith(".json"):
                script += f"""
    request_{i!s} = GriptapeNodes.handle_request(RegisterLibraryFromFileRequest(file_path={lib!r}))
"""
            else:
                script += f"""
    request_{i!s} = GriptapeNodes.handle_request(RegisterLibraryFromRequirementSpecifierRequest(requirement_specifier={lib!r}))
"""
        return script

    def _extract_parameters_from_shape(self, workflow_shape: dict[str, Any]) -> tuple[list[dict], list[dict]]:
        """Extract input and output parameters from workflow shape.

        Args:
            workflow_shape: The workflow shape containing input/output parameter structure

        Returns:
            Tuple of (input_params, output_params)
        """
        input_params = []
        if "input" in workflow_shape:
            for node_params in workflow_shape["input"].values():
                if isinstance(node_params, dict):
                    input_params.extend(node_params.values())

        output_params = []
        if "output" in workflow_shape:
            for node_params in workflow_shape["output"].values():
                if isinstance(node_params, dict):
                    output_params.extend(node_params.values())

        return input_params, output_params

    def _build_project_activation_script(self, project_file_path: Path | None) -> str:
        """Build a script to load and activate the parent engine's project.

        The project must be activated before libraries are registered so that nodes which
        resolve situations during init see the project's definitions, and so that the
        `save_workflow` situation resolves to the same directory the parent engine uses.

        Args:
            project_file_path: Path to the parent engine's project file, if it has one

        Returns:
            Project activation script as string
        """
        if project_file_path is None:
            return ""

        return f"""
    project_result = GriptapeNodes.handle_request(LoadProjectTemplateRequest(project_path=Path({str(project_file_path)!r})))
    if isinstance(project_result, LoadProjectTemplateResultSuccess):
        activate_result = GriptapeNodes.handle_request(SetCurrentProjectRequest(project_id=project_result.project_id))
        if activate_result.failed():
            print(f"Failed to activate project {str(project_file_path)!r}: {{activate_result}}")
    else:
        print(f"Failed to load project {str(project_file_path)!r}: {{project_result}}")
"""

    def _build_script_header(self, libraries: list[str], project_file_path: Path | None) -> str:
        """Build the header section of the workflow script.

        Args:
            libraries: List of libraries needed for the workflow
            project_file_path: Path to the parent engine's project file, if it has one

        Returns:
            Script header as string
        """
        return f'''
"""
Generated executor workflow for invoking published Griptape Cloud structure.
This workflow was automatically created to execute structure: {self.workflow_builder_input.structure.structure_id}
"""

from pathlib import Path

from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes
from griptape_nodes.retained_mode.events.flow_events import CreateFlowRequest
from griptape_nodes.retained_mode.events.node_events import CreateNodeRequest
from griptape_nodes.retained_mode.events.library_events import (
    RegisterLibraryFromFileRequest,
    RegisterLibraryFromRequirementSpecifierRequest,
)
from griptape_nodes.retained_mode.events.parameter_events import (
    AddParameterToNodeRequest,
    SetParameterValueRequest,
)
from griptape_nodes.retained_mode.events.project_events import (
    LoadProjectTemplateRequest,
    LoadProjectTemplateResultSuccess,
    SetCurrentProjectRequest,
)
from griptape_nodes.retained_mode.events.connection_events import CreateConnectionRequest
from griptape_nodes.retained_mode.events.workflow_events import SaveWorkflowRequest

def main():
    {self._build_project_activation_script(project_file_path)}
    {self._build_library_registration_script(libraries)}

    context_manager = GriptapeNodes.ContextManager()
    if not context_manager.has_current_workflow():
        context_manager.push_workflow(workflow_name="{self.workflow_builder_input.executor_workflow_name}")

    # Create the main flow
    flow_response = GriptapeNodes.handle_request(CreateFlowRequest(parent_flow_name=None))
    flow_name = flow_response.flow_name

    with GriptapeNodes.ContextManager().flow(flow_name):'''

    def _build_node_creation_script(self) -> str:
        """Build the node creation section of the workflow script.

        Args:
            structure_id: The Griptape Cloud structure ID
            workflow_shape: Input/output parameter structure

        Returns:
            Node creation script as string
        """
        return f"""
        # Create StartNode
        start_node_response = GriptapeNodes.handle_request(CreateNodeRequest(
            node_type="GriptapeCloudStartFlow",
            specific_library_name="Griptape Cloud Library",
            node_name="Griptape Cloud Start Flow",
            metadata={{
                "structure_id": "{self.workflow_builder_input.structure.structure_id}",
                "structure_name": "{self.workflow_builder_input.structure.name}",
                "structure_description": "{self.workflow_builder_input.structure.description}",
                "integration_id": "{self.workflow_builder_input.webhook_integration.integration_id if self.workflow_builder_input.webhook_integration else None}",
                "webhook_url": "{self.workflow_builder_input.webhook_integration.webhook_url if self.workflow_builder_input.webhook_integration else None}",
                "hide_structure_config": {True}
            }},
            initial_setup=True
        ))
        start_node_name = start_node_response.node_name

        # Create GriptapeCloudPublishedWorkflow node
        published_wf_response = GriptapeNodes.handle_request(CreateNodeRequest(
            node_type="GriptapeCloudPublishedWorkflow",
            specific_library_name="Griptape Cloud Library",
            node_name="Griptape Cloud Published Workflow",
            metadata={{
                "workflow_shape": {self.workflow_builder_input.workflow_shape!r},
                "structure_id": "{self.workflow_builder_input.structure.structure_id}",
                "structure_name": "{self.workflow_builder_input.structure.name}",
                "structure_description": "{self.workflow_builder_input.structure.description}",
                "integration_id": "{self.workflow_builder_input.webhook_integration.integration_id if self.workflow_builder_input.webhook_integration else None}",
                "webhook_url": "{self.workflow_builder_input.webhook_integration.webhook_url if self.workflow_builder_input.webhook_integration else None}",
            }},
            initial_setup=True
        ))
        published_wf_name = published_wf_response.node_name

        # Create EndNode
        end_node_response = GriptapeNodes.handle_request(CreateNodeRequest(
            node_type="GriptapeCloudEndFlow",
            specific_library_name="Griptape Cloud Library",
            node_name="Griptape Cloud End Flow",
            initial_setup=True
        ))
        end_node_name = end_node_response.node_name"""

    def _build_parameter_configuration_script(self, input_params: list[dict], output_params: list[dict]) -> str:
        """Build the parameter configuration section of the workflow script.

        Args:
            input_params: List of input parameter configurations
            output_params: List of output parameter configurations

        Returns:
            Parameter configuration script as string
        """
        script = """

        # Configure StartNode parameters
        with GriptapeNodes.ContextManager().node(start_node_name):"""

        script += self._build_node_parameters(
            input_params,
            "GriptapeCloudStartNode",
            mode_input=False,
            mode_property=True,
            mode_output=True,
            omit_parameters=GriptapeCloudStartFlow.get_default_node_parameter_names(),
        )

        script += """

        # Configure GriptapeCloudPublishedWorkflow parameters
        with GriptapeNodes.ContextManager().node(published_wf_name):"""

        script += self._build_node_parameters(
            input_params,
            "GriptapeCloudPublishedWorkflow input",
            mode_input=True,
            mode_property=True,
            mode_output=False,
            omit_parameters=GriptapeCloudPublishedWorkflow.get_default_node_parameter_names(),
        )
        script += self._build_node_parameters(
            output_params,
            "GriptapeCloudPublishedWorkflow output",
            mode_input=False,
            mode_property=True,
            mode_output=True,
            omit_parameters=GriptapeCloudPublishedWorkflow.get_default_node_parameter_names(),
        )

        script += """

        # Configure EndNode parameters
        with GriptapeNodes.ContextManager().node(end_node_name):"""

        script += self._build_node_parameters(
            output_params,
            "GriptapeCloudEndNode",
            mode_input=True,
            mode_property=True,
            mode_output=False,
            omit_parameters=["was_successful", "result_details", "exec_in", "failed"],
        )

        return script

    def _build_node_parameters(
        self,
        params: list[dict],
        _node_type: str,
        *,
        mode_input: bool,
        mode_property: bool,
        mode_output: bool,
        omit_parameters: list[str] | None = None,
    ) -> str:
        """Build parameter configuration for a specific node.

        Args:
            params: List of parameter configurations
            _node_type: Type of node (for documentation purposes)
            mode_input: Whether input mode is allowed
            mode_property: Whether property mode is allowed
            mode_output: Whether output mode is allowed
            omit_parameters: List of parameter names to omit from configuration

        Returns:
            Parameter configuration script as string
        """
        if omit_parameters is None:
            omit_parameters = []

        # Check if there are any parameters left after omitting
        param_names = {param["name"] for param in params}
        remaining_params = param_names - set(omit_parameters)

        if len(remaining_params) == 0:
            return """
            pass
        """

        # Get supported fields from AddParameterToNodeRequest dataclass
        # Exclude mode_allowed_* fields since they are passed explicitly below
        supported_fields = {f.name for f in fields(AddParameterToNodeRequest)} - {
            "mode_allowed_input",
            "mode_allowed_property",
            "mode_allowed_output",
        }

        script = ""
        for param in params:
            param_name = param.get("name")
            if param_name not in omit_parameters:
                # Build param_config with only fields supported by AddParameterToNodeRequest
                param_config = {k: v for k, v in param.items() if k in supported_fields}
                param_config["parameter_name"] = param_name
                script += f"""
            GriptapeNodes.handle_request(AddParameterToNodeRequest(
                **{param_config},
                mode_allowed_input={mode_input},
                mode_allowed_property={mode_property},
                mode_allowed_output={mode_output},
                initial_setup=True
            ))"""
        return script

    def _build_connection_creation_script(self, input_params: list[dict], output_params: list[dict]) -> str:
        """Build the connection creation section of the workflow script.

        Args:
            input_params: List of input parameter configurations
            output_params: List of output parameter configurations

        Returns:
            Connection creation script as string
        """
        script = """

    # Create connections between StartNode and GriptapeCloudPublishedWorkflow"""

        # Add connections for each input parameter
        for param in input_params:
            script += f"""
    GriptapeNodes.handle_request(CreateConnectionRequest(
        source_node_name=start_node_name,
        source_parameter_name="{param["name"]}",
        target_node_name=published_wf_name,
        target_parameter_name="{param["name"]}",
        initial_setup=True
    ))"""

        script += """

    # Create connections between GriptapeCloudPublishedWorkflow and EndNode"""

        # Add connections for each output parameter
        for param in output_params:
            if param["name"] not in ["exec_out", "failure"]:
                script += f"""
    GriptapeNodes.handle_request(CreateConnectionRequest(
        source_node_name=published_wf_name,
        source_parameter_name="{param["name"]}",
        target_node_name=end_node_name,
        target_parameter_name="{param["name"]}",
        initial_setup=True
    ))"""

        control_flow: dict = {"exec_out": "exec_in", "failure": "failed"}
        for key, val in control_flow.items():
            script += f"""
    GriptapeNodes.handle_request(CreateConnectionRequest(
        source_node_name=published_wf_name,
        source_parameter_name="{key}",
        target_node_name=end_node_name,
        target_parameter_name="{val}",
        initial_setup=True
    ))"""

        return script

    def _build_start_flow_value_script(self) -> str:
        """Build a script section that persists GriptapeCloudStartFlow parameter values on the generated start flow node."""
        commands = self.workflow_builder_input.griptape_cloud_start_flow_node_commands
        if commands is None:
            return ""

        script = """

    # Set parameter values for Griptape Cloud Start Flow
    unique_values_dict = """ + repr(self.workflow_builder_input.unique_parameter_uuid_to_values)

        items = dict(self.workflow_builder_input.griptape_cloud_start_flow_input)
        for param in GriptapeCloudStartFlow.get_default_node_parameter_names():
            if param in {"exec_in", "exec_out", "failed", "was_successful", "result_details"}:
                continue
            if param not in items:
                items[param] = None

        for param_name, param_value in items.items():
            for command in commands.set_parameter_value_commands:
                if command.set_parameter_value_command.parameter_name == param_name:
                    script += f"""
    GriptapeNodes.handle_request(SetParameterValueRequest(
        node_name=start_node_name,
        parameter_name="{param_name}",
        value=unique_values_dict.get({command.unique_value_uuid!r}, {param_value!r}),
        initial_setup=True
    ))"""

        return script

    def _build_script_footer(self) -> str:
        """Build the footer section of the workflow script.

        Returns:
            Script footer as string
        """
        return f"""

    # Save the workflow
    save_response = GriptapeNodes.handle_request(SaveWorkflowRequest(
        file_name="{self.workflow_builder_input.executor_workflow_name}",
        pickle_control_flow_result={self.workflow_builder_input.pickle_control_flow_result}))

    if save_response.succeeded():
        # Report the saved path so the parent process does not have to guess at it.
        print(f"{SAVED_WORKFLOW_PATH_PREFIX}{{save_response.file_path}}")
        print(f"Successfully created executor workflow: {self.workflow_builder_input.executor_workflow_name}")
    else:
        print(f"Failed to create executor workflow")
        exit(1)

if __name__ == "__main__":
    main()
"""

    def _build_simple_workflow_script(
        self,
        project_file_path: Path | None = None,
    ) -> str:
        """Build a simple workflow creation script using PublishedWorkflow node.

        Args:
            project_file_path: Path to the parent engine's project file, if it has one

        Returns:
            Complete Python script as string
        """
        # Extract parameters from workflow shape
        input_params, output_params = self._extract_parameters_from_shape(self.workflow_builder_input.workflow_shape)

        # Build script sections
        header = self._build_script_header(self.workflow_builder_input.libraries, project_file_path)
        nodes = self._build_node_creation_script()
        params = self._build_parameter_configuration_script(input_params, output_params)
        connections = self._build_connection_creation_script(input_params, output_params)
        start_flow_values = self._build_start_flow_value_script()
        footer = self._build_script_footer()

        return header + nodes + params + connections + start_flow_values + footer

    def _execute_workflow_script(self, script: str) -> Path | None:
        """Execute the workflow creation script in a subprocess.

        Returns:
            The path the subprocess saved the executor workflow to, or None if it did not report one.
        """
        temp_script_path = Path(__file__).parent / f"temp_executor_{uuid.uuid4().hex}.py"

        try:
            with temp_script_path.open("w", encoding="utf-8") as f:
                f.write(script)

            # Execute the script in a subprocess to isolate the GriptapeNodes state. The subprocess
            # does not run engine app initialization, so it cannot derive the workspace directory
            # from anything but user config; pass it explicitly so both processes agree on it.
            subprocess_env = os.environ | {
                "GTN_CONFIG_WORKSPACE_DIRECTORY": str(GriptapeNodes.ConfigManager().workspace_path),
                "GTN_CONFIG_ENABLE_WORKSPACE_FILE_WATCHING": "false",
            }
            result = subprocess.run(  # noqa: S603
                [sys.executable, str(temp_script_path)],
                capture_output=True,
                text=True,
                cwd=temp_script_path.parent,
                timeout=300,
                env=subprocess_env,
                check=False,
            )

            # Print subprocess output
            if result.stdout:
                logger.debug(result.stdout)
            if result.stderr:
                logger.debug(result.stderr)

            if result.returncode != 0:
                error_msg = f"Executor workflow generation failed: {result.stderr}"
                logger.error("Failed to generate executor workflow: %s", result.stderr)
                raise RuntimeError(error_msg)

            saved_workflow_path = self._parse_saved_workflow_path(result.stdout)
            if saved_workflow_path is None:
                logger.warning(
                    "Executor workflow subprocess did not report where it saved the workflow. Subprocess output: %s %s",
                    result.stdout,
                    result.stderr,
                )

            logger.info(
                "Successfully generated executor workflow: %s", self.workflow_builder_input.executor_workflow_name
            )

            return saved_workflow_path

        finally:
            # Clean up temporary script
            if temp_script_path.exists():
                temp_script_path.unlink()

    def _parse_saved_workflow_path(self, stdout: str) -> Path | None:
        """Extract the path the subprocess saved the executor workflow to from its output."""
        for line in reversed(stdout.splitlines()):
            if line.startswith(SAVED_WORKFLOW_PATH_PREFIX):
                return Path(line.removeprefix(SAVED_WORKFLOW_PATH_PREFIX).strip())
        return None
