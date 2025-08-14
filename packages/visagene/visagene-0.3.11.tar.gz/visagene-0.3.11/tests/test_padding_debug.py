import cupy as cp
import pixtreme as px

import visagene_source as vg


def debug_padding():
    """Debug padding implementation"""
    # Load a test image
    image = px.imread("examples/example.png")
    image = px.to_float32(image)

    # Initialize the face detection model
    model = vg.OnnxFaceDetection(model_path="models/face_detection.onnx")

    # Get face without any padding first
    faces = model.get(image, crop_size=512, padding=0.0)
    if not faces:
        print("No faces detected")
        return

    face = faces[0]
    kps = face.kps

    print("Debugging crop function behavior:")
    print(f"Original keypoints:\n{kps}")

    # Test original crop behavior
    size = 512
    output_orig, matrix_orig = px.crop_from_kps(image, kps, size * 2)
    print(f"\nOriginal crop (size * 2 = {size * 2}):")
    print(f"  Output shape before resize: {output_orig.shape}")
    output_resized = px.resize(output_orig, (size, size), interpolation=px.INTER_AUTO)
    print(f"  Output shape after resize: {output_resized.shape}")
    print(f"  Matrix before adjustment:\n{matrix_orig}")
    matrix_adjusted = matrix_orig / 2
    print(f"  Matrix after /2:\n{matrix_adjusted}")

    # Test with different sizes to understand the pattern
    test_sizes = [256, 512, 1024]
    for test_size in test_sizes:
        output_test, matrix_test = px.crop_from_kps(image, kps, test_size)
        print(f"\nTest with crop size {test_size}:")
        print(f"  Output shape: {output_test.shape}")
        print(f"  Matrix:\n{matrix_test}")


if __name__ == "__main__":
    debug_padding()
