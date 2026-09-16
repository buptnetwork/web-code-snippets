<!--
  五条理由的全场导航条。用在单元三～七的首页，high 指明当前高亮到第几条。
  对应教案 2.3「做成全场导航条，后面每进一个单元高亮一条」。
-->
<script setup lang="ts">
const props = defineProps<{ active: number }>()

const items = [
  { no: '①', label: '技术史规律' },
  { no: '②', label: '表达精度' },
  { no: '③', label: '判断与取舍' },
  { no: '④', label: '决策杠杆' },
  { no: '⑤', label: '领域事实' },
]
</script>

<template>
  <div class="abs-bl w-full px-14 pb-4 flex items-center gap-2 text-xs">
    <div
      v-for="(it, i) in items"
      :key="it.no"
      class="flex-1 flex items-center gap-1.5 px-2 py-1 rounded transition-all duration-300"
      :class="i + 1 === props.active
        ? 'bg-teal-500/15 text-teal-600 dark:text-teal-300 font-bold'
        : 'opacity-30'"
    >
      <span>{{ it.no }}</span>
      <span class="truncate">{{ it.label }}</span>
    </div>
  </div>
</template>
