import os

import cupy as cp
import onnxruntime
import pixtreme as px
import tensorrt as trt

from .base import BaseModelLoader
from .schema import VisageneFace


class BaseFaceDetection(BaseModelLoader):
    """
    Base class for face detection models.

    Detects faces in images and returns bounding boxes, keypoints,
    and confidence scores for identified faces.
    """

    def __init__(
        self,
        model_path: str | None = None,
        model_bytes: bytes | None = None,
        device: str = "cuda",
    ) -> None:
        super().__init__(model_path, model_bytes, device)

        # Face detection parameters
        self.input_size = (640, 640)
        self.center_cache = {}
        self.nms_thresh = 0.4
        self.det_thresh = 0.5
        self.input_mean = 127.5 / 255.0
        self.input_std = 128.0 / 255.0
        self.use_kps = False

    def forward(self, image: cp.ndarray, threshold: float) -> tuple[list[cp.ndarray], list[cp.ndarray], list[cp.ndarray]]:
        """
        Placeholder for the forward method.
        """
        # Must be implemented by subclasses
        raise NotImplementedError("forward method must be implemented in subclass")

    def get(
        self,
        image: cp.ndarray,
        crop_size: int = 512,
        max_num: int = 0,
        metric: str = "default",
        padding: float = 0.0,
        normalize_rotation: bool = True,
    ) -> list[VisageneFace]:
        im_ratio = float(image.shape[0]) / image.shape[1]
        model_ratio = float(self.input_size[1]) / self.input_size[0]
        if im_ratio > model_ratio:
            new_height = self.input_size[1]
            new_width = int(new_height / im_ratio)
        else:
            new_width = self.input_size[0]
            new_height = int(new_width * im_ratio)
        det_scale = cp.float32(new_height) / image.shape[0]

        resized_image = px.resize(image, (new_width, new_height), interpolation=px.INTER_AUTO)

        det_image = cp.zeros((self.input_size[1], self.input_size[0], 3), dtype=cp.float32)
        det_image[:new_height, :new_width, :] = resized_image

        scores_list, bboxes_list, kpss_list = self.forward(det_image, self.det_thresh)

        if not scores_list:
            return []

        scores = cp.vstack(scores_list).astype(cp.float32)

        scores_ravel = scores.ravel()
        order = scores_ravel.argsort()[::-1]

        bboxes = cp.vstack(bboxes_list).astype(cp.float32) / det_scale

        pre_det = cp.hstack((bboxes, scores))

        pre_det = pre_det[order, :]
        keep = self.nms(pre_det)
        det = pre_det[keep, :]
        if self.use_kps:
            kpss = cp.vstack(kpss_list).astype(cp.float32) / det_scale
            kpss = kpss[order, :, :]
            kpss = kpss[keep, :, :]
        else:
            kpss = None
        if max_num > 0 and det.shape[0] > max_num:
            area = (det[:, 2] - det[:, 0]) * (det[:, 3] - det[:, 1])
            image_center = cp.array([image.shape[0] // 2, image.shape[1] // 2], dtype=cp.float32)

            offsets = cp.vstack(
                [(det[:, 0] + det[:, 2]) / 2 - image_center[1], (det[:, 1] + det[:, 3]) / 2 - image_center[0]]
            ).astype(cp.float32)

            offset_dist_squared = cp.sum(cp.power(offsets, 2.0), 0)

            if metric == "max":
                values = area
            else:
                values = area - offset_dist_squared * 2.0  # some extra weight on the centering
            bindex = cp.argsort(values)[::-1]  # some extra weight on the centering

            bindex = bindex[0:max_num]
            det = det[bindex, :]
            if kpss is not None:
                kpss = kpss[bindex, :]

        bboxes = det
        results = []

        for i in range(bboxes.shape[0]):
            bbox = bboxes[i, :4]
            score = bboxes[i, 4]
            kps = None
            if kpss is not None:
                kps = kpss[i]

            if kps is not None:
                bbox = bbox.astype(cp.float32)
                cropped_image, M = self.crop(
                    image, kps, size=crop_size, padding=padding, normalize_rotation=normalize_rotation
                )

                face = VisageneFace(bbox=bbox, score=score, kps=kps, image=cropped_image, matrix=M)
                results.append(face)

        return results

    def nms(self, dets: cp.ndarray):
        """Non-Maximum Suppression"""
        thresh = self.nms_thresh
        x1 = dets[:, 0]
        y1 = dets[:, 1]
        x2 = dets[:, 2]
        y2 = dets[:, 3]
        scores = dets[:, 4]

        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            xx1 = cp.maximum(x1[i], x1[order[1:]]).astype(cp.float32)
            yy1 = cp.maximum(y1[i], y1[order[1:]]).astype(cp.float32)
            xx2 = cp.minimum(x2[i], x2[order[1:]]).astype(cp.float32)
            yy2 = cp.minimum(y2[i], y2[order[1:]]).astype(cp.float32)

            w = cp.maximum(0.0, xx2 - xx1 + 1)
            h = cp.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h
            ovr = inter / (areas[i] + areas[order[1:]] - inter)

            inds = cp.where(ovr <= thresh)[0]
            order = order[inds + 1]

        return keep

    def distance2bbox(self, points: cp.ndarray, distance: cp.ndarray, max_shape=None) -> cp.ndarray:
        """Convert distance predictions to bounding boxes"""
        points = points.astype(cp.float32)
        distance = distance.astype(cp.float32)

        x1, y1 = points[:, 0] - distance[:, 0], points[:, 1] - distance[:, 1]
        x2, y2 = points[:, 0] + distance[:, 2], points[:, 1] + distance[:, 3]

        if max_shape is not None:
            x1, x2 = cp.clip(x1, 0, max_shape[1]), cp.clip(x2, 0, max_shape[1])
            y1, y2 = cp.clip(y1, 0, max_shape[0]), cp.clip(y2, 0, max_shape[0])

        return cp.stack([x1, y1, x2, y2], axis=-1)

    def distance2kps(self, points: cp.ndarray, distance: cp.ndarray, max_shape=None) -> cp.ndarray:
        """Convert distance predictions to keypoints"""
        points = points.astype(cp.float32)
        distance = distance.astype(cp.float32)

        preds = [
            (
                cp.clip(points[:, i % 2] + distance[:, i], 0, max_shape[1] if max_shape else cp.inf)
                if i % 2 == 0
                else cp.clip(points[:, i % 2] + distance[:, i], 0, max_shape[0] if max_shape else cp.inf)
            )
            for i in range(distance.shape[1])
        ]
        return cp.stack(preds, axis=-1)

    def crop_from_kps_with_padding(
        self, image: cp.ndarray, kps: cp.ndarray, size: int = 512, padding: float = 0.0, normalize_rotation: bool = True
    ) -> tuple[cp.ndarray, cp.ndarray]:
        """Crop face image using keypoints with padding support

        This is a custom implementation that supports padding by scaling the destination points
        """
        # Standard face landmark positions (from InsightFace)
        dst = cp.array(
            [[38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366], [41.5493, 92.3655], [70.7299, 92.2041]],
            dtype=cp.float32,
        )

        # Scale and offset adjustment
        if size % 112 == 0:
            ratio = float(size) / 112.0
            diff_x = 0
        else:
            ratio = float(size) / 128.0
            diff_x = int(8.0 * ratio)
        dst = dst * ratio
        dst[:, 0] += diff_x

        # Apply padding by scaling down the destination points
        # This makes the face appear smaller in the output, including more background
        if padding > 0:
            dst_center = cp.mean(dst, axis=0)
            scale_factor = 1 / (1 + padding)
            dst = (dst - dst_center) * scale_factor + dst_center

        # Centralize points
        src_mean = cp.mean(kps, axis=0)
        dst_mean = cp.mean(dst, axis=0)
        src_centered = kps - src_mean
        dst_centered = dst - dst_mean

        # Scale adjustment
        src_dists = cp.linalg.norm(src_centered, axis=1)
        dst_dists = cp.linalg.norm(dst_centered, axis=1)
        scale = cp.sum(dst_dists) / cp.sum(src_dists)

        if normalize_rotation:
            # Rotation (standard behavior)
            U, _, VT = cp.linalg.svd(cp.dot(dst_centered.T, src_centered))
            R = cp.dot(U, VT)

            if cp.linalg.det(R) < 0:
                U[:, -1] *= -1
                R = cp.dot(U, VT)

            # Translation
            T = dst_mean - scale * cp.dot(R, src_mean)

            # Construct transformation matrix
            M = cp.zeros((2, 3))
            M[0:2, 0:2] = scale * R
            M[:, 2] = T
        else:
            # No rotation normalization - use axis-aligned crop
            # Use identity rotation matrix (no rotation)
            R = cp.eye(2)

            # Translation to center the face without rotation
            T = dst_mean - scale * src_mean

            # Construct transformation matrix
            M = cp.zeros((2, 3))
            M[0:2, 0:2] = scale * R
            M[:, 2] = T

        # Crop using affine transformation
        cropped_image = px.affine_transform(image, M, (size, size))

        return cropped_image, M

    def crop(
        self, image: cp.ndarray, kps: cp.ndarray, size: int = 512, padding: float = 0.0, normalize_rotation: bool = True
    ) -> tuple[cp.ndarray, cp.ndarray]:
        """Crop face image using keypoints with optional padding and rotation normalization

        Args:
            image: Input image
            kps: Keypoints for face alignment
            size: Target output size
            padding: Padding ratio (0.0 to 1.0) to include more context around the face
            normalize_rotation: If False, preserves original face rotation

        Returns:
            Cropped face image and transformation matrix
        """
        # Use custom implementation with padding and rotation control
        output_image, matrix = self.crop_from_kps_with_padding(image, kps, size * 2, padding, normalize_rotation)

        # Resize to target size
        output_image = px.resize(output_image, (size, size), interpolation=px.INTER_AUTO)
        matrix /= 2

        return output_image, matrix


class OnnxFaceDetection(BaseFaceDetection):
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

        input_cfg = self.session.get_inputs()[0]
        input_shape = input_cfg.shape
        if not isinstance(input_shape[2], str):
            self.input_size = tuple(input_shape[2:4][::-1])
        input_name = input_cfg.name
        self.input_shape = input_shape
        outputs = self.session.get_outputs()
        output_names = []
        for o in outputs:
            output_names.append(o.name)
        self.input_name = input_name
        self.output_names = output_names

        self.input_mean = 127.5 / 255.0
        self.input_std = 128.0 / 255.0

        # Initialize face detection variables based on output count
        num_outputs = len(output_names)
        self.use_kps = False
        self._anchor_ratio = 1.0
        self._num_anchors = 1

        if num_outputs == 6:
            self.fmc = 3
            self._feat_stride_fpn = [8, 16, 32]
            self._num_anchors = 2
        elif num_outputs == 9:
            self.fmc = 3
            self._feat_stride_fpn = [8, 16, 32]
            self._num_anchors = 2
            self.use_kps = True
        elif num_outputs == 10:
            self.fmc = 5
            self._feat_stride_fpn = [8, 16, 32, 64, 128]
            self._num_anchors = 1
        elif num_outputs == 15:
            self.fmc = 5
            self._feat_stride_fpn = [8, 16, 32, 64, 128]
            self._num_anchors = 1
            self.use_kps = True

        # print("Face detection model initialized with")
        # print(f"    Input names: {[element.name for element in self.session.get_inputs()]}")
        # print(f"    Input shapes: {[element.shape for element in self.session.get_inputs()]}")
        # print(f"    Input Mean: {self.input_mean}, Input Std: {self.input_std}")
        # print(f"    Output names: {[element.name for element in self.session.get_outputs()]}")
        # print(f"    Output shapes: {[element.shape for element in self.session.get_outputs()]}")
        # print()
        # print(f"    Input sizes: {self.input_size}, anchors: {self._num_anchors}, feature strides: {self._feat_stride_fpn}")
        # print(f"    Using keypoints: {self.use_kps}")
        # print(f"    Feature map count: {self.fmc}")
        # print(f"    Device: {device}, Device ID: {device_id}")
        # print(f"    Providers: {self.session.get_providers()}")
        # print("OnnxFaceDetection initialized successfully.")

    def forward(self, image: cp.ndarray, threshold: float) -> tuple[list[cp.ndarray], list[cp.ndarray], list[cp.ndarray]]:
        scores_list = []
        bboxes_list = []
        kpss_list = []

        batch = px.images_to_batch(image, std=self.input_std, size=self.input_size, mean=self.input_mean)

        batch = px.to_numpy(batch)

        net_outs = self.session.run(self.output_names, {self.input_name: batch})
        # net_outs = [px.to_cupy(o) for o in net_outs]
        net_outs = [cp.asarray(o) for o in net_outs]

        input_height = batch.shape[2]
        input_width = batch.shape[3]
        fmc = self.fmc
        for idx, stride in enumerate(self._feat_stride_fpn):
            scores = net_outs[idx].astype(cp.float32)
            bbox_preds = net_outs[idx + fmc].astype(cp.float32)
            bbox_preds = bbox_preds * stride

            height = input_height // stride
            width = input_width // stride
            key = (height, width, stride)
            if key in self.center_cache:
                anchor_centers = self.center_cache[key]
            else:
                anchor_centers = cp.stack(cp.mgrid[:height, :width][::-1], axis=-1).astype(cp.float32)
                anchor_centers = (anchor_centers * stride).reshape((-1, 2))
                if self._num_anchors > 1:
                    anchor_centers = cp.stack([anchor_centers] * self._num_anchors, axis=1).reshape((-1, 2))
                if len(self.center_cache) < 100:
                    self.center_cache[key] = anchor_centers

            pos_inds = cp.where(scores >= threshold)[0]
            bboxes = self.distance2bbox(anchor_centers, bbox_preds)
            pos_scores = scores[pos_inds]
            pos_bboxes = bboxes[pos_inds]
            scores_list.append(pos_scores)
            bboxes_list.append(pos_bboxes)
            if self.use_kps:
                kps_preds = net_outs[idx + fmc * 2].astype(cp.float32) * stride
                kpss = self.distance2kps(anchor_centers, kps_preds)
                kpss = kpss.reshape((kpss.shape[0], -1, 2))
                pos_kpss = kpss[pos_inds]
                kpss_list.append(pos_kpss)
        return scores_list, bboxes_list, kpss_list


class TrtFaceDetection(BaseFaceDetection):
    def __init__(self, model_path: str | None = None, model_bytes: bytes | None = None, device: str = "cuda") -> None:
        super().__init__(model_path, model_bytes, device)
        # print("Initializing TRT Face Detection")

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
                    spatial_range=(640, 640, 640),
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

            # print("face detection engine loaded ✔  tensors:", self.engine)

            """Initialize processing"""
            # Prepare CuPy stream and device buffers
            self.stream = cp.cuda.Stream()
            self.d_inputs = {}
            self.d_outputs = {}

            # Automatically get tensor names
            input_names = []
            output_names = []

            for name in self.engine:
                # shape = self.ctx.get_tensor_shape(name)
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

            # Initialize face detection variables based on output count
            num_outputs = len(output_names)
            self.use_kps = False
            self._anchor_ratio = 1.0
            self._num_anchors = 1

            if num_outputs == 6:
                self.fmc = 3
                self._feat_stride_fpn = [8, 16, 32]
                self._num_anchors = 2
            elif num_outputs == 9:
                self.fmc = 3
                self._feat_stride_fpn = [8, 16, 32]
                self._num_anchors = 2
                self.use_kps = True
            elif num_outputs == 10:
                self.fmc = 5
                self._feat_stride_fpn = [8, 16, 32, 64, 128]
                self._num_anchors = 1
            elif num_outputs == 15:
                self.fmc = 5
                self._feat_stride_fpn = [8, 16, 32, 64, 128]
                self._num_anchors = 1
                self.use_kps = True

            # Get input size from the input tensor
            input_shape = list(self.d_inputs[self.input_tensor].shape)
            if len(input_shape) >= 4 and input_shape[2] > 0 and input_shape[3] > 0:
                self.input_size = (input_shape[3], input_shape[2])  # (width, height)

            # Buffer pool
            self.input_buffer = None
            self.output_buffer = None

            # print("TrtFaceDetection initialized with")
            # print(f"    Input names: {self.input_tensor}")
            # print(f"    Input size: {self.input_size}")
            # print(f"    Input shape: {self.d_inputs[self.input_tensor].shape}")
            # print(f"    Input Mean: {self.input_mean}, Input Std: {self.input_std}")
            # print(f"    Output names: {self.output_names}")
            # print(f"    Output shapes: {[self.d_outputs[name].shape for name in self.output_names]}")
            # print(
            #    f"    Input sizes: {self.input_size}, anchors: {self._num_anchors}, feature strides: {self._feat_stride_fpn}"
            # )
            # print(f"    Using keypoints: {self.use_kps}")
            # print(f"    Feature map count: {self.fmc}")
            # print(f"    Device: {device}, Device ID: {device_id}")
            # print("TrtFaceDetection initialized successfully.")

    def forward(self, image: cp.ndarray, threshold: float) -> tuple[list[cp.ndarray], list[cp.ndarray], list[cp.ndarray]]:
        """Forward pass using TensorRT"""
        # print("TrtFaceDetection: Running forward pass...")
        scores_list = []
        bboxes_list = []
        kpss_list = []

        # Convert images to batch format
        batch: cp.ndarray = px.images_to_batch(image, std=self.input_std, mean=self.input_mean)

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
        net_outs = []
        for name in self.output_names:
            output_data = self.d_outputs[name]
            net_outs.append(output_data)

        input_height = batch.shape[2]
        input_width = batch.shape[3]
        fmc = self.fmc

        for idx, stride in enumerate(self._feat_stride_fpn):
            scores = net_outs[idx].astype(cp.float32)
            bbox_preds = net_outs[idx + fmc].astype(cp.float32)
            bbox_preds = bbox_preds * stride

            height = input_height // stride
            width = input_width // stride
            key = (height, width, stride)
            if key in self.center_cache:
                anchor_centers = self.center_cache[key]
            else:
                anchor_centers = cp.stack(cp.mgrid[:height, :width][::-1], axis=-1).astype(cp.float32)
                anchor_centers = (anchor_centers * stride).reshape((-1, 2))
                if self._num_anchors > 1:
                    anchor_centers = cp.stack([anchor_centers] * self._num_anchors, axis=1).reshape((-1, 2))
                if len(self.center_cache) < 100:
                    self.center_cache[key] = anchor_centers

            pos_inds = cp.where(scores >= threshold)[0]
            bboxes = self.distance2bbox(anchor_centers, bbox_preds)
            pos_scores = scores[pos_inds]
            pos_bboxes = bboxes[pos_inds]
            scores_list.append(pos_scores)
            bboxes_list.append(pos_bboxes)
            if self.use_kps:
                kps_preds = net_outs[idx + fmc * 2].astype(cp.float32) * stride
                kpss = self.distance2kps(anchor_centers, kps_preds)
                kpss = kpss.reshape((kpss.shape[0], -1, 2))
                pos_kpss = kpss[pos_inds]
                kpss_list.append(pos_kpss)

        return scores_list, bboxes_list, kpss_list

        return scores_list, bboxes_list, kpss_list
