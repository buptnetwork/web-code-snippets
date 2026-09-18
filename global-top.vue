<script setup lang="ts">
import ClassroomHost from './components/classroom/ClassroomHost.vue'
</script>

<template>
  <ClassroomHost
    :frontmatter="$nav.slides[0]?.meta?.slide?.frontmatter"
    :allowed="!!($nav.isPlaying || $nav.isPresenter) && !$nav.isPrintMode"
    :page="$nav.currentSlideNo"
  />
</template>
