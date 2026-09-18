<script setup lang="ts">
import { computed } from 'vue'
import type { ClassroomSnapshot } from '../../types/classroom'
import { publicComments, publicResults } from '../../services/classroom-presentation'
import JoinQrCode from './JoinQrCode.vue'
import ChoiceResults from './ChoiceResults.vue'
import CommentWall from './CommentWall.vue'
const props = defineProps<{ snapshot: ClassroomSnapshot; studentBase: string; warning: string }>()
defineEmits<{ hide: [] }>()
const results = computed(() => publicResults(props.snapshot))
const comments = computed(() => publicComments(props.snapshot))
const activity = computed(() => props.snapshot.currentActivity)
</script>

<template>
  <section class="cr-shell cr-display" aria-label="课堂互动展示" @click.stop @pointerdown.stop @keydown.stop>
    <header class="cr-row cr-between">
      <div><span class="cr-eyebrow">课堂互动</span><p class="cr-muted">{{ snapshot.session.displayName }}</p></div>
      <button class="cr-button cr-quiet" type="button" @click="$emit('hide')">仅在本窗口收起</button>
    </header>
    <p v-if="warning" class="cr-notice" role="status">{{ warning }} · 当前内容可能不是最新状态</p>
    <div class="cr-display-content">
      <template v-if="snapshot.displayMode === 'join'">
        <h2 class="cr-heading">把你的想法带进课堂</h2>
        <JoinQrCode v-if="snapshot.session.joinCode" :code="snapshot.session.joinCode" :student-base="studentBase" />
        <p v-else class="cr-empty">等待教师提供加入码。</p>
      </template>
      <template v-else-if="activity && activity.status !== 'draft'">
        <span class="cr-tag">{{ activity.type === 'text' ? '自由表达' : activity.selectionMode === 'multiple' ? '多项选择' : '单项选择' }}</span>
        <h2 class="cr-heading cr-prewrap">{{ activity.title }}</h2>
        <template v-if="snapshot.displayMode === 'results'">
          <ChoiceResults v-if="activity.type === 'choice' && results" :options="activity.options || []" :results="results" :multiple="activity.selectionMode === 'multiple'" :correct-ids="activity.answersRevealed ? activity.correctOptionIds : []" />
          <p v-else-if="activity.type === 'choice'" class="cr-empty">教师尚未公开统计结果。</p>
          <CommentWall v-else :comments="comments" />
        </template>
        <ol v-else-if="activity.type === 'choice'" class="cr-option-list">
          <li v-for="option in activity.options" :key="option.id">{{ option.label }}</li>
        </ol>
        <p v-else class="cr-empty">请在手机页面写下你的想法。</p>
      </template>
      <p v-else class="cr-empty">等待教师发布活动。</p>
    </div>
  </section>
</template>
