import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\admin\CaseEdit.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到当前场景标签的 el-select
idx = content.find('场景标签')
if idx >= 0:
    # 扩大范围看完整结构
    start = max(0, idx - 50)
    end = min(len(content), idx + 600)
    print(f"=== 场景标签位置 {idx} ===")
    print(content[start:end])
