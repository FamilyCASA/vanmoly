path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Show team HTML template
idx = content.find('team-member-card')
if idx >= 0:
    print(content[max(0,idx-200):idx+600])
