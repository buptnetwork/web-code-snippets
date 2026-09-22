<script setup lang="ts">
import ClassroomHost from './components/classroom/ClassroomHost.vue'
import './styles/index.css'
</script>

<template>
  <ClassroomHost
    :frontmatter="$nav.slides[0]?.meta?.slide?.frontmatter"
    :allowed="!!($nav.isPlaying || $nav.isPresenter) && !$nav.isPrintMode"
    :page="$nav.currentSlideNo"
  />
</template>
