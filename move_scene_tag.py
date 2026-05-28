import sys, re
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

changed = False

# 1. 移除旧的场景标签位置（在 cover-subtitle 后面的）
old_scene = r'''            <div class="cover-scene-tags" v-if="caseData.scene_tag">
              <span class="scene-tag-item">{{ caseData.scene_tag }}</span>
            </div>'''
if old_scene in content:
    # 检查是否只有一处
    count = content.count(old_scene)
    if count == 1:
        content = content.replace(old_scene, '')
        print("[OK] 旧位置场景标签已移除")
        changed = True
    else:
        print(f"[WARN] 旧场景标签出现{count}次，只移除第一处")
        content = content.replace(old_scene, '', 1)
        changed = True
else:
    print("[INFO] 旧位置场景标签不存在或已被移除")

# 2. 在 .cover-style div 后面添加场景标签
new_scene = '''            <div class="cover-scene-tags" v-if="caseData.scene_tag">
              <span class="scene-tag-item">{{ caseData.scene_tag }}</span>
            </div>'''

# 找到 cover-style 的结束位置
m = re.search(r'(<div class="cover-style"[^>]*>.*?</div>)', content)
if m:
    pos = m.end()
    content = content[:pos] + '\n' + new_scene + content[pos:]
    print("[OK] 场景标签已添加到风格标签下方")
    changed = True
else:
    print("[ERR] cover-style 未找到")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[DONE]" if changed else "[NO CHANGES]")
