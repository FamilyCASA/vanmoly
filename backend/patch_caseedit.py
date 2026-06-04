from pathlib import Path

f = Path(r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\admin\CaseEdit.vue')
content = f.read_text(encoding='utf-8')

# 1. 效果图图集标签：6阶段 → 9阶段
content = content.replace('效果图图集（6阶段）</h4>', '效果图图集（9阶段）</h4>')

# 2. 移除幻灯片配置Tab里的材质展示配置区域
old_block = """              <el-divider content-position="left" v-if="slideConfig.show_material">材质展示配置</el-divider>
              <div v-if="slideConfig.show_material" class="showcase-material-section">
                <el-form-item label="展示物料">
                  <el-select
                    v-model="slideConfig.showcase_material_ids"
                    multiple
                    filterable
                    placeholder="选择要在幻灯片中展示的物料"
                    style="width: 100%"
                    :loading="showcaseLoading"
                  >
                    <el-option-group
                      v-for="group in showcaseGrouped"
                      :key="group.label"
                      :label="group.label"
                    >
                      <el-option
                        v-for="item in group.options"
                        :key="item.id"
                        :label="item.sku_name"
                        :value="item.id"
                      >
                        <span>{{ item.sku_name }}</span>
                        <el-tag size="small" type="info" style="margin-left:8px">{{ item.l2 }}</el-tag>
                      </el-option>
                    </el-option-group>
                  </el-select>
                  <div class="form-tip">从已配置的物料中选择要展示在幻灯片"材质解析"页的物料</div>
                </el-form-item>
              </div>

              <el-divider content-position="left">风格与配色</el-divider>"""

new_block = '              <el-divider content-position="left">风格与配色</el-divider>'

if old_block in content:
    content = content.replace(old_block, new_block)
    print("✅ 已移除材质展示配置区域")
else:
    print("⚠️  未找到材质展示配置区域，可能已移除或结构有变化")

f.write_text(content, encoding='utf-8')
print("✅ CaseEdit.vue 已更新")
print("改动：1) 效果图图集 6阶段→9阶段  2) 移除幻灯片配置Tab里的材质展示配置区域")
