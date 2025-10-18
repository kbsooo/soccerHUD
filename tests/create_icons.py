"""
크롬 익스텐션용 임시 아이콘 생성
"""

import cv2
import numpy as np
from pathlib import Path


def create_icon(size, output_path):
    """간단한 축구공 아이콘 생성"""
    # 흰색 배경
    img = np.ones((size, size, 3), dtype=np.uint8) * 255

    # 보라색 배경 (그라데이션)
    for y in range(size):
        ratio = y / size
        r = int(102 + (118 - 102) * ratio)
        g = int(126 + (75 - 126) * ratio)
        b = int(234 + (162 - 234) * ratio)
        img[y, :] = [b, g, r]

    # 축구공 (흰색 원)
    center = (size // 2, size // 2)
    radius = int(size * 0.35)
    cv2.circle(img, center, radius, (255, 255, 255), -1)

    # 검은색 오각형 패턴 (간단하게 선으로)
    cv2.circle(img, center, radius, (0, 0, 0), 2)

    # "S" 텍스트 (SoccerHUD)
    font_scale = size / 64
    thickness = max(1, int(size / 32))
    cv2.putText(
        img,
        'S',
        (int(center[0] - size * 0.12), int(center[1] + size * 0.15)),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (0, 0, 0),
        thickness,
    )

    # 저장
    cv2.imwrite(str(output_path), img)
    print(f'✅ {output_path.name} 생성 완료')


if __name__ == '__main__':
    icons_dir = Path(__file__).parent.parent / 'extension' / 'icons'
    icons_dir.mkdir(exist_ok=True)

    create_icon(16, icons_dir / 'icon16.png')
    create_icon(48, icons_dir / 'icon48.png')
    create_icon(128, icons_dir / 'icon128.png')

    print('\n🎨 모든 아이콘 생성 완료!')
