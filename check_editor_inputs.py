import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Check if editor has input fields for width/depth/height
for field in ['width', 'depth', 'height']:
    count = c.count(f'v-model="mat.{field}"')
    count2 = c.count(f"mat.{field}")
    print(f"Editor mat.{field}: v-model={count}, references={count2}")
