"""Reusable ownership-check helper for per-user resource isolation.

Every route that resolves a row owned by a user (sessions now; documents and
messages in later sprints) must verify that row's `user_id` equals the JWT
subject before returning data (NFR-005). This is a single indexed primary-key
lookup plus an equality check -- O(1) relative to table size, comfortably
within NFR-016's tens-to-low-hundreds-of-users target.
"""

from __future__ import annotations

import uuid
from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")

_NOT_FOUND = HTTPException(status_code=404, detail="Not found.")


def get_owned_or_404(db: Session, model: type[ModelT], obj_id: uuid.UUID, user_id: uuid.UUID) -> ModelT:
    """Fetch ``model`` by primary key ``obj_id`` and ensure it belongs to ``user_id``.

    Raises 404 both when the row does not exist and when it exists but belongs
    to a different user, so an attacker cannot distinguish "not found" from
    "not yours" (AC-009).
    """
    obj = db.get(model, obj_id)
    if obj is None or getattr(obj, "user_id") != user_id:
        raise _NOT_FOUND
    return obj
