# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect('D:/desktop/VANMOLY-SYS-V3.0/backend/instance/vanmoly_v3.db')
c = conn.cursor()

# 添加 atmosphere 字段
c.execute("ALTER TABLE case_study ADD COLUMN atmosphere VARCHAR(20)")
conn.commit()
print('添加 atmosphere 字段成功')

# 映射现有数据
# 温馨 -> modern / 暖色系
# 清新 -> nordic / 白色系
# 简约 -> minimalist / 简单线条
# 浪漫 -> 奶油风/法式
# 雅致 -> 新中式/中式
# 沉稳 -> 现代/深色系

style_map = {
    'modern': '温馨',
    'nordic': '清新',
    'minimalist': '简约',
    'chinese': '雅致',
    '奶油风': '浪漫',
    '法式': '浪漫',
    '新中式': '雅致',
}

# 更新现有案例
for old_style, atmosphere in style_map.items():
    c.execute("UPDATE case_study SET atmosphere = ? WHERE style = ?", (atmosphere, old_style))
    if c.rowcount > 0:
        print(f'更新 {old_style} -> {atmosphere}: {c.rowcount} 条')

conn.commit()
conn.close()
print('done')