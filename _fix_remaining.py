# coding: utf-8
import re

with open(r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseDetailV2.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# === FIX 1: phase1 layout_images img :src ===
content = content.replace(
    ':src="img" alt="户型图"',
    ':src="resolveImgUrl(img)" alt="户型图"'
)
# 防止重复替换（已经替换过则跳过）
content = content.replace(
    ':src="resolveImgUrl(img)" alt="户型图"',
    ':src="resolveImgUrl(img)" alt="户型图"'
)

# === FIX 2: design_concept v-html ===
content = content.replace(
    '<p class="phase-body">{{ caseDetail.design_concept }}</p>',
    '<p class="phase-body rich-text" v-html="caseDetail.design_concept"></p>'
)

# === FIX 3: phase5 showcase 全宽展示 grid ===
old_grid = """.phase-images-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.phase-img-card {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 4/3;
}
.phase-img-card img {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform 0.4s;
}
.phase-img-card:hover img { transform: scale(1.05); }"""

new_grid = """.phase-images-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  width: 100%;
}
.phase-img-card {
  position: relative;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  flex: 0 0 calc(25% - 5px);
  max-width: calc(25% - 5px);
}
.phase-img-card img {
  width: 100%;
  height: auto;
  max-height: 320px;
  object-fit: cover;
  display: block;
  transition: transform 0.4s;
}
.phase-img-card:hover img { transform: scale(1.02); }"""

content = content.replace(old_grid, new_grid)

# === FIX 4: spaces 瀑布流全宽展示（description在图片上方） ===
# 替换 gallery-masonry 为全宽样式
old_gallery = """.gallery-masonry {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.gallery-item {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 1;
}

.gallery-item.large {
  grid-column: span 2;
  grid-row: span 2;
}

.gallery-item.wide {
  grid-column: span 2;
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.gallery-item:hover img {
  transform: scale(1.05);
}

.item-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.gallery-item:hover .item-overlay {
  opacity: 1;
}"""

new_gallery = """.gallery-masonry {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.gallery-item {
  position: relative;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
}

.gallery-item img {
  width: 100%;
  height: auto;
  max-height: 280px;
  object-fit: cover;
  display: block;
  transition: transform 0.5s ease;
}

.gallery-item:hover img { transform: scale(1.02); }

.gallery-item-desc {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.85));
  color: #fff;
  padding: 24px 12px 10px;
  font-size: 12px;
  line-height: 1.5;
  opacity: 0;
  transition: opacity 0.3s;
}

.gallery-item:hover .gallery-item-desc { opacity: 1; }

.item-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.2);
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity 0.3s;
}
.gallery-item:hover .item-overlay { opacity: 1; }"""

content = content.replace(old_gallery, new_gallery)

# === FIX 5: spaces 模板中显示 description（放在 img 上方 overlay） ===
# 修改有简介的 gallery-item，加入 description
old_gallery_item_template = """                  <div
                    v-for="(item, idx) in space.itemsNoDesc"
                    :key="item.id || idx"
                    class="gallery-item"
                    :class="{ large: idx % 5 === 0, wide: idx % 5 === 3 }"
                    @click="openImagePreview(0, space.items.map(i => resolveImgUrl(i)))"
                  >
                    <img :src="resolveImgUrl(item)" loading="lazy" />
                    <div class="item-overlay"><el-icon><ZoomIn /></el-icon></div>
                  </div>"""

new_gallery_item_template = """                  <div
                    v-for="(item, idx) in space.itemsNoDesc"
                    :key="item.id || idx"
                    class="gallery-item"
                    @click="openImagePreview(0, space.items.map(i => resolveImgUrl(i)))"
                  >
                    <img :src="resolveImgUrl(item)" loading="lazy" />
                    <div class="gallery-item-desc" v-if="item.description">{{ item.description }}</div>
                    <div class="item-overlay"><el-icon><ZoomIn /></el-icon></div>
                  </div>"""

content = content.replace(old_gallery_item_template, new_gallery_item_template)

with open(r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseDetailV2.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done! Fixes applied.')