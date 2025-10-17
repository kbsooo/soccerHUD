#!/usr/bin/env python3
"""
YOLOv8 축구 이미지 테스트 스크립트

목적:
1. 축구 관련 이미지에서 공과 선수 탐지
2. 탐지 정확도 확인
3. 시각화 결과 저장
"""

from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path
import urllib.request

def download_sample_image():
    """샘플 축구 이미지 다운로드"""
    print("=" * 60)
    print("샘플 축구 이미지 다운로드")
    print("=" * 60)

    # Ultralytics 샘플 이미지 (축구 경기 장면)
    sample_urls = [
        "https://ultralytics.com/images/zidane.jpg",  # 축구 선수
    ]

    output_dir = Path("sample_videos")
    output_dir.mkdir(exist_ok=True)

    downloaded_files = []

    for i, url in enumerate(sample_urls):
        output_path = output_dir / f"sample_{i+1}.jpg"

        if output_path.exists():
            print(f"✓ 이미 존재: {output_path}")
            downloaded_files.append(output_path)
            continue

        try:
            print(f"다운로드 중: {url}")
            urllib.request.urlretrieve(url, output_path)
            print(f"✓ 저장: {output_path}")
            downloaded_files.append(output_path)
        except Exception as e:
            print(f"✗ 다운로드 실패: {e}")

    print()
    return downloaded_files

def test_detection_on_image(model, image_path):
    """이미지에서 객체 탐지 테스트"""
    print("=" * 60)
    print(f"이미지 테스트: {image_path.name}")
    print("=" * 60)

    # 이미지 읽기
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"✗ 이미지를 읽을 수 없습니다: {image_path}")
        return None

    print(f"이미지 크기: {image.shape[1]}x{image.shape[0]}")

    # YOLO 추론
    print("YOLO 추론 실행 중...")
    results = model(image, verbose=False)

    # 결과 분석
    result = results[0]
    boxes = result.boxes

    print(f"✓ 총 탐지 객체 수: {len(boxes)}")

    # 클래스별 카운트
    class_counts = {}
    ball_detected = False
    person_count = 0

    for box in boxes:
        cls_id = int(box.cls[0])
        cls_name = model.names[cls_id]
        confidence = float(box.conf[0])

        if cls_name not in class_counts:
            class_counts[cls_name] = 0
        class_counts[cls_name] += 1

        if cls_name == 'sports ball':
            ball_detected = True
            print(f"  ⚽ 공 탐지! 신뢰도: {confidence:.2%}")
        elif cls_name == 'person':
            person_count += 1

    print(f"\n클래스별 탐지:")
    for cls_name, count in class_counts.items():
        print(f"  - {cls_name}: {count}개")

    # 축구 관련 평가
    print(f"\n축구 관련 평가:")
    print(f"  - 공 탐지: {'✓ YES' if ball_detected else '✗ NO'}")
    print(f"  - 선수 탐지: {person_count}명")

    # 시각화 저장
    output_dir = Path("test_results")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"result_{image_path.stem}.jpg"

    # 결과 이미지에 바운딩 박스 그리기
    annotated = result.plot()
    cv2.imwrite(str(output_path), annotated)
    print(f"\n✓ 결과 이미지 저장: {output_path}")

    print()
    return {
        'ball_detected': ball_detected,
        'person_count': person_count,
        'total_objects': len(boxes),
        'class_counts': class_counts
    }

def test_detection_speed(model):
    """추론 속도 테스트"""
    print("=" * 60)
    print("추론 속도 테스트 (더미 이미지)")
    print("=" * 60)

    import time

    # 640x640 더미 이미지 생성
    dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

    # 워밍업
    print("워밍업 (5회)...")
    for _ in range(5):
        _ = model(dummy_image, verbose=False)

    # 실제 측정
    num_iterations = 50
    print(f"측정 시작 ({num_iterations}회)...")

    start_time = time.time()
    for _ in range(num_iterations):
        _ = model(dummy_image, verbose=False)
    end_time = time.time()

    total_time = end_time - start_time
    avg_time = total_time / num_iterations
    fps = 1 / avg_time

    print(f"\n결과:")
    print(f"  - 총 시간: {total_time:.2f}초")
    print(f"  - 평균 시간: {avg_time*1000:.1f}ms")
    print(f"  - FPS: {fps:.1f}")

    # 평가
    if fps >= 30:
        print(f"  - 평가: ✅ 매우 우수 (30+ FPS)")
    elif fps >= 20:
        print(f"  - 평가: ✅ 우수 (20+ FPS)")
    elif fps >= 15:
        print(f"  - 평가: ⚠️ 보통 (15+ FPS)")
    else:
        print(f"  - 평가: ❌ 부족 (< 15 FPS)")

    print()
    return fps

def main():
    """메인 함수"""
    print("\n")
    print("⚽ YOLOv8 축구 이미지 테스트")
    print("\n")

    # 1. 모델 로딩
    print("=" * 60)
    print("YOLOv8 모델 로딩")
    print("=" * 60)
    model = YOLO('yolov8s.pt')
    print("✓ 모델 로딩 완료")
    print()

    # 2. 샘플 이미지 다운로드
    image_files = download_sample_image()

    if not image_files:
        print("⚠️ 샘플 이미지가 없습니다.")
        print("sample_videos/ 디렉토리에 축구 이미지를 추가하세요.")
        return

    # 3. 이미지 테스트
    results_summary = []
    for image_path in image_files:
        result = test_detection_on_image(model, image_path)
        if result:
            results_summary.append(result)

    # 4. 속도 테스트
    fps = test_detection_speed(model)

    # 5. 전체 요약
    print("=" * 60)
    print("전체 요약")
    print("=" * 60)

    if results_summary:
        total_balls = sum(1 for r in results_summary if r['ball_detected'])
        total_persons = sum(r['person_count'] for r in results_summary)

        print(f"테스트 이미지 수: {len(results_summary)}")
        print(f"공 탐지 이미지: {total_balls}/{len(results_summary)}")
        print(f"총 선수 탐지: {total_persons}명")

    print(f"평균 FPS: {fps:.1f}")

    # Go/No-Go 결정
    print("\n" + "=" * 60)
    print("Phase 0 검증 결과")
    print("=" * 60)

    if fps >= 20:
        print("✅ FPS 목표 달성 (20+ FPS)")
        go_fps = True
    else:
        print("❌ FPS 목표 미달 (< 20 FPS)")
        go_fps = False

    # 정확도는 실제 축구 영상 필요
    print("⚠️ 정확도 검증: 실제 축구 영상 필요")
    print("   → sample_videos/에 축구 영상을 추가하고")
    print("   → tests/test_yolo_video.py 실행")

    print("\n다음 단계:")
    if go_fps:
        print("  1. 실제 축구 영상으로 정확도 검증")
        print("  2. CoreML 변환 테스트")
        print("  3. Phase 1 백엔드 개발 시작")
    else:
        print("  1. 모델 경량화 고려 (yolov8n)")
        print("  2. 입력 해상도 조정")
        print("  3. 재측정")

    print()

if __name__ == "__main__":
    main()
