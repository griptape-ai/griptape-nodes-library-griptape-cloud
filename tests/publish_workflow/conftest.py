"""Shared fixtures for the publish workflow tests."""

from collections.abc import Iterator

import pytest
from griptape_nodes.retained_mode.events.project_events import (
    GetCurrentProjectRequest,
    GetCurrentProjectResultSuccess,
    SetCurrentProjectRequest,
)
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes
from griptape_nodes.retained_mode.managers.config_manager import ConfigManager
from griptape_nodes.retained_mode.managers.settings import PROJECTS_TO_REGISTER_KEY


@pytest.fixture
def isolated_config_manager(monkeypatch: pytest.MonkeyPatch) -> Iterator[ConfigManager]:
    """Keep engine state these tests touch out of the developer's real configuration.

    A workspace directory in the environment outranks every config layer, including the runtime
    override these tests rely on, so it is removed. Loading a project template persists the
    project's path to the user config, so the original list is restored afterwards. The engine is a
    singleton shared by every test in the process, so the current project is restored too; a project
    left active would silently become the project the next test reads or the next subprocess
    inherits. Clearing the config layers on the way out restores the state the engine boots with
    under pytest, which registers no project of its own.
    """
    monkeypatch.delenv("GTN_CONFIG_WORKSPACE_DIRECTORY", raising=False)

    config_manager = GriptapeNodes.ConfigManager()
    original_projects = config_manager.get_config_value(key=PROJECTS_TO_REGISTER_KEY, default=[])
    original_project_result = GriptapeNodes.handle_request(GetCurrentProjectRequest())

    yield config_manager

    if isinstance(original_project_result, GetCurrentProjectResultSuccess):
        GriptapeNodes.handle_request(
            SetCurrentProjectRequest(project_id=original_project_result.project_info.project_id)
        )
    config_manager.clear_project_layers()
    config_manager.load_configs()
    config_manager.set_workspace_override(None)
    config_manager.set_config_value(key=PROJECTS_TO_REGISTER_KEY, value=original_projects)
