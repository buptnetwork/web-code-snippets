<script setup lang="ts">
// 每页右上角的校徽角标。
// 封面（cover）与整屏高光页（full）不放，保持干净；其余页统一铺。
// 校徽在 36px 下外圈环绕字不可读，但蓝色圆章形状一眼可认——角标要的是形状识别，不是文字阅读。
</script>

<template>
  <img
    v-if="$nav.currentLayout !== 'cover' && $nav.currentLayout !== 'full'"
    src="/images/common/bupt_logo.png"
    alt=""
    class="absolute top-4 right-5 h-9 w-9 select-none pointer-events-none opacity-40 dark:opacity-70"
  />
</template>
