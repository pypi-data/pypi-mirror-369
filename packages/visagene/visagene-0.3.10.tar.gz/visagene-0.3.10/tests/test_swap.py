import os

import cupy as cp
import pixtreme as px
import tensorrt as trt

import visagene_source as vg


def test_face_embeddings():
    # Load a test image
    source_image = px.imread("examples/example2.png")
    source_image = px.to_float32(source_image)
    target_image = px.imread("examples/example.png")
    target_image = px.to_float32(target_image)

    # Initialize the face detection model to get faces first
    detector = vg.TrtFaceDetection(model_path="models/face_detection.onnx")
    source_faces = detector.get(source_image)
    target_faces = detector.get(target_image)

    if len(source_faces) == 0 and len(target_faces) == 0:
        print("No faces detected for embedding test.")
        return

    print(f"Found {len(source_faces)} faces in source image for embedding extraction.")
    print(f"Found {len(target_faces)} faces in target image for embedding extraction.")

    source_face = source_faces[0]
    target_face = target_faces[0]

    # Initialize the face embedding models
    embedding = vg.TrtFaceEmbedding(model_path="models/face_embedding.onnx")
    source_latent = embedding.get(source_face)

    onnx_swapper = vg.OnnxFaceSwap(model_path="models/face_swap.onnx")
    trt_swapper = vg.TrtFaceSwap(model_path="models/face_swap.onnx")

    # Perform face swap using ONNX model
    onnx_swapped_image = onnx_swapper.get(target_face.image, source_latent)
    trt_swapped_image = trt_swapper.get(target_face.image, source_latent)

    px.imshow("Onnx Swapped Image", onnx_swapped_image)
    px.imshow("Trt Swapped Image", trt_swapped_image)

    px.waitkey(0)
    px.destroy_all_windows()


if __name__ == "__main__":
    test_face_embeddings()
