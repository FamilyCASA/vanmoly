import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# ===== 1. Update SPACE material table header =====
old_space_thead = """                <thead>
                  <tr>
                    <th class="smat-th-name">名称</th>
                    <th>品牌</th>
                    <th>规格</th>
                    <th>单位</th>
                    <th>数量</th>
                    <th>单价</th>
                    <th>金额</th>
                  </tr>
                </thead>"""

new_space_thead = """                <thead>
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

content = content.replace(old_space_thead, new_space_thead, 1)

# ===== 2. Update SPACE material table body =====
old_space_tbody = """                  <tr
                    v-for="(item, iIdx) in matPage"
                    :key="item.id || iIdx"
                    class="smat-row"
                    @click.stop="openMaterialDetail(item)"
                  >
                    <td class="smat-name">{{ item.material_name || '-' }}</td>
                    <td>{{ item.brand || '-' }}</td>
                    <td>{{ item.spec || '-' }}</td>
                    <td>{{ item.unit || '-' }}</td>
                    <td class="smat-num">{{ item.quantity }}</td>
                    <td class="smat-num">¥{{ item.unit_price }}</td>
                    <td class="smat-num smat-price">¥{{ item.total_price }}</td>
                  </tr>"""

new_space_tbody = """                  <tr
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

content = content.replace(old_space_tbody, new_space_tbody, 1)

# ===== 3. Update SPACE material tfoot colspan =====
old_space_tfoot = """                  <tr>
                    <td colspan="4"></td>
                    <td colspan="2" style="text-align:right;font-weight:600;">空间小计</td>"""

new_space_tfoot = """                  <tr>
                    <td colspan="9"></td>
                    <td colspan="2" style="text-align:right;font-weight:600;">空间小计</td>"""

content = content.replace(old_space_tfoot, new_space_tfoot, 1)

# ===== 4. Update CATEGORY material table header =====
old_cat_thead = """                    <th class="smat-th-name">名称</th>
                      <th>花色</th>
                      <th>品牌</th>
                      <th>规格</th>
                      <th>单位</th>
                      <th>单价</th>
                      <th>环保</th>"""

new_cat_thead = """                    <th class="smat-th-idx">序号</th>
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
                      <th>金额</th>"""

content = content.replace(old_cat_thead, new_cat_thead, 1)

# ===== 5. Update CATEGORY material table body =====
old_cat_tbody = """                      <td class="smat-name">{{ item.material_name || '-' }}</td>
                      <td>{{ item.color_name || '-' }}</td>
                      <td>{{ item.brand || '-' }}</td>
                      <td>{{ item.spec || '-' }}</td>
                      <td>{{ item.unit || '-' }}</td>
                      <td class="smat-num">¥{{ item.unit_price }}</td>
                      <td>{{ item.env_level || '合格' }}</td>"""

new_cat_tbody = """                      <td class="smat-idx">{{ iIdx + 1 }}</td>
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
                      <td class="smat-num smat-price">¥{{ item.total_price }}</td>"""

content = content.replace(old_cat_tbody, new_cat_tbody, 1)

# ===== 6. Update CSS for 12-column table =====
# Find .smat-table CSS
old_smat_css = ".smat-table {"
idx = content.find(old_smat_css)
if idx > 0:
    # Find the end of the CSS block (next })
    end = content.find('}', idx)
    # Find next CSS rule
    next_rule = content.find('\n.', end + 1)
    # Get the full smat CSS block area
    pass

# We need to add CSS for new columns
new_css = """
.smat-th-idx { width: 36px; text-align: center; }
.smat-th-custom { width: 100px; }
.smat-th-name { width: 120px; }
.smat-idx { text-align: center; color: #999; font-size: 12px; }
.smat-custom { font-size: 12px; max-width: 100px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.smat-measure { font-size: 12px; }
"""

# Insert before .material-config-content
anchor = ".material-config-content {"
if anchor in content:
    content = content.replace(anchor, new_css + anchor, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 前端物料表格已更新为12列")
print("  序号 | 自定义商品名称 | 物料名称 | 规格 | 品牌 | 材质 | 花色 | 定制计量值 | 计量单位 | 数量 | 单价 | 金额")
