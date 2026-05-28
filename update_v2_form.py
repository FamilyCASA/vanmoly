import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\admin\MaterialManageV2.vue'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Add three fields after "材质" field
old_material_field = """            <el-form-item label="材质">
              <el-input v-model="editDialog.form.material" placeholder="如: 橡木实木+环保漆" />
            </el-form-item>

            <el-form-item label="简短描述">"""

new_material_field = """            <el-form-item label="材质">
              <el-input v-model="editDialog.form.material" placeholder="如: 橡木实木+环保漆" />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="花色">
                  <el-input v-model="editDialog.form.color_name" placeholder="如: 胡桃木纹" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="环保等级">
                  <el-select v-model="editDialog.form.env_level" style="width: 100%">
                    <el-option label="合格" value="合格" />
                    <el-option label="E1" value="E1" />
                    <el-option label="E0" value="E0" />
                    <el-option label="ENF" value="ENF" />
                    <el-option label="CARB P2" value="CARB P2" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="供应链">
                  <el-select v-model="editDialog.form.supply_chain" style="width: 100%">
                    <el-option label="直供" value="直供" />
                    <el-option label="经销商" value="经销商" />
                    <el-option label="代采" value="代采" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="简短描述">"""

content = content.replace(old_material_field, new_material_field, 1)

# Now add default values in openEditDialog for these three fields
old_open_edit = """        is_public: true,"""
# Find the right context - there might be multiple
# Let's find the openEditDialog function
idx = content.find('openEditDialog(')
if idx > 0:
    # Find the form initialization in this function
    # Look for the form data object
    form_idx = content.find('is_public: true,', idx)
    if form_idx > 0:
        # Check if color_name already there
        check = content[form_idx:form_idx+200]
        if 'color_name' not in check:
            content = content[:form_idx] + """is_public: true,
          color_name: '',
          env_level: '合格',
          supply_chain: '直供',""" + content[form_idx + len('is_public: true,'):]
            print("✅ 新增物料默认值已添加")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 前端编辑对话框补齐: color_name/env_level/supply_chain")
