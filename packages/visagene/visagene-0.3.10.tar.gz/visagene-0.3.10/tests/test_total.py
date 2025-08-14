import os

import cupy as cp
import pixtreme as px
import tensorrt as trt

import visagene_source as vg


def test_face_swap():
    crop_size = 1024
    swap_size = 256
    dim = crop_size // swap_size
    print(f"Testing face swap with crop size {crop_size} and swap size {swap_size}.")
    print(f"Subsampling dimension: {dim} (crop_size // swap_size)")

    # Initialize the face detection model to get faces first
    detector = vg.OnnxFaceDetector(model_path="models/face_detection.onnx")

    # Initialize the face embedding model to get source embedding
    extractor = vg.OnnxFaceFeatureExtractor(model_path="models/face_embedding.onnx")

    # Initialize the face swap models
    swapper = vg.OnnxFaceSwapper(model_path="models/reswapper_256-1567500_originalInswapperClassCompatible.dynamic.onnx")

    # Initialize the face enhancement model
    enhancer = vg.OnnxFaceEnhancer(model_path="models/GFPGANv1.4.onnx")

    # Load test images
    source_image = px.imread("examples/example2.png")  # Source face
    target_image = px.imread("examples/example.png")  # Target face

    source_image = px.to_float32(source_image)
    target_image = px.to_float32(target_image)

    # Detect source face
    source_faces = detector.get(source_image, crop_size=crop_size)
    assert len(source_faces) > 0, "No source faces detected for swap test."
    assert len(source_faces) == 1, "Multiple source faces detected, expected only one."
    assert source_faces[0].image.shape == (crop_size, crop_size, 3), "Source face image shape mismatch."

    # Detect target face
    target_faces = detector.get(target_image, crop_size=crop_size)
    assert len(target_faces) > 0, "No target faces detected for swap test."
    assert len(target_faces) == 1, "Multiple target faces detected, expected only one."
    assert target_faces[0].image.shape == (crop_size, crop_size, 3), "Target face image shape mismatch."

    print(f"Found {len(source_faces)} source faces and {len(target_faces)} target faces.")

    # Get source face embedding
    source_face = source_faces[0]  # Use first detected face
    source_latent = extractor.get(source_face)
    assert source_latent is not None, "Failed to extract source face embedding."
    assert source_latent.shape == (1, 512), "Source face embedding shape mismatch."

    # Test both swap models
    target_face = target_faces[0]  # Use first detected target face
    px.imshow("Source Face", source_face.image)
    px.imshow("Target Face", target_face.image)

    print("\nProcessing face swap:")
    print(f"Source face bbox: {source_face.bbox}, score: {source_face.score}")
    print(f"Target face bbox: {target_face.bbox}, score: {target_face.score}")

    # Test ONNX swap
    print("Testing ONNX swap...")
    swapped_image = swapper.get(target_face.image, source_latent)
    px.imshow("Swapped Face", swapped_image)
    assert swapped_image is not None, "ONNX swap failed."
    if isinstance(swapped_image, list):
        print(f"ONNX swap result: {len(swapped_image)} images, first shape: {swapped_image[0].shape}")
        swapped_image = swapped_image[0]
    else:
        print(f"ONNX swap result shape: {swapped_image.shape}")

    # Test batch swap (ONNX)

    subsample_images = px.subsample_image(target_face.image, dim=dim)

    for i, img in enumerate(subsample_images):
        print(f"Subsampled image {i} shape: {img.shape}")
        assert img.shape == (swap_size, swap_size, 3), f"Subsampled image {i} shape mismatch: {img.shape}"
        # px.imshow(f"Subsampled Image {i}", img)

    print("Testing ONNX batch swap...")
    batch_swapped = swapper.batch_get(subsample_images, source_latent)
    assert batch_swapped is not None, "ONNX batch swap failed."

    for i, img in enumerate(batch_swapped):
        assert img.shape == (swap_size, swap_size, 3), f"Batch swapped image {i} shape mismatch: {img.shape}"
        print(f"Batch swapped image {i} shape: {img.shape}")
        # px.imshow(f"Batch Swapped Image {i}", img)
        px.imshow(f"Batch Swapped Face {i}", img)
        batch_swapped[i] = enhancer.get(img)
        px.imshow(f"Enhanced Batch Swapped Face {i}", batch_swapped[i])

    batch_swapped_image = px.subsample_image_back(batch_swapped, dim=dim)
    batch_swapped_image = px.resize(batch_swapped_image, fx=0.25, fy=0.25, interpolation=px.INTER_LINEAR)

    # Display results
    # px.imshow("Source Face", source_face.image)
    # px.imshow("Target Face", target_face.image)
    # px.imshow("Swapped Face", swapped_image)
    px.imshow("Batch Swapped Face", batch_swapped_image)

    px.waitkey(0)
    px.destroy_all_windows()


if __name__ == "__main__":
    test_face_swap()
