"""Tests for executor workflow generation.

The builder generates the executor workflow in a subprocess. The subprocess does not run engine
app initialization, so it only agrees with its parent on where to save the workflow if the parent
tells it: the project to activate and the workspace directory to use. These tests pin the parent's
workspace somewhere other than the developer's own workspace and assert the workflow lands there.

No Griptape Cloud API calls are made; only the structure metadata the generated script embeds is
needed, so a stand-in structure is enough.
"""

import datetime
import json
from pathlib import Path

import pytest
from griptape_cloud_client.models.default_structure_code import DefaultStructureCode
from griptape_cloud_client.models.structure_code_type_2 import StructureCodeType2
from griptape_cloud_client.models.update_structure_response_content import UpdateStructureResponseContent
from griptape_nodes.retained_mode.events.project_events import (
    GetCurrentProjectRequest,
    GetCurrentProjectResultSuccess,
    LoadProjectTemplateRequest,
    LoadProjectTemplateResultSuccess,
    SetCurrentProjectRequest,
)
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes
from griptape_nodes.retained_mode.managers.config_manager import ConfigManager

from griptape_cloud.publish_workflow.griptape_cloud_workflow_builder import (
    SAVED_WORKFLOW_PATH_PREFIX,
    GriptapeCloudWorkflowBuilder,
    GriptapeCloudWorkflowBuilderInput,
)

LIBRARY_ROOT = Path(__file__).parents[2]


@pytest.fixture
def builder_input() -> GriptapeCloudWorkflowBuilderInput:
    """Builder input for a minimal published workflow, with a stand-in structure."""
    timestamp = datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC)
    structure = UpdateStructureResponseContent(
        code=StructureCodeType2(default=DefaultStructureCode()),
        created_at=timestamp,
        created_by="test",
        description="Test structure",
        env_vars=[],
        latest_deployment_id="d-1",
        name="Test Structure",
        organization_id="o-1",
        structure_id="s-1",
        updated_at=timestamp,
        webhook_enabled=False,
    )
    workflow_shape = {
        "input": {"Griptape Cloud Start Flow": {"payload": {"name": "payload", "type": "json", "tooltip": ""}}},
        "output": {"Griptape Cloud End Flow": {"output": {"name": "output", "type": "str", "tooltip": ""}}},
    }
    return GriptapeCloudWorkflowBuilderInput(
        workflow_name="test_workflow",
        workflow_shape=workflow_shape,
        executor_workflow_name="test_workflow_executor",
        structure=structure,
        libraries=[str(LIBRARY_ROOT / "griptape_nodes_library.json")],
    )


def _activate_project(project_dir: Path, workspace: Path) -> None:
    """Write a project that declares its own workspace, then make it the current project."""
    project_file = project_dir / "project.yml"
    project_file.write_text(
        "\n".join(
            [
                'project_template_schema_version: "1.0.0"',
                'name: "Test Project"',
                'description: "Declares its own workspace directory"',
                f"workspace_dir: {json.dumps(str(workspace))}",
            ]
        ),
        encoding="utf-8",
    )

    load_result = GriptapeNodes.handle_request(LoadProjectTemplateRequest(project_path=project_file))
    assert isinstance(load_result, LoadProjectTemplateResultSuccess), f"Could not load project: {load_result}"
    activate_result = GriptapeNodes.handle_request(SetCurrentProjectRequest(project_id=load_result.project_id))
    assert activate_result.succeeded(), f"Could not activate project: {activate_result}"


def test_executor_workflow_saved_in_active_project_workspace(
    isolated_config_manager: ConfigManager,
    builder_input: GriptapeCloudWorkflowBuilderInput,
    tmp_path: Path,
) -> None:
    """The executor workflow lands in the workspace the active project declares."""
    project_dir = tmp_path / "project"
    workspace = project_dir / "workspace"
    workspace.mkdir(parents=True)
    _activate_project(project_dir, workspace)

    assert isolated_config_manager.workspace_path == workspace.resolve(), (
        "The project did not take effect, so this test would pass without generating anything in the right place."
    )

    executor_workflow_path = GriptapeCloudWorkflowBuilder(builder_input).generate_executor_workflow()

    assert executor_workflow_path.exists()
    assert executor_workflow_path == workspace.resolve() / "test_workflow_executor.py"


def test_executor_workflow_saved_in_overridden_workspace_without_a_project(
    isolated_config_manager: ConfigManager,
    builder_input: GriptapeCloudWorkflowBuilderInput,
    tmp_path: Path,
) -> None:
    """The executor workflow lands in the parent's workspace even when no project file is involved.

    This is the common case: no project of the developer's own, just whatever workspace the engine
    resolved. The subprocess cannot see a runtime override, so the workspace has to be passed to it.
    """
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    isolated_config_manager.set_workspace_override(workspace)
    assert isolated_config_manager.workspace_path == workspace.resolve()

    current_project = GriptapeNodes.handle_request(GetCurrentProjectRequest())
    assert isinstance(current_project, GetCurrentProjectResultSuccess)
    assert current_project.project_info.project_file_path is None, (
        "A project is active, so the subprocess could resolve the workspace from it instead."
    )

    executor_workflow_path = GriptapeCloudWorkflowBuilder(builder_input).generate_executor_workflow()

    assert executor_workflow_path.exists()
    assert executor_workflow_path == workspace.resolve() / "test_workflow_executor.py"


def test_generated_script_activates_the_current_project(builder_input: GriptapeCloudWorkflowBuilderInput) -> None:
    """The generated script activates the project it was given, and compiles either way."""
    project_file = Path("/projects/test/project.yml")

    with_project = GriptapeCloudWorkflowBuilder(builder_input)._build_simple_workflow_script(project_file)
    compile(with_project, "<generated>", "exec")
    assert "handle_request(LoadProjectTemplateRequest" in with_project
    assert str(project_file) in with_project

    without_project = GriptapeCloudWorkflowBuilder(builder_input)._build_simple_workflow_script(None)
    compile(without_project, "<generated>", "exec")
    assert "handle_request(LoadProjectTemplateRequest" not in without_project


@pytest.mark.parametrize(
    ("stdout", "expected"),
    [
        (f"noise\n{SAVED_WORKFLOW_PATH_PREFIX}/workspace/executor.py\nmore noise\n", Path("/workspace/executor.py")),
        ("nothing to report\n", None),
    ],
)
def test_parse_saved_workflow_path(
    builder_input: GriptapeCloudWorkflowBuilderInput, stdout: str, expected: Path | None
) -> None:
    """The path the subprocess reports is read back out of its output."""
    assert GriptapeCloudWorkflowBuilder(builder_input)._parse_saved_workflow_path(stdout) == expected
