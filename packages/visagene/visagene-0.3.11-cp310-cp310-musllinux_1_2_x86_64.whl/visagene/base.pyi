from __future__ import annotations
import builtins as __builtins__
import typing
__all__ = ['BaseModelLoader']
class BaseModelLoader:
    """
    Common base class for model loading and device management.
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
__test__: dict = {}
