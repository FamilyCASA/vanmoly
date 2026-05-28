import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find matSearching and matSaving definitions
for var in ['matSearching', 'matSaving', 'materialDialogVisible', 'currentMaterialSpace', 'materialSKUs', 'categoryTree', 'l1Categories']:
    idx = content.find(f'{var} = ref')
    if idx >= 0:
        print(f"=== {var} ===")
        print(content[idx:idx+80])
    else:
        idx2 = content.find(f'const {var}')
        if idx2 >= 0:
            print(f"=== {var} (const) ===")
            print(content[idx2:idx2+80])
        else:
            print(f"=== {var} NOT FOUND ===")
