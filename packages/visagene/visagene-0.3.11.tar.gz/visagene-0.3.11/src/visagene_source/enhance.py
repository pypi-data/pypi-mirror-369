import os

import cupy as cp
import onnxruntime
import pixtreme as px
import tensorrt as trt

from .base import BaseModelLoader


class BaseFaceEnhance(BaseModelLoader):
    """
    Base class for face enhancement models.

    Improves face image quality by reducing artifacts, enhancing details,
    and restoring facial features using generative models like GFPGAN.
    """

    def __init__(
        self,
        model_path: str | None = None,
        model_bytes: bytes | None = None,
        device: str = "cuda",
    ) -> None:
        super().__init__(model_path, model_bytes, device)

        # Face enhancement parameters
        self.input_size = 512
        self.input_mean = 0.5
        self.input_std = 0.5

    def forward(self, batch: cp.ndarray) -> cp.ndarray:
        """
        Placeholder for the forward method.
        """
        # Must be implemented by subclasses
        raise NotImplementedError("forward method must be implemented in subclass")

    def get(self, image: cp.ndarray) -> cp.ndarray:
        batch = px.image_to_batch(
            image,
            size=self.input_size,
            std=self.input_std,
            mean=self.input_mean,
            swap_rb=True,
            layout="HWC",
        )

        # print(f"BaseFaceEnhance.get: Processing batch with shape: {batch.shape}")

        # Forward pass
        preds = self.forward(batch)

        images = px.batch_to_images(preds, std=self.input_std, mean=self.input_mean, swap_rb=True, layout="NCHW")

        return images[0]

    def batch_get(self, images: list[cp.ndarray]) -> list[cp.ndarray]:
        """
        Process a batch of images for face enhancement.

        Args:
            images (list[cp.ndarray]): List of input images.

        Returns:
            list[cp.ndarray]: List of enhanced images.
        """
        batch = px.images_to_batch(
            images,
            std=self.input_std,
            size=self.input_size,
            mean=self.input_mean,
            swap_rb=True,
            layout="HWC",
        )

        # print(f"BaseFaceEnhance.batch_get: Processing batch with shape: {batch.shape}")
        # BaseFaceEnhance.batch_get: Processing batch with shape: (16, 3, 512, 512)

        # Forward pass
        # preds = self.forward(batch)
        # This model's input shape is (1, 3, 512, 512), so we need to for loop through each image
        preds = []
        for img in batch:
            pred = self.forward(img[None, ...])
            preds.append(pred)

        preds = cp.concatenate(preds, axis=0)
        return px.batch_to_images(preds, std=self.input_std, mean=self.input_mean, swap_rb=True, layout="NCHW")


class OnnxFaceEnhance(BaseFaceEnhance):
    """GFPGAN Face enhancer using ONNX Runtime for face quality improvement."""

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
        onnxruntime.preload_dlls()
        sees_options = onnxruntime.SessionOptions()
        sees_options.log_severity_level = 4
        sees_options.log_verbosity_level = 4

        provider_options = [{}]
        if "cuda" in device:
            providers = ["CUDAExecutionProvider"]
            provider_options = [{"device_id": device_id}]
        else:
            providers = ["CPUExecutionProvider"]

        onnx_params = {
            "session_options": sees_options,
            "providers": providers,
            "provider_options": provider_options,
        }

        self.session = onnxruntime.InferenceSession(model_bytes, **onnx_params)
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        self.dtype = self.session.get_inputs()[0].type

        self.input_size = self.input_shape[2]  # Assuming NHWC format

        # print("Face enhancement model initialized with")
        # print(f"    Input name: {self.input_name}")
        # print(f"    Input shape: {self.input_shape}")
        # print(f"    Input dtype: {self.dtype}")
        # print(f"    Input size: {self.input_size}")
        # print(f"    Input mean: {self.input_mean}, Input std: {self.input_std}")
        # print(f"    Device: {device}, Device ID: {device_id}")
        # print(f"    Providers: {self.session.get_providers()}")
        # print("OnnxGfpgan initialized successfully.")

    def forward(self, batch: cp.ndarray) -> cp.ndarray:
        """
        Execute ONNX inference on a preprocessed batch.

        Args:
            batch (cp.ndarray): Preprocessed batch tensor of shape (N, C, H, W).

        Returns:
            cp.ndarray: Output tensor from the model.
        """
        batch_numpy = cp.asnumpy(batch)
        preds = self.session.run(None, {self.input_name: batch_numpy})
        return cp.asarray(preds[0])


class TrtFaceEnhance(BaseFaceEnhance):
    """Face enhancer using TensorRT for high-performance face quality improvement."""

    def __init__(
        self,
        model_path: str | None = None,
        model_bytes: bytes | None = None,
        device: str = "cuda",
    ) -> None:
        # Extract device_id from device string
        device_id = 0
        if ":" in device:
            device_id = int(device.split(":")[-1])

        super().__init__(model_path, model_bytes, device)
        self.device_id = device_id

        if model_path is not None and model_path.endswith(".trt"):
            with open(model_path, "rb") as f:
                model_bytes = f.read()
        elif model_path is not None and model_path.endswith(".onnx"):
            # print("Converting ONNX model to TensorRT engine...")
            trt_path = model_path.replace(".onnx", ".trt")

            if not os.path.exists(trt_path):
                px.onnx_to_trt_fixed_shape(
                    onnx_path=model_path,
                    engine_path=trt_path,
                    input_shape=(1, 3, 512, 512),  # Example input size
                    precision="tf32",  # Use tf32 for better performance
                )
                if not os.path.exists(trt_path):
                    raise FileNotFoundError(f"Failed to convert ONNX model to TensorRT engine: {trt_path}")
            model_path = trt_path

        if model_path is not None:
            with open(model_path, "rb") as f:
                model_bytes = f.read()

        if model_bytes is None:
            raise ValueError("model_bytes must be provided if model_path is not specified")

        self.initialize(model_bytes)

    def initialize(self, model_bytes: bytes) -> None:
        with cp.cuda.Device(self.device_id):
            # Load the TensorRT engine
            logger = trt.Logger(trt.Logger.WARNING)
            runtime = trt.Runtime(logger)

            self.engine = runtime.deserialize_cuda_engine(model_bytes)
            self.ctx = self.engine.create_execution_context()
            self.stream = cp.cuda.Stream()

            # print("TrtGfpgan TensorRT engine loaded ✓")

            # Initialize buffers
            self.d_inputs: dict[str, cp.ndarray | None] = {}
            self.d_outputs: dict[str, cp.ndarray] = {}

            for name in self.engine:
                if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT:
                    self.d_inputs[name] = None  # Lazy allocation
                    self.input_name = name
                else:
                    dtype = trt.nptype(self.engine.get_tensor_dtype(name))
                    shape = tuple(max(int(s), 1) for s in self.engine.get_tensor_shape(name))
                    buf = cp.empty(shape, dtype=dtype)
                    self.d_outputs[name] = buf
                    self.ctx.set_tensor_address(name, buf.data.ptr)

            self.input_size = 512

            # print(f"TrtFaceEnhance initialized with input size: {self.input_size}")
            # print(f"Input mean: {self.input_mean}, Input std: {self.input_std}")

    def forward(self, batch: cp.ndarray) -> cp.ndarray:
        """
        Execute TensorRT inference on a preprocessed batch.

        Args:
            batch (cp.ndarray): Preprocessed batch tensor of shape (N, C, H, W).

        Returns:
            cp.ndarray: Output tensor from the model.
        """
        with cp.cuda.Device(self.device_id):
            batch_shape = tuple(int(x) for x in batch.shape)

            # Allocate input buffer if needed
            input_buffer = self.d_inputs[self.input_name]
            if input_buffer is None or input_buffer.shape != batch_shape:
                input_buffer = cp.empty(batch_shape, dtype=batch.dtype)
                self.d_inputs[self.input_name] = input_buffer
                self.ctx.set_tensor_address(self.input_name, input_buffer.data.ptr)

            # Copy data to input buffer
            input_buffer[:] = batch

            # Run inference
            assert self.ctx.execute_async_v3(self.stream.ptr), "TensorRT execution failed"
            self.stream.synchronize()

            # Get output
            output_name = list(self.d_outputs.keys())[0]
            return self.d_outputs[output_name].copy()
