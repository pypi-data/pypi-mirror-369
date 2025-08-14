from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import pixtreme as px
__all__ = ['PasteBack', 'cp', 'paste_back', 'px']
class PasteBack:
    def __init__(self, blursize: float = 1.0):
        ...
    def create_mask(self, size: tuple):
        ...
    def get(self, target_image: cp.ndarray, paste_image: cp.ndarray, M: cp.ndarray) -> cp.ndarray:
        ...
def paste_back(target_image: cp.ndarray, paste_image: cp.ndarray, M: cp.ndarray, mask: cp.ndarray = None) -> cp.ndarray:
    ...
__test__: dict = {}
