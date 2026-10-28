"""Generated routers: one per architecture component that owns endpoints.

Only `api_backend` owns HTTP endpoints in this architecture (the worker
consumes jobs, it does not serve routes), split here by resource for
readability: `auth` and `sessions` (the latter also carries the
session-nested documents and messages routes the API spec declares).
"""
