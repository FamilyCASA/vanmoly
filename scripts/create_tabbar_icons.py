import os
from PIL import Image, ImageDraw

tabbar_dir = r"D:\desktop\VANMOLY-SYS-V3.0\miniapp-native\images\tabbar"
os.makedirs(tabbar_dir, exist_ok=True)

SIZE = 81

def make_icon(bg_color, fg_char, out_path):
    img = Image.new('RGBA', (SIZE, SIZE), bg_color)
    draw = ImageDraw.ImageDraw(img)
    # Draw a simple circle outline
    draw.ellipse([10, 10, SIZE-10, SIZE-10], outline=(255,255,255,200), width=4)
    img.save(out_path, 'PNG')
    size_kb = os.path.getsize(out_path) / 1024
    print(f"Created {os.path.basename(out_path)}: {size_kb:.1f}KB")

icons = [
    # (filename, bg_color, symbol)
    ('home.png',           (200, 160, 100, 255)),
    ('home-active.png',    (139, 69, 19, 255)),
    ('case.png',           (200, 160, 100, 255)),
    ('case-active.png',    (139, 69, 19, 255)),
    ('consult.png',        (200, 160, 100, 255)),
    ('consult-active.png', (139, 69, 19, 255)),
]

for fname, color in icons:
    out = os.path.join(tabbar_dir, fname)
    make_icon(color, None, out)

# Also fix gift.png
gift_path = r"D:\desktop\VANMOLY-SYS-V3.0\miniapp-native\images\gift.png"
img_gift = Image.new('RGBA', (200, 200), (255, 255, 255, 0))
draw_gift = ImageDraw.ImageDraw(img_gift)
draw_gift.rectangle([20, 20, 180, 180], outline=(255, 200, 0, 255), width=5)
img_gift.save(gift_path, 'PNG')
print(f"Created gift.png: {os.path.getsize(gift_path)/1024:.1f}KB")