import os

import cupy as cp
import pixtreme as px
import tensorrt as trt

import visagene_source as vg


def test_convert():
    px.onnx_to_trt_dynamic_shape(
        onnx_path="models/face_detection.onnx",
        engine_path="models/face_detection.trt",
        batch_range=(1, 1, 1),
        spatial_range=(16, 640, 4096),
    )

    px.onnx_to_trt_dynamic_shape(
        onnx_path="models/face_embedding.onnx",
        engine_path="models/face_embedding.trt",
        batch_range=(1, 1, 64),
        spatial_range=(112, 112, 112),
    )

    px.onnx_to_trt_dynamic_shape(
        onnx_path="models/reswapper_256-1567500_originalInswapperClassCompatible.dynamic.onnx",
        engine_path="models/reswapper_256-1567500_originalInswapperClassCompatible.dynamic.trt",
        batch_range=(1, 1, 64),
        spatial_range=(256, 256, 256),
    )

    px.onnx_to_trt_dynamic_shape(
        onnx_path="models/GFPGANv1.4.onnx",
        engine_path="models/GFPGANv1.4.trt",
        batch_range=(1, 1, 1),
        spatial_range=(512, 512, 512),
    )


if __name__ == "__main__":
    test_convert()
