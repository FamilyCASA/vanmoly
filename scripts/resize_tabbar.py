import sys
import os

try:
    from PIL import Image
    print('PIL_OK')
except ImportError:
    print('NO_PIL')
    sys.exit(1)

tabbar_dir = r"D:\desktop\VANMOLY-SYS-V3.0\miniapp-native\images\tabbar"
files = ['home.png', 'home-active.png', 'case.png', 'case-active.png',
         'consult.png', 'consult-active.png']

for fname in files:
    fpath = os.path.join(tabbar_dir, fname)
    if not os.path.exists(fpath):
        print(f"MISSING: {fname}")
        continue
    img = Image.open(fpath)
    w, h = img.size
    size_kb = os.path.getsize(fpath) / 1024
    print(f"{fname}: {w}x{h}, {size_kb:.1f}KB", end='')
    if size_kb > 40:
        # resize to 81x81 (微信tabbar推荐尺寸)
        img_resized = img.resize((81, 81), Image.LANCZOS)
        img_resized.save(fpath, optimize=True)
        new_size = os.path.getsize(fpath) / 1024
        print(f" -> RESIZED to {new_size:.1f}KB")
    else:
        print(" -> OK")