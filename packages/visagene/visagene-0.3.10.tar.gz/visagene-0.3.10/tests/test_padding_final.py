import cupy as cp
import pixtreme as px

import visagene_source as vg


def test_final_padding():
    """Final test to confirm padding functionality"""
    # Load a test image
    image = px.imread("examples/example.png")
    image = px.to_float32(image)

    # Initialize the face detection model
    model = vg.OnnxFaceDetection(model_path="models/face_detection.onnx")

    print("Testing padding functionality:")
    print("-" * 50)

    # Test with different padding values
    for padding in [0.0, 0.2, 0.4]:
        faces = model.get(image, crop_size=512, padding=padding)

        if faces:
            face = faces[0]
            print(f"\nPadding = {padding}:")
            print(f"  Face image shape: {face.image.shape}")
            print(f"  BBox (original coords): {face.bbox[:4]}")
            print(f"  Matrix shape: {face.matrix.shape}")
            print(f"  Matrix values:\n{face.matrix}")

            # Save for visual comparison
            output_path = f"final_test_padding_{padding}.png"
            px.imwrite(output_path, face.image)
            print(f"  Saved to: {output_path}")

    print("\n" + "-" * 50)
    print("Padding calculation for crop_size=512:")
    print(f"  padding=0.0 → crops 1024x1024, resizes to 512x512")
    print(f"  padding=0.2 → crops 1024x1024 with face 20% smaller")
    print(f"  padding=0.4 → crops 1024x1024 with face 40% smaller")
    print("\nThe larger the padding, the more background is included.")


if __name__ == "__main__":
    test_final_padding()
