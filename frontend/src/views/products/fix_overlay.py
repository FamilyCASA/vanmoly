import re

with open('ProductList.vue', 'r', encoding='utf-8') as f:
    content = f.read()

fixes = []

# 策略：悬浮覆盖层改为深色半透明（更适合白色页面上的 hover 效果）
# 这样按钮白字在深色背景上清晰可见

old_overlay = """.card-overlay {
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
}"""

new_overlay = """.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(26,26,26,0.82);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border-radius: 16px 16px 0 0;
}"""

if old_overlay in content:
    content = content.replace(old_overlay, new_overlay)
    fixes.append('Fix: overlay background -> dark rgba(26,26,26,0.82)')
else:
    fixes.append('WARN: old overlay pattern not found, trying regex...')
    # 用正则强制替换 background 行
    content = re.sub(
        r'\.card-overlay \{[^}]*background:\s*rgba\(255,255,255,[^)]+\);[^}]*\}',
        lambda m: re.sub(r'background:\s*rgba\(255,255,255,[^)]+\);', 'background: rgba(26,26,26,0.82);', m.group(0)),
        content,
        flags=re.DOTALL
    )
    fixes.append('Fix: overlay background -> dark (regex)')

# 按钮样式：在深色覆盖层上用白字 + 半透明白边
old_primary = """.overlay-btn.primary {
  background: #1a1a1a;
  color: #FFFFFF;
  font-weight: 600;
}"""
new_primary = """.overlay-btn.primary {
  background: #FFFFFF;
  color: #1a1a1a;
  font-weight: 600;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
}"""
if old_primary in content:
    content = content.replace(old_primary, new_primary)
    fixes.append('Fix: primary button -> white bg, dark text')

old_ghost = """.overlay-btn.ghost {
  background: rgba(0,0,0,0.04);
  color: #1a1a1a;
  border: 1px solid rgba(0,0,0,0.15);
  font-weight: 500;
}"""
new_ghost = """.overlay-btn.ghost {
  background: rgba(255,255,255,0.15);
  color: #FFFFFF;
  border: 1px solid rgba(255,255,255,0.35);
  font-weight: 500);
}"""
if old_ghost in content:
    content = content.replace(old_ghost, new_ghost)
    fixes.append('Fix: ghost button -> glass white text')
elif 'overlay-btn.ghost' in content:
    fixes.append('WARN: ghost button pattern not found, checking...')
    # 找 ghost 当前内容
    m = re.search(r'\.overlay-btn\.ghost \{([^}]+)\}', content)
    if m:
        fixes.append(f'  Current ghost: {m.group(1).strip()[:60]}')

# 修复 page-header padding（被 Navbar 遮挡）
if '.page-header {\n  position: relative;\n  padding: 72px 80px 56px;' in content:
    content = content.replace(
        '.page-header {\n  position: relative;\n  padding: 72px 80px 56px;\n  overflow: hidden;\n}',
        '.page-header {\n  position: relative;\n  padding: 110px 80px 56px;\n  overflow: hidden;\n}'
    )
    fixes.append('Fix: page-header padding-top 72px -> 110px')

# 修复 cat-bar.sticky top
if 'top: 0;\n  z-index: 100;' in content and '.cat-bar.sticky' in content:
    content = re.sub(
        r'(\.cat-bar\.sticky[^{]*\{[^}]*)top:\s*0;',
        r'\1top: 64px;',
        content,
        flags=re.DOTALL
    )
    fixes.append('Fix: cat-bar.sticky top -> 64px')

with open('ProductList.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixes applied:')
for f_item in fixes:
    print(f'  {f_item}')
print(f'Done. File length: {len(content)}')
