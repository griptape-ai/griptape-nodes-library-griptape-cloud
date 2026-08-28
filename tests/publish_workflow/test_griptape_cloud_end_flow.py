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
    MAX_PATH_LENGTH,
    GriptapeCloudEndFlow,
)

# An answer of the shape a prompt node hands to an End Flow parameter, long enough to stand in for one.
GENERATED_TEXT = "# Cat\n\nA **cat** (*Felis catus*) is a small, domesticated carnivorous mammal.\n" * 4

# The same, written the way generated prose usually is: full of slashes, so that no single
# `/`-separated run of it is long enough to name a file even though the whole is far too long to be
# a path. Markdown links, dates, units and "and/or" all put slashes in ordinary output.
GENERATED_TEXT_WITH_SLASHES = "Cats weigh 4/5 kg, live 12/18 years, and hunt day and/or night. " * 20

# The largest path limit across the platforms the engine runs on: 1024 on macOS, 4096 on Linux. The
# guard is set to the smallest of them, so it rejects values shorter than this that the local OS
# would still answer about; text has to be longer than this to be refused wherever the test runs.
LONGEST_PLATFORM_PATH_LENGTH = 4096

TEXT_SHAPES = pytest.mark.parametrize(
    "text",
    [GENERATED_TEXT, GENERATED_TEXT_WITH_SLASHES],
    ids=["one long component", "many short components"],
)


@TEXT_SHAPES
def test_generated_text_cannot_be_looked_up(text: str) -> None:
    """Text on an output parameter is not treated as a candidate file, however it is punctuated.

    Text resolves to a path under the project directory the same way a file name does, and asking
    whether that path exists raises rather than answering. The error was reported against the
    workflow run, naming the whole of the generated answer as a file name too long. Slashes in the
    text keep every component short while the path as a whole stays far too long, so a per-component
    limit alone lets the same failure through.
    """
    assert not GriptapeCloudEndFlow._can_be_looked_up(text)


@TEXT_SHAPES
def test_the_os_refuses_the_paths_the_guard_rejects(text: str, tmp_path: Path) -> None:
    """Refusing to look a path up is standing in for a real refusal, whatever the punctuation.

    The text is repeated past the largest limit any of the platforms enforces so that the refusal is
    demonstrated wherever the test runs. The realistic lengths above are rejected by the guard well
    before this point, which is the margin the guard is deliberately carrying.
    """
    over_long = text * (1 + LONGEST_PLATFORM_PATH_LENGTH // len(text))

    assert not GriptapeCloudEndFlow._can_be_looked_up(over_long)
    with pytest.raises(OSError, match=r"[Ff]ile name too long"):
        (tmp_path / over_long).exists()


def test_the_length_limits_are_the_ones_the_os_enforces(tmp_path: Path) -> None:
    """Each limit is low enough that the OS still answers, and no lower than it has to be.

    A limit set too high leaves the reported failure reachable; one set too low silently skips
    uploading files with legitimately long names.
    """
    longest_name = tmp_path / ("n" * MAX_FILE_NAME_LENGTH)
    assert GriptapeCloudEndFlow._can_be_looked_up(str(longest_name))
    assert not longest_name.exists(), "The OS answered rather than raising, so the name limit holds."

    over_by_one = tmp_path / ("n" * (MAX_FILE_NAME_LENGTH + 1))
    assert not GriptapeCloudEndFlow._can_be_looked_up(str(over_by_one))
    assert MAX_PATH_LENGTH > MAX_FILE_NAME_LENGTH, "A path holds at least one name."


@pytest.mark.parametrize(
    "value",
    [
        "{outputs}/generated.png",
        "/structure/staging/griptape-nodes-outputs/generated.png",
        "generated.png",
    ],
    ids=["macro", "absolute path", "bare file name"],
)
def test_output_file_values_can_still_be_looked_up(value: str) -> None:
    """The values that do name a file are still resolved and looked up."""
    assert GriptapeCloudEndFlow._can_be_looked_up(value)


def test_looking_up_an_over_long_path_reports_no_file(tmp_path: Path) -> None:
    """Asking whether an over-long path is a file is answered, not raised.

    The engine's request handler catches whatever a handler raises, logs it as an unhandled
    exception against the request, and returns a failure. Sending it a path the OS refuses is
    therefore reported to the user as a workflow error even though the caller recovers, so the
    request has to not be sent at all.
    """
    assert GriptapeCloudEndFlow._is_existing_file(tmp_path / GENERATED_TEXT_WITH_SLASHES) is False


def test_looking_up_a_real_file_finds_it(tmp_path: Path) -> None:
    """A file that exists is still found, so the guards did not swallow the case that matters."""
    output_file = tmp_path / "generated.png"
    output_file.write_bytes(b"")

    assert GriptapeCloudEndFlow._is_existing_file(output_file) is True
    assert GriptapeCloudEndFlow._is_existing_file(tmp_path / "absent.png") is False
