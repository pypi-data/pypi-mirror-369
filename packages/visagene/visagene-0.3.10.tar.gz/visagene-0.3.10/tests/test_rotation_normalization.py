import cupy as cp
import numpy as np
import pixtreme as px

import visagene_source as vg


def test_rotation_normalization():
    """Test rotation normalization functionality"""
    # Load a test image
    image = px.imread("examples/example.png")
    image = px.to_float32(image)

    # Initialize the face detection model
    model = vg.OnnxFaceDetection(model_path="models/face_detection.onnx")

    print("Testing rotation normalization functionality:")
    print("-" * 50)

    # Test with default (normalize_rotation=True)
    faces_normalized = model.get(image, crop_size=512, padding=0.0, normalize_rotation=True)

    # Test without rotation normalization
    faces_not_normalized = model.get(image, crop_size=512, padding=0.0, normalize_rotation=False)

    if faces_normalized and faces_not_normalized:
        face_norm = faces_normalized[0]
        face_no_norm = faces_not_normalized[0]

        print("\nWith rotation normalization (default):")
        print(f"  Matrix:\n{face_norm.matrix}")

        print("\nWithout rotation normalization:")
        print(f"  Matrix:\n{face_no_norm.matrix}")

        # Calculate the rotation angle from the matrix
        def get_rotation_angle(matrix):
            """Extract rotation angle from transformation matrix"""
            # The rotation part is in the upper-left 2x2 submatrix
            rotation_matrix = matrix[:2, :2]
            # Angle is atan2(sin, cos) where sin is M[1,0] and cos is M[0,0]
            # But we need to normalize by scale first
            scale = cp.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
            sin_theta = rotation_matrix[1, 0] / scale
            cos_theta = rotation_matrix[0, 0] / scale
            angle = cp.arctan2(sin_theta, cos_theta)
            return float(angle) * 180 / np.pi  # Convert to degrees

        angle_norm = get_rotation_angle(face_norm.matrix)
        angle_no_norm = get_rotation_angle(face_no_norm.matrix)

        print(f"\nRotation angles:")
        print(f"  With normalization: {angle_norm:.2f} degrees")
        print(f"  Without normalization: {angle_no_norm:.2f} degrees")

        # Save images for visual comparison
        px.imwrite("face_rotation_normalized.png", face_norm.image)
        px.imwrite("face_rotation_not_normalized.png", face_no_norm.image)

        print("\nImages saved:")
        print("  face_rotation_normalized.png - Face aligned to standard orientation")
        print("  face_rotation_not_normalized.png - Face in original orientation")

        # Check that the matrices are different
        matrix_diff = cp.abs(face_norm.matrix - face_no_norm.matrix).max()
        print(f"\nMax matrix difference: {matrix_diff}")

        if matrix_diff > 0.01:
            print("✓ Rotation normalization is working correctly")
        else:
            print("✗ Warning: Matrices are too similar, rotation normalization may not be working")

    print("\n" + "-" * 50)


if __name__ == "__main__":
    test_rotation_normalization()
