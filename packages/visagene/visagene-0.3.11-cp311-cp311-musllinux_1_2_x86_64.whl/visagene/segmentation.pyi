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
__all__ = ['BaseFaceSegmentation', 'BaseModelLoader', 'OnnxFaceSegmentation', 'TrtFaceSegmentation', 'cp', 'onnxruntime', 'os', 'px', 'trt']
class BaseFaceSegmentation(visagene.base.BaseModelLoader):
    """
    
        Base class for face segmentation models.
    
        Segments facial regions like eyes, nose, mouth, and skin
        to enable targeted operations like face swapping and enhancement.
        
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def batch_get(self, images: list[cp.ndarray], MAX_BATCH_SIZE: int = 16) -> list[cp.ndarray]:
        """
        
                Face segmentation inference method.
                Common implementation shared by Onnx and Trt versions.
                Supports batch processing for multiple images.
                
        """
    def composite_masks(self, preds: cp.ndarray) -> cp.ndarray:
        """
        
                Composite masks into a single image.
                
        """
    def forward(self, batch: cp.ndarray) -> cp.ndarray:
        """
        
                Placeholder for the forward method.
                
        """
    def get(self, image: cp.ndarray) -> cp.ndarray:
        """
        
                Face segmentation method for a single image.
                
        """
    def init_indexes(self, indexes: list) -> None:
        ...
class OnnxFaceSegmentation(BaseFaceSegmentation):
    """
    Face segmentation using ONNX Runtime for inference.
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def forward(self, batch: cp.ndarray) -> cp.ndarray:
        ...
    def initialize(self, model_bytes: bytes, device: str, device_id: str = '0') -> None:
        ...
class TrtFaceSegmentation(BaseFaceSegmentation):
    """
    Face segmentation using TensorRT for high-performance inference.
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def forward(self, batch: cp.ndarray) -> cp.ndarray:
        """
        Forward pass using TensorRT
        """
    def initialize(self, model_bytes: bytes, device: str, device_id: str) -> None:
        ...
__test__: dict = {}
