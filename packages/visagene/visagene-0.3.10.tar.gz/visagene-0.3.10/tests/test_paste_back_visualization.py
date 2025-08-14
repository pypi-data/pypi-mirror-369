import cupy as cp
import pixtreme as px

import visagene_source as vg
from visagene_source.paste import paste_back


def visualize_padding_and_rotation():
    """Visualize padding and rotation effects using paste_back"""
    # Load a test image
    image = px.imread("examples/example.png")
    image = px.to_float32(image)

    # Initialize the face detection model
    model = vg.OnnxFaceDetection(model_path="models/face_detection.onnx")

    print("Visualizing padding and rotation effects with paste_back:")
    print("-" * 60)

    # Test different configurations
    configs = [
        {"padding": 0.0, "normalize_rotation": True, "color": [1.0, 0.8, 0.8], "name": "Normal"},
        {"padding": 0.2, "normalize_rotation": True, "color": [0.8, 1.0, 0.8], "name": "Padding 0.2"},
        {"padding": 0.0, "normalize_rotation": False, "color": [0.8, 0.8, 1.0], "name": "No Rotation Norm"},
        {"padding": 0.2, "normalize_rotation": False, "color": [1.0, 1.0, 0.8], "name": "Padding + No Rot"},
    ]

    # Create a copy of the original image for visualization
    result_image = image.copy()

    for config in configs:
        faces = model.get(image, crop_size=512, padding=config["padding"], normalize_rotation=config["normalize_rotation"])

        if faces:
            face = faces[0]

            # Apply color tint to the face image
            tinted_face = face.image.copy()
            color = cp.array(config["color"]).reshape(1, 1, 3)
            tinted_face = tinted_face * color  # Apply color tint

            # Create a simple mask (you can adjust the blur for smoother blending)
            mask = cp.ones((tinted_face.shape[0], tinted_face.shape[1], 3), dtype=cp.float32) * 0.7

            # Add a border to show the crop area
            border_width = 5
            tinted_face[:border_width, :] = color
            tinted_face[-border_width:, :] = color
            tinted_face[:, :border_width] = color
            tinted_face[:, -border_width:] = color

            # Paste back to result image
            result_image = paste_back(result_image, tinted_face, face.matrix, mask)

            print(f"\n{config['name']}:")
            print(f"  Padding: {config['padding']}")
            print(f"  Normalize rotation: {config['normalize_rotation']}")
            print(f"  Color tint: {config['color']}")
            print(f"  Matrix:\n{face.matrix}")

    # Save the result
    output_path = "paste_back_visualization.png"
    px.imwrite(output_path, result_image)
    print(f"\nVisualization saved to: {output_path}")

    # Also save individual examples for comparison
    for i, config in enumerate(configs):
        faces = model.get(image, crop_size=512, padding=config["padding"], normalize_rotation=config["normalize_rotation"])
        if faces:
            face = faces[0]
            individual_path = f"face_example_{i}_{config['name'].replace(' ', '_')}.png"
            px.imwrite(individual_path, face.image)
            print(f"Individual face saved to: {individual_path}")

    print("\n" + "-" * 60)
    print("Color coding:")
    print("  Red tint: Normal (no padding, with rotation normalization)")
    print("  Green tint: With padding 0.2")
    print("  Blue tint: Without rotation normalization")
    print("  Yellow tint: Both padding and no rotation normalization")


if __name__ == "__main__":
    visualize_padding_and_rotation()
