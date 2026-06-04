import re

with open('ProductList.vue', 'r', encoding='utf-8') as f:
    content = f.read()

fixes = []

# 强制修复1: page-header padding-top 必须 110px
fixes.append('=== Fix 1: Force .page-header padding-top ===')
# 找到所有 .page-header 的 CSS 定义
page_header_pattern = r'\.page-header \{\n  position: relative;\n  padding: \d+px 80px \d+px;'
matches = re.findall(page_header_pattern, content)
fixes.append(f'Found {len(matches)} .page-header patterns: {matches}')

# 直接替换所有 padding 变体
for old_pad in ['72px', '90px', '80px', '36px']:
    old = f'.page-header {{\n  position: relative;\n  padding: {old} 80px 56px;\n  overflow: hidden;\n}}'
    new = '.page-header {{\n  position: relative;\n  padding: 110px 80px 56px;\n  overflow: hidden;\n}}'
    if old in content:
        content = content.replace(old, new)
        fixes.append(f'  Replaced padding: {old} 80px 56px -> 110px 80px 56px')

# 强制修复2: cat-bar.sticky top 必须 64px
fixes.append('=== Fix 2: Force .cat-bar.sticky top ===')
old2 = '.cat-bar.sticky {{\n  position: sticky;\n  top: 0;\n  z-index: 100;'
new2 = '.cat-bar.sticky {{\n  position: sticky;\n  top: 64px;\n  z-index: 100;'
if old2 in content:
    content = content.replace(old2, new2)
    fixes.append('  Replaced top: 0 -> top: 64px')
else:
    # 检查当前值
    match = re.search(r'\.cat-bar\.sticky \{[^}]*top:\s*(\S+);', content)
    if match:
        fixes.append(f'  Current top value: {match.group(1)}')
        if match.group(1) != '64px':
            content = re.sub(r'(\.cat-bar\.sticky \{[^}]*top:\s*)\S+;', r'\g<1>64px;', content)
            fixes.append('  Forced top: 64px')

# 强制修复3: 悬浮覆盖层按钮必须可见
fixes.append('=== Fix 3: Force overlay button visibility ===')
# 主按钮：深色背景 + 白色文字
old3 = '.overlay-btn.primary {{\n  background: #1a1a1a;\n  color: #FFFFFF;\n  font-weight: 600;\n}}'
if old3 in content:
    fixes.append('  Primary button already correct (#1a1a1a bg, #FFFFFF text)')
else:
    # 强制写入正确样式
    content = re.sub(
        r'\.overlay-btn\.primary \{[^}]*\}',
        '.overlay-btn.primary {{\n  background: #1a1a1a;\n  color: #FFFFFF;\n  font-weight: 600;\n}}',
        content
    )
    fixes.append('  Forced primary button style')

# 强制修复4: 覆盖层背景必须足够不透明
fixes.append('=== Fix 4: Force overlay background ===')
old4 = 'background: rgba(255,255,255,0.96);'
if old4 in content:
    fixes.append('  Overlay bg already 0.96')
else:
    content = re.sub(
        r'background:\s*rgba\(255,255,255,0\.\d+\);',
        'background: rgba(255,255,255,0.96);',
        content
    )
    fixes.append('  Forced overlay bg to 0.96')

# 强制修复5: 响应式 padding 同步
fixes.append('=== Fix 5: Force responsive padding ===')
resp = [
    ('padding: 56px 48px 44px;', 'padding: 90px 48px 44px;'),
    ('padding: 44px 28px 36px;', 'padding: 80px 28px 36px;'),
    ('padding: 36px 20px 28px;', 'padding: 72px 20px 28px;'),
]
for old, new in resp:
    if old in content:
        content = content.replace(old, new)
        fixes.append(f'  Responsive: {old} -> {new}')

# 写回文件
with open('ProductList.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('\n'.join(fixes))
print('\n=== DONE ===')
print(f'File length: {len(content)} chars')
