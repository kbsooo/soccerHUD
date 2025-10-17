#!/usr/bin/env python3
"""
YOLOv8 기본 테스트 스크립트

목적:
1. YOLOv8 모델 로딩 확인
2. 사전학습 모델(COCO)로 추론 테스트
3. 'sports ball', 'person' 클래스 확인
"""

from ultralytics import YOLO
import torch
import platform

def test_yolo_installation():
    """YOLOv8 설치 확인"""
    print("=" * 60)
    print("1. YOLOv8 설치 확인")
    print("=" * 60)

    print(f"✓ Ultralytics version: {YOLO.__version__ if hasattr(YOLO, '__version__') else 'OK'}")
    print(f"✓ PyTorch version: {torch.__version__}")
    print(f"✓ Platform: {platform.system()} {platform.machine()}")

    # MPS (Metal Performance Shaders) 사용 가능 여부 확인 (Mac M-series)
    if torch.backends.mps.is_available():
        print("✓ MPS (Metal) available: YES")
    else:
        print("⚠ MPS (Metal) available: NO")

    print()

def test_model_loading():
    """YOLOv8 모델 로딩 테스트"""
    print("=" * 60)
    print("2. YOLOv8 모델 로딩 테스트")
    print("=" * 60)

    try:
        # YOLOv8-small 모델 다운로드 및 로딩
        print("YOLOv8-small 모델 다운로드 중...")
        model = YOLO('yolov8s.pt')
        print("✓ 모델 로딩 성공")

        # 모델 정보 출력
        print(f"✓ 모델 타입: {type(model)}")
        print(f"✓ 클래스 수: {len(model.names)}")

        # COCO 데이터셋 클래스 확인
        print("\n주요 클래스:")
        for idx, name in model.names.items():
            if name in ['person', 'sports ball', 'ball']:
                print(f"  - {idx}: {name}")

        print()
        return model

    except Exception as e:
        print(f"✗ 모델 로딩 실패: {e}")
        return None

def test_dummy_inference(model):
    """더미 이미지로 추론 테스트"""
    print("=" * 60)
    print("3. 더미 이미지 추론 테스트")
    print("=" * 60)

    if model is None:
        print("✗ 모델이 로딩되지 않아 테스트를 건너뜁니다.")
        return

    try:
        # 더미 이미지 생성 (640x640, RGB)
        import numpy as np
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

        print("더미 이미지로 추론 실행 중...")
        results = model(dummy_image, verbose=False)

        print("✓ 추론 성공")
        print(f"✓ 결과 타입: {type(results)}")
        print(f"✓ 탐지 객체 수: {len(results[0].boxes)}")

        print()

    except Exception as e:
        print(f"✗ 추론 실패: {e}")

def test_device_compatibility(model):
    """디바이스 호환성 테스트"""
    print("=" * 60)
    print("4. 디바이스 호환성 테스트")
    print("=" * 60)

    if model is None:
        print("✗ 모델이 로딩되지 않아 테스트를 건너뜁니다.")
        return

    # CPU 테스트
    print("CPU 디바이스 테스트...")
    try:
        import numpy as np
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        results = model(dummy_image, device='cpu', verbose=False)
        print("✓ CPU 추론 성공")
    except Exception as e:
        print(f"✗ CPU 추론 실패: {e}")

    # MPS 테스트 (Mac M-series)
    if torch.backends.mps.is_available():
        print("\nMPS (Metal) 디바이스 테스트...")
        try:
            dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            results = model(dummy_image, device='mps', verbose=False)
            print("✓ MPS 추론 성공")
        except Exception as e:
            print(f"⚠ MPS 추론 실패 (CPU로 fallback): {e}")

    print()

def main():
    """메인 함수"""
    print("\n")
    print("🔍 YOLOv8 기본 테스트 시작")
    print("\n")

    # 1. 설치 확인
    test_yolo_installation()

    # 2. 모델 로딩
    model = test_model_loading()

    # 3. 더미 추론
    test_dummy_inference(model)

    # 4. 디바이스 호환성
    test_device_compatibility(model)

    print("=" * 60)
    print("✅ 모든 기본 테스트 완료")
    print("=" * 60)
    print("\n다음 단계: tests/test_yolo_video.py로 실제 영상 테스트")
    print()

if __name__ == "__main__":
    main()
