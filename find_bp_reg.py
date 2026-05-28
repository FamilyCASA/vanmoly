import sys; sys.stdout.reconfigure(encoding='utf-8')
import os

# Find where material_bp is registered
for root, dirs, files in os.walk(r'D:\desktop\VANMOLY-SYS-V3.0\backend'):
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root, f)
            try:
                with open(fp, encoding='utf-8') as fh:
                    c = fh.read()
                if 'material_bp' in c and f != 'material_routes.py':
                    print(f"{fp}:")
                    for i, line in enumerate(c.split('\n'), 1):
                        if 'material_bp' in line or 'material' in line.lower():
                            print(f"  {i}: {line.strip()}")
            except:
                pass
