#!/usr/bin/env bash
# Container entrypoint: runs the schema migration once, then the API and the
# RQ worker for the 'documents' queue concurrently, both logging to
# stdout/stderr. If either process exits -- crash or otherwise -- the other is
# killed and this script exits with the first process's status, so the
# container actually stops instead of looking healthy with only one process
# left running (AC-038/AC-039/AC-040).
set -uo pipefail

alembic upgrade head
migrate_status=$?
if [ "$migrate_status" -ne 0 ]; then
  echo "start.sh: alembic upgrade head failed with status $migrate_status" >&2
  exit "$migrate_status"
fi

rq worker documents --url "$REDIS_URL" &
worker_pid=$!

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
api_pid=$!

# Waits for whichever of the two exits first and captures its exit status.
wait -n "$worker_pid" "$api_pid"
exit_code=$?

if ! kill -0 "$worker_pid" 2>/dev/null; then
  echo "start.sh: the RQ worker exited with status $exit_code" >&2
else
  echo "start.sh: the API server exited with status $exit_code" >&2
fi

# Do not leave the surviving process running once its sibling has died.
kill "$worker_pid" "$api_pid" 2>/dev/null
wait "$worker_pid" "$api_pid" 2>/dev/null

exit "$exit_code"
