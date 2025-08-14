from typing import Tuple

import cupy as cp
import numpy as np
import onnxruntime
import pixtreme as px

from .base import BaseModelLoader
from .schema import VisageneFace


class BaseFaceAnalysis(BaseModelLoader):
    """
    Base class for face analysis models.

    Analyzes faces to extract attributes such as gender and age.
    """

    def __init__(
        self,
        model_path: str | None = None,
        model_bytes: bytes | None = None,
        device: str = "cuda",
    ) -> None:
        super().__init__(model_path, model_bytes, device)

        # Face analysis parameters
        self.input_size = None  # Will be set from model
        self.taskname = "genderage"

        self.input_mean = 0.0
        self.input_std = 1.0 / 128.0

    def forward(self, face_image: cp.ndarray) -> cp.ndarray:
        """
        Placeholder for the forward method.
        Must be implemented by subclasses.

        Args:
            face_image: Face image as CuPy array

        Returns:
            Model output as CuPy array
        """
        raise NotImplementedError("forward method must be implemented in subclass")

    def get(self, face: VisageneFace) -> Tuple[int, int]:
        """
        Get gender and age attributes for a face.

        Args:
            image: Original image (not used in base implementation, kept for compatibility)
            face: Face object containing the cropped face image

        Returns:
            Tuple of (gender, age) where gender: 0=Female, 1=Male
        """
        # Use the pre-cropped and aligned face image
        face_image = face.image

        # Forward pass
        pred = self.forward(face_image)

        # Interpret output
        assert len(pred) == 3, f"Expected 3 outputs for genderage, got {len(pred)}"

        # Gender: argmax of first two values
        gender = int(cp.argmax(pred[:2]))

        # Age: third value * 100
        age = int(cp.round(pred[2] * 100))

        return gender, age


class OnnxFaceAnalysis(BaseFaceAnalysis):
    """
    ONNX-based face analysis implementation.

    Uses ONNX Runtime for inference on gender and age prediction models.
    """

    def __init__(
        self,
        model_path: str | None = None,
        model_bytes: bytes | None = None,
        device: str = "cuda",
    ) -> None:
        super().__init__(model_path, model_bytes, device)

        if self.model_bytes is None and self.model_path is not None:
            with open(self.model_path, "rb") as f:
                self.model_bytes = f.read()

        assert self.model_bytes is not None, "model_bytes must be provided if model_path is not specified"
        self.initialize(self.model_bytes, self.device, self.device_id)

    def initialize(self, model_bytes: bytes, device: str, device_id: str = "0") -> None:
        """Initialize ONNX Runtime session."""
        # Setup ONNX Runtime
        sess_options = onnxruntime.SessionOptions()
        sess_options.log_severity_level = 4
        sess_options.log_verbosity_level = 4

        provider_options = [{}]
        if "cuda" in device:
            providers = ["CUDAExecutionProvider"]
            provider_options = [{"device_id": device_id}]
        else:
            providers = ["CPUExecutionProvider"]

        onnx_params = {
            "session_options": sess_options,
            "providers": providers,
            "provider_options": provider_options,
        }

        self.session = onnxruntime.InferenceSession(model_bytes, **onnx_params)

        # Get input/output info
        input_cfg = self.session.get_inputs()[0]
        input_shape = input_cfg.shape
        input_name = input_cfg.name
        self.input_shape = input_shape

        # Extract input size from shape [batch, channels, height, width]
        if len(input_shape) >= 4:
            # Handle both static and dynamic shapes
            height = input_shape[2]
            width = input_shape[3]
            self.input_size = (width, height)  # (W, H) format

        outputs = self.session.get_outputs()
        output_names = []
        for o in outputs:
            output_names.append(o.name)
        self.input_name = input_name
        self.output_names = output_names

    def forward(self, face_image: cp.ndarray) -> cp.ndarray:
        """
        Run forward pass on face image.

        Args:
            face_image: Face image as CuPy array (H, W, C) in range [0, 1]

        Returns:
            Model output as CuPy array [female_score, male_score, age_normalized]
        """
        # Prepare batch
        batch = px.image_to_batch(
            face_image,
            size=self.input_size,
            mean=self.input_mean,
            std=self.input_std,
            swap_rb=True,  # ONNX models expect BGR
        )

        # Convert to numpy for ONNX Runtime
        batch_np = px.to_numpy(batch)

        # Run inference
        net_outs = self.session.run(self.output_names, {self.input_name: batch_np})

        # Convert back to CuPy
        output = cp.asarray(net_outs[0][0])  # Remove batch dimension

        return output
