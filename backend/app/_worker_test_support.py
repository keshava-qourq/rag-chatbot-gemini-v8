"""A trivial job body used only by tests/integration/test_worker_entrypoint.py.

Needs to be importable by both the test process and a real `rq worker`
subprocess spawned in a separate process, so it lives as a plain module-level
function rather than inside the test file itself.
"""

from pathlib import Path


def write_marker(path: str) -> None:
    Path(path).write_text("done")
