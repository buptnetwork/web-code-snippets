<script setup lang="ts">
import { classroomUi, openClassroom } from './composables/useClassroomUi'
import { readCourseMetadata } from './services/slidev-classroom-adapter'
const enabled = import.meta.env.VITE_CLASSROOM_ENABLED === 'true'
</script>

<template>
  <button
    v-if="enabled && ($nav.isPlaying || $nav.isPresenter) && !$nav.isPrintMode && readCourseMetadata($nav.slides[0]?.meta?.slide?.frontmatter)"
    class="classroom-nav-button" type="button" :title="`课堂互动 · ${classroomUi.status}`"
    :aria-expanded="classroomUi.panelOpen" aria-label="打开课堂互动" aria-haspopup="dialog"
    @click.stop="openClassroom" @pointerdown.stop @keydown.space.stop @keydown.enter.stop
  >互动<span v-if="classroomUi.status !== '未连接'" class="classroom-status-dot" /></button>
</template>

<style scoped>
.classroom-nav-button { display: inline-flex; align-items: center; gap: 5px; padding: 5px 9px; border-radius: 6px; font-size: 13px; cursor: pointer; }
.classroom-nav-button:hover { background: #8882; }
.classroom-nav-button:focus-visible { outline: 2px solid #0d9488; }
.classroom-status-dot { width: 6px; height: 6px; border-radius: 50%; background: #0d9488; }
@media print { .classroom-nav-button { display: none; } }
</style>
