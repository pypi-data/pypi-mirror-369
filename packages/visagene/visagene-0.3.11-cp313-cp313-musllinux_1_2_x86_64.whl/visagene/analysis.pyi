from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import numpy as np
import onnxruntime as onnxruntime
import pixtreme as px
import typing
import visagene.base
from visagene.base import BaseModelLoader
from visagene.schema import VisageneFace
__all__ = ['BaseFaceAnalysis', 'BaseModelLoader', 'OnnxFaceAnalysis', 'VisageneFace', 'cp', 'np', 'onnxruntime', 'px']
class BaseFaceAnalysis(visagene.base.BaseModelLoader):
    """
    
        Base class for face analysis models.
    
        Analyzes faces to extract attributes such as gender and age.
        
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def forward(self, face_image: cp.ndarray) -> cp.ndarray:
        """
        
                Placeholder for the forward method.
                Must be implemented by subclasses.
        
                Args:
                    face_image: Face image as CuPy array
        
                Returns:
                    Model output as CuPy array
                
        """
    def get(self, face: VisageneFace) -> tuple[int, int]:
        """
        
                Get gender and age attributes for a face.
        
                Args:
                    image: Original image (not used in base implementation, kept for compatibility)
                    face: Face object containing the cropped face image
        
                Returns:
                    Tuple of (gender, age) where gender: 0=Female, 1=Male
                
        """
class OnnxFaceAnalysis(BaseFaceAnalysis):
    """
    
        ONNX-based face analysis implementation.
    
        Uses ONNX Runtime for inference on gender and age prediction models.
        
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def forward(self, face_image: cp.ndarray) -> cp.ndarray:
        """
        
                Run forward pass on face image.
        
                Args:
                    face_image: Face image as CuPy array (H, W, C) in range [0, 1]
        
                Returns:
                    Model output as CuPy array [female_score, male_score, age_normalized]
                
        """
    def initialize(self, model_bytes: bytes, device: str, device_id: str = '0') -> None:
        """
        Initialize ONNX Runtime session.
        """
__test__: dict = {}
