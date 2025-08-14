import cupy as cp
import pixtreme as px

import visagene_source as vg
from visagene_source.paste import paste_back


def test_paste_back_individual():
    """Test paste_back with individual results"""
    # Load a test image
    image = px.imread("examples/example.png")
    image = px.to_float32(image)

    # Initialize the face detection model
    model = vg.OnnxFaceDetection(model_path="models/face_detection.onnx")

    print("Testing paste_back with padding=0.2, normalize_rotation=False")
    print("-" * 60)

    # Detect face with padding and no rotation normalization
    faces = model.get(image, crop_size=512, padding=1.0, normalize_rotation=True)

    if not faces:
        print("No faces detected!")
        return

    face = faces[0]
    print(f"Face detected:")
    print(f"  BBox: {face.bbox[:4]}")
    print(f"  Image shape: {face.image.shape}")
    print(f"  Matrix:\n{face.matrix}")

    # Create a copy of the original image for paste_back
    result_image = image.copy()

    # Apply a color tint to make the effect visible
    tinted_face = face.image.copy()
    # Apply green tint
    tinted_face[:, :, 0] *= 0.7  # Reduce red
    tinted_face[:, :, 1] *= 1.2  # Increase green
    tinted_face[:, :, 2] *= 0.7  # Reduce blue
    tinted_face = cp.clip(tinted_face, 0, 1)

    # Add a border to show the crop area
    border = 10
    # Green border
    green = cp.array([0, 1, 0], dtype=cp.float32)
    tinted_face[:border, :] = green
    tinted_face[-border:, :] = green
    tinted_face[:, :border] = green
    tinted_face[:, -border:] = green

    # Create a soft mask for better blending
    mask = cp.ones((tinted_face.shape[0], tinted_face.shape[1], 3), dtype=cp.float32)
    # Create a gradient mask from center
    y, x = cp.mgrid[: mask.shape[0], : mask.shape[1]]
    center_y, center_x = mask.shape[0] / 2, mask.shape[1] / 2
    dist = cp.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
    max_dist = cp.sqrt(center_x**2 + center_y**2)
    mask = 1 - (dist / max_dist) * 0.3  # Soft fade at edges
    mask = cp.stack([mask, mask, mask], axis=2)

    # Apply paste_back
    result = paste_back(result_image, tinted_face, face.matrix, mask)

    # Save the result
    output_path = "paste_back_padding_0.2_no_rotation.png"
    px.imwrite(output_path, result)
    print(f"\nResult saved to: {output_path}")

    # Also test with normal settings for comparison
    faces_normal = model.get(image, crop_size=512, padding=0.0, normalize_rotation=True)
    if faces_normal:
        face_normal = faces_normal[0]
        result_normal = image.copy()

        # Apply red tint for normal face
        tinted_normal = face_normal.image.copy()
        tinted_normal[:, :, 0] *= 1.2  # Increase red
        tinted_normal[:, :, 1] *= 0.7  # Reduce green
        tinted_normal[:, :, 2] *= 0.7  # Reduce blue
        tinted_normal = cp.clip(tinted_normal, 0, 1)

        # Add red border
        red = cp.array([1, 0, 0], dtype=cp.float32)
        tinted_normal[:border, :] = red
        tinted_normal[-border:, :] = red
        tinted_normal[:, :border] = red
        tinted_normal[:, -border:] = red

        # Use same mask
        mask_normal = cp.ones((tinted_normal.shape[0], tinted_normal.shape[1], 3), dtype=cp.float32)

        result_normal = paste_back(result_normal, tinted_normal, face_normal.matrix, mask_normal)

        output_path_normal = "paste_back_normal.png"
        px.imwrite(output_path_normal, result_normal)
        print(f"Normal result saved to: {output_path_normal}")

    print("\n" + "-" * 60)
    print("Color coding:")
    print("  Green: With padding 0.2 and no rotation normalization")
    print("  Red: Normal (no padding, with rotation normalization)")


if __name__ == "__main__":
    test_paste_back_individual()
