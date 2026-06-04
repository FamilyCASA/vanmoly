from pathlib import Path

f = Path(r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\admin\CaseEdit.vue')
content = f.read_text(encoding='utf-8')

# 1. 效果图图集：6阶段 -> 9阶段
old1 = '效果图图集（6阶段）</h4>'
new1 = '效果图图集（9阶段）</h4>'
if old1 in content:
    content = content.replace(old1, new1)
    print("[OK] 效果图图集标签已更新为9阶段")
else:
    print("[WARN] 未找到'效果图图集（6阶段）'，可能已修改")

# 2. 移除幻灯片配置Tab里的材质展示配置区域
old2 = (
    '<div v-if="slideConfig.show_material" class="showcase-material-section">\n'
    '                <el-form-item label="展示物料">\n'
    '                  <el-select\n'
    '                    v-model="slideConfig.showcase_material_ids"\n'
    '                    multiple\n'
    '                    filterable\n'
    '                    placeholder="选择要在幻灯片中展示的物料"\n'
    '                    style="width: 100%"\n'
    '                    :loading="showcaseLoading"\n'
    '                  >\n'
    '                    <el-option-group\n'
    '                      v-for="group in showcaseGrouped"\n'
    '                      :key="group.label"\n'
    '                      :label="group.label"\n'
    '                    >\n'
    '                      <el-option\n'
    '                        v-for="item in group.options"\n'
    '                        :key="item.id"\n'
    '                        :label="item.sku_name"\n'
    '                        :value="item.id"\n'
    '                      >\n'
    '                        <span>{{ item.sku_name }}</span>\n'
    '                        <el-tag size="small" type="info" style="margin-left:8px">{{ item.l2 }}</el-tag>\n'
    '                      </el-option>\n'
    '                    </el-option-group>\n'
    '                  </el-select>\n'
    '                  <div class="form-tip">从已配置的物料中选择要展示在幻灯片"材质解析"页的物料</div>\n'
    '                </el-form-item>\n'
    '              </div>\n\n'
)

if old2 in content:
    content = content.replace(old2, '')
    print("[OK] 已移除幻灯片配置Tab里的材质展示配置区域")
elif 'showcase-material-section' in content:
    print("[WARN] 找到了材质配置区域但文本不匹配，尝试定位...")
    idx = content.find('showcase-material-section')
    print(f"  位置: {idx}")
else:
    print("[INFO] 材质展示配置区域已不存在（可能已移除）")

f.write_text(content, encoding='utf-8')
print("\nDone. CaseEdit.vue 已保存")
