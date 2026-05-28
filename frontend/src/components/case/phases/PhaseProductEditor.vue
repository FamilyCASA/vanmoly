<template>
  <div class="phase-product-editor">
    <el-form label-position="top">
      <!-- 物料展示图（最多20张） -->
      <el-form-item label="物料展示图（最多20张）">
        <div class="image-upload-grid">
          <div
            v-for="(img, idx) in productGallery"
            :key="idx"
            class="uploaded-image-card"
          >
            <img :src="img.url || img" alt="物料图" />
            <div v-if="img.uploading" class="uploading-mask">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>上传中...</span>
            </div>
            <div class="img-overlay">
              <el-icon class="delete-btn" @click="removeImage(idx)">
                <Close />
              </el-icon>
            </div>
          </div>
          <div
            v-if="productGallery.length < 20"
            class="upload-trigger"
            @click="triggerUpload"
          >
            <el-icon><Plus /></el-icon>
            <span>上传物料图</span>
          </div>
        </div>
        <el-upload
          ref="uploadRef"
          :action="uploadUrl"
          :headers="uploadHeaders"
          :show-file-list="false"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :before-upload="beforeUpload"
          accept="image/*"
          style="display: none;"
        />
        <div class="upload-tip">展示瓷砖、地板、卫浴、灯具、家具等物料实拍</div>
      </el-form-item>

      <!-- 物料清单 -->
      <el-form-item label="物料清单">
        <div class="product-list-header">
          <el-button type="primary" size="small" @click="addProduct">
            <el-icon><Plus /></el-icon>添加物料
          </el-button>
          <span class="product-count">共 {{ productList.length }} 项物料</span>
        </div>
        <el-table :data="productList" border size="small" style="width: 100%">
          <el-table-column prop="material_name" label="物料名称" min-width="120">
            <template #default="{ row }">
              <el-input v-model="row.material_name" size="small" placeholder="物料名称" @input="emitUpdate" />
            </template>
          </el-table-column>
          <el-table-column prop="brand" label="品牌" width="100">
            <template #default="{ row }">
              <el-input v-model="row.brand" size="small" placeholder="品牌" @input="emitUpdate" />
            </template>
          </el-table-column>
          <el-table-column prop="category" label="分类" width="100">
            <template #default="{ row }">
              <el-input v-model="row.category" size="small" placeholder="分类" @input="emitUpdate" />
            </template>
          </el-table-column>
          <el-table-column prop="sku_code" label="SKU编码" width="120">
            <template #default="{ row }">
              <el-input v-model="row.sku_code" size="small" placeholder="SKU编码" @input="emitUpdate" />
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="80">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" size="small" :min="0" :precision="0" controls-position="right" @change="emitUpdate" />
            </template>
          </el-table-column>
          <el-table-column prop="unit_price" label="单价(元)" width="100">
            <template #default="{ row }">
              <el-input-number v-model="row.unit_price" size="small" :min="0" :precision="2" controls-position="right" @change="emitUpdate" />
            </template>
          </el-table-column>
          <el-table-column label="小计" width="100">
            <template #default="{ row }">
              <span style="font-weight: 600; color: #e6a23c;">¥{{ ((row.quantity || 0) * (row.unit_price || 0)).toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="图片" width="80">
            <template #default="{ row }">
              <el-image v-if="row.material_image" :src="row.material_image" style="width:40px;height:40px" fit="cover" />
              <span v-else style="color:#c0c4cc;font-size:12px">无图</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="60" fixed="right">
            <template #default="{ $index }">
              <el-button type="danger" link size="small" @click="removeProduct($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 合计 -->
        <div class="product-total" v-if="productList.length > 0">
          <span>物料合计：</span>
          <span class="total-amount">¥{{ totalAmount }}</span>
        </div>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Close, Loading } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const uploadUrl = '/api/v3/upload'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

const uploadRef = ref(null)
const productGallery = ref([])
const productList = ref([])

// 合计金额
const totalAmount = computed(() => {
  return productList.value.reduce((sum, item) => {
    return sum + (item.quantity || 0) * (item.unit_price || 0)
  }, 0).toFixed(2)
})

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    productGallery.value = newVal.product_gallery || []
    productList.value = newVal.product_list || []
  }
}, { immediate: true })

const triggerUpload = () => {
  uploadRef.value?.$el?.querySelector('input')?.click()
}

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (productGallery.value.length >= 20) {
    ElMessage.warning('最多上传20张物料图')
    return false
  }
  const localUrl = URL.createObjectURL(file)
  productGallery.value.push({ url: localUrl, uploading: true })
  emitUpdate()
  return true
}

const handleUploadSuccess = (res) => {
  const url = res?.url || res?.data?.url || res?.file_url || res?.data?.file_url
  if (url) {
    const uploadingIdx = productGallery.value.findIndex(img => img.uploading)
    if (uploadingIdx >= 0) {
      URL.revokeObjectURL(productGallery.value[uploadingIdx].url)
      productGallery.value[uploadingIdx] = { url, uploading: false }
    } else {
      productGallery.value.push({ url, uploading: false })
    }
    emitUpdate()
  } else {
    handleUploadError(new Error('返回格式异常'))
  }
}

const handleUploadError = (err) => {
  const uploadingIdx = productGallery.value.findIndex(img => img.uploading)
  if (uploadingIdx >= 0) {
    URL.revokeObjectURL(productGallery.value[uploadingIdx].url)
    productGallery.value.splice(uploadingIdx, 1)
    emitUpdate()
  }
  ElMessage.error('图片上传失败：' + (err?.message || '未知错误'))
}

const removeImage = (idx) => {
  const img = productGallery.value[idx]
  if (img && img.url && img.url.startsWith('blob:')) {
    URL.revokeObjectURL(img.url)
  }
  productGallery.value.splice(idx, 1)
  emitUpdate()
}

const addProduct = () => {
  productList.value.push({
    material_name: '',
    brand: '',
    category: '',
    sku_code: '',
    quantity: 1,
    unit_price: 0,
    material_image: ''
  })
  emitUpdate()
}

const removeProduct = (idx) => {
  productList.value.splice(idx, 1)
  emitUpdate()
}

const emitUpdate = () => {
  emit('update:modelValue', {
    product_gallery: productGallery.value.filter(img => !img.uploading).map(img => ({ url: img.url })),
    product_list: productList.value
  })
}
</script>

<style scoped>
.phase-product-editor {
  width: 100%;
}

.image-upload-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.uploaded-image-card {
  width: 150px;
  height: 150px;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  border: 1px solid #dcdfe6;
}

.uploaded-image-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.uploading-mask {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.85);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #409eff;
  font-size: 12px;
  gap: 4px;
}

.img-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.uploaded-image-card:hover .img-overlay {
  opacity: 1;
}

.delete-btn {
  font-size: 24px;
  color: white;
  cursor: pointer;
}

.upload-trigger {
  width: 150px;
  height: 150px;
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #8c939d;
}

.upload-trigger:hover {
  border-color: #409eff;
  color: #409eff;
}

.upload-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.product-list-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.product-count {
  font-size: 13px;
  color: #909399;
}

.product-total {
  margin-top: 12px;
  text-align: right;
  font-size: 15px;
  padding: 8px 12px;
  background: #fdf6ec;
  border-radius: 4px;
}

.total-amount {
  font-weight: 700;
  color: #e6a23c;
  font-size: 18px;
}
</style>
