<!--
  本课路线图导航条（1.9.1 提出，后续各节可回访并高亮当前位置）。
  active 指明当前高亮到第几个环节（1~8）；active=0 表示总览、不高亮任何一节。
  对应教案 1.9.1「做成后续各节可回访、可高亮当前位置的形式」。
-->
<script setup lang="ts">
const props = defineProps<{ active?: number }>()

const items = [
  { no: '①', label: '算法是什么' },
  { no: '②', label: '怎么写下来' },
  { no: '③', label: '怎么数次数' },
  { no: '④', label: '怎么严格表述' },
  { no: '⑤', label: '输入不同怎么办' },
  { no: '⑥', label: '偶尔昂贵怎么办' },
  { no: '⑦', label: '理论靠得住吗' },
  { no: '⑧', label: '怎么验证' },
]
</script>

<template>
  <div class="w-full grid grid-cols-4 gap-x-3 gap-y-2 text-xs">
    <div
      v-for="(it, i) in items"
      :key="it.no"
      class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md border transition-all duration-300"
      :class="i + 1 === props.active
        ? 'bg-teal-500/15 border-teal-500/60 text-teal-700 dark:text-teal-300 font-bold'
        : 'border-gray-400/25 opacity-45'"
    >
      <span class="shrink-0">{{ it.no }}</span>
      <span class="truncate">{{ it.label }}</span>
    </div>
  </div>
</template>
