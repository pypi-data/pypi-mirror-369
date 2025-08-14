from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import onnx as onnx
import onnxruntime as onnxruntime
import os as os
import pixtreme as px
import typing
import visagene.base
from visagene.base import BaseModelLoader
from visagene.emap import load_emap
from visagene.schema import VisageneFace
__all__ = ['BaseFaceFeatureExtractor', 'BaseModelLoader', 'OnnxFaceFeatureExtractor', 'TrtFaceFeatureExtractor', 'VisageneFace', 'cp', 'load_emap', 'onnx', 'onnxruntime', 'os', 'px']
class BaseFaceFeatureExtractor(visagene.base.BaseModelLoader):
    """
    
        Base class for face feature extraction models.
    
        Extracts facial embeddings/features from face images for recognition,
        comparison, and identity-based operations like face swapping.
        
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def forward(self, images: cp.ndarray | list[cp.ndarray]) -> cp.ndarray:
        """
        
                Placeholder for the forward method.
                
        """
    def get(self, face) -> cp.ndarray:
        """
        
                Extract embedding for a single face.
                Common implementation shared by Onnx and Trt versions.
                
        """
class OnnxFaceFeatureExtractor(BaseFaceFeatureExtractor):
    """
    Face feature extractor using ONNX Runtime for inference.
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def forward(self, images: cp.ndarray | list[cp.ndarray]) -> cp.ndarray:
        ...
    def get(self, face: VisageneFace) -> cp.ndarray:
        """
        Extract embedding for a single face
        """
    def initialize(self, model_bytes: bytes, device: str, device_id: str = '0') -> None:
        ...
class TrtFaceFeatureExtractor(BaseFaceFeatureExtractor):
    """
    Face feature extractor using TensorRT for high-performance inference.
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def forward(self, images: cp.ndarray | list[cp.ndarray]) -> cp.ndarray:
        """
        Forward pass using TensorRT
        """
    def get(self, face: VisageneFace) -> cp.ndarray:
        """
        Extract embedding for a single face
        """
    def initialize(self, model_bytes: bytes, device: str, device_id: str) -> None:
        ...
__test__: dict = {}
