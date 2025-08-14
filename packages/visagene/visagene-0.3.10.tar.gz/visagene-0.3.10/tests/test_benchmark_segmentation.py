import time

import cupy as cp
import numpy as np
import pixtreme as px

import visagene_source as vg


def benchmark_segmentation():
    """Benchmark segmentation models (ONNX vs TRT)"""
    # モデルパス
    model_path = "models/face_segmentation.onnx"

    # モデルの初期化
    print("=== Initializing Models ===")
    print("Loading ONNX model...")
    onnx_model = vg.OnnxSegmentation(model_path=model_path)

    print("\nLoading TRT model...")
    trt_model = vg.TrtSegmentation(model_path=model_path)

    # テスト画像の準備
    print("\n=== Preparing Test Images ===")
    image_path = "examples/example2.png"
    image = px.imread(image_path)
    image = px.to_float32(image)
    image = px.resize(image, (512, 512), interpolation=px.INTER_AUTO)

    # ウォームアップ
    print("\n=== Warming Up ===")
    warmup_iterations = 10

    print("ONNX warmup...")
    for _ in range(warmup_iterations):
        _ = onnx_model.get(image)

    print("TRT warmup...")
    for _ in range(warmup_iterations):
        _ = trt_model.get(image)

    # 単一画像ベンチマーク
    print("\n=== Single Image Benchmark ===")
    iterations = 100

    # ONNX単一画像
    print(f"\nONNX single image ({iterations} iterations):")
    start_time = time.time()
    for _ in range(iterations):
        _ = onnx_model.get(image)
    cp.cuda.Device().synchronize()  # GPU処理の完了を待つ
    onnx_single_time = time.time() - start_time
    onnx_single_avg = onnx_single_time / iterations * 1000  # ms
    print(f"  Total time: {onnx_single_time:.3f} seconds")
    print(f"  Average time per image: {onnx_single_avg:.3f} ms")
    print(f"  FPS: {iterations / onnx_single_time:.2f}")

    # TRT単一画像
    print(f"\nTRT single image ({iterations} iterations):")
    start_time = time.time()
    for _ in range(iterations):
        _ = trt_model.get(image)
    cp.cuda.Device().synchronize()
    trt_single_time = time.time() - start_time
    trt_single_avg = trt_single_time / iterations * 1000  # ms
    print(f"  Total time: {trt_single_time:.3f} seconds")
    print(f"  Average time per image: {trt_single_avg:.3f} ms")
    print(f"  FPS: {iterations / trt_single_time:.2f}")

    # 高速化比率
    speedup_single = onnx_single_avg / trt_single_avg
    print(f"\nSpeedup (single image): {speedup_single:.2f}x")

    # バッチ処理ベンチマーク
    print("\n=== Batch Processing Benchmark ===")
    batch_sizes = [4, 8, 16]

    for batch_size in batch_sizes:
        print(f"\n--- Batch size: {batch_size} ---")
        batch_images = [image] * batch_size
        batch_iterations = max(10, 100 // batch_size)  # バッチサイズに応じて反復回数を調整

        # ONNXバッチ処理
        print(f"ONNX batch ({batch_iterations} iterations):")
        start_time = time.time()
        for _ in range(batch_iterations):
            _ = onnx_model.batch_get(batch_images)
        cp.cuda.Device().synchronize()
        onnx_batch_time = time.time() - start_time
        onnx_batch_avg = onnx_batch_time / (batch_iterations * batch_size) * 1000
        print(f"  Total time: {onnx_batch_time:.3f} seconds")
        print(f"  Average time per image: {onnx_batch_avg:.3f} ms")
        print(f"  Throughput: {batch_iterations * batch_size / onnx_batch_time:.2f} images/sec")

        # TRTバッチ処理
        print(f"TRT batch ({batch_iterations} iterations):")
        start_time = time.time()
        for _ in range(batch_iterations):
            _ = trt_model.batch_get(batch_images)
        cp.cuda.Device().synchronize()
        trt_batch_time = time.time() - start_time
        trt_batch_avg = trt_batch_time / (batch_iterations * batch_size) * 1000
        print(f"  Total time: {trt_batch_time:.3f} seconds")
        print(f"  Average time per image: {trt_batch_avg:.3f} ms")
        print(f"  Throughput: {batch_iterations * batch_size / trt_batch_time:.2f} images/sec")

        # 高速化比率
        speedup_batch = onnx_batch_avg / trt_batch_avg
        print(f"Speedup (batch {batch_size}): {speedup_batch:.2f}x")

    # メモリ使用量の比較
    print("\n=== Memory Usage ===")
    print("Note: Memory usage is approximate and includes model weights")

    # 結果サマリー
    print("\n=== SUMMARY ===")
    print(f"Single image performance:")
    print(f"  ONNX: {onnx_single_avg:.3f} ms/image")
    print(f"  TRT:  {trt_single_avg:.3f} ms/image")
    print(f"  Speedup: {speedup_single:.2f}x")
    print(f"\nThroughput (single image):")
    print(f"  ONNX: {1000 / onnx_single_avg:.2f} FPS")
    print(f"  TRT:  {1000 / trt_single_avg:.2f} FPS")


def benchmark_precision():
    """精度の比較（オプション）"""
    print("\n=== Precision Comparison ===")
    model_path = "models/face_segmentation.onnx"

    # モデルの初期化
    onnx_model = vg.OnnxSegmentation(model_path=model_path)
    trt_model = vg.TrtSegmentation(model_path=model_path)

    # テスト画像
    image_path = "examples/example2.png"
    image = px.imread(image_path)
    image = px.to_float32(image)
    image = px.resize(image, (512, 512), interpolation=px.INTER_AUTO)

    # 推論実行
    onnx_result = onnx_model.get(image)
    trt_result = trt_model.get(image)

    # 結果の比較
    diff = cp.abs(onnx_result - trt_result)
    max_diff = cp.max(diff)
    mean_diff = cp.mean(diff)

    print(f"Maximum absolute difference: {max_diff}")
    print(f"Mean absolute difference: {mean_diff}")

    # ピクセル単位の一致率
    tolerance = 0.01
    matching_pixels = cp.sum(diff < tolerance)
    total_pixels = diff.size
    match_rate = matching_pixels / total_pixels * 100

    print(f"Pixel match rate (tolerance={tolerance}): {match_rate:.2f}%")


def test_segmentation():
    """Segmentation model test function"""
    print("=" * 60)
    print("Face Segmentation Benchmark: ONNX vs TensorRT")
    print("=" * 60)

    benchmark_segmentation()

    # 精度比較も実行する場合
    benchmark_precision()


if __name__ == "__main__":
    test_segmentation()
