with open('ProductList.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 "产品网格" 注释行的行号
insert_idx = None
for i, line in enumerate(lines):
    if '<!-- ===== 产品网格 ===== -->' in line:
        # 往前找空行，插入在 cat-bar 的 </div> 之后、空行之前
        # 实际结构是: ...</div>\n\n  <!-- ===== 产品网格 ===== -->
        # 在 i-1 应该是空行，i-2 应该是 "  </div>"
        insert_idx = i  # 在注释行之前插入，即 i 的位置
        break

if insert_idx is None:
    print('[ERROR] 找不到 产品网格 标记')
    exit(1)

print(f'[INFO] 找到插入点，行号 ~{insert_idx+1}')

# 检查是否已经插入过（防止重复执行）
already_has = any('filter-bar' in l for l in lines)
if already_has:
    print('[SKIP] filter-bar 已存在，跳过插入')
    print('Done (no-op)')
    exit(0)

filter_bar_html = '''    <!-- ===== 筛选栏 ===== -->
    <div class="filter-bar">
      <div class="filter-inner">
        <div class="search-box">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
          <input
            v-model="filters.keyword"
            @input="onSearchInput"
            placeholder="搜索产品名称、品牌、SKU..."
            class="search-input"
          />
        </div>
        <div class="filter-selects">
          <select v-model="filters.brand" @change="onFilterChange" class="filter-select">
            <option value="">全部品牌</option>
            <option v-for="b in filterOptions.brands" :key="b" :value="b">{{ b }}</option>
          </select>
          <select v-model="filters.unit" @change="onFilterChange" class="filter-select">
            <option value="">全部单位</option>
            <option v-for="u in filterOptions.units" :key="u" :value="u">{{ u }}</option>
          </select>
          <select v-model="filters.env_level" @change="onFilterChange" class="filter-select">
            <option value="">全部环保等级</option>
            <option v-for="e in filterOptions.env_levels" :key="e" :value="e">{{ e }}</option>
          </select>
        </div>
      </div>
    </div>

'''

# 在 "产品网格" 注释行之前插入（insert_idx 位置）
lines.insert(insert_idx, filter_bar_html)

with open('ProductList.vue', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('[OK] filter-bar HTML 插入成功')
print('Done')
