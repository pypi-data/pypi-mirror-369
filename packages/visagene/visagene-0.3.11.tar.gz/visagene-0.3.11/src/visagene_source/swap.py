import os

import cupy as cp
import onnxruntime
import pixtreme as px

from .base import BaseModelLoader


class BaseFaceSwap(BaseModelLoader):
    """
    Base class for face swapping models.

    Performs face identity transfer by swapping facial features
    from a source identity onto a target face image.
    """

    def __init__(
        self,
        model_path: str | None = None,
        model_bytes: bytes | None = None,
        device: str = "cuda",
    ) -> None:
        super().__init__(model_path, model_bytes, device)

        # Face swapping parameters
        self.input_mean = 0.0
        self.input_std = 1.0
        self.patch = 256
        self.input_size = (self.patch, self.patch)  # Default input size for face swap models

    def forward(self, batch: cp.ndarray, latent: cp.ndarray) -> cp.ndarray:
        """
        Placeholder for the forward method.
        """
        # Must be implemented by subclasses
        raise NotImplementedError("forward method must be implemented in subclass")

    def get(self, target_image: cp.ndarray, latent: cp.ndarray) -> cp.ndarray:
        """
        Inference with TensorRT face swap model.
        """
        batch = px.images_to_batch(
            target_image,
            std=self.input_std,
            size=self.input_size,
            mean=self.input_mean,
            swap_rb=True,
            layout="HWC",
        )
        latent_row = cp.asarray(latent, cp.float32).reshape(-1, 512)
        preds = self.forward(batch, latent_row)
        output_images = px.batch_to_images(preds, swap_rb=True, layout="NCHW")
        return output_images[0]


class OnnxFaceSwap(BaseFaceSwap):
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

        self.input_mean = 0.0
        self.input_std = 1.0

        inputs = self.session.get_inputs()
        self.input_names = []
        for inp in inputs:
            self.input_names.append(inp.name)
        outputs = self.session.get_outputs()
        output_names = []
        for out in outputs:
            output_names.append(out.name)
        self.output_names = output_names
        assert len(self.output_names) == 1
        input_cfg = inputs[0]
        self.input_size = tuple(input_cfg.shape[2:4][::-1])

        # print("Face swap model initialized with")
        # print(f"    Input names: {[element.name for element in self.session.get_inputs()]}")
        # print(f"    Input shapes: {[element.shape for element in self.session.get_inputs()]}")
        # print(f"    Input Mean: {self.input_mean}, Input Std: {self.input_std}")
        # print(f"    Output names: {[element.name for element in self.session.get_outputs()]}")
        # print(f"    Output shapes: {[element.shape for element in self.session.get_outputs()]}")
        # print(f"    Input sizes: {self.input_size}")
        # print(f"    Device: {device}, Device ID: {device_id}")
        # print(f"    Providers: {self.session.get_providers()}")
        # print("OnnxSwap initialized successfully.")

    def forward(self, batch: cp.ndarray, latent: cp.ndarray) -> cp.ndarray:
        """Forward pass using ONNX"""
        batch_numpy = px.to_numpy(batch)
        latent_numpy = px.to_numpy(latent)

        # Normalize input
        batch_numpy = (batch_numpy - self.input_mean) / self.input_std

        pred = self.session.run(self.output_names, {self.input_names[0]: batch_numpy, self.input_names[1]: latent_numpy})[0]
        return cp.asarray(pred)

    def batch_get(
        self, target_images: list[cp.ndarray], latent: cp.ndarray | list[cp.ndarray], max_batch: int = 16
    ) -> list[cp.ndarray]:
        """
        Face swap inference method using the new TrtSwap-compatible interface.
        """
        batch = px.images_to_batch(
            target_images,
            std=self.input_std,
            size=self.input_size,
            mean=self.input_mean,
            swap_rb=True,
            layout="HWC",
        )
        latent_row = cp.asarray(latent, cp.float32).reshape(-1, 512)

        batch_size = batch.shape[0]
        if batch_size > max_batch:
            preds = []
            for start in range(0, batch_size, max_batch):
                end = min(start + max_batch, batch_size)
                batch_part = batch[start:end]
                latent_part = cp.repeat(latent_row, batch_part.shape[0], axis=0)
                preds_part = self.forward(batch_part, latent_part)
                preds.append(preds_part)
            preds = cp.concatenate(preds, axis=0)
        else:
            latent_row = cp.repeat(latent_row, batch_size, axis=0)
            preds = self.forward(batch, latent_row)

        output_images = px.batch_to_images(preds, swap_rb=True, layout="NCHW")
        return output_images


class TrtFaceSwap(BaseFaceSwap):
    """Face swapper using TensorRT for high-performance face identity transfer."""

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
                # px.onnx_to_trt_fixed_shape(
                #    onnx_path,
                #    trt_path,
                #    (1, 3, self.patch, self.patch),
                #    precision="tf32",
                # )
                px.onnx_to_trt_dynamic_shape(
                    onnx_path,
                    trt_path,
                    precision="bf16",
                    batch_range=(1, 1, 32),
                    spatial_range=(self.patch, self.patch, self.patch),
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

        with cp.cuda.Device(self.device_id):
            logger = trt.Logger(trt.Logger.WARNING)
            runtime = trt.Runtime(logger)

            self.engine = runtime.deserialize_cuda_engine(model_bytes)
            self.ctx = self.engine.create_execution_context()
            self.stream = cp.cuda.Stream()

            # print("face swap engine loaded ✔  tensors:", self.engine)

            # Determine bindings by number of dimensions
            self.target_name, self.source_name = None, None
            self.d_inputs: dict[str, cp.ndarray | None] = {}
            self.d_outputs: dict[str, cp.ndarray] = {}

            for name in self.engine:
                if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT:
                    if len(self.engine.get_tensor_shape(name)) == 4:
                        self.target_name = name
                    else:  # len == 2
                        self.source_name = name
                    self.d_inputs[name] = None  # Lazy allocation
                else:
                    dtype = trt.nptype(self.engine.get_tensor_dtype(name))
                    shape = tuple(max(int(s), 1) for s in self.engine.get_tensor_shape(name))
                    buf = cp.empty(shape, dtype=dtype)
                    self.d_outputs[name] = buf
                    self.ctx.set_tensor_address(name, buf.data.ptr)

            if not self.target_name or not self.source_name:
                raise RuntimeError("Failed to detect target/source bindings")

            self.input_mean, self.input_std = 0.0, 1.0

            self.output_names = [name for name in self.engine if self.engine.get_tensor_mode(name) == trt.TensorIOMode.OUTPUT]

            # print("TrtSwap initialized with")
            # print(f"    Target input: {self.target_name}")
            # print(f"    Source input: {self.source_name}")
            # print(f"    Output names: {self.output_names}")
            # print(f"    Patch size: {self.patch}")
            # print(f"    Input Mean: {self.input_mean}, Input Std: {self.input_std}")
            # print(f"    Device: {device}, Device ID: {device_id}")
            # print("TrtSwap initialized successfully.")

    def forward(self, batch: cp.ndarray, latent: cp.ndarray) -> cp.ndarray:
        """Forward pass using TensorRT"""
        # 1. Convert shape to pure Python int
        img_shape = tuple(int(x) for x in batch.shape)  # (N,3,self.patch,self.patch)
        lat_shape = (int(latent.shape[0]), 512)  # (N,512)

        # 2. Assert for type safety
        assert self.target_name is not None and self.source_name is not None

        # 3. Register to TensorRT
        self.ctx.set_input_shape(self.target_name, img_shape)
        self.ctx.set_input_shape(self.source_name, lat_shape)

        # 4. Allocate input buffers as needed
        for name, need_shape, src in [(self.target_name, img_shape, batch), (self.source_name, lat_shape, latent)]:
            current_buf = self.d_inputs[name]
            if current_buf is None or current_buf.shape != need_shape:
                buf = cp.empty(need_shape, dtype=src.dtype)
                self.d_inputs[name] = buf
                self.ctx.set_tensor_address(name, buf.data.ptr)

            input_buf = self.d_inputs[name]
            assert input_buf is not None  # For type safety
            input_buf[:] = src if name == self.source_name else (src - self.input_mean) / self.input_std

        # 5. Reallocate output buffers for each batch
        out_shape = (img_shape[0], 3, self.patch, self.patch)  # (N,3,self.patch,self.patch)
        out_name = self.output_names[0]
        if self.d_outputs[out_name].shape != out_shape:
            buf = cp.empty(out_shape, dtype=self.d_outputs[out_name].dtype)
            self.d_outputs[out_name] = buf
            self.ctx.set_tensor_address(out_name, buf.data.ptr)

        # 6. Execute inference
        self.ctx.execute_async_v3(self.stream.ptr)
        self.stream.synchronize()

        return cp.copy(self.d_outputs[out_name])

    def batch_get(
        self, target_images: list[cp.ndarray], latent: cp.ndarray | list[cp.ndarray], max_batch: int = 16
    ) -> list[cp.ndarray]:
        """
        Inference with TensorRT face swap model.
        """
        batch = px.images_to_batch(
            target_images,
            std=self.input_std,
            size=(self.patch, self.patch),
            mean=self.input_mean,
            swap_rb=True,
            layout="HWC",
        )

        latent_rows = cp.empty((0, 512), dtype=cp.float32)
        if isinstance(latent, list):
            for i, _latent in enumerate(latent):
                _latent = cp.asarray(_latent, cp.float32).reshape(-1, 512)
                latent_rows = cp.concatenate((latent_rows, _latent), axis=0)
        else:
            _latent = cp.asarray(latent, cp.float32).reshape(-1, 512)
            latent_rows = cp.concatenate((latent_rows, _latent), axis=0)

        batch_size = batch.shape[0]
        if batch_size > max_batch:
            # If batch size exceeds max_batch, split into smaller batches
            preds = []
            for start in range(0, batch_size, max_batch):
                end = min(start + max_batch, batch_size)
                batch_part = batch[start:end]

                if latent_rows.shape[0] == 1:
                    latent_part = cp.repeat(latent_rows[0], batch_part.shape[0], axis=0)
                else:
                    latent_part = cp.asarray(latent_rows[start // max_batch], cp.float32).reshape(-1, 512)

                preds_part = self.forward(batch_part, latent_part)
                preds.append(preds_part)
            preds = cp.concatenate(preds, axis=0)
        else:
            # If batch size is within max_batch, process the entire batch
            if latent_rows.shape[0] == 1:
                latent_row = cp.repeat(latent_rows[0], batch_size, axis=0)
            else:
                latent_row = latent_rows
            preds = self.forward(batch, latent_row)

        output_images = px.batch_to_images(preds, swap_rb=True, layout="NCHW")

        if len(output_images) == 1:
            return output_images[0]
        else:
            return output_images
