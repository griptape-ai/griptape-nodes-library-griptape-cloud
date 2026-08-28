"""Tests for the engine config and project template packaged alongside a published workflow.

The cloud worker runs the workflow with the config and project template written into the package, so
both have to describe the engine that published the workflow — including its project-adjacent and
workspace config layers — while leaving out the parts that only mean something on the publishing
machine. Directories on the publishing machine are the case that matters most: the cloud worker
shares none of them, and a project template that names one it cannot resolve is refused outright.

No Griptape Cloud API calls are made; only the config and template assembly is exercised, so no
structure is created and no package is built.
"""

import copy
import json
import logging
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from griptape_nodes.retained_mode.events.project_events import (
    LoadProjectTemplateRequest,
    LoadProjectTemplateResultSuccess,
    SetCurrentProjectRequest,
)
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes
from griptape_nodes.retained_mode.managers.config_manager import ConfigManager

from griptape_cloud.publish_workflow.griptape_cloud_publisher import (
    ENGINE_DISTRIBUTION_NAME,
    MACHINE_SPECIFIC_TEMPLATE_FIELDS,
    GriptapeCloudPublisher,
)

PACKAGED_TOP_LEVEL_DIR = "/structure"


def _load_project_adjacent_config(config_manager: ConfigManager, project_dir: Path, config: dict) -> None:
    """Write a project-adjacent config and merge it into the engine as the project layer."""
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "griptape_nodes_config.json").write_text(json.dumps(config), encoding="utf-8")
    config_manager.load_project_config(project_dir)


def _init_repo_with_a_commit(git_exe: str, repo_dir: Path) -> str:
    """Make repo_dir a git checkout holding one commit and no remotes, and return the commit.

    Identity and signing are passed per-command so the test does not depend on, or write to, the
    developer's git configuration.
    """
    config = ["-c", "user.email=tests@example.com", "-c", "user.name=Tests", "-c", "commit.gpgsign=false"]
    (repo_dir / "tracked.txt").write_text("tracked", encoding="utf-8")
    for args in (
        ["init", "--quiet"],
        ["add", "tracked.txt"],
        ["commit", "--quiet", "--message", "Initial commit"],
    ):
        subprocess.run([git_exe, "-C", str(repo_dir), *config, *args], check=True, capture_output=True)  # noqa: S603

    return (
        subprocess.check_output([git_exe, "-C", str(repo_dir), "rev-parse", "HEAD"])  # noqa: S603
        .decode()
        .strip()
    )


def _write_project(project_dir: Path, **fields: object) -> Path:
    """Write a project template file, filling in the fields every template must declare.

    The body is written as JSON, which is valid YAML and needs no dumper to quote paths correctly.
    """
    project_dir.mkdir(parents=True, exist_ok=True)
    project_file = project_dir / "project.yml"
    body = {
        "project_template_schema_version": "1.0.0",
        "name": project_dir.name,
        "situations": {},
        "directories": {},
        **fields,
    }
    project_file.write_text(json.dumps(body), encoding="utf-8")
    return project_file


def _activate_project_with_a_parent(tmp_path: Path) -> Path:
    """Make current a project that inherits from a parent, as a project on a developer's machine can.

    Returns the parent's file path, which the caller deletes to stand in for a cloud worker that has
    never seen it. The parent contributes an environment entry so a test can tell whether the
    packaged template kept what it inherited.
    """
    parent_file = _write_project(
        tmp_path / "parent",
        environment={"PUBLISHED_FROM_PARENT": "yes"},
        workspace_dir="./workspace",
    )
    child_file = _write_project(
        tmp_path / "child",
        parent_project_path=f"../{parent_file.parent.name}/{parent_file.name}",
        libraries_dir="./libraries",
    )

    load_result = GriptapeNodes.handle_request(LoadProjectTemplateRequest(project_path=child_file))
    assert isinstance(load_result, LoadProjectTemplateResultSuccess), f"Could not load project: {load_result}"
    activate_result = GriptapeNodes.handle_request(SetCurrentProjectRequest(project_id=load_result.project_id))
    assert activate_result.succeeded(), f"Could not activate project: {activate_result}"

    return parent_file


def test_packaged_config_carries_the_project_adjacent_layer(
    isolated_config_manager: ConfigManager, tmp_path: Path
) -> None:
    """A library setting made in a project-adjacent config reaches the cloud runtime.

    Packaging only the user config layer left the published workflow running on default settings,
    with nothing to indicate it was configured differently than it was locally.
    """
    _load_project_adjacent_config(
        isolated_config_manager,
        tmp_path / "project",
        {"griptape_cloud_library": {"GT_CLOUD_PUBLISH_DOWNLOAD_MODELS": False}},
    )

    config = GriptapeCloudPublisher._build_packaged_config([], PACKAGED_TOP_LEVEL_DIR)

    assert config["griptape_cloud_library"]["GT_CLOUD_PUBLISH_DOWNLOAD_MODELS"] is False


def test_packaged_config_leaves_out_keys_specific_to_the_publishing_machine(
    isolated_config_manager: ConfigManager, tmp_path: Path
) -> None:
    """Local project paths are not packaged; the cloud worker loads the bundled project template."""
    local_project_file = tmp_path / "project" / "project.yml"
    _load_project_adjacent_config(
        isolated_config_manager,
        tmp_path / "project",
        {
            "project_file": str(local_project_file),
            "project_workspaces": {str(local_project_file): str(tmp_path / "workspace")},
        },
    )
    assert "project_file" in isolated_config_manager.merged_config, (
        "The keys under test are not in the engine config, so this test would pass without dropping anything."
    )

    config = GriptapeCloudPublisher._build_packaged_config([], PACKAGED_TOP_LEVEL_DIR)

    assert "project_file" not in config
    assert "project_workspaces" not in config


def test_packaged_config_points_the_cloud_runtime_at_the_package() -> None:
    """The packaged config describes the cloud runtime rather than the publishing machine."""
    library_paths = [f"{PACKAGED_TOP_LEVEL_DIR}/libraries/griptape_nodes_library.json"]

    config = GriptapeCloudPublisher._build_packaged_config(library_paths, PACKAGED_TOP_LEVEL_DIR)

    assert config["workspace_directory"] == PACKAGED_TOP_LEVEL_DIR
    assert config["app_events"]["on_app_initialization_complete"]["libraries_to_register"] == library_paths
    assert config["app_events"]["on_app_initialization_complete"]["workflows_to_register"] == []
    assert config["enable_workspace_file_watching"] is False


def test_building_the_packaged_config_leaves_the_engine_config_alone(isolated_config_manager: ConfigManager) -> None:
    """Packaging a config does not reconfigure the engine doing the publishing.

    The config is assembled by overwriting entries, so it has to be a copy. Building it from the
    engine's own dictionaries pointed the running engine's workspace at the package directory and
    emptied the libraries and workflows it had registered.
    """
    user_config_before = copy.deepcopy(isolated_config_manager.user_config)
    merged_config_before = copy.deepcopy(isolated_config_manager.merged_config)

    GriptapeCloudPublisher._build_packaged_config([], PACKAGED_TOP_LEVEL_DIR)

    assert isolated_config_manager.user_config == user_config_before
    assert isolated_config_manager.merged_config == merged_config_before


def test_the_engine_distribution_is_found() -> None:
    """The engine's distribution is found under the name it is actually installed as.

    Publishing pins the engine in requirements.txt, and this lookup is what decides whether it is
    pinned by revision or by version number. A name matching no installed distribution is
    indistinguishable from a released install, so publishing from a checkout of an untagged revision
    pinned a version that does not exist and the deployment failed to build in the cloud.
    """
    dist = GriptapeCloudPublisher._find_griptape_nodes_distribution()

    assert dist is not None, f"No distribution named '{ENGINE_DISTRIBUTION_NAME}' is installed."
    assert dist.metadata["Name"] == ENGINE_DISTRIBUTION_NAME


def test_publishing_warns_when_the_pinned_commit_is_on_no_remote(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """A commit that exists only locally is called out before the cloud build fails on it.

    The published workflow installs the engine by checking the pinned commit out of the remote, so
    an unpushed commit fails the deployment build with the same opaque `git checkout` error that a
    version tag which was never cut did. A local warning costs a line; the build failure costs a
    round trip through the cloud to diagnose.
    """
    git_exe = shutil.which("git")
    assert git_exe is not None, "git is needed to resolve the engine revision publishing pins."
    commit = _init_repo_with_a_commit(git_exe, tmp_path)

    with caplog.at_level(logging.WARNING, logger="griptape_nodes"):
        GriptapeCloudPublisher._warn_if_commit_is_not_installable(git_exe, tmp_path, commit)

    assert "on no remote branch" in caplog.text
    assert commit in caplog.text


def test_publishing_warns_when_the_checkout_has_uncommitted_changes(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Changes that are not in the pinned commit do not reach the cloud, so they are called out.

    Untracked files are left out of the check: they are not part of the checkout, and warning on
    them would fire on every publish from a working directory.
    """
    git_exe = shutil.which("git")
    assert git_exe is not None, "git is needed to resolve the engine revision publishing pins."
    commit = _init_repo_with_a_commit(git_exe, tmp_path)
    (tmp_path / "tracked.txt").write_text("changed", encoding="utf-8")
    (tmp_path / "untracked.txt").write_text("new", encoding="utf-8")

    with caplog.at_level(logging.WARNING, logger="griptape_nodes"):
        GriptapeCloudPublisher._warn_if_commit_is_not_installable(git_exe, tmp_path, commit)

    assert "uncommitted changes" in caplog.text


@pytest.mark.usefixtures("isolated_config_manager")
def test_packaged_project_template_leaves_out_locations_from_the_publishing_machine(tmp_path: Path) -> None:
    """The packaged template names no directory and no parent from the machine that published it.

    What it inherited from its parent is kept, which is what makes dropping the parent link safe:
    the packaged template is the fully merged result, so the parent has nothing left to contribute.
    """
    _activate_project_with_a_parent(tmp_path)
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()

    GriptapeCloudPublisher._write_project_template(bundle_dir)

    written = yaml.safe_load((bundle_dir / "project.yml").read_text(encoding="utf-8"))
    assert set(written) & set(MACHINE_SPECIFIC_TEMPLATE_FIELDS) == set()
    assert written["environment"]["PUBLISHED_FROM_PARENT"] == "yes"


@pytest.mark.usefixtures("isolated_config_manager")
def test_packaged_project_template_loads_where_the_publishing_machine_is_not(tmp_path: Path) -> None:
    """The cloud worker can load and activate the packaged template with the parent nowhere in sight.

    Deleting the parent stands in for the cloud runtime, which has none of the publishing machine's
    projects. A packaged template that still declared its parent could not be loaded there at all,
    and the worker would run the workflow with no project and no situations.
    """
    parent_file = _activate_project_with_a_parent(tmp_path)
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    parent_file.unlink()

    GriptapeCloudPublisher._write_project_template(bundle_dir)

    load_result = GriptapeNodes.handle_request(LoadProjectTemplateRequest(project_path=bundle_dir / "project.yml"))
    assert isinstance(load_result, LoadProjectTemplateResultSuccess), (
        f"Could not load the packaged project template: {load_result}"
    )
    activate_result = GriptapeNodes.handle_request(SetCurrentProjectRequest(project_id=load_result.project_id))
    assert activate_result.succeeded(), f"Could not activate the packaged project template: {activate_result}"
