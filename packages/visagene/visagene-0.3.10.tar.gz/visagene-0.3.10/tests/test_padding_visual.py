import cupy as cp
import numpy as np
import pixtreme as px

import visagene_source as vg


def save_padding_comparison():
    """Save images to visually compare padding differences"""
    # Load a test image
    image = px.imread("examples/example.png")
    image = px.to_float32(image)

    # Initialize the face detection model
    model = vg.OnnxFaceDetection(model_path="models/face_detection.onnx")

    # Test with different padding values
    padding_values = [0.0, 0.2, 0.4]
    crop_size = 512

    print(f"Original image shape: {image.shape}")

    for padding in padding_values:
        faces = model.get(image, crop_size=crop_size, padding=padding)
        if faces:
            face = faces[0]

            # Calculate padding info
            padded_size = int(crop_size * (1 + padding))
            extra_pixels = padded_size - crop_size

            print(f"\nPadding={padding}:")
            print(f"  Crop size before resize: {padded_size}x{padded_size}")
            print(f"  Final image size: {face.image.shape}")
            print(f"  Extra pixels captured: {extra_pixels} ({extra_pixels // 2} per side)")

            # Save the cropped face image
            output_path = f"face_padding_{padding}.png"
            px.imwrite(output_path, face.image)
            print(f"  Saved to: {output_path}")

            # Also save a difference image if not the first one
            if padding > 0.0:
                faces_no_padding = model.get(image, crop_size=crop_size, padding=0.0)
                if faces_no_padding:
                    diff = cp.abs(face.image - faces_no_padding[0].image)
                    diff_normalized = diff / cp.max(diff) if cp.max(diff) > 0 else diff
                    diff_path = f"face_padding_diff_{padding}.png"
                    px.imwrite(diff_path, diff_normalized)
                    print(f"  Difference image saved to: {diff_path}")
                    print(f"  Max pixel difference: {cp.max(diff)}")
                    print(f"  Mean pixel difference: {cp.mean(diff)}")


if __name__ == "__main__":
    save_padding_comparison()
