<script setup lang="ts">
import { computed, defineAsyncComponent, ref, watch } from 'vue'
import { classroomUi } from '../../composables/useClassroomUi'
import { readCourseMetadata, resolveClassroomConfig } from '../../services/slidev-classroom-adapter'
const props = defineProps<{ frontmatter: unknown; allowed: boolean; page: number }>()
const enabled = import.meta.env.VITE_CLASSROOM_ENABLED === 'true'
const metadata = computed(() => readCourseMetadata(props.frontmatter))
const loadError = ref('')
const loading = ref(true)
const config = computed(() => {
  try { return resolveClassroomConfig(import.meta.env, window.location.origin) }
  catch { return null }
})
const Runtime = defineAsyncComponent({
  loader: async () => {
    try { return await import('./ClassroomRuntime.vue') }
    finally { loading.value = false }
  },
  onError(_error, _retry, fail) { loadError.value = '互动模块加载失败，请刷新页面重试。'; fail() },
})
watch(() => props.allowed, allowed => {
  if (!allowed) { classroomUi.activated = false; classroomUi.panelOpen = false }
})
</script>

<template>
  <template v-if="enabled && allowed && metadata && classroomUi.activated">
    <Teleport v-if="(!config || loadError || loading) && classroomUi.panelOpen" to="body">
      <div class="classroom-load-error" role="status" @click.stop @keydown.stop @keydown.esc="classroomUi.panelOpen = false">
        <p>{{ loadError || (!config ? '互动配置无效：API 与学生入口必须使用同源 HTTP(S) 地址。' : '正在加载互动模块…') }}</p>
        <button type="button" @click="classroomUi.panelOpen = false">关闭</button>
      </div>
    </Teleport>
    <Runtime v-if="config && !loadError" :key="`${metadata.courseId}:${metadata.deckId}`" :metadata="metadata" :config="config" :page="page" />
  </template>
</template>

<style scoped>
.classroom-load-error { position: fixed; inset: 20% 10% auto; z-index: 300; padding: 24px; color: #991b1b; background: white; border: 1px solid #fca5a5; border-radius: 12px; box-shadow: 0 20px 80px #0005; }
.classroom-load-error button { margin-top: 16px; cursor: pointer; text-decoration: underline; }
@media print { .classroom-load-error { display: none; } }
</style>
