import os

import cupy as cp
import pixtreme as px
import tensorrt as trt

import visagene_source as vg


def test_face_detection():
    # Load a test image
    image = px.imread("examples/example.png")
    image = px.to_float32(image)

    # Initialize the face detection model
    model = vg.OnnxFaceDetection(model_path="models/face_detection.onnx")

    faces = model.get(image)

    print(f"Detected {len(faces)} faces.")
    for i, face in enumerate(faces):
        print(f"type(face): {type(face)}")
        print(f"Face bbox: {face.bbox}, score: {face.score}, kps: {face.kps}, matrix: {face.matrix}")
        px.imshow(f"Onnx Detected Face {i}", face.image)

    engine = vg.TrtFaceDetection(model_path="models/face_detection.onnx")
    faces_trt = engine.get(image)

    print(f"Detected {len(faces_trt)} faces (TensorRT).")
    for i, face in enumerate(faces_trt):
        print(f"type(face): {type(face)}")
        print(f"Face bbox: {face.bbox}, score: {face.score}, kps: {face.kps}, matrix: {face.matrix}")
        px.imshow(f"Trt Detected Face {i}", face.image)

    px.waitkey(0)
    px.destroy_all_windows()


def test_face_detection_with_padding():
    """Test face detection with padding functionality"""
    # Load a test image
    image = px.imread("examples/example.png")
    image = px.to_float32(image)

    # Initialize the face detection model
    model = vg.OnnxFaceDetection(model_path="models/face_detection.onnx")

    # Test without padding
    faces_no_padding = model.get(image, crop_size=512, padding=0.0)

    # Test with padding
    faces_with_padding = model.get(image, crop_size=512, padding=0.2)

    print(f"\nTesting padding functionality:")
    print(f"Detected {len(faces_no_padding)} faces without padding")
    print(f"Detected {len(faces_with_padding)} faces with padding (0.2)")

    # Verify same number of faces detected
    assert len(faces_no_padding) == len(faces_with_padding), "Different number of faces detected with padding"

    # Compare results
    for i in range(len(faces_no_padding)):
        face_no_pad = faces_no_padding[i]
        face_with_pad = faces_with_padding[i]

        print(f"\nFace {i}:")
        print(f"  No padding - bbox: {face_no_pad.bbox[:4]}")
        print(f"  With padding - bbox: {face_with_pad.bbox[:4]}")
        print(f"  BBox should be same (original coords): {cp.allclose(face_no_pad.bbox, face_with_pad.bbox)}")

        print(f"  No padding - matrix shape: {face_no_pad.matrix.shape}")
        print(f"  With padding - matrix shape: {face_with_pad.matrix.shape}")
        print(f"  Matrix different (due to padding): {not cp.allclose(face_no_pad.matrix, face_with_pad.matrix)}")

        # Calculate and display padding information
        crop_size = 512
        padding_ratio = 0.2
        padded_size = int(crop_size * (1 + padding_ratio))
        pixel_difference = padded_size - crop_size

        print(f"\n  Padding calculation (padding={padding_ratio}):")
        print(f"    Original crop size: {crop_size}x{crop_size} pixels")
        print(f"    Padded crop size: {padded_size}x{padded_size} pixels")
        print(f"    Extra pixels per side: {pixel_difference // 2} pixels")
        print(f"    Total extra pixels: {pixel_difference} pixels")

        # Display matrix values to show the difference
        print(f"\n  Matrix comparison:")
        print(f"    No padding matrix:\n{face_no_pad.matrix}")
        print(f"    With padding matrix:\n{face_with_pad.matrix}")

        # Display images side by side
        px.imshow(f"Face {i} - No Padding", face_no_pad.image)
        px.imshow(f"Face {i} - With Padding (0.2)", face_with_pad.image)

    px.waitkey(0)
    px.destroy_all_windows()


if __name__ == "__main__":
    test_face_detection()
    test_face_detection_with_padding()
