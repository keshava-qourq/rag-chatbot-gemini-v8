"""Exercises app.storage against whichever backend is configured.

No mocks: when S3_BUCKET is set (the sandbox, every real deployment) this
writes to and reads from the real bucket and cleans up after itself; when it
is unset (a bare local clone) it round-trips through MEDIA_ROOT instead.
"""

from app import storage


def test_save_load_delete_round_trip() -> None:
    key = storage.make_key("test-session", "roundtrip.txt")
    payload = b"hello from the toolchain prep ticket"

    storage.save(key, payload, content_type="text/plain")
    try:
        assert storage.load(key) == payload
        assert storage.url(key)
    finally:
        storage.delete(key)
