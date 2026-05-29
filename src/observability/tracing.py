"""Langfuse observability — no-ops gracefully when LANGFUSE_PUBLIC_KEY is absent."""
from __future__ import annotations
import os
from contextlib import nullcontext

try:
    from langfuse import propagate_attributes
except ImportError:
    def propagate_attributes(**_kwargs):
        return nullcontext()

_client = None


def get_langfuse():
    global _client
    if _client is not None:
        return _client
    if not os.environ.get("LANGFUSE_PUBLIC_KEY"):
        return None
    try:
        from langfuse import Langfuse
        _client = Langfuse(
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            secret_key=os.environ["LANGFUSE_SECRET_KEY"],
            host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        )
    except ImportError:
        pass
    return _client
