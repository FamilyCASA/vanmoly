import re

path = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Find problematic patterns: strings that end with Chinese but no closing quote
problems = []
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    # Pattern: Chinese chars at the end without a proper string termination
    # This regex looks for strings that end with non-ASCII chars but no closing quote
    m = re.search(r"= '[^']*[\u4e00-\u9fff]+$", stripped)
    if m:
        problems.append((i, stripped))
    m2 = re.search(r"== '[^']*[\u4e00-\u9fff]+$", stripped)
    if m2:
        problems.append((i, stripped))

print(f'Found {len(problems)} potential issues:')
for ln, txt in problems:
    print(f'  Line {ln}: {txt[:120]}')

# Also check for specific known bad patterns
bad_patterns = [
    '\u91c7\u5e01',   # 采品 (from 已采品)
    '\u93ae\u6ca1',   # 没 (from 已没)
    '\u8349\u7a86',   # 草稿
    '\u5df2\u53d1\u5e03',  # 已发布 (might be truncated)
]