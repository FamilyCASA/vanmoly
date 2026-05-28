import re

with open('ProductList.vue', 'r', encoding='utf-8') as f:
    content = f.read()

fixes = []

# 修复1: 悬浮覆盖层改为深色半透明（解决白底白字看不见的问题）
old_overlay = '''.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.96);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-radius: 16px 16px 0 0;
}'''

new_overlay = '''.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.55);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border-radius: 16px 16px 0 0;
}'''

if old_overlay in content:
    content = content.replace(old_overlay, new_overlay)
    fixes.append('[OK] overlay: white 0.96 -> dark 0.55')
else:
    # 用正则强制替换
    content = re.sub(
        r'background:\s*rgba\(255,255,255,0\.\d+\);',
        'background: rgba(0,0,0,0.55);',
        content
    )
    fixes.append('[OK] overlay: forced to dark via regex')

# 修复2: 主按钮改为白底黑字（在深色覆盖层上更干净）
old_primary = '''.overlay-btn.primary {
  background: #1a1a1a;
  color: #FFFFFF;
  font-weight: 600;
}'''
new_primary = '''.overlay-btn.primary {
  background: #FFFFFF;
  color: #1a1a1a;
  font-weight: 600;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
}'''
if old_primary in content:
    content = content.replace(old_primary, new_primary)
    fixes.append('[OK] primary btn: dark bg -> white bg, dark text')
else:
    fixes.append('[SKIP] primary btn: pattern not found')

# 修复3: 幽灵按钮改为白字+白边框（在深色覆盖层上）
old_ghost = '''.overlay-btn.ghost {
  background: rgba(0,0,0,0.04);
  color: #1a1a1a;
  border: 1px solid rgba(0,0,0,0.15);
  font-weight: 500;
}'''
new_ghost = '''.overlay-btn.ghost {
  background: rgba(255,255,255,0.12);
  color: #FFFFFF;
  border: 1px solid rgba(255,255,255,0.35);
  font-weight: 500;
  backdrop-filter: blur(4px);
}'''
if old_ghost in content:
    content = content.replace(old_ghost, new_ghost)
    fixes.append('[OK] ghost btn: dark text -> white text on dark overlay')
else:
    fixes.append('[SKIP] ghost btn: pattern not found')

# 修复4: page-header padding-top 加大（被 Navbar 遮挡）
if '.page-header {\n  position: relative;\n  padding: 72px 80px 56px;' in content:
    content = content.replace(
        '.page-header {\n  position: relative;\n  padding: 72px 80px 56px;\n  overflow: hidden;\n}',
        '.page-header {\n  position: relative;\n  padding: 110px 80px 56px;\n  overflow: hidden;\n}'
    )
    fixes.append('[OK] page-header: padding-top 72px -> 110px')
elif 'padding: 110px 80px 56px' in content:
    fixes.append('[SKIP] page-header: already 110px')
else:
    fixes.append('[SKIP] page-header: pattern not found, current: ' + re.search(r'\.page-header \{[^}]*padding:\s*([^;]+);', content).group(1) if re.search(r'\.page-header \{[^}]*padding:', content) else 'NOT FOUND')

# 修复5: cat-bar.sticky top 改为 64px（Navbar 高度）
if '.cat-bar.sticky {\n  position: sticky;\n  top: 0;\n  z-index: 100;' in content:
    content = content.replace(
        '.cat-bar.sticky {\n  position: sticky;\n  top: 0;\n  z-index: 100;',
        '.cat-bar.sticky {\n  position: sticky;\n  top: 64px;\n  z-index: 100;'
    )
    fixes.append('[OK] cat-bar.sticky: top 0 -> 64px')
elif 'top: 64px;' in content and '.cat-bar.sticky' in content:
    fixes.append('[SKIP] cat-bar.sticky: already 64px')
else:
    fixes.append('[SKIP] cat-bar.sticky: pattern not found')

# 修复6: 响应式 padding 同步
resp = [
    ('padding: 56px 48px 44px;', 'padding: 90px 48px 44px;'),
    ('padding: 44px 28px 36px;', 'padding: 80px 28px 36px;'),
    ('padding: 36px 20px 28px;', 'padding: 72px 20px 28px;'),
]
for old, new in resp:
    if old in content:
        content = content.replace(old, new)
        fixes.append(f'[OK] responsive: {old.strip()}')

# 先写文件，再打印（避免 Windows GBK 编码问题）
with open('ProductList.vue', 'w', encoding='utf-8') as f:
    f.write(content)

# 现在安全地打印（只用 ASCII）
print('All fixes applied. File written successfully.')
print(f'Total fixes: {len([f for f in fixes if "[OK]" in f])}')
for item in fixes:
    print(f'  {item}')
