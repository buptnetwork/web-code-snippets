<script setup lang="ts">
import type { ChoiceOption, ChoiceStatistics } from '../../types/classroom'
defineProps<{ options: ChoiceOption[]; results: ChoiceStatistics; correctIds?: string[]; multiple?: boolean }>()
function percentage(count: number, total: number) { return total > 0 ? Math.min(100, Math.round(count / total * 100)) : 0 }
</script>

<template>
  <div class="cr-results">
    <p class="cr-muted">已收到 {{ results.respondentCount }} 份回答<span v-if="multiple"> · 多选题，各项比例之和可能超过 100%</span></p>
    <div v-for="option in options" :key="option.id" class="cr-result-row">
      <div class="cr-row cr-between">
        <span>{{ option.label }} <span v-if="correctIds?.includes(option.id)" class="cr-tag">正确答案</span></span>
        <strong>{{ results.counts[option.id] || 0 }} 人 · {{ percentage(results.counts[option.id] || 0, results.respondentCount) }}%</strong>
      </div>
      <div class="cr-bar"><div :style="{ width: `${percentage(results.counts[option.id] || 0, results.respondentCount)}%` }" /></div>
    </div>
  </div>
</template>
