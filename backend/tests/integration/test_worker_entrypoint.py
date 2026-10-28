"""Integration tests for the container entrypoint (backend/scripts/start.sh).

Covers:
- AC-038: the entrypoint/CMD runs uvicorn and an RQ worker on the 'documents'
  queue concurrently.
- AC-039: a job enqueued on the real Redis 'documents' queue is picked up and
  processed by a worker started the same way the entrypoint starts it, with no
  manual intervention beyond starting the worker process.
- AC-040: if either process exits, the entrypoint propagates that exit status
  rather than leaving the container looking healthy with only the other
  process still running.
"""

from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

import redis
from rq import Queue

from app.config import REDIS_URL

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
START_SH = BACKEND_DIR / "scripts" / "start.sh"
DOCKERFILE = BACKEND_DIR / "Dockerfile"


def test_ac038_entrypoint_runs_uvicorn_and_worker_on_documents_queue_concurrently() -> None:
    script = START_SH.read_text()

    assert "rq worker documents" in script
    assert "uvicorn app.main:app" in script
    # Both are backgrounded (concurrent), not run sequentially one after another.
    assert "&" in script
    assert "wait -n" in script
    assert "alembic upgrade head" in script

    dockerfile = DOCKERFILE.read_text()
    assert "start.sh" in dockerfile
    # The old single-process CMD must be gone.
    assert 'CMD ["sh", "-c", "alembic upgrade head && uvicorn' not in dockerfile


def test_ac039_job_enqueued_on_documents_queue_is_picked_up_by_a_running_worker(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "marker.txt"
    conn = redis.from_url(REDIS_URL)
    queue = Queue("documents", connection=conn)

    job = queue.enqueue(
        "app._worker_test_support.write_marker",
        str(marker),
        job_id=f"test-ac039-{uuid.uuid4()}",
    )

    # Run a worker the same way the entrypoint does (`rq worker documents --url
    # $REDIS_URL`), but in burst mode so the test process does not hang forever;
    # burst mode still drains and processes every currently-queued job, which is
    # exactly what "picked up and processed... without manual intervention"
    # means. A generous timeout: other integration tests may leave slow,
    # failing jobs (real S3/Gemini calls with retries) on the same queue.
    env = dict(os.environ)
    env["REDIS_URL"] = REDIS_URL
    result = subprocess.run(
        [sys.executable, "-m", "rq.cli", "worker", "documents", "--burst", "--url", REDIS_URL],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert marker.read_text() == "done"
    assert job.get_status(refresh=True) in ("finished", None)


def _write_stub(path: Path, body: str) -> None:
    path.write_text(f"#!/usr/bin/env bash\n{body}\n")
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def test_ac040_a_crashing_worker_makes_the_entrypoint_exit_with_its_status() -> None:
    """Stubs stand in for alembic/uvicorn/rq so this runs without a real DB/queue.

    The rq stub exits non-zero immediately (simulating a worker crash); the
    uvicorn stub sleeps, simulating the API staying up. The entrypoint must not
    silently keep running with just the API alive -- it must exit with the
    worker's status. `exec sleep` (rather than a shell that backgrounds a
    child) so killing the stub's pid terminates the sleep directly, with no
    orphaned grandchild left holding the test's stdout/stderr pipe open.
    """
    with tempfile.TemporaryDirectory() as stub_dir_str:
        stub_dir = Path(stub_dir_str)
        _write_stub(stub_dir / "alembic", "exit 0")
        _write_stub(stub_dir / "uvicorn", "exec sleep 60")
        _write_stub(stub_dir / "rq", "exit 7")

        env = dict(os.environ)
        env["PATH"] = f"{stub_dir}:{env['PATH']}"
        env["REDIS_URL"] = "redis://stub:6379/0"

        start = time.monotonic()
        result = subprocess.run(
            ["bash", str(START_SH)],
            cwd=BACKEND_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=20,
        )
        elapsed = time.monotonic() - start

        assert result.returncode == 7, result.stdout + result.stderr
        # The failure is visible in the logs, not silently absorbed.
        assert "exited with status 7" in result.stderr
        # It should not have waited out the uvicorn stub's full 60s sleep: the
        # entrypoint kills the survivor once the other process has exited.
        assert elapsed < 15


def test_ac040_a_crashing_api_makes_the_entrypoint_exit_with_its_status() -> None:
    with tempfile.TemporaryDirectory() as stub_dir_str:
        stub_dir = Path(stub_dir_str)
        _write_stub(stub_dir / "alembic", "exit 0")
        _write_stub(stub_dir / "uvicorn", "exit 3")
        _write_stub(stub_dir / "rq", "exec sleep 60")

        env = dict(os.environ)
        env["PATH"] = f"{stub_dir}:{env['PATH']}"
        env["REDIS_URL"] = "redis://stub:6379/0"

        result = subprocess.run(
            ["bash", str(START_SH)],
            cwd=BACKEND_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=20,
        )

        assert result.returncode == 3, result.stdout + result.stderr
        assert "exited with status 3" in result.stderr
