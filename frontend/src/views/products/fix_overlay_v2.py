import re

with open('ProductList.vue', 'r', encoding='utf-8') as f:
    content = f.read()

fixes = []

# ===== 修复悬浮覆盖层：改为深色毛玻璃 =====
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
    fixes.append('✓ overlay: white 0.96 → dark 0.55')
else:
    # 用正则找并替换
    pattern = r'\.card-overlay \{[^}]*background:\s*rgba\(255,255,255,[^)]+\)[^}]*\}'
    replacement = '''.card-overlay {
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
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    if new_content != content:
        content = new_content
        fixes.append('✓ overlay: fixed via regex')
    else:
        fixes.append('⚠ overlay: pattern not matched, manual check needed')

# ===== 修复 primary 按钮：白色背景+深色文字 =====
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
    fixes.append('✓ primary btn: dark → white bg / dark text')
else:
    fixes.append('⚠ primary btn: pattern not found')

# ===== 修复 ghost 按钮：白色文字+白色边框 =====
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
    fixes.append('✓ ghost btn: dark text → white text')
else:
    fixes.append('⚠ ghost btn: pattern not found')

# ===== 修复 page-header padding-top（被 Navbar 遮挡）=====
# Navbar 约 64px 高，padding-top 至少 64+32=96px
old_header_pad = 'padding: 72px 80px 56px;'
new_header_pad = 'padding: 110px 80px 56px;'
if old_header_pad in content:
    content = content.replace(old_header_pad, new_header_pad)
    fixes.append('✓ page-header: 72px → 110px padding-top')
else:
    fixes.append('⚠ page-header padding: pattern not found')

# ===== 修复 cat-bar.sticky top（被 Navbar 遮挡）=====
old_sticky = 'top: 0;\n  z-index: 100;'
new_sticky = 'top: 64px;\n  z-index: 100;'
if old_sticky in content:
    content = content.replace(old_sticky, new_sticky)
    fixes.append('✓ cat-bar.sticky: top 0 → 64px')
else:
    fixes.append('⚠ cat-bar.sticky top: pattern not found')

# ===== 响应式同步 =====
resp_fixes = [
    ('padding: 56px 48px 44px;', 'padding: 90px 48px 44px;'),
    ('padding: 44px 28px 36px;', 'padding: 80px 28px 36px;'),
    ('padding: 36px 20px 28px;', 'padding: 72px 20px 28px;'),
]
for old, new in resp_fixes:
    if old in content:
        content = content.replace(old, new)
        fixes.append(f'✓ responsive: {old.strip()} → {new.strip()}')

with open('ProductList.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('修复完成：')
for item in fixes:
    print(f'  {item}')
print(f'\n共应用 {len(fixes)} 项修复')
