# 앱 아이콘 만들기: 남색 바탕에 달력 한 장, 빨간날 하나와 휴가 기간 표시 (글자 없음)
#   draw(size)              → 모서리 둥근 아이콘 (안드로이드 런처, 웹앱 manifest)
#   draw(size, square=True) → 모서리까지 꽉 찬 네모 (아이폰 홈 화면은 iOS가 알아서 둥글게 깎음. 투명 모서리면 검게 나옴)
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res')
SIZES = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}
NAVY, WATER, INK, RED, WHITE = (0x13, 0x23, 0x3A), (0xE2, 0xEE, 0xF5), (0x13, 0x23, 0x3A), (0xB8, 0x23, 0x5A), (0xFF, 0xFF, 0xFF)

def draw(size, square=False):
    S = 16  # 크게 그려서 줄이기 (가장자리 부드럽게)
    W = size * S
    im = Image.new('RGBA', (W, W), NAVY + (255,) if square else (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if not square:
        d.rounded_rectangle([0, 0, W - 1, W - 1], radius=int(W * 0.22), fill=NAVY)
    # 달력 종이
    x0, y0, x1, y1 = int(W * 0.17), int(W * 0.22), int(W * 0.83), int(W * 0.84)
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(W * 0.06), fill=WHITE)
    # 위쪽 띠 (빨간날 색)
    d.rounded_rectangle([x0, y0, x1, y0 + int(W * 0.15)], radius=int(W * 0.06), fill=RED)
    d.rectangle([x0, y0 + int(W * 0.08), x1, y0 + int(W * 0.15)], fill=RED)
    # 고리 두 개
    for cx in (int(W * 0.36), int(W * 0.64)):
        d.rounded_rectangle([cx - int(W * 0.03), int(W * 0.15), cx + int(W * 0.03), int(W * 0.30)], radius=int(W * 0.03), fill=INK)
    # 날짜 칸 4×3: 한 줄은 휴가 기간(얕은 물 색), 그중 하루는 빨간날
    cols, rows = 4, 3
    gx0, gy0, gx1, gy1 = x0 + int(W * 0.07), y0 + int(W * 0.22), x1 - int(W * 0.07), y1 - int(W * 0.07)
    cw, ch = (gx1 - gx0) / cols, (gy1 - gy0) / rows
    for row in range(rows):
        for col in range(cols):
            cx0, cy0 = gx0 + col * cw, gy0 + row * ch
            box = [int(cx0 + cw * 0.12), int(cy0 + ch * 0.12), int(cx0 + cw * 0.88), int(cy0 + ch * 0.88)]
            if row == 1:
                fill = RED if col == 2 else WATER
            else:
                fill = (0xD2, 0xDB, 0xE4)
            d.rounded_rectangle(box, radius=int(W * 0.02), fill=fill)
    return im.resize((size, size), Image.LANCZOS)

if __name__ == '__main__':
    for name, size in SIZES.items():
        folder = os.path.join(OUT, 'mipmap-' + name)
        os.makedirs(folder, exist_ok=True)
        draw(size).save(os.path.join(folder, 'ic_launcher.png'))
        print(name, size)
