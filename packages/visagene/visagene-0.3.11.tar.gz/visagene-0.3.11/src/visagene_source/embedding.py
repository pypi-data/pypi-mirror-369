import os

import cupy as cp
import onnx
import onnxruntime
import pixtreme as px

from .base import BaseModelLoader
from .emap import load_emap
from .schema import VisageneFace


class BaseFaceEmbedding(BaseModelLoader):
    """
    Base class for face feature extraction models.

    Extracts facial embeddings/features from face images for recognition,
    comparison, and identity-based operations like face swapping.
    """

    def __init__(
        self,
        model_path: str | None = None,
        model_bytes: bytes | None = None,
        device: str = "cuda",
    ) -> None:
        super().__init__(model_path, model_bytes, device)

        # Face feature extraction parameters
        self.input_size = (112, 112)
        self.input_mean = 127.5 / 255.0
        self.input_std = 127.5 / 255.0

    def forward(self, images: cp.ndarray | list[cp.ndarray]) -> cp.ndarray:
        """
        Placeholder for the forward method.
        """
        # Must be implemented by subclasses
        raise NotImplementedError("forward method must be implemented in subclass")

    def get(self, face) -> cp.ndarray:
        """
        Extract embedding for a single face.
        Common implementation shared by Onnx and Trt versions.
        """
        # Load emap if not already loaded
        if not hasattr(self, "emap"):
            import os

            script_dir = os.path.dirname(os.path.abspath(__file__))
            emap_path = os.path.join(script_dir, "emap.npy")
            self.emap = cp.load(emap_path)

        # Forward pass to get raw embedding
        embedding = self.forward(face.image)

        # Calculate normalized embedding
        normed_embedding = embedding / cp.linalg.norm(embedding)
        latent = normed_embedding.reshape((1, -1))
        latent = cp.dot(latent, self.emap)
        latent = latent / cp.linalg.norm(latent)

        return latent


class OnnxFaceEmbedding(BaseFaceEmbedding):
    """Face feature extractor using ONNX Runtime for inference."""

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
        self.emap = load_emap()
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
        modelproto = onnx.load_model_from_string(model_bytes)

        find_sub = False
        find_mul = False

        graph = modelproto.graph
        for nid, node in enumerate(graph.node[:8]):
            if node.name.startswith("Sub") or node.name.startswith("_minus"):
                find_sub = True
            if node.name.startswith("Mul") or node.name.startswith("_mul"):
                find_mul = True
        if find_sub and find_mul:
            input_mean = 0.0
            input_std = 1.0
        else:
            input_mean = 127.5 / 255.0
            input_std = 127.5 / 255.0

        self.input_mean = input_mean
        self.input_std = input_std

        input_cfg = self.session.get_inputs()[0]
        input_shape = input_cfg.shape
        input_name = input_cfg.name
        self.input_size = tuple(input_shape[2:4][::-1])
        self.input_shape = input_shape
        outputs = self.session.get_outputs()
        output_names = []
        for out in outputs:
            output_names.append(out.name)
        self.input_name = input_name
        self.output_names = output_names
        assert len(self.output_names) == 1
        self.output_shape = outputs[0].shape

        # print("Face embedding model initialized with")
        # print(f"    Input names: {[element.name for element in self.session.get_inputs()]}")
        # print(f"    Input shapes: {[element.shape for element in self.session.get_inputs()]}")
        # print(f"    Input Mean: {self.input_mean}, Input Std: {self.input_std}")
        # print(f"    Output names: {[element.name for element in self.session.get_outputs()]}")
        # print(f"    Output shapes: {[element.shape for element in self.session.get_outputs()]}")
        # print(f"    Input sizes: {self.input_size}")
        # print(f"    Device: {device}, Device ID: {device_id}")
        # print(f"    Providers: {self.session.get_providers()}")
        # print("OnnxEmbeddings initialized successfully.")

    def get(self, face: VisageneFace) -> cp.ndarray:
        """Extract embedding for a single face"""
        embedding = self.forward(face.image)

        # Calculate normalized embedding
        normed_embedding = embedding / cp.linalg.norm(embedding)
        latent = normed_embedding.reshape((1, -1))
        latent = cp.dot(latent, self.emap)
        latent = latent / cp.linalg.norm(latent)

        return latent

    def forward(self, images: cp.ndarray | list[cp.ndarray]) -> cp.ndarray:
        if not isinstance(images, list):
            images = [images]
        input_size = self.input_size

        # Convert images to batch format
        batch = px.images_to_batch(images, std=self.input_std, size=input_size, mean=self.input_mean)

        # Ensure the batch has the correct shape (4D for ONNX)
        if batch.ndim == 5:
            # Remove the extra batch dimension if present
            batch = batch.squeeze(0)

        blob = px.to_numpy(batch)
        net_out = self.session.run(self.output_names, {self.input_name: blob})[0]
        net_out = cp.asarray(net_out)

        return net_out


class TrtFaceEmbedding(BaseFaceEmbedding):
    """Face feature extractor using TensorRT for high-performance inference."""

    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = "cuda") -> None:
        super().__init__(model_path, model_bytes, device)

        if self.model_bytes is None and self.model_path is not None:
            if self.model_path.endswith(".onnx"):
                onnx_path = self.model_path
                trt_path = self.model_path.replace(".onnx", ".trt")
            else:
                onnx_path = self.model_path.replace(".trt", ".onnx")
                trt_path = self.model_path

            if not os.path.exists(trt_path) and os.path.exists(onnx_path):
                px.onnx_to_trt_dynamic_shape(
                    onnx_path,
                    trt_path,
                    precision="bf16",
                    batch_range=(1, 1, 1),
                    spatial_range=(112, 112, 112),
                )
            elif os.path.exists(trt_path):
                self.model_path = trt_path
            else:
                raise FileNotFoundError(
                    f"Model file not found: onnx: {onnx_path}:{os.path.exists(onnx_path)}, trt: {trt_path}:{os.path.exists(trt_path)}"
                )

            self.model_path = trt_path

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        with open(self.model_path, "rb") as f:
            self.model_bytes = f.read()
        self.initialize(self.model_bytes, self.device, self.device_id)

    def initialize(self, model_bytes: bytes, device: str, device_id: str) -> None:
        import tensorrt as trt

        self.emap = load_emap()

        with cp.cuda.Device(self.device_id):
            # Load the TensorRT engine
            self.logger = trt.Logger(trt.Logger.WARNING)
            self.runtime = trt.Runtime(self.logger)

            self.engine = self.runtime.deserialize_cuda_engine(model_bytes)
            self.ctx = self.engine.create_execution_context()

            # print("face embedding engine loaded ✔  tensors:", self.engine)

            # Prepare CuPy stream and device buffers
            self.stream = cp.cuda.Stream()
            self.d_inputs = {}
            self.d_outputs = {}

            # Automatically get tensor names
            input_names = []
            output_names = []

            for name in self.engine:
                shape = tuple(max(int(s), 1) for s in self.engine.get_tensor_shape(name))
                dtype = trt.nptype(self.engine.get_tensor_dtype(name))

                # Convert TensorRT shape to list for CuPy compatibility
                shape_list = [int(dim) for dim in shape]

                # Create a CuPy array for the tensor
                d_arr = cp.empty(shape_list, dtype=dtype)

                if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT:
                    self.d_inputs[name] = d_arr
                    input_names.append(name)
                else:
                    self.d_outputs[name] = d_arr
                    output_names.append(name)

            # Use the first input/output tensor names
            self.input_tensor = input_names[0] if input_names else "input"
            self.output_tensor = output_names[0] if output_names else "output"
            self.output_names = output_names

            # Set tensor addresses only once during initialization
            for name in self.engine:
                if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT:
                    self.ctx.set_tensor_address(name, self.d_inputs[name].data.ptr)
                else:
                    self.ctx.set_tensor_address(name, self.d_outputs[name].data.ptr)

            # Get input/output shapes
            input_shape = list(self.d_inputs[self.input_tensor].shape)
            output_shape = list(self.d_outputs[self.output_tensor].shape)

            self.input_shape = input_shape
            self.output_shape = output_shape
            self.input_size = tuple(input_shape[2:4][::-1]) if len(input_shape) >= 4 else (112, 112)

            # Set normalization parameters
            self.input_mean = 127.5 / 255.0
            self.input_std = 127.5 / 255.0

            # print("TrtEmbeddings initialized with")
            # print(f"    Input tensor: {self.input_tensor}")
            # print(f"    Input shape: {self.input_shape}")
            # print(f"    Input size: {self.input_size}")
            # print(f"    Input Mean: {self.input_mean}, Input Std: {self.input_std}")
            # print(f"    Output tensor: {self.output_tensor}")
            # print(f"    Output shape: {self.output_shape}")
            # print(f"    Device: {device}, Device ID: {device_id}")
            # print("TrtEmbeddings initialized successfully.")

    def forward(self, images: cp.ndarray | list[cp.ndarray]) -> cp.ndarray:
        """Forward pass using TensorRT"""
        if not isinstance(images, list):
            images = [images]

        # Convert images to batch format
        batch = px.images_to_batch(images, std=self.input_std, size=self.input_size, mean=self.input_mean)

        # Copy input data to GPU buffer
        in_gpu = self.d_inputs[self.input_tensor]
        if in_gpu.shape != batch.shape:
            # Explicitly delete old buffer
            del self.d_inputs[self.input_tensor]
            # Allocate new buffer
            in_gpu = cp.empty(batch.shape, dtype=batch.dtype)
            self.d_inputs[self.input_tensor] = in_gpu
            # Reset tensor address
            self.ctx.set_tensor_address(self.input_tensor, in_gpu.data.ptr)

        # Copy data
        in_gpu[:] = batch

        # Execute the TensorRT engine asynchronously
        self.ctx.execute_async_v3(self.stream.ptr)

        # Wait for inference completion
        self.stream.synchronize()

        # Get output data
        out_gpu = self.d_outputs[self.output_tensor]

        # Return a copy to avoid memory issues
        return cp.copy(out_gpu).flatten()

    def get(self, face: VisageneFace) -> cp.ndarray:
        """Extract embedding for a single face"""
        embedding = self.forward(face.image)

        # Calculate normalized embedding
        normed_embedding = embedding / cp.linalg.norm(embedding)
        latent = normed_embedding.reshape((1, -1))
        latent = cp.dot(latent, self.emap)
        latent = latent / cp.linalg.norm(latent)

        return latent
        return latent
