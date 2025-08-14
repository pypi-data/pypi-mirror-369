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
from visagene.schema import VisageneFace
__all__ = ['BaseFaceDetection', 'BaseModelLoader', 'OnnxFaceDetection', 'TrtFaceDetection', 'VisageneFace', 'cp', 'onnxruntime', 'os', 'px', 'trt']
class BaseFaceDetection(visagene.base.BaseModelLoader):
    """
    
        Base class for face detection models.
    
        Detects faces in images and returns bounding boxes, keypoints,
        and confidence scores for identified faces.
        
    """
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def crop(self, image: cp.ndarray, kps: cp.ndarray, size: int = 512, padding: float = 0.0, normalize_rotation: bool = True) -> tuple[cp.ndarray, cp.ndarray]:
        """
        Crop face image using keypoints with optional padding and rotation normalization
        
                Args:
                    image: Input image
                    kps: Keypoints for face alignment
                    size: Target output size
                    padding: Padding ratio (0.0 to 1.0) to include more context around the face
                    normalize_rotation: If False, preserves original face rotation
        
                Returns:
                    Cropped face image and transformation matrix
                
        """
    def crop_from_kps_with_padding(self, image: cp.ndarray, kps: cp.ndarray, size: int = 512, padding: float = 0.0, normalize_rotation: bool = True) -> tuple[cp.ndarray, cp.ndarray]:
        """
        Crop face image using keypoints with padding support
        
                This is a custom implementation that supports padding by scaling the destination points
                
        """
    def distance2bbox(self, points: cp.ndarray, distance: cp.ndarray, max_shape = None) -> cp.ndarray:
        """
        Convert distance predictions to bounding boxes
        """
    def distance2kps(self, points: cp.ndarray, distance: cp.ndarray, max_shape = None) -> cp.ndarray:
        """
        Convert distance predictions to keypoints
        """
    def forward(self, image: cp.ndarray, threshold: float) -> tuple[list[cp.ndarray], list[cp.ndarray], list[cp.ndarray]]:
        """
        
                Placeholder for the forward method.
                
        """
    def get(self, image: cp.ndarray, crop_size: int = 512, max_num: int = 0, metric: str = 'default', padding: float = 0.0, normalize_rotation: bool = True) -> list[VisageneFace]:
        ...
    def nms(self, dets: cp.ndarray):
        """
        Non-Maximum Suppression
        """
class OnnxFaceDetection(BaseFaceDetection):
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def forward(self, image: cp.ndarray, threshold: float) -> tuple[list[cp.ndarray], list[cp.ndarray], list[cp.ndarray]]:
        ...
    def initialize(self, model_bytes: bytes, device: str, device_id: str = '0') -> None:
        ...
class TrtFaceDetection(BaseFaceDetection):
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = 'cuda') -> None:
        ...
    def forward(self, image: cp.ndarray, threshold: float) -> tuple[list[cp.ndarray], list[cp.ndarray], list[cp.ndarray]]:
        """
        Forward pass using TensorRT
        """
    def initialize(self, model_bytes: bytes, device: str, device_id: str) -> None:
        ...
__test__: dict = {}
