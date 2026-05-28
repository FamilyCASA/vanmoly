import re

with open('ProductList.vue', 'r', encoding='utf-8') as f:
    content = f.read()

log = []

# ===== 修复1: fetchProducts 传 is_public=true =====
old_params = "  const params = { page: pagination.page, page_size: pagination.page_size, status: 'active' }"
new_params = "  const params = { page: pagination.page, page_size: pagination.page_size, status: 'active', is_public: true }"
if old_params in content:
    content = content.replace(old_params, new_params)
    log.append('[OK] fetchProducts: added is_public=true')
else:
    log.append('[SKIP] fetchProducts params pattern not found')

# ===== 修复2: filters 加 brand/unit/env_level =====
old_filters = "const filters = reactive({ category_id: null, keyword: '' })"
new_filters = "const filters = reactive({ category_id: null, keyword: '', brand: '', unit: '', env_level: '' })"
if old_filters in content:
    content = content.replace(old_filters, new_filters)
    log.append('[OK] filters: added brand/unit/env_level')
else:
    log.append('[SKIP] filters pattern not found, trying alternate...')
    # 可能已经改过了
    if 'brand:' in content and 'filters = reactive' in content:
        log.append('[SKIP] filters already has brand (may already patched)')

# ===== 修复3: 在 fetchProducts 里传 brand/unit/env_level =====
old_kw = "    if (filters.keyword) params.keyword = filters.keyword"
new_kw = """    if (filters.keyword) params.keyword = filters.keyword
    if (filters.brand) params.brand = filters.brand
    if (filters.unit) params.unit = filters.unit
    if (filters.env_level) params.env_level = filters.env_level"""
if old_kw in content:
    content = content.replace(old_kw, new_kw)
    log.append('[OK] fetchProducts: added brand/unit/env_level params')
else:
    log.append('[SKIP] fetchProducts keyword pattern not found')

# ===== 修复4: 加 filterOptions ref =====
old_cattree = 'const categoryTree = ref([])'
new_cattree = '''const categoryTree = ref([])
const filterOptions = ref({ brands: [], units: [], env_levels: [] })'''
if old_cattree in content:
    content = content.replace(old_cattree, new_cattree)
    log.append('[OK] added filterOptions ref')
else:
    log.append('[SKIP] categoryTree pattern not found')

# ===== 修复5: 加搜索防抖 + 筛选变更函数 =====
old_selectCat = '''const selectCat = (id) => {
  filters.category_id = id
  pagination.page = 1
  fetchProducts()
}'''
new_selectCat = '''const selectCat = (id) => {
  filters.category_id = id
  pagination.page = 1
  fetchProducts()
}

let _searchTimer = null
const onSearchInput = () => {
  clearTimeout(_searchTimer)
  _searchTimer = setTimeout(() => {
    pagination.page = 1
    fetchProducts()
  }, 400)
}

const onFilterChange = () => {
  pagination.page = 1
  fetchProducts()
}'''
if old_selectCat in content:
    content = content.replace(old_selectCat, new_selectCat)
    log.append('[OK] added onSearchInput + onFilterChange')
else:
    log.append('[SKIP] selectCat pattern not found')

# ===== 修复6: 加 fetchFilterOptions 函数 =====
# 找 fetchCategories 结尾
old_fetchcat = '  } catch (e) { console.error(\'获取分类失败\', e) }\n}'
new_fetchcat = '''  } catch (e) { console.error('获取分类失败', e) }
}

const fetchFilterOptions = async () => {
  try {
    const res = await request.get('/materials/filter-options')
    filterOptions.value = res?.data || { brands: [], units: [], env_levels: [] }
  } catch (e) { console.error('获取筛选选项失败', e) }
}'''
if old_fetchcat in content:
    content = content.replace(old_fetchcat, new_fetchcat)
    log.append('[OK] added fetchFilterOptions')
else:
    log.append('[SKIP] fetchCategories end pattern not found')

# ===== 修复7: onMounted 里加 fetchFilterOptions =====
old_mounted = "  fetchCategories()\n  fetchProducts()"
new_mounted = "  fetchCategories()\n  fetchFilterOptions()\n  fetchProducts()"
if old_mounted in content:
    content = content.replace(old_mounted, new_mounted)
    log.append('[OK] onMounted: added fetchFilterOptions call')
else:
    log.append('[SKIP] onMounted pattern not found')

# ===== 修复8: 模板里加搜索栏（在 cat-bar 和 products-wrap 之间）=====
old_template_marker = '    </div>\n\n    <!-- ===== 产品网格 ===== -->'
new_filter_bar = '''    </div>

    <!-- ===== 筛选栏 ===== -->
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

    <!-- ===== 产品网格 ===== -->'''
if old_template_marker in content:
    content = content.replace(old_template_marker, new_filter_bar)
    log.append('[OK] template: added filter bar (search + selects)')
else:
    log.append('[SKIP] template marker not found (filter bar may already exist)')

# ===== 修复9: 加 filter-bar CSS =====
# 在 <style scoped> 前面插入 CSS
css_to_add = '''
/* ===== 筛选栏 ===== */
.filter-bar {
  background: #FFFFFF;
  border-bottom: 1px solid rgba(0,0,0,0.05);
  padding: 14px 80px;
  position: sticky;
  top: 112px;
  z-index: 99;
}
.filter-inner {
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 16px;
}
.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #F5F5F5;
  border-radius: 980px;
  padding: 8px 16px;
  flex: 1;
  max-width: 420px;
}
.search-box svg { flex-shrink: 0; }
.search-input {
  border: none;
  background: none;
  outline: none;
  font-size: 13px;
  color: #1a1a1a;
  width: 100%;
  font-family: inherit;
}
.search-input::placeholder { color: #999; }
.filter-selects {
  display: flex;
  gap: 8px;
}
.filter-select {
  appearance: none;
  -webkit-appearance: none;
  background: #F5F5F5;
  border: none;
  border-radius: 980px;
  padding: 8px 32px 8px 16px;
  font-size: 13px;
  color: #555;
  cursor: pointer;
  outline: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23999'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 10px 6px;
}
.filter-select:hover { background-color: #EBEBEB; }
'''

# 在 </style> 前插入
if '</style>' in content:
    content = content.replace('</style>', css_to_add + '\n</style>')
    log.append('[OK] added filter-bar CSS')
else:
    log.append('[SKIP] </style> not found')

# 写回
with open('ProductList.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixes applied:')
for l in log:
    print(f'  {l}')
print(f'Done. Total: {len([l for l in log if "[OK]" in l])} fixes applied')
