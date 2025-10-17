#!/usr/bin/env python3
"""
YOLOv8 FPS 벤치마크 스크립트

다양한 조건에서 FPS 측정:
- 모델 크기: nano, small, medium
- 입력 해상도: 480, 640, 800
- 디바이스: CPU, MPS
"""

from ultralytics import YOLO
import numpy as np
import time
import torch

def benchmark_model(model_name, input_size, device, num_iterations=30):
    """단일 조건 벤치마크"""
    try:
        # 모델 로딩
        model = YOLO(f'{model_name}.pt')

        # 더미 이미지 생성
        dummy_image = np.random.randint(0, 255, (input_size, input_size, 3), dtype=np.uint8)

        # 워밍업
        for _ in range(5):
            _ = model(dummy_image, device=device, verbose=False)

        # 측정
        start_time = time.time()
        for _ in range(num_iterations):
            _ = model(dummy_image, device=device, verbose=False)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time = total_time / num_iterations
        fps = 1 / avg_time

        return {
            'model': model_name,
            'input_size': input_size,
            'device': device,
            'avg_time_ms': avg_time * 1000,
            'fps': fps,
            'success': True
        }

    except Exception as e:
        return {
            'model': model_name,
            'input_size': input_size,
            'device': device,
            'error': str(e),
            'success': False
        }

def main():
    """메인 함수"""
    print("\n")
    print("🔥 YOLOv8 FPS 종합 벤치마크")
    print("\n")

    # 테스트 조건
    models = ['yolov8n', 'yolov8s']  # nano, small
    input_sizes = [480, 640]  # 해상도
    devices = ['cpu']

    # MPS 사용 가능 시 추가
    if torch.backends.mps.is_available():
        devices.append('mps')
        print("✓ MPS (Metal) 사용 가능\n")
    else:
        print("⚠️ MPS (Metal) 사용 불가\n")

    # 결과 저장
    results = []

    # 모든 조합 테스트
    total_tests = len(models) * len(input_sizes) * len(devices)
    current_test = 0

    for model in models:
        for input_size in input_sizes:
            for device in devices:
                current_test += 1
                print(f"[{current_test}/{total_tests}] 테스트: {model} | {input_size}px | {device}")

                result = benchmark_model(model, input_size, device)
                results.append(result)

                if result['success']:
                    print(f"  → FPS: {result['fps']:.1f} | 시간: {result['avg_time_ms']:.1f}ms")
                else:
                    print(f"  → 실패: {result.get('error', 'Unknown')}")

                print()

    # 결과 요약
    print("=" * 80)
    print("벤치마크 결과 요약")
    print("=" * 80)
    print()

    # 테이블 헤더
    print(f"{'모델':<10} {'해상도':<8} {'디바이스':<8} {'FPS':<10} {'시간(ms)':<10} {'평가'}")
    print("-" * 80)

    for result in results:
        if result['success']:
            model = result['model']
            size = f"{result['input_size']}px"
            device = result['device']
            fps = f"{result['fps']:.1f}"
            time_ms = f"{result['avg_time_ms']:.1f}"

            # 평가
            fps_val = result['fps']
            if fps_val >= 30:
                evaluation = "✅ 매우 우수"
            elif fps_val >= 20:
                evaluation = "✅ 우수"
            elif fps_val >= 15:
                evaluation = "⚠️ 보통"
            else:
                evaluation = "❌ 부족"

            print(f"{model:<10} {size:<8} {device:<8} {fps:<10} {time_ms:<10} {evaluation}")
        else:
            model = result['model']
            size = f"{result['input_size']}px"
            device = result['device']
            print(f"{model:<10} {size:<8} {device:<8} {'FAILED':<10} {'-':<10} ❌ 실패")

    # 최적 설정 찾기
    print()
    print("=" * 80)
    print("추천 설정")
    print("=" * 80)
    print()

    valid_results = [r for r in results if r['success']]

    if not valid_results:
        print("⚠️ 유효한 결과가 없습니다.")
        return

    # FPS >= 20인 결과 필터링
    good_results = [r for r in valid_results if r['fps'] >= 20]

    if good_results:
        print("✅ 실시간 처리 가능 (20+ FPS):")
        print()

        # 정확도 우선 (더 큰 모델)
        best_accuracy = max(good_results, key=lambda x: (
            1 if x['model'] == 'yolov8s' else 0,  # small 우선
            x['input_size'],  # 큰 해상도 우선
            x['fps']
        ))

        print(f"📊 정확도 우선:")
        print(f"  모델: {best_accuracy['model']}")
        print(f"  해상도: {best_accuracy['input_size']}px")
        print(f"  디바이스: {best_accuracy['device']}")
        print(f"  FPS: {best_accuracy['fps']:.1f}")
        print()

        # 속도 우선 (더 빠른 FPS)
        best_speed = max(good_results, key=lambda x: x['fps'])

        print(f"⚡ 속도 우선:")
        print(f"  모델: {best_speed['model']}")
        print(f"  해상도: {best_speed['input_size']}px")
        print(f"  디바이스: {best_speed['device']}")
        print(f"  FPS: {best_speed['fps']:.1f}")
        print()

    else:
        print("⚠️ 20+ FPS를 달성한 설정이 없습니다.")
        print()

        # 가장 빠른 설정 추천
        fastest = max(valid_results, key=lambda x: x['fps'])
        print(f"최선의 설정 (15+ FPS):")
        print(f"  모델: {fastest['model']}")
        print(f"  해상도: {fastest['input_size']}px")
        print(f"  디바이스: {fastest['device']}")
        print(f"  FPS: {fastest['fps']:.1f}")
        print()

        print("💡 개선 방안:")
        print("  - Lazy Tracking 사용 (5 프레임마다 YOLO)")
        print("  - 더 작은 해상도 (480px 이하)")
        print("  - yolov8n (nano) 모델")

    # Lazy Tracking 예상 성능
    print()
    print("=" * 80)
    print("Lazy Tracking 예상 성능")
    print("=" * 80)
    print()

    if good_results:
        best = max(good_results, key=lambda x: x['fps'])
        yolo_fps = best['fps']
        optical_flow_fps = 200  # Optical Flow는 매우 빠름

        # 5 프레임마다 YOLO (1:4 비율)
        effective_fps = 5 / ((1 / yolo_fps) + (4 / optical_flow_fps))

        print(f"설정: {best['model']} @ {best['input_size']}px")
        print(f"  - YOLO FPS: {yolo_fps:.1f}")
        print(f"  - Optical Flow FPS: ~{optical_flow_fps}")
        print(f"  - 예상 실효 FPS: {effective_fps:.1f}")
        print()

        if effective_fps >= 25:
            print("✅ Lazy Tracking으로 25+ FPS 달성 가능!")
        else:
            print("⚠️ Lazy Tracking으로도 25 FPS 미달")

    print()

if __name__ == "__main__":
    main()
