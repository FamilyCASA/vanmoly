import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Check if save payload already has width/depth/height
save_idx = c.find('const saveMaterialConfig')
if save_idx > 0:
    block = c[save_idx:save_idx+800]
    for field in ['width', 'depth', 'height']:
        print(f'save.{field}: {"YES" if field in block else "NO"}')

# Check openMaterialConfig load
load_idx = c.find('const openMaterialConfig')
if load_idx > 0:
    block2 = c[load_idx:load_idx+800]
    for field in ['width', 'depth', 'height']:
        print(f'load.{field}: {"YES" if field in block2 else "NO"}')
