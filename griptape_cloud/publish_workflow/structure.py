import argparse
import json
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

LIBRARIES = ["REPLACE_LIBRARIES"]
PICKLE_DEFAULT = "REPLACE_PICKLE_DEFAULT"
WEBHOOK_MODE_ARGS_COUNT = 4
START_FLOW_NODE_NAME = "Griptape Cloud Start Flow"


logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger("griptape_nodes")

load_dotenv()

workspace_dir = Path(__file__).parent

os.environ["GTN_CONFIG_STORAGE_BACKEND"] = "gtc"
os.environ["GTN_ENABLE_WORKSPACE_FILE_WATCHING"] = "false"
os.environ["GTN_CONFIG_WORKSPACE_DIRECTORY"] = str(workspace_dir)
os.environ.setdefault("CC", shutil.which("gcc") or shutil.which("cc") or "/usr/bin/gcc")


def _apply_init_patch() -> None:
    """Temp fix for infinite recursion during GriptapeNodes initialization.

    Two bugs compound:
    1. SingletonMeta saves the instance only AFTER __init__ completes, so any call
       to get_instance() during __init__ tries to create a new instance → recursion.
    2. SecretsManager.get_secret() eagerly evaluates str(self.workspace_env_path) as
       a label string when building the search_order list, which calls ProjectManager(),
       which calls get_instance() before _project_manager is assigned → recursion.

    Patch 1: Save the singleton instance early (before __init__ completes) so that
    recursive get_instance() calls return the partial instance instead of recursing.

    Patch 2: workspace_env_path falls back to config_manager when _project_manager
    isn't ready yet (AttributeError), so get_secret() can finish without recursing.
    """
    from griptape_nodes.retained_mode.managers.secrets_manager import SecretsManager
    from griptape_nodes.utils.metaclasses import SingletonMeta

    def _patched_singleton_call(cls: type, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            instance = cls.__new__(cls, *args, **kwargs)
            cls._instances[cls] = instance
            try:
                instance.__init__(*args, **kwargs)
            except Exception:
                del cls._instances[cls]
                raise
        return cls._instances[cls]

    SingletonMeta.__call__ = _patched_singleton_call

    original_workspace_env_path = SecretsManager.workspace_env_path.fget

    def _safe_workspace_env_path(self: SecretsManager) -> Path:
        try:
            return original_workspace_env_path(self)  # type: ignore[misc]  # temp patch: fget may be None per property typing
        except AttributeError:
            # _project_manager not assigned yet during __init__; derive path from config
            ws = Path(self.config_manager.merged_config.get("workspace_directory", ".")).resolve()
            return ws / ".env"

    SecretsManager.workspace_env_path = property(_safe_workspace_env_path)  # type: ignore[misc]  # temp patch: monkey-patching read-only property


def _set_libraries(libraries: list[str]) -> None:
    from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes
    from griptape_nodes.retained_mode.managers.settings import LIBRARIES_TO_REGISTER_KEY

    config_manager = GriptapeNodes.ConfigManager()
    config_manager.set_config_value(
        key="enable_workspace_file_watching",
        value=False,
    )
    config_manager.set_config_value(
        key="workspace_directory",
        value=str(workspace_dir),
    )
    config_manager.set_config_value(
        key=LIBRARIES_TO_REGISTER_KEY,
        value=libraries,
    )


def _parse_webhook_args(raw_body: str, query_params_json: str, headers_json: str) -> tuple[dict, bool]:
    """Parse webhook arguments into flow input and pickle flag.

    Args:
        raw_body: The raw webhook body as a string
        query_params_json: Query parameters as a JSON string
        headers_json: Headers as a JSON string

    Returns:
        A tuple of (flow_input dict, pickle_result bool)
    """
    try:
        body_data = json.loads(raw_body) if raw_body else {}
    except json.JSONDecodeError:
        body_data = {"raw_body": raw_body}

    try:
        query_params = json.loads(query_params_json) if query_params_json else {}
    except json.JSONDecodeError:
        query_params = {}

    try:
        headers = json.loads(headers_json) if headers_json else {}
    except json.JSONDecodeError:
        headers = {}

    flow_input = {
        START_FLOW_NODE_NAME: {
            "payload": body_data,
            "query_params": query_params,
            "headers": headers,
        }
    }

    pickle_result = False

    return flow_input, pickle_result


def _parse_argparse_args() -> tuple[dict, bool]:
    """Parse command-line arguments using argparse.

    Returns:
        A tuple of (flow_input dict, pickle_result bool)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        default=None,
        help="The input to the flow",
    )
    parser.add_argument(
        "--pickle-control-flow-result",
        action="store_true",
        default=PICKLE_DEFAULT,
        help="Whether to pickle the control flow result",
    )

    args = parser.parse_args()
    flow_input_str = args.input
    pickle_result = args.pickle_control_flow_result

    try:
        flow_input = json.loads(flow_input_str) if flow_input_str else {}
    except json.JSONDecodeError as e:
        msg = f"Error decoding JSON input: {e}"
        logger.info(msg)
        raise

    return flow_input, pickle_result


def _load_project_template(project_path: Path) -> None:
    """Load and activate a project template before libraries are registered.

    The project template must be active before libraries so that nodes which
    resolve situations during init (e.g. save_node_output) see the template's
    definitions, including the metadata sidecar directory.
    """
    from griptape_nodes.retained_mode.events.project_events import (
        LoadProjectTemplateRequest,
        LoadProjectTemplateResultSuccess,
        SetCurrentProjectRequest,
    )
    from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

    load_result = GriptapeNodes.handle_request(LoadProjectTemplateRequest(project_path=project_path))
    if not isinstance(load_result, LoadProjectTemplateResultSuccess):
        logger.warning("Failed to load project template from %s: %s", project_path, load_result)
        return
    set_result = GriptapeNodes.handle_request(SetCurrentProjectRequest(project_id=load_result.project_id))
    if set_result.failed():
        logger.warning("Failed to set project as current: %s", set_result)
        return
    logger.info("Loaded and activated project template from %s", project_path)


# Patch singleton + secrets initialization order bug before triggering GriptapeNodes init
_apply_init_patch()

# Load project template before libraries so that situations are available
# during node initialization.
_project_file = workspace_dir / "project.yml"
if _project_file.exists():
    _load_project_template(_project_file)

# Set libraries before importing workflow so that library reloading
# happens before the workflow is loaded
_set_libraries(LIBRARIES)

from griptape_nodes.drivers.storage import StorageBackend  # noqa: E402
from structure_workflow_executor import StructureWorkflowExecutor  # noqa: E402
from workflow import execute_workflow  # type: ignore[attr-defined]  # noqa: E402

if __name__ == "__main__":
    if len(sys.argv) == WEBHOOK_MODE_ARGS_COUNT and not any(arg.startswith("-") for arg in sys.argv[1:]):
        raw_body = sys.argv[1]
        query_params_json = sys.argv[2]
        headers_json = sys.argv[3]
        flow_input, pickle_result = _parse_webhook_args(raw_body, query_params_json, headers_json)
    else:
        flow_input, pickle_result = _parse_argparse_args()

    workflow_file_path = Path(__file__).parent / "workflow.py"
    workflow_runner = StructureWorkflowExecutor(
        storage_backend=StorageBackend("gtc"),
        skip_library_loading=True,
        workflows_to_register=[workflow_file_path.as_posix()],
    )

    execute_workflow(input=flow_input, workflow_executor=workflow_runner, pickle_control_flow_result=pickle_result)
