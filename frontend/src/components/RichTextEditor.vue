<template>
  <div class="rich-text-editor" style="border: 1px solid #ccc">
    <Toolbar
      :editor="editorRef"
      :defaultConfig="toolbarConfig"
      :mode="mode"
      style="border-bottom: 1px solid #ccc"
    />
    <Editor
      v-model="valueHtml"
      :defaultConfig="editorConfig"
      :mode="mode"
      style="height: 300px; overflow-y: hidden;"
      @onCreated="onCreated"
      @onChange="onChange"
    />
  </div>
</template>

<script setup>
import { ref, shallowRef, onBeforeUnmount, watch, computed } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '请输入内容...'
  },
  mode: {
    type: String,
    default: 'simple' // simple | default
  },
  height: {
    type: String,
    default: '300px'
  }
})

const emit = defineEmits(['update:modelValue'])

// 编辑器实例
const editorRef = shallowRef()

// HTML内容
const valueHtml = ref(props.modelValue || '')

// 监听外部变化
watch(() => props.modelValue, (newVal) => {
  if (newVal !== valueHtml.value) {
    valueHtml.value = newVal || ''
  }
})

// 工具栏配置
const toolbarConfig = {
  toolbarKeys: [
    'bold',
    'underline',
    'italic',
    'through',
    '|',
    'fontSize',
    'fontFamily',
    'color',
    'bgColor',
    '|',
    'bulletedList',
    'numberedList',
    'justifyLeft',
    'justifyCenter',
    'justifyRight',
    '|',
    'insertLink',
    'insertImage',
    '|',
    'undo',
    'redo',
    '|',
    'fullScreen'
  ]
}

// 编辑器配置
const editorConfig = {
  placeholder: props.placeholder,
  MENU_CONF: {
    // 上传图片配置
    uploadImage: {
      // 自定义上传
      async customUpload(file, insertFn) {
        // TODO: 实现图片上传
        // const url = await uploadFile(file)
        // insertFn(url)
        console.log('upload image:', file.name)
      }
    }
  }
}

// 编辑器创建
const onCreated = (editor) => {
  editorRef.value = editor
}

// 内容变化
const onChange = (editor) => {
  emit('update:modelValue', editor.getHtml())
}

// 组件销毁前
onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor) {
    editor.destroy()
  }
})
</script>

<style scoped>
.rich-text-editor {
  width: 100%;
}
</style>
