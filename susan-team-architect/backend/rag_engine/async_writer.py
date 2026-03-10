# rag_engine/async_writer.py
"""Async batch writer for chunk inserts.

Accumulates chunks in an internal buffer and flushes them to a
caller-supplied *store_fn* either when the buffer reaches *batch_size*
or when :meth:`flush` is called explicitly.
"""
from __future__ import annotations

import atexit
import threading
from typing import Callable


class AsyncBatchWriter:
    """Accumulates chunks and flushes in configurable batches.

    Parameters
    ----------
    store_fn:
        Callable that receives ``list[dict]`` and returns the count of
        successfully written chunks.
    batch_size:
        Number of chunks that triggers an automatic flush.
    flush_interval:
        Reserved for future periodic-flush support (seconds).
    """

    def __init__(
        self,
        store_fn: Callable[[list[dict]], int],
        batch_size: int = 100,
        flush_interval: float = 5.0,
    ):
        self._store_fn = store_fn
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._buffer: list[dict] = []
        self._lock = threading.Lock()
        self._total_written = 0
        self._total_errors = 0
        self._closed = False
        atexit.register(self.flush)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, chunk: dict) -> None:
        """Append a chunk; auto-flush when batch_size is reached."""
        with self._lock:
            self._buffer.append(chunk)
            if len(self._buffer) >= self._batch_size:
                self._flush_locked()

    def flush(self) -> int:
        """Force-flush the current buffer regardless of size."""
        with self._lock:
            return self._flush_locked()

    def stats(self) -> dict:
        """Return writer statistics."""
        with self._lock:
            return {
                "buffered": len(self._buffer),
                "total_written": self._total_written,
                "total_errors": self._total_errors,
            }

    def close(self) -> None:
        """Flush remaining chunks and unregister the atexit hook."""
        self.flush()
        try:
            atexit.unregister(self.flush)
        except Exception:
            pass
        self._closed = True

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "AsyncBatchWriter":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _flush_locked(self) -> int:
        """Flush while the lock is already held."""
        if not self._buffer:
            return 0
        batch = self._buffer[:]
        self._buffer.clear()
        try:
            count = self._store_fn(batch)
            self._total_written += count
            return count
        except Exception:
            self._total_errors += 1
            return 0
