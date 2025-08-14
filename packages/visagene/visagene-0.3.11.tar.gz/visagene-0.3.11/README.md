# Visagene

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![CUDA](https://img.shields.io/badge/cuda-12.x-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Visagene is a high-performance face detection, recognition, and manipulation library with GPU acceleration support. It supports both ONNX Runtime and TensorRT for inference, providing features such as face detection, feature extraction, face swapping, and image enhancement.

## Key Features

- **Face Detection**: High-precision face detection with bounding boxes and keypoints
- **Feature Extraction**: Extract face embeddings for recognition and comparison
- **Face Swapping**: Natural face replacement from source to target images
- **Image Enhancement**: Face quality improvement using GFPGANv1.4
- **Segmentation**: Precise segmentation of facial features (eyes, nose, mouth, etc.)
- **Paste Back**: Natural blending of processed faces back to original images

## Technical Highlights

- **GPU Acceleration**: Fast GPU processing using CuPy
- **Flexible Inference**: Support for both ONNX Runtime and TensorRT
- **Memory Efficient**: Optimized GPU memory usage
- **Type Safe**: Data schemas defined with Pydantic
- **Extensible**: Easy to add new models by inheriting base classes

## Installation

### Prerequisites

- Python 3.10 or higher
- CUDA 12.x
- cuDNN 8.x or higher

### Install via pip

```bash
pip install visagene
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/visagene.git
cd visagene

# Install development dependencies
pip install -e ".[dev]"
```

## Usage

### Basic Face Detection

```python
import pixtreme as px
import visagene_source as vg

# Load image
image = px.imread("path/to/image.jpg")
image = px.to_float32(image)

# Initialize face detector
detector = vg.OnnxDetector(model_path="models/detection.onnx")

# Detect faces
faces = detector.get(image)

print(f"Detected {len(faces)} faces")
for face in faces:
    print(f"Bounding box: {face.bbox}")
    print(f"Confidence score: {face.score}")
```

### Face Swapping Pipeline

```python
# Initialize models
detector = vg.OnnxDetector(model_path="models/detection.onnx")
extractor = vg.OnnxExtractor(model_path="models/embedding.onnx")
swapper = vg.OnnxSwapper(model_path="models/swap.onnx")
enhancer = vg.OnnxEnhancer(model_path="models/enhance.onnx")

# Load source and target images
source_image = px.imread("source.jpg")
target_image = px.imread("target.jpg")

# Extract source face embedding
source_faces = detector.get(source_image)
source_embedding = extractor.get(source_faces[0])

# Detect target face and swap
target_faces = detector.get(target_image)
swapped_face = swapper.get(target_faces[0].image, source_embedding)

# Enhance face quality
enhanced_face = enhancer.get(swapped_face)

# Paste back to original image
result = vg.paste_back(target_image, enhanced_face, target_faces[0].matrix)
```

### High-Speed Inference with TensorRT

```python
# Use TensorRT versions of models
detector = vg.TrtDetector(model_path="models/detection.trt")
extractor = vg.TrtExtractor(model_path="models/embedding.trt")
swapper = vg.TrtSwapper(model_path="models/swap.trt")
enhancer = vg.TrtEnhancer(model_path="models/enhance.trt")

# Usage is identical
faces = detector.get(image)
```

## Model Architecture

### Class Hierarchy

```
BaseModelLoader
├── BaseDetector
│   ├── OnnxDetector
│   └── TrtDetector
├── BaseExtractor
│   ├── OnnxExtractor
│   └── TrtExtractor
├── BaseSwapper
│   ├── OnnxSwapper
│   └── TrtSwapper
├── BaseEnhancer
│   ├── OnnxEnhancer
│   └── TrtEnhancer
└── BaseSegmentation
    └── OnnxSegmentation
```

### Data Schema

The library uses Pydantic for type-safe data structures:

```python
class VisageneFace(BaseModel):
    bbox: cp.ndarray      # Bounding box (x1, y1, x2, y2)
    score: float          # Detection confidence score
    kps: cp.ndarray       # Facial keypoints
    matrix: cp.ndarray    # Affine transformation matrix
    image: cp.ndarray     # Cropped face image
```

## Dependencies

### Core Dependencies

- **numpy**: Numerical computing library
- **cupy-cuda12x** (>=13.4.1): CUDA-accelerated array library
- **onnxruntime-gpu** (>=1.22.0): ONNX inference engine
- **tensorrt** (>=10.11.0.33): NVIDIA TensorRT inference engine
- **pixtreme** (>=0.3.0): High-performance image processing library
- **pydantic**: Data validation and schema definition

### Development Dependencies

- **black**: Code formatter
- **pytest**: Testing framework
- **flake8**: Linter
- **isort**: Import sorter
- **cython**: C-extensions for Python
- **build tools**: setuptools, wheel, packaging

## Model Requirements

The library requires pre-trained ONNX models for operation. The models are not included in the repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

- **minamik** - *Initial work* - [mia@sync.dev](mailto:mia@sync.dev)

## Acknowledgments

- [ONNX Runtime](https://onnxruntime.ai/) - High-performance inference engine
- [TensorRT](https://developer.nvidia.com/tensorrt) - NVIDIA's high-speed inference library
- [CuPy](https://cupy.dev/) - GPU-accelerated computing with Python

