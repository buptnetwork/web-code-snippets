<script setup lang="ts">
import type { ClassroomComment } from '../../types/classroom'
defineProps<{ comments: ClassroomComment[] }>()
</script>

<template>
  <div class="cr-comment-wall">
    <p v-if="!comments.length" class="cr-empty">等待教师选出值得分享的想法。</p>
    <article v-for="comment in comments" :key="comment.responseId" class="cr-comment" :class="{ 'cr-pinned': comment.pinned }">
      <span v-if="comment.pinned" class="cr-tag">精选</span>
      <p class="cr-prewrap">{{ comment.text }}</p>
    </article>
  </div>
</template>
