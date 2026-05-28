import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find saveMaterialConfig
idx = content.find('const saveMaterialConfig')
end = content.find('const ', idx+30)
print("=== saveMaterialConfig ===")
print(content[idx:end])
