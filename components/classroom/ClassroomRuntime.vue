<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { createClassroomStore } from '../../composables/useClassroom'
import { classroomUi, openClassroom } from '../../composables/useClassroomUi'
import type { ClassroomConfig, CourseMetadata } from '../../types/classroom'
import TeacherPanel from './TeacherPanel.vue'
import ClassroomOverlay from './ClassroomOverlay.vue'
import './classroom.css'

const props = defineProps<{ config: ClassroomConfig; metadata: CourseMetadata; page: number }>()
let storage: Storage | undefined
try { storage = window.sessionStorage } catch { /* 浏览器可能禁止存储。 */ }
// 只有这个全局运行时拥有 store；翻页、收起面板不会再创建连接。
const store = createClassroomStore(props.metadata, props.config, { storage })
const { state } = store
const dialog = ref<HTMLDialogElement>()
const locallyHidden = ref(false)
let previousFocus: HTMLElement | null = null
const labels = { idle: '未连接', connecting: '正在连接', connected: '实时同步中', reconnecting: '正在重连', ended: '课堂已结束' }
const showDisplay = computed(() => state.snapshot?.session.status === 'active' && state.snapshot.displayMode !== 'hidden' && !locallyHidden.value)
watch(() => state.phase, value => { classroomUi.status = labels[value] }, { immediate: true })
watch([() => state.snapshot?.sessionId, () => state.snapshot?.displayMode, () => state.snapshot?.currentActivity?.activityId], () => { locallyHidden.value = false })
watch(() => state.error, value => { if (value) classroomUi.panelOpen = true })
watch(() => classroomUi.panelOpen, async open => {
  if (open) {
    previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null
    await nextTick()
    if (classroomUi.panelOpen && dialog.value && !dialog.value.open) dialog.value.showModal()
  }
  else {
    dialog.value?.close()
    previousFocus?.focus({ preventScroll: true })
  }
}, { immediate: true })
function closePanel() { classroomUi.panelOpen = false }
function visibilityChanged() { if (document.visibilityState === 'visible') store.reconnect() }
function pageHidden() {
  store.dispose()
  classroomUi.activated = false
  classroomUi.panelOpen = false
}
function displayKey(event: KeyboardEvent) {
  if (event.key === 'Escape') { event.preventDefault(); locallyHidden.value = true }
}
onMounted(() => {
  window.addEventListener('pagehide', pageHidden)
  document.addEventListener('visibilitychange', visibilityChanged)
})
onUnmounted(() => {
  window.removeEventListener('pagehide', pageHidden)
  document.removeEventListener('visibilitychange', visibilityChanged)
  store.dispose()
  classroomUi.status = '未连接'
})
</script>

<template>
  <Teleport to="body">
    <div class="cr-root">
      <ClassroomOverlay v-if="showDisplay && state.snapshot" :snapshot="state.snapshot" :student-base="config.studentBase" :warning="state.warning" @hide="locallyHidden = true" @keydown="displayKey" />
      <button v-if="!classroomUi.panelOpen" class="cr-button cr-resume" type="button" @click.stop="openClassroom" @keydown.space.stop @keydown.enter.stop>课堂互动 · {{ classroomUi.status }}</button>
      <dialog ref="dialog" class="cr-shell cr-panel" aria-labelledby="cr-panel-title" @cancel.prevent="closePanel" @click.stop @pointerdown.stop @keydown.stop @keyup.stop @wheel.stop>
        <header class="cr-row cr-between cr-panel-header">
          <div><span class="cr-eyebrow">课堂工作台</span><h2 id="cr-panel-title" class="cr-subheading">课堂互动</h2></div>
          <button class="cr-button" type="button" aria-label="收起互动面板" @click="closePanel">收起 · Esc</button>
        </header>
        <TeacherPanel v-if="classroomUi.panelOpen" :store="store" :config="config" :metadata="metadata" :page="page" @close="closePanel" @restore-display="locallyHidden = false" />
      </dialog>
    </div>
  </Teleport>
</template>
