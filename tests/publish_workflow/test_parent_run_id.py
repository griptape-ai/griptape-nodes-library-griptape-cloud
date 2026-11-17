"""Tests for how a published workflow's structure run counts its spend toward the run that started it.

The Griptape Cloud Published Workflow node names its own workflow run on the structure run it
starts, as an environment variable, and the published structure's entry point hands that id to its
executor. An environment variable rather than an argument, because a structure published before
this existed parses its arguments strictly and would refuse one it doesn't know; it ignores an
environment variable instead.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from griptape_cloud_client.models.create_structure_run_request_content import CreateStructureRunRequestContent
from griptape_cloud_client.types import UNSET
from griptape_nodes.exe_types.core_types import Parameter
from griptape_nodes.exe_types.node_types import aprocess_scope
from griptape_nodes.retained_mode.events.budget_events import RunAttribution

import griptape_cloud.publish_workflow as publish_workflow_package
from griptape_cloud.publish_workflow.griptape_cloud_published_workflow import GriptapeCloudPublishedWorkflow
from griptape_cloud.publish_workflow.structure_workflow_executor import PARENT_RUN_ID_ENV_VAR

PUBLISH_WORKFLOW_DIR = Path(publish_workflow_package.__file__).parent
WORKFLOW_SHAPE = {"input": {"Griptape Cloud Start Flow": {"prompt": {}}}, "output": {}}
# Starting the engine in a fresh process takes a few seconds; this leaves room for a slow CI runner.
ENTRY_POINT_TIMEOUT_SECONDS = 120


def _run_node(monkeypatch: pytest.MonkeyPatch, run: RunAttribution | None) -> CreateStructureRunRequestContent:
    """Run the node against stubbed Griptape Cloud calls and return the structure run request it sent."""
    node = GriptapeCloudPublishedWorkflow(
        name="Published Workflow",
        metadata={"structure_id": "structure-1", "workflow_shape": WORKFLOW_SHAPE},
    )
    # Publishing adds a parameter for each of the workflow's inputs to the node it generates.
    node.add_parameter(Parameter(name="prompt", type="str"))
    node.set_parameter_value("prompt", "a cat")
    sent: list[CreateStructureRunRequestContent] = []

    def call_api(_endpoint: Any, _expected_type: type, action: str, **kwargs: Any) -> Any:
        assert action == "create structure run"
        sent.append(kwargs["body"])
        return SimpleNamespace(structure_run_id="structure-run-1")

    monkeypatch.setattr(node, "_call_api", call_api)
    monkeypatch.setattr(node, "_wait_for_latest_structure_deployment", lambda **_: None)
    monkeypatch.setattr(node, "_poll_structure_run_events", lambda **_: iter([]))
    monkeypatch.setattr(
        node,
        "_get_structure_run",
        lambda **_: SimpleNamespace(structure_run_id="structure-run-1", status="SUCCEEDED", output=UNSET),
    )

    with aprocess_scope(node=node, run=run):
        node._process()

    assert node.get_parameter_value("was_successful"), node.get_parameter_value("result_details")
    assert len(sent) == 1
    return sent[0]


def test_the_structure_run_names_the_run_that_started_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """The node's own run id rides on the structure run, and its arguments are the ones they always were.

    The arguments are unchanged so that a structure published before this, which parses them
    strictly, still runs.
    """
    body = _run_node(monkeypatch, RunAttribution(run_id="run-1", workflow="Parent"))

    request = body.to_dict()
    assert request["env_vars"] == [{"name": PARENT_RUN_ID_ENV_VAR, "value": "run-1"}]
    assert request["args"] == ["-i", json.dumps({"Griptape Cloud Start Flow": {"prompt": "a cat"}})]


def test_a_node_outside_a_run_names_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """A node that isn't executing for a workflow run starts the structure run with no environment."""
    body = _run_node(monkeypatch, None)

    assert "env_vars" not in body.to_dict()


def _run_entry_point(tmp_path: Path, env_overrides: dict[str, str]) -> dict[str, Any]:
    """Run the published structure's entry point as Griptape Cloud would, and report what its executor got.

    The packaged `structure.py` and `structure_workflow_executor.py` run unchanged, in a process of
    their own: the entry point patches engine singletons at import, which must not leak into this
    test process. `workflow.py`, which publishing generates, is replaced by one that prints the
    executor's parent run id instead of running a flow.
    """
    package_dir = tmp_path / "package"
    package_dir.mkdir()
    for name in ("structure.py", "structure_workflow_executor.py"):
        shutil.copy(PUBLISH_WORKFLOW_DIR / name, package_dir / name)
    (package_dir / "workflow.py").write_text(
        "import json\n"
        "def execute_workflow(input, workflow_executor, pickle_control_flow_result):\n"
        "    print('EXECUTOR ' + json.dumps({'parent_run_id': workflow_executor._parent_run_id}))\n"
    )

    env = {key: value for key, value in os.environ.items() if not key.startswith("GTN_")}
    env.pop(PARENT_RUN_ID_ENV_VAR, None)
    # Keep the engine's user config and data, which starting it writes, out of the developer's own.
    env["XDG_CONFIG_HOME"] = str(tmp_path / "config")
    env["XDG_DATA_HOME"] = str(tmp_path / "data")
    env.update(env_overrides)

    completed = subprocess.run(  # noqa: S603
        [sys.executable, "structure.py", "-i", "{}"],
        cwd=package_dir,
        env=env,
        capture_output=True,
        text=True,
        timeout=ENTRY_POINT_TIMEOUT_SECONDS,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    lines = [line for line in completed.stdout.splitlines() if line.startswith("EXECUTOR ")]
    assert len(lines) == 1, completed.stdout
    return json.loads(lines[0].removeprefix("EXECUTOR "))


def test_the_entry_point_hands_the_parent_run_to_its_executor(tmp_path: Path) -> None:
    """The structure's executor counts the workflow's spend toward the run named on the structure run."""
    executor = _run_entry_point(tmp_path, {PARENT_RUN_ID_ENV_VAR: "run-1"})

    assert executor == {"parent_run_id": "run-1"}


def test_the_entry_point_runs_without_a_parent_run(tmp_path: Path) -> None:
    """A structure run started without a parent, such as from a webhook, keeps its own run ids."""
    executor = _run_entry_point(tmp_path, {})

    assert executor == {"parent_run_id": None}
