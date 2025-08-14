import os

import cupy as cp
import pixtreme as px
import tensorrt as trt

import visagene_source as vg


def test_face_embeddings():
    # Load a test image
    image = px.imread("examples/example.png")
    image = px.to_float32(image)

    # Initialize the face detection model to get faces first
    detector = vg.OnnxFaceDetection(model_path="models/face_detection.onnx")
    faces = detector.get(image)

    if len(faces) == 0:
        print("No faces detected for embedding test.")
        return

    print(f"Found {len(faces)} faces for embedding extraction.")

    # Initialize the face embedding models
    onnx_embedding = vg.OnnxFaceEmbedding(model_path="models/face_embedding.onnx")
    trt_embedding = vg.TrtFaceEmbedding(model_path="models/face_embedding.onnx")

    for i, face in enumerate(faces):
        print(f"\nProcessing Face {i}:")
        print(f"Face bbox: {face.bbox}, score: {face.score}")

        # Extract embeddings using ONNX
        onnx_latent = onnx_embedding.get(face)
        print(f"ONNX Embedding shape: {onnx_latent.shape}")
        print(f"ONNX Embedding norm: {px.to_numpy(cp.linalg.norm(onnx_latent))}")

        # Extract embeddings using TensorRT
        trt_latent = trt_embedding.get(face)
        print(f"TRT Embedding shape: {trt_latent.shape}")
        print(f"TRT Embedding norm: {px.to_numpy(cp.linalg.norm(trt_latent))}")

        # Compare embeddings similarity
        similarity = px.to_numpy(cp.dot(onnx_latent.flatten(), trt_latent.flatten()))
        print(f"ONNX vs TRT similarity: {similarity}")

        # Display the face image
        px.imshow(f"Face {i} for Embedding", face.image)

    px.waitkey(0)
    px.destroy_all_windows()


if __name__ == "__main__":
    test_face_embeddings()
