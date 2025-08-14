import pixtreme as px

import visagene_source as vg


def test_face_enhancement():
    # Load a test image
    image = px.imread("examples/example.png")
    image = px.to_float32(image)

    # Initialize the face detection model to get faces first
    detector = vg.OnnxFaceDetection(model_path="models/face_detection.onnx")
    faces = detector.get(image, crop_size=512)
    face_image = faces[0].image

    big_faces = detector.get(image, crop_size=2048)
    big_face_image = big_faces[0].image

    # Initialize the face enhancement model

    enhancer = vg.OnnxFaceEnhance(model_path="models/face_enhance.onnx")
    enhanced_face_image = enhancer.get(face_image)
    enhanced_face_image = px.resize(enhanced_face_image, (1024, 1024), interpolation=px.INTER_AUTO)

    sub_images = px.subsample_image(big_face_image, 4)
    enhanced_sub_images = enhancer.batch_get(sub_images)
    composited_image = px.subsample_image_back(enhanced_sub_images, 4)
    composited_image = px.resize(composited_image, (1024, 1024), interpolation=px.INTER_AREA)

    # Display results
    px.imshow("Original Face", face_image)
    px.imshow("Enhanced Face", enhanced_face_image)
    px.imshow("Composited Enhanced Image", composited_image)

    print(f"Full image enhanced shape: {enhanced_face_image.shape}")

    px.waitkey(0)
    px.destroy_all_windows()


if __name__ == "__main__":
    test_face_enhancement()
