import os

import cupy as cp
import onnxruntime
import pixtreme as px
import tensorrt as trt

from .base import BaseModelLoader


class BaseFaceSegmentation(BaseModelLoader):
    """
    Base class for face segmentation models.

    Segments facial regions like eyes, nose, mouth, and skin
    to enable targeted operations like face swapping and enhancement.
    """

    def __init__(
        self,
        model_path: str | None = None,
        model_bytes: bytes | None = None,
        device: str = "cuda",
    ) -> None:
        super().__init__(model_path, model_bytes, device)

        # Face segmentation parameters
        self.input_size = (512, 512)
        self.input_mean = (0.485, 0.456, 0.406)
        self.input_std = (0.229, 0.224, 0.225)

        indexes = [
            [1, 3, 14, 15, 16, 17, 18],  # Outer face
            [2, 4, 5],  # Skin
            [6, 7, 8, 9, 10, 11, 12, 13],  # Facial features
        ]
        self.init_indexes(indexes)

    def forward(self, batch: cp.ndarray) -> cp.ndarray:
        """
        Placeholder for the forward method.
        """
        # Must be implemented by subclasses
        raise NotImplementedError("forward method must be implemented in subclass")

    def init_indexes(self, indexes: list) -> None:
        self.num_categories = len(indexes)

        # Create all indices and category mapping
        all_indices = []
        category_ids = []
        for cat_idx, index_list in enumerate(indexes):
            all_indices.extend(index_list)
            category_ids.extend([cat_idx] * len(index_list))

        self.all_indices = cp.array(all_indices)  # All class indices
        self.category_ids = cp.array(category_ids)  # Corresponding category IDs

    def get(self, image: cp.ndarray) -> cp.ndarray:
        """
        Face segmentation method for a single image.
        """

        images = [image]
        batch = px.images_to_batch(
            images,
            std=self.input_std,
            size=self.input_size,
            mean=self.input_mean,
            swap_rb=True,
            layout="HWC",
        )

        preds = self.forward(batch)  # Ensure model is loaded
        masks = self.composite_masks(preds)
        masks = px.batch_to_images(masks, swap_rb=True, layout="NCHW")
        return masks[0]

    def batch_get(self, images: list[cp.ndarray], MAX_BATCH_SIZE: int = 16) -> list[cp.ndarray]:
        """
        Face segmentation inference method.
        Common implementation shared by Onnx and Trt versions.
        Supports batch processing for multiple images.
        """

        # Split processing if batch size is too large
        if len(images) > MAX_BATCH_SIZE:
            results = []
            for i in range(0, len(images), MAX_BATCH_SIZE):
                batch_images = images[i : i + MAX_BATCH_SIZE]
                sub_batch = px.images_to_batch(
                    batch_images,
                    std=self.input_std,
                    size=self.input_size,
                    mean=self.input_mean,
                    swap_rb=True,
                    layout="HWC",
                )

                batch_results = self.forward(sub_batch)
                masks = self.composite_masks(batch_results)
                masks = px.batch_to_images(masks, swap_rb=True, layout="NCHW")
                results.extend(masks)
            return results
        else:
            batch = px.images_to_batch(
                images,
                std=self.input_std,
                size=self.input_size,
                mean=self.input_mean,
                swap_rb=True,
                layout="HWC",
            )
            preds = self.forward(batch)
            masks = self.composite_masks(preds)
            masks = px.batch_to_images(masks, swap_rb=True, layout="NCHW")
            return masks

    def composite_masks(self, preds: cp.ndarray) -> cp.ndarray:
        """
        Composite masks into a single image.
        """
        # Stack masks along the channel dimension
        # Adjust if preds has shape (1, N, 19, 512, 512)
        if preds.ndim == 5 and preds.shape[0] == 1:
            preds = preds[0]  # (N, 19, 512, 512)

        batch_size = preds.shape[0]

        # Calculate softmax for entire batch
        # exp(x - max) / sum(exp(x - max)) for numerical stability
        max_vals = cp.max(preds, axis=1, keepdims=True)  # (N, 1, 512, 512)
        exp_vals = cp.exp(preds - max_vals)
        prob = exp_vals / cp.sum(exp_vals, axis=1, keepdims=True)  # (N, 19, 512, 512)

        # Calculate argmax for entire batch
        pred = cp.argmax(prob, axis=1)  # (N, 512, 512)

        # Vectorized processing for entire batch
        # Execute all comparisons at once
        pred_expanded = pred[..., cp.newaxis]  # (N, 512, 512, 1)

        # Expand indices to batch dimension
        indices_expanded = self.all_indices[cp.newaxis, cp.newaxis, cp.newaxis, :]  # (1, 1, 1, num_all_indices)

        # Calculate all class matches at once
        all_matches = (pred_expanded == indices_expanded).astype(cp.float32)  # (N, 512, 512, num_all_indices)

        # Create category masks at once
        category_masks = cp.arange(self.num_categories)[:, cp.newaxis] == self.category_ids[cp.newaxis, :]

        # Aggregate by category using Einstein summation
        # all_matches: (N, 512, 512, num_all_indices), category_masks: (3, num_all_indices)
        # Calculate and aggregate masks for each category
        _masks = cp.einsum("nijk,mk->mnijk", all_matches, category_masks.astype(cp.float32))
        _masks = cp.sum(_masks, axis=-1)  # (3, N, 512, 512)

        # Combine masks for each batch
        masks_list = []
        for n in range(batch_size):
            # Stack 3 category masks for each batch
            # _masks[i, n] has shape (512, 512)
            mask = cp.stack([_masks[0, n], _masks[1, n], _masks[2, n]], axis=0)  # (3, 512, 512)
            masks_list.append(mask)

        # Combine along batch dimension
        masks = cp.stack(masks_list, axis=0)  # (N, 3, 512, 512)

        return masks


class OnnxFaceSegmentation(BaseFaceSegmentation):
    """Face segmentation using ONNX Runtime for inference."""

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
        self.output_shape = self.session.get_outputs()[0].shape
        self.output_name = self.session.get_outputs()[0].name

    def forward(self, batch: cp.ndarray) -> cp.ndarray:
        batch_numpy = cp.asnumpy(batch)
        preds = self.session.run(None, {self.input_name: batch_numpy})
        preds = cp.asarray(preds)

        return preds


class TrtFaceSegmentation(BaseFaceSegmentation):
    """Face segmentation using TensorRT for high-performance inference."""

    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = "cuda") -> None:
        super().__init__(model_path, model_bytes, device)
        # print("Initializing TRT Segmentation")

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
                    precision="bf16",  # bf16からfp16に変更してメモリ使用量を削減
                    batch_range=(1, 1, 16),  # バッチサイズを32から16に削減
                    spatial_range=(512, 512, 512),
                    workspace=1024 * 1024 * 1024 * 2,  # 2GB workspace
                )
            elif os.path.exists(trt_path):
                self.model_path = trt_path
            else:
                # print(f"Model files not found: onnx: {onnx_path}, trt: {trt_path}")
                raise FileNotFoundError(
                    f"Model file not found: onnx: {onnx_path}:{os.path.exists(onnx_path)}, trt: {trt_path}:{os.path.exists(trt_path)}"
                )

            self.model_path = trt_path

        if self.model_bytes is None:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            with open(self.model_path, "rb") as f:
                self.model_bytes = f.read()
        self.initialize(self.model_bytes, self.device, self.device_id)

    def initialize(self, model_bytes: bytes, device: str, device_id: str) -> None:
        with cp.cuda.Device(self.device_id):
            # print("Initializing TensorRT engine...")
            self.logger = trt.Logger(trt.Logger.WARNING)
            self.runtime = trt.Runtime(self.logger)

            self.engine = self.runtime.deserialize_cuda_engine(model_bytes)
            self.ctx = self.engine.create_execution_context()

            # print("face segmentation engine loaded ✔  tensors:", self.engine)

            """Initialize processing"""
            # Prepare CuPy stream and device buffers
            self.stream = cp.cuda.Stream()
            self.d_inputs = {}
            self.d_outputs = {}

            # Automatically get tensor names
            input_names = []
            output_names = []

            for name in self.engine:
                shape = tuple(max(int(s), 1) for s in self.engine.get_tensor_shape(name))
                # print(f"Tensor {name} shape: {shape}")
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

            # Use the first input tensor name
            self.input_tensor = input_names[0] if input_names else "input"
            self.output_names = output_names

            # Set tensor addresses only once during initialization
            for name in self.engine:
                if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT:
                    self.ctx.set_tensor_address(name, self.d_inputs[name].data.ptr)
                else:
                    self.ctx.set_tensor_address(name, self.d_outputs[name].data.ptr)

            # Get input size from the input tensor
            input_shape = list(self.d_inputs[self.input_tensor].shape)
            if len(input_shape) >= 4 and input_shape[2] > 0 and input_shape[3] > 0:
                self.input_size = (input_shape[3], input_shape[2])  # (width, height)

            # print("TrtSegmentation initialized with")
            # print(f"    Input names: {self.input_tensor}")
            # print(f"    Input size: {self.input_size}")
            # print(f"    Input shape: {self.d_inputs[self.input_tensor].shape}")
            # print(f"    Input Mean: {self.input_mean}, Input Std: {self.input_std}")
            # print(f"    Output names: {self.output_names}")
            # print(f"    Output shapes: {[self.d_outputs[name].shape for name in self.output_names]}")
            # print(f"    Device: {device}, Device ID: {device_id}")
            # print("TrtSegmentation initialized successfully.")

    def forward(self, batch: cp.ndarray) -> cp.ndarray:
        """Forward pass using TensorRT"""
        # Set input shape for dynamic batch
        batch_shape = tuple(int(x) for x in batch.shape)  # (N, 3, 512, 512)
        self.ctx.set_input_shape(self.input_tensor, batch_shape)

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

        # Update output buffer size for dynamic batch
        output_shape = (batch_shape[0], 19, 512, 512)  # (N, 19, 512, 512)
        for name in self.output_names:
            if self.d_outputs[name].shape != output_shape:
                # Reallocate output buffer
                del self.d_outputs[name]
                self.d_outputs[name] = cp.empty(output_shape, dtype=cp.float32)
                self.ctx.set_tensor_address(name, self.d_outputs[name].data.ptr)

        # Execute the TensorRT engine asynchronously
        self.ctx.execute_async_v3(self.stream.ptr)

        # Wait for inference completion
        self.stream.synchronize()

        # Get output data
        preds = None
        for name in self.output_names:
            output_data = self.d_outputs[name]
            preds = cp.copy(output_data)  # Copy to avoid memory issues

        return preds
