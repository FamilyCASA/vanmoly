path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('.cover-colors-labeled')
if idx >= 0:
    # print next 600 chars to see exact formatting
    chunk = content[idx:idx+700]
    print(repr(chunk))
