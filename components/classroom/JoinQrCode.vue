<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import QRCode from 'qrcode'
import { studentJoinUrl } from '../../services/slidev-classroom-adapter'

const props = defineProps<{ code: string; studentBase: string }>()
const url = computed(() => studentJoinUrl(props.studentBase, props.code, window.location.origin))
const image = ref('')
const message = ref('')
watch(url, async (value, _, onCleanup) => {
  let cancelled = false
  onCleanup(() => { cancelled = true })
  image.value = ''
  message.value = ''
  try {
    const result = await QRCode.toDataURL(value, { width: 360, margin: 4, errorCorrectionLevel: 'M' })
    if (!cancelled) image.value = result
  }
  catch { if (!cancelled) message.value = '二维码生成失败，可使用下方链接和加入码。' }
}, { immediate: true })
async function copy() {
  try { await navigator.clipboard.writeText(url.value); message.value = '已复制学生加入链接。' }
  catch { message.value = '请手动选择并复制下方链接。' }
}
</script>

<template>
  <div class="cr-qr">
    <img v-if="image" :src="image" alt="学生加入本次课堂的二维码" width="300" height="300">
    <p class="cr-join-code">{{ code }}</p>
    <p class="cr-muted">扫码加入，或在学生入口输入上方加入码</p>
    <a class="cr-link cr-break" :href="url" target="_blank" rel="noopener noreferrer">{{ url }}</a>
    <button class="cr-button" type="button" @click="copy">复制加入链接</button>
    <p v-if="message" class="cr-muted" role="status">{{ message }}</p>
  </div>
</template>
