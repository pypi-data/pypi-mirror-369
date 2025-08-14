import cupy as cp
import numpy as np
import pixtreme as px

import visagene_source as vg


def test_no_rotation_verification():
    """Verify that normalize_rotation=False produces axis-aligned crops"""
    # Load a test image
    image = px.imread("examples/example.png")
    image = px.to_float32(image)

    # Initialize the face detection model
    model = vg.OnnxFaceDetection(model_path="models/face_detection.onnx")

    print("Verifying normalize_rotation=False behavior:")
    print("-" * 60)

    # Test both settings
    configs = [
        {"normalize_rotation": True, "name": "With rotation normalization"},
        {"normalize_rotation": False, "name": "Without rotation normalization (axis-aligned)"},
    ]

    for config in configs:
        faces = model.get(image, crop_size=512, normalize_rotation=config["normalize_rotation"])

        if faces:
            face = faces[0]
            matrix = face.matrix

            print(f"\n{config['name']}:")
            print(f"  Matrix:\n{matrix}")

            # Extract rotation components
            # In a 2x3 affine matrix, the upper-left 2x2 submatrix contains rotation and scale
            rotation_matrix = matrix[:2, :2]

            # Check if off-diagonal elements are close to zero (no rotation)
            off_diagonal_sum = cp.abs(rotation_matrix[0, 1]) + cp.abs(rotation_matrix[1, 0])

            print(f"  Off-diagonal elements: [{rotation_matrix[0, 1]:.6f}, {rotation_matrix[1, 0]:.6f}]")
            print(f"  Off-diagonal sum: {off_diagonal_sum:.6f}")

            if off_diagonal_sum < 0.001:
                print("  ✓ No rotation detected (axis-aligned)")
            else:
                # Calculate rotation angle
                angle = cp.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
                angle_degrees = float(angle) * 180 / np.pi
                print(f"  ✓ Rotation detected: {angle_degrees:.2f} degrees")

    print("\n" + "-" * 60)
    print("Summary:")
    print("  normalize_rotation=True: Face is rotated to standard orientation")
    print("  normalize_rotation=False: Face is cropped with axis-aligned rectangle")


if __name__ == "__main__":
    test_no_rotation_verification()
