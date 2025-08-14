from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import onnxruntime as onnxruntime
import os as os
import pixtreme as px
import typing
import visagene.base
from visagene.base import BaseModelLoader
__all__ = ['BaseFaceSwap', 'BaseModelLoader', 'OnnxFaceSwap', 'TrtFaceSwap', 'cp', 'onnxruntime', 'os', 'px']
class BaseFaceSwap(visagene.base.BaseModelLoader):
    """
    
        Base class for face swapping models.
    
        Performs face identity transfer by swapping facial features
        from a source identity onto a target face image.
        
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def forward(self, batch: cp.ndarray, latent: cp.ndarray) -> cp.ndarray:
        """
        
                Placeholder for the forward method.
                
        """
    def get(self, target_image: cp.ndarray, latent: cp.ndarray) -> cp.ndarray:
        """
        
                Inference with TensorRT face swap model.
                
        """
class OnnxFaceSwap(BaseFaceSwap):
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def batch_get(self, target_images: list[cp.ndarray], latent: cp.ndarray | list[cp.ndarray], max_batch: int = 16) -> list[cp.ndarray]:
        """
        
                Face swap inference method using the new TrtSwap-compatible interface.
                
        """
    def forward(self, batch: cp.ndarray, latent: cp.ndarray) -> cp.ndarray:
        """
        Forward pass using ONNX
        """
    def initialize(self, model_bytes: bytes, device: str, device_id: str = '0') -> None:
        ...
class TrtFaceSwap(BaseFaceSwap):
    """
    Face swapper using TensorRT for high-performance face identity transfer.
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def batch_get(self, target_images: list[cp.ndarray], latent: cp.ndarray | list[cp.ndarray], max_batch: int = 16) -> list[cp.ndarray]:
        """
        
                Inference with TensorRT face swap model.
                
        """
    def forward(self, batch: cp.ndarray, latent: cp.ndarray) -> cp.ndarray:
        """
        Forward pass using TensorRT
        """
    def initialize(self, model_bytes: bytes, device: str, device_id: str) -> None:
        ...
__test__: dict = {}
