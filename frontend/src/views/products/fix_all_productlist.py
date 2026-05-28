import re

with open('ProductList.vue', 'r', encoding='utf-8') as f:
    content = f.read()

fixes = []

# 修复1: page-header padding-top 加大，避免被 Navbar (64px) 遮挡
old1 = '.page-header {\n  position: relative;\n  padding: 72px 80px 56px;\n  overflow: hidden;\n}'
new1 = '.page-header {\n  position: relative;\n  padding: 110px 80px 56px;\n  overflow: hidden;\n}'
if old1 in content:
    content = content.replace(old1, new1)
    fixes.append('Fix 1: page-header padding-top 72px -> 110px')
else:
    fixes.append('Fix 1: already applied or pattern not found')

# 修复2: cat-bar.sticky top 从 0 改为 64px（Navbar 高度）
old2 = '.cat-bar.sticky {\n  position: sticky;\n  top: 0;\n  z-index: 100;'
new2 = '.cat-bar.sticky {\n  position: sticky;\n  top: 64px;\n  z-index: 100;'
if old2 in content:
    content = content.replace(old2, new2)
    fixes.append('Fix 2: cat-bar.sticky top: 0 -> 64px')
else:
    fixes.append('Fix 2: already applied or pattern not found')

# 修复3: 悬浮覆盖层不够不透明 → 0.88 改为 0.96
old3 = '  background: rgba(255,255,255,0.88);\n  backdrop-filter: blur(6px);\n  -webkit-backdrop-filter: blur(6px);'
new3 = '  background: rgba(255,255,255,0.96);\n  backdrop-filter: blur(8px);\n  -webkit-backdrop-filter: blur(8px);'
if old3 in content:
    content = content.replace(old3, new3)
    fixes.append('Fix 3: overlay bg opacity 0.88 -> 0.96')
else:
    fixes.append('Fix 3: already applied or pattern not found')

# 修复4: 主按钮确保白字 + 加粗
old4 = '.overlay-btn.primary {\n  background: #1a1a1a;\n  color: #fff;\n}'
new4 = '.overlay-btn.primary {\n  background: #1a1a1a;\n  color: #FFFFFF;\n  font-weight: 600;\n}'
if old4 in content:
    content = content.replace(old4, new4)
    fixes.append('Fix 4: primary button color #fff -> #FFFFFF + font-weight 600')
else:
    fixes.append('Fix 4: already applied or pattern not found')

# 修复5: ghost 按钮增强对比度（深色边框和文字）
old5 = '.overlay-btn.ghost {\n  background: rgba(0,0,0,0.03);\n  color: #333;\n  border: 1px solid rgba(0,0,0,0.1);\n}'
new5 = '.overlay-btn.ghost {\n  background: rgba(0,0,0,0.04);\n  color: #1a1a1a;\n  border: 1px solid rgba(0,0,0,0.15);\n  font-weight: 500;\n}'
if old5 in content:
    content = content.replace(old5, new5)
    fixes.append('Fix 5: ghost button contrast enhanced')
else:
    fixes.append('Fix 5: already applied or pattern not found')

# 修复6: 响应式 padding 同步调整
resp_fixes = [
    ('  .page-header { padding: 56px 48px 44px; }', '  .page-header { padding: 90px 48px 44px; }'),
    ('  .page-header { padding: 44px 28px 36px; }', '  .page-header { padding: 80px 28px 36px; }'),
    ('  .page-header { padding: 36px 20px 28px; }', '  .page-header { padding: 72px 20px 28px; }'),
]
for old, new in resp_fixes:
    if old in content:
        content = content.replace(old, new)
        fixes.append(f'Fix 6: responsive {old.strip()}')

# 修复7: 检查 .drawer-mask 拼写（不是 .drawer-mask）
# HTML 中是 drawer-mask，CSS 中应该是 .drawer-mask
if '.drawer-mask' in content:
    fixes.append('Fix 7: .drawer-mask spelling OK')
else:
    # 查找是否有拼写错误
    mask_match = re.search(r'\.drawer-\w+', content)
    if mask_match:
        fixes.append(f'Fix 7: found .{mask_match.group(0)} - check spelling')

with open('ProductList.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Applied fixes:')
for item in fixes:
    print(f'  {item}')
print(f'Total: {len(fixes)} fixes applied')
