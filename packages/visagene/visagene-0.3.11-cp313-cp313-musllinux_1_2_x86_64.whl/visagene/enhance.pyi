from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import onnxruntime as onnxruntime
import os as os
import pixtreme as px
import tensorrt as trt
import typing
import visagene.base
from visagene.base import BaseModelLoader
__all__ = ['BaseFaceEnhance', 'BaseModelLoader', 'OnnxFaceEnhance', 'TrtFaceEnhance', 'cp', 'onnxruntime', 'os', 'px', 'trt']
class BaseFaceEnhance(visagene.base.BaseModelLoader):
    """
    
        Base class for face enhancement models.
    
        Improves face image quality by reducing artifacts, enhancing details,
        and restoring facial features using generative models like GFPGAN.
        
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def batch_get(self, images: list[cp.ndarray]) -> list[cp.ndarray]:
        """
        
                Process a batch of images for face enhancement.
        
                Args:
                    images (list[cp.ndarray]): List of input images.
        
                Returns:
                    list[cp.ndarray]: List of enhanced images.
                
        """
    def forward(self, batch: cp.ndarray) -> cp.ndarray:
        """
        
                Placeholder for the forward method.
                
        """
    def get(self, image: cp.ndarray) -> cp.ndarray:
        ...
class OnnxFaceEnhance(BaseFaceEnhance):
    """
    GFPGAN Face enhancer using ONNX Runtime for face quality improvement.
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def forward(self, batch: cp.ndarray) -> cp.ndarray:
        """
        
                Execute ONNX inference on a preprocessed batch.
        
                Args:
                    batch (cp.ndarray): Preprocessed batch tensor of shape (N, C, H, W).
        
                Returns:
                    cp.ndarray: Output tensor from the model.
                
        """
    def initialize(self, model_bytes: bytes, device: str, device_id: str = '0') -> None:
        ...
class TrtFaceEnhance(BaseFaceEnhance):
    """
    Face enhancer using TensorRT for high-performance face quality improvement.
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def forward(self, batch: cp.ndarray) -> cp.ndarray:
        """
        
                Execute TensorRT inference on a preprocessed batch.
        
                Args:
                    batch (cp.ndarray): Preprocessed batch tensor of shape (N, C, H, W).
        
                Returns:
                    cp.ndarray: Output tensor from the model.
                
        """
    def initialize(self, model_bytes: bytes) -> None:
        ...
__test__: dict = {}
