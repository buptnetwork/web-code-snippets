<!--
  「对应第 1 次课」绑定条。
  课前课（讲二）每个语法点都要标出"你会在第 1 次课的哪个文件见到它"，
  这是课前课与第 1 次课之间的绑定装置，底稿要求做成固定位置、与正文视觉分开的小条。
  用法：<LessonLink>…内容…</LessonLink>，可放在一页正文之后。
-->
<script setup lang="ts">
withDefaults(defineProps<{ label?: string }>(), { label: '对应第 1 次课' })
</script>

<template>
  <div class="lesson-link mt-4 flex items-start gap-2.5 px-3.5 py-2 rounded-lg border-l-4 border-sky-500/70 bg-sky-500/8 text-[13px] leading-relaxed">
    <span class="shrink-0 px-2 py-0.5 rounded bg-sky-500/15 text-sky-700 dark:text-sky-300 font-bold text-xs tracking-wide">{{ label }}</span>
    <span class="opacity-85"><slot /></span>
  </div>
</template>
