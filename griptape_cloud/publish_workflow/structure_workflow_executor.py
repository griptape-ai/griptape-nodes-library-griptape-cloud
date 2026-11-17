import json
import os

from griptape.artifacts import TextArtifact
from griptape.drivers.event_listener.griptape_cloud_event_listener_driver import GriptapeCloudEventListenerDriver
from griptape.events import FinishStructureRunEvent
from griptape_nodes.bootstrap.workflow_executors.local_workflow_executor import LocalWorkflowExecutor

# Names the run of the engine that started this structure run, so the published workflow's spend
# counts toward it. Sent as an environment variable rather than an argument: a structure published
# before this variable existed ignores it, where it would refuse an argument it doesn't know.
PARENT_RUN_ID_ENV_VAR = "GTN_PARENT_RUN_ID"


def parent_run_id_from_env() -> str | None:
    """The starting engine's run id, or None when the structure run was started without one."""
    return os.environ.get(PARENT_RUN_ID_ENV_VAR) or None


class StructureWorkflowExecutor(LocalWorkflowExecutor):
    def _submit_output(self, output: dict) -> None:
        if "GT_CLOUD_STRUCTURE_RUN_ID" in os.environ:
            kwargs: dict = {
                "batched": False,
            }
            if "GT_CLOUD_BASE_URL" in os.environ:
                base_url = os.environ["GT_CLOUD_BASE_URL"]
                if "http://localhost" in base_url or "http://127.0.0.1" in base_url:
                    kwargs["headers"] = {}
            gtc_event_listener = GriptapeCloudEventListenerDriver(**kwargs)
            gtc_event_listener.try_publish_event_payload(
                FinishStructureRunEvent(output_task_output=TextArtifact(json.dumps(output))).to_dict()
            )
