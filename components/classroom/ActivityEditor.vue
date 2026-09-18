<script setup lang="ts">
import { ref } from 'vue'
import type { ActivityDraft } from '../../types/classroom'
import { validateActivityDraft } from '../../services/classroom-presentation'
import { randomRequestId } from '../../composables/useClassroom'
const props = defineProps<{ initial?: ActivityDraft; busy: boolean; page: number }>()
const emit = defineEmits<{ save: [draft: ActivityDraft]; cancel: [] }>()
const type = ref(props.initial?.type || 'text')
const title = ref(props.initial?.title || '')
const selectionMode = ref(props.initial?.selectionMode || 'single')
const options = ref(props.initial?.options?.map(option => ({ ...option })) || [{ id: randomRequestId(), label: '' }, { id: randomRequestId(), label: '' }])
const correctIds = ref([...(props.initial?.correctOptionIds || [])])
const error = ref('')
function remove(id: string) { options.value = options.value.filter(option => option.id !== id); correctIds.value = correctIds.value.filter(value => value !== id) }
function submit() {
  const draft: ActivityDraft = { type: type.value, title: title.value.trim(), sourceSlide: props.initial?.sourceSlide || props.page }
  if (type.value === 'choice') Object.assign(draft, { selectionMode: selectionMode.value, options: options.value.map(option => ({ ...option, label: option.label.trim() })), correctOptionIds: [...correctIds.value] })
  error.value = validateActivityDraft(draft) || ''
  if (!error.value) emit('save', draft)
}
</script>

<template>
  <form class="cr-card cr-stack" @submit.prevent="submit">
    <div class="cr-row cr-between"><h3 class="cr-subheading">{{ initial ? '编辑 / 复制活动' : '新建活动' }}</h3><button type="button" class="cr-button cr-quiet" @click="emit('cancel')">取消</button></div>
    <label class="cr-label">互动类型<select v-model="type" class="cr-input"><option value="text">自由文本</option><option value="choice">选择题</option></select></label>
    <label class="cr-label">题干<textarea v-model="title" class="cr-input" rows="3" maxlength="500" required placeholder="你想请同学们讨论什么？" /></label>
    <template v-if="type === 'choice'">
      <label class="cr-label">选择方式<select v-model="selectionMode" class="cr-input" @change="correctIds = []"><option value="single">单选</option><option value="multiple">多选</option></select></label>
      <p class="cr-muted">勾选正确选项；全部不勾选表示投票。答案不会写入课件。</p>
      <div v-for="(option, index) in options" :key="option.id" class="cr-row">
        <input v-model="correctIds" type="checkbox" :value="option.id" :aria-label="`选项 ${index + 1} 为正确答案`">
        <input v-model="option.label" class="cr-input" :aria-label="`选项 ${index + 1}`" :placeholder="`选项 ${index + 1}`" maxlength="100" required>
        <button type="button" class="cr-button cr-quiet" :disabled="options.length <= 2" :aria-label="`删除选项 ${index + 1}`" @click="remove(option.id)">删除</button>
      </div>
      <button type="button" class="cr-button" :disabled="options.length >= 8" @click="options.push({ id: randomRequestId(), label: '' })">添加选项</button>
    </template>
    <p v-if="error" class="cr-error" role="alert">{{ error }}</p>
    <button class="cr-button cr-primary" :disabled="busy" type="submit">保存为草稿</button>
  </form>
</template>
