import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Old 12-column thead (space material)
old_thead = """                <thead>
                  <tr>
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
                  </tr>
                </thead>"""

# New 17-column thead
new_thead = """                <thead>
                  <tr>
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
                  </tr>
                </thead>"""

# Old 12-column tbody (space material)
old_tbody = """                  <tr
                    v-for="(item, iIdx) in matPage"
                    :key="item.id || iIdx"
                    class="smat-row"
                    @click.stop="openMaterialDetail(item)"
                  >
                    <td class="smat-idx">{{ iIdx + 1 }}</td>
                    <td class="smat-custom">{{ item.custom_name || '' }}</td>
                    <td class="smat-name">{{ item.material_name || '' }}</td>
                    <td>{{ item.spec || '' }}</td>
                    <td>{{ item.brand || '' }}</td>
                    <td>{{ item.material || '' }}</td>
                    <td>{{ item.color_name || '' }}</td>
                    <td class="smat-measure">{{ item.custom_measure || '' }}</td>
                    <td>{{ item.unit || '' }}</td>
                    <td class="smat-num">{{ item.quantity }}</td>
                    <td class="smat-num">¥{{ item.unit_price }}</td>
                    <td class="smat-num smat-price">¥{{ item.total_price }}</td>
                  </tr>"""

# New 17-column tbody (space material)
new_tbody = """                  <tr
                    v-for="(item, iIdx) in matPage"
                    :key="item.id || iIdx"
                    class="smat-row"
                    @click.stop="openMaterialDetail(item)"
                  >
                    <td class="smat-idx">{{ iIdx + 1 }}</td>
                    <td class="smat-custom">{{ item.custom_name || '' }}</td>
                    <td>{{ item.category_level1 || '' }}</td>
                    <td>{{ item.category_level2 || '' }}</td>
                    <td class="smat-name">{{ item.material_name || '' }}</td>
                    <td>{{ item.spec || '' }}</td>
                    <td>{{ item.brand || '' }}</td>
                    <td>{{ item.material || '' }}</td>
                    <td>{{ item.color_name || '' }}</td>
                    <td class="smat-dim">{{ item.width || '' }}</td>
                    <td class="smat-dim">{{ item.depth || '' }}</td>
                    <td class="smat-dim">{{ item.height || '' }}</td>
                    <td class="smat-measure">{{ item.custom_measure || '' }}</td>
                    <td class="smat-num">{{ item.quantity }}</td>
                    <td>{{ item.unit || '' }}</td>
                    <td class="smat-num">¥{{ item.unit_price }}</td>
                    <td class="smat-num smat-price">¥{{ item.total_price }}</td>
                  </tr>"""

# Replace space material table
count_th = c.count(old_thead)
count_td = c.count(old_tbody)
print(f"Old thead found: {count_th}, Old tbody found: {count_td}")

c = c.replace(old_thead, new_thead)
c = c.replace(old_tbody, new_tbody)

# Now fix the category material table (uses catPage instead of matPage)
old_cat_tbody = """                  <tr
                      v-for="(item, iIdx) in catPage"
                      :key="item.id || iIdx"
                      class="smat-row"
                      @click.stop="openMaterialDetail(item)"
                    >
                      <td class="smat-idx">{{ iIdx + 1 }}</td>
                      <td class="smat-custom">{{ item.custom_name || '' }}</td>
                      <td class="smat-name">{{ item.material_name || '' }}</td>
                      <td>{{ item.spec || '' }}</td>
                      <td>{{ item.brand || '' }}</td>
                      <td>{{ item.material || '' }}</td>
                      <td>{{ item.color_name || '' }}</td>
                      <td class="smat-measure">{{ item.custom_measure || '' }}</td>
                      <td>{{ item.unit || '' }}</td>
                      <td class="smat-num">{{ item.quantity }}</td>
                      <td class="smat-num">¥{{ item.unit_price }}</td>
                      <td class="smat-num smat-price">¥{{ item.total_price }}</td>
                    </tr>"""

new_cat_tbody = """                  <tr
                      v-for="(item, iIdx) in catPage"
                      :key="item.id || iIdx"
                      class="smat-row"
                      @click.stop="openMaterialDetail(item)"
                    >
                      <td class="smat-idx">{{ iIdx + 1 }}</td>
                      <td class="smat-custom">{{ item.custom_name || '' }}</td>
                      <td>{{ item.category_level1 || '' }}</td>
                      <td>{{ item.category_level2 || '' }}</td>
                      <td class="smat-name">{{ item.material_name || '' }}</td>
                      <td>{{ item.spec || '' }}</td>
                      <td>{{ item.brand || '' }}</td>
                      <td>{{ item.material || '' }}</td>
                      <td>{{ item.color_name || '' }}</td>
                      <td class="smat-dim">{{ item.width || '' }}</td>
                      <td class="smat-dim">{{ item.depth || '' }}</td>
                      <td class="smat-dim">{{ item.height || '' }}</td>
                      <td class="smat-measure">{{ item.custom_measure || '' }}</td>
                      <td class="smat-num">{{ item.quantity }}</td>
                      <td>{{ item.unit || '' }}</td>
                      <td class="smat-num">¥{{ item.unit_price }}</td>
                      <td class="smat-num smat-price">¥{{ item.total_price }}</td>
                    </tr>"""

count_cat = c.count(old_cat_tbody)
print(f"Old cat tbody found: {count_cat}")
c = c.replace(old_cat_tbody, new_cat_tbody)

# Fix tfoot colspan for 17 columns: first 15 cols blank, then "space subtotal", then amount
old_tfoot = '                    <td colspan="10"></td>'
new_tfoot = '                    <td colspan="15"></td>'
c = c.replace(old_tfoot, new_tfoot)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print("Done: 17-column table updated in CaseSlidePreview.vue")
