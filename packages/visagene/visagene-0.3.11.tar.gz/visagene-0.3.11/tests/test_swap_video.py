import os
import timeit

import cupy as cp
import pixtreme as px

import visagene_source as vg


def test_face_swap(source_dir: str, target_dir: str, output_dir: str, force: bool = False):
    # Initialize the face detection model to get faces first
    detector = vg.OnnxDetector(model_path="models/detection.onnx")

    # Initialize the face embedding model to get source embedding
    extractor = vg.OnnxExtractor(model_path="models/embedding.onnx")

    # Initialize the face enhancement model
    enhancer = vg.OnnxEnhancer(model_path="models/GFPGANv1.4.onnx")

    # Initialize the face swap models
    swapper = vg.OnnxSwapper(model_path="models/swap.onnx")

    mask = px.create_rounded_mask((512, 512), mask_offsets=(0.03, 0.03, 0.03, 0.03), blur_size=31, sigma=16)
    black_image = cp.zeros((512, 512, 3), dtype=cp.float32)

    source_pathes = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith((".png", ".jpg", ".jpeg")):
                source_pathes.append(os.path.join(root, file))

    target_pathes = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith((".png", ".jpg", ".jpeg")):
                target_pathes.append(os.path.join(root, file))

    for source_path in source_pathes:
        source_name = os.path.splitext(os.path.basename(source_path))[0]
        source_image = px.imread(source_path)  # Source face
        source_image = px.to_float32(source_image)

        # Detect source face
        source_faces = detector.get(source_image)
        if len(source_faces) == 0:
            print("No source faces detected for swap test.")
            continue

        # Get source face embedding
        source_face = source_faces[0]  # Use first detected face
        source_latent = extractor.get(source_face)
        print(f"Source embedding shape: {source_latent.shape}")

        for target_path in target_pathes:
            print(f"Processing swap from {source_path} to {target_path}")

            target_dit_name = os.path.dirname(target_path).split(os.sep)[-1]
            target_name = os.path.splitext(os.path.basename(target_path))[0]

            _output_dir = os.path.join(output_dir, target_dit_name)
            os.makedirs(_output_dir, exist_ok=True)

            output_path = os.path.join(_output_dir, f"swapped_{source_name}_vs_{target_name}.png")
            stacked_output_path = os.path.join(_output_dir, f"debug_{source_name}_vs_{target_name}.png")

            print(f"Source name: {source_name}")
            print(f"Target name: {target_name}")
            print(f"Output directory: {_output_dir}")
            print(f"Output path: {output_path}")
            print(f"Stacked output path: {stacked_output_path}")

            # Load test images
            target_image = px.imread(target_path)  # Target face
            target_image = px.to_float32(target_image)

            if os.path.exists(output_path) and os.path.exists(stacked_output_path) and not force:
                print(f"Output already exists: {output_path}, skipping.")
                continue

            # Detect target face
            target_faces = detector.get(target_image)
            if len(target_faces) == 0:
                print("No target faces detected for swap test.")

                px.imwrite(output_path, target_image)
                stacked_faces_image = px.stack_images(
                    [
                        px.resize(source_face.image, (512, 512), interpolation=px.INTER_AUTO),
                        black_image,
                        black_image,
                        black_image,
                        black_image,
                        black_image,
                        black_image,
                    ],
                    axis=0,
                )
                h, w = target_image.shape[:2]
                if h >= w:
                    stacked_images = px.stack_images([target_image, target_image, stacked_faces_image], axis=1)
                else:
                    _stacked_images = px.stack_images([target_image, target_image], axis=0)
                    stacked_images = px.stack_images([_stacked_images, stacked_faces_image], axis=1)
                px.imwrite(stacked_output_path, stacked_images)
                px.imshow("results", stacked_images)
                px.waitkey(1)

                continue

            print(f"Found {len(source_faces)} source faces and {len(target_faces)} target faces.")

            # Test swap models
            pasted_image = target_image.copy()
            source_face_image = source_face.image
            target_face_images = []
            enhanced_images = []

            for i, target_face in enumerate(target_faces):
                print(f"\nProcessing face swap {i}:")
                print(f"Target face bbox: {target_face.bbox}, score: {target_face.score}")

                try:
                    target_face_image = target_face.image

                    swapped_image = swapper.get(target_face_image, source_latent)
                    enhanced_image = enhancer.get(swapped_image)
                    pasted_image = vg.paste_back(
                        target_image=pasted_image, paste_image=enhanced_image, M=target_face.matrix, mask=mask
                    )

                    target_face_images.append(target_face_image)
                    enhanced_images.append(enhanced_image)

                except Exception as e:
                    print(f"Error during face swap: {e}")
                    continue

            max_face_count = 2
            stacked_faces = []

            stacked_faces.append(px.resize(source_face_image, (512, 512), interpolation=px.INTER_AUTO))

            for i in range(max_face_count):
                if i < len(target_face_images):
                    stacked_faces.append(px.resize(target_face_images[i], (512, 512), interpolation=px.INTER_AUTO))
                    stacked_faces.append(px.resize(enhanced_images[i], (512, 512), interpolation=px.INTER_AUTO))
                    stacked_faces.append(px.resize(enhanced_images[i], (512, 512), interpolation=px.INTER_AUTO) * mask)
                else:
                    stacked_faces.append(black_image)
                    stacked_faces.append(black_image)
                    stacked_faces.append(black_image)

            stacked_faces_image = px.stack_images(stacked_faces, axis=0)

            h, w = pasted_image.shape[:2]
            if h >= w:
                stacked_images = px.stack_images([target_image, pasted_image, stacked_faces_image], axis=1)
            else:
                _stacked_images = px.stack_images([target_image, pasted_image], axis=0)
                stacked_images = px.stack_images([_stacked_images, stacked_faces_image], axis=1)

            px.imwrite(output_path, pasted_image)
            px.imwrite(stacked_output_path, stacked_images)
            px.imshow("results", stacked_images)
            px.waitkey(1)
            print(f"Saved swapped image to {output_path}")

    px.destroy_all_windows()
    print("Face swap test completed.")


if __name__ == "__main__":
    source_dir = "Z:\\Projects\\rashisa\\01_swap\\source\\1_Vo"
    target_dir = "Z:\\Projects\\rashisa\\01_swap\\target"
    output_dir = "Z:\\Projects\\rashisa\\01_swap\\output2"
    os.makedirs(output_dir, exist_ok=True)

    test_face_swap(source_dir=source_dir, target_dir=target_dir, output_dir=output_dir, force=False)
