import os
from PIL import Image, ImageDraw

tabbar_dir = r"D:\desktop\VANMOLY-SYS-V3.0\miniapp-native\images\tabbar"
os.makedirs(tabbar_dir, exist_ok=True)

SIZE = 81

icons = [
    ('home.png',           (26,26,46,255)),
    ('home-active.png',   (212,175,55,255)),
    ('case.png',           (26,26,46,255)),
    ('case-active.png',   (212,175,55,255)),
    ('product.png',        (26,26,46,255)),
    ('product-active.png', (212,175,55,255)),
    ('consult.png',        (26,26,46,255)),
    ('consult-active.png', (212,175,55,255)),
]

for fname, color in icons:
    img = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))
    draw = ImageDraw.ImageDraw(img)
    cx, cy = SIZE // 2, SIZE // 2
    r = 30
    # outer ring
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=color, width=4)
    # inner dot
    r2 = 10
    draw.ellipse([cx-r2, cy-r2, cx+r2, cy+r2], fill=color)

    out = os.path.join(tabbar_dir, fname)
    img.save(out, 'PNG')
    print(f"Created {fname}: {os.path.getsize(out)/1024:.1f}KB")