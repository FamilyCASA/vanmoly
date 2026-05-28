path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Find team template HTML
idx = content.find('team-member-card')
if idx >= 0:
    print("=== TEAM HTML ===")
    print(content[max(0,idx-100):idx+800])
    print()

# Find all team-related CSS
for cls in ['team-avatar-wrap', 'team-avatar-img', 'team-avatar-placeholder', 'team-member-card', 'team-cards', 'team-member-info', 'team-role-tag', 'team-member-name', 'team-member-bio']:
    i = content.find('.' + cls)
    while i >= 0:
        end = content.find('\n}', i)
        print(f"=== .{cls} (pos {i}) ===")
        print(content[i:end+2])
        print()
        i = content.find('.' + cls, end)
