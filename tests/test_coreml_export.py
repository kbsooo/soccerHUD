#!/usr/bin/env python3
"""
CoreML 변환 테스트 스크립트

목적:
1. YOLOv8 → CoreML 변환
2. CoreML 모델 추론 테스트
3. PyTorch vs CoreML 성능 비교
"""

from ultralytics import YOLO
import numpy as np
import time
from pathlib import Path

def export_to_coreml(model_name='yolov8s'):
    """YOLOv8를 CoreML로 변환"""
    print("=" * 60)
    print(f"CoreML 변환: {model_name}")
    print("=" * 60)

    try:
        # 모델 로딩
        print(f"1. {model_name}.pt 로딩 중...")
        model = YOLO(f'{model_name}.pt')
        print("✓ 로딩 완료")

        # CoreML 변환
        print("\n2. CoreML 변환 시작...")
        print("   (이 작업은 1-2분 소요될 수 있습니다)")

        output_path = model.export(
            format='coreml',
            nms=True,  # NMS 포함
            imgsz=640,  # 입력 크기
        )

        print(f"✓ 변환 완료: {output_path}")

        # 파일 크기 확인
        if Path(output_path).exists():
            size_mb = Path(output_path).stat().st_size / (1024 * 1024)
            print(f"✓ 모델 크기: {size_mb:.1f} MB")

        print()
        return output_path

    except Exception as e:
        print(f"✗ CoreML 변환 실패: {e}")
        print()
        return None

def test_coreml_inference(coreml_path):
    """CoreML 모델 추론 테스트"""
    print("=" * 60)
    print("CoreML 모델 추론 테스트")
    print("=" * 60)

    if coreml_path is None or not Path(coreml_path).exists():
        print("✗ CoreML 모델 파일이 없습니다.")
        return

    try:
        # CoreML 모델 로딩
        print(f"CoreML 모델 로딩: {coreml_path}")
        model = YOLO(coreml_path)
        print("✓ 로딩 완료")

        # 더미 이미지 생성
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

        # 추론 테스트
        print("\n추론 테스트 중...")
        results = model(dummy_image, verbose=False)
        print("✓ 추론 성공")

        print()

    except Exception as e:
        print(f"✗ CoreML 추론 실패: {e}")
        print()

def benchmark_pytorch_vs_coreml(model_name='yolov8s', coreml_path=None):
    """PyTorch vs CoreML 성능 비교"""
    print("=" * 60)
    print("PyTorch vs CoreML 성능 비교")
    print("=" * 60)

    dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    num_iterations = 30

    # PyTorch (MPS)
    print("1. PyTorch + MPS")
    try:
        pt_model = YOLO(f'{model_name}.pt')

        # 워밍업
        for _ in range(5):
            _ = pt_model(dummy_image, device='mps', verbose=False)

        # 측정
        start = time.time()
        for _ in range(num_iterations):
            _ = pt_model(dummy_image, device='mps', verbose=False)
        end = time.time()

        pt_fps = num_iterations / (end - start)
        pt_time = (end - start) / num_iterations * 1000

        print(f"   FPS: {pt_fps:.1f}")
        print(f"   시간: {pt_time:.1f}ms")

    except Exception as e:
        print(f"   ✗ 실패: {e}")
        pt_fps = None

    # CoreML
    print("\n2. CoreML (Metal)")
    if coreml_path and Path(coreml_path).exists():
        try:
            coreml_model = YOLO(coreml_path)

            # 워밍업
            for _ in range(5):
                _ = coreml_model(dummy_image, verbose=False)

            # 측정
            start = time.time()
            for _ in range(num_iterations):
                _ = coreml_model(dummy_image, verbose=False)
            end = time.time()

            coreml_fps = num_iterations / (end - start)
            coreml_time = (end - start) / num_iterations * 1000

            print(f"   FPS: {coreml_fps:.1f}")
            print(f"   시간: {coreml_time:.1f}ms")

        except Exception as e:
            print(f"   ✗ 실패: {e}")
            coreml_fps = None
    else:
        print("   ⚠️ CoreML 모델 없음")
        coreml_fps = None

    # 비교
    print("\n3. 비교")
    if pt_fps and coreml_fps:
        improvement = (coreml_fps - pt_fps) / pt_fps * 100
        if improvement > 0:
            print(f"   CoreML이 {improvement:.1f}% 더 빠름")
        else:
            print(f"   PyTorch가 {abs(improvement):.1f}% 더 빠름")
    else:
        print("   ⚠️ 비교 불가")

    print()

def main():
    """메인 함수"""
    print("\n")
    print("🍎 CoreML 변환 및 테스트")
    print("\n")

    # yolov8s만 테스트 (실제 사용할 모델)
    model_name = 'yolov8s'

    # 1. CoreML 변환
    coreml_path = export_to_coreml(model_name)

    # 2. 추론 테스트
    if coreml_path:
        test_coreml_inference(coreml_path)

    # 3. 성능 비교
    benchmark_pytorch_vs_coreml(model_name, coreml_path)

    # 최종 정리
    print("=" * 60)
    print("요약")
    print("=" * 60)

    if coreml_path and Path(coreml_path).exists():
        print("✅ CoreML 변환 성공")
        print(f"   파일: {coreml_path}")
        print("\n다음 단계:")
        print("  - FastAPI 서버에서 CoreML 모델 사용")
        print("  - Electron 앱에 CoreML 모델 번들링")
    else:
        print("❌ CoreML 변환 실패")
        print("\n대안:")
        print("  - PyTorch + MPS 사용 (43 FPS)")
        print("  - 성능은 충분히 좋음")

    print()

if __name__ == "__main__":
    main()
