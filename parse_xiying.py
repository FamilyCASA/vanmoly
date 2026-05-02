import pandas as pd
import json
import sys

# 设置输出编码
sys.stdout.reconfigure(encoding='utf-8')

# 解析西映餐椅
print("=== 西映24-餐厅系统-餐椅.xlsx ===")
df1 = pd.read_excel(r'D:\desktop\报价标准数据库\供应链\西映\西映24-餐厅系统-餐椅.xlsx')
print("列名:", df1.columns.tolist())
print("\n总行数:", len(df1))

# 保存到文件
with open('xiying_chair.json', 'w', encoding='utf-8') as f:
    df1.to_json(f, orient='records', force_ascii=False)
print("数据已保存到 xiying_chair.json")

# 解析西映餐桌
print("\n=== 西映24-餐厅系统-餐桌.xlsx ===")
df2 = pd.read_excel(r'D:\desktop\报价标准数据库\供应链\西映\西映24-餐厅系统-餐桌.xlsx')
print("列名:", df2.columns.tolist())
print("总行数:", len(df2))

with open('xiying_table.json', 'w', encoding='utf-8') as f:
    df2.to_json(f, orient='records', force_ascii=False)
print("数据已保存到 xiying_table.json")

# 解析西映妆台书桌边几
print("\n=== 西映24-家居配套系统-妆台&书桌&边几.xlsx ===")
df3 = pd.read_excel(r'D:\desktop\报价标准数据库\供应链\西映\西映24-家居配套系统-妆台&书桌&边几.xlsx')
print("列名:", df3.columns.tolist())
print("总行数:", len(df3))

with open('xiying_furniture.json', 'w', encoding='utf-8') as f:
    df3.to_json(f, orient='records', force_ascii=False)
print("数据已保存到 xiying_furniture.json")

print("\n解析完成！")
