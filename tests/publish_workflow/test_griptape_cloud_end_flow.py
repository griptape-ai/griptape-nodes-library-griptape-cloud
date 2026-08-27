"""Tests for how the End Flow node tells an output file apart from output text in the cloud runtime.

Every string an End Flow parameter carries is a candidate file to upload, so the node resolves it and
asks the engine whether it exists. Text arrives on those parameters as often as paths do, and it
resolves to a path just as readily, so the values the OS cannot be asked about have to be recognized
as text before the question is put to it.

Only that judgement is exercised here; nothing is resolved or uploaded, so no Griptape Cloud API
calls are made.
"""

from pathlib import Path

import pytest

from griptape_cloud.publish_workflow.griptape_cloud_end_flow import (
    MAX_FILE_NAME_LENGTH,
    GriptapeCloudEndFlow,
)

# An answer of the shape a prompt node hands to an End Flow parameter, long enough to stand in for one.
GENERATED_TEXT = "# Cat\n\nA **cat** (*Felis catus*) is a small, domesticated carnivorous mammal.\n" * 4


def test_generated_text_does_not_name_a_file(tmp_path: Path) -> None:
    """Text on an output parameter is not treated as a candidate file.

    Text resolves to a path under the project directory the same way a file name does, and asking
    whether that path exists raises rather than answering. The error was reported against the
    workflow run, naming the whole of the generated answer as a file name too long.
    """
    assert len(GENERATED_TEXT) > MAX_FILE_NAME_LENGTH, "The value under test is short enough to name a file."
    with pytest.raises(OSError, match="File name too long"):
        (tmp_path / GENERATED_TEXT).exists()

    assert GriptapeCloudEndFlow._might_name_a_file(GENERATED_TEXT) is False


@pytest.mark.parametrize(
    "value",
    [
        "{outputs}/generated.png",
        "/structure/staging/griptape-nodes-outputs/generated.png",
        "generated.png",
    ],
    ids=["macro", "absolute path", "bare file name"],
)
def test_output_file_values_still_name_a_file(value: str) -> None:
    """The values that do name a file are still resolved and looked up."""
    assert GriptapeCloudEndFlow._might_name_a_file(value) is True
