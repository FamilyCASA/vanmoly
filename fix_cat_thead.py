import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Old category material thead (indented differently)
old_cat_thead = """                    <tr>
                      <th class="smat-th-idx">序号</th>
                      <th class="smat-th-custom">自定义商品名称</th>
                      <th class="smat-th-name">物料名称</th>
                      <th>规格</th>
                      <th>品牌</th>
                      <th>材质</th>
                      <th>花色</th>
                      <th>定制计量值</th>
                      <th>计量单位</th>
                      <th>数量</th>
                      <th>单价</th>
                      <th>金额</th>
                    </tr>"""

new_cat_thead = """                    <tr>
                      <th class="smat-th-idx">序号</th>
                      <th class="smat-th-custom">自定义商品名称</th>
                      <th>一级分类</th>
                      <th>二级分类</th>
                      <th class="smat-th-name">物料名称</th>
                      <th>规格</th>
                      <th>品牌</th>
                      <th>材质</th>
                      <th>花色</th>
                      <th>宽度</th>
                      <th>深度</th>
                      <th>高度</th>
                      <th>定制计量值</th>
                      <th>数量</th>
                      <th>计量单位</th>
                      <th>单价</th>
                      <th>金额</th>
                    </tr>"""

count = c.count(old_cat_thead)
print(f"Cat thead found: {count}")
c = c.replace(old_cat_thead, new_cat_thead)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print("Done")
