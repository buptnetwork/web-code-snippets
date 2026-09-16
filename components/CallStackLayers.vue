<!--
  mini 程序「调用栈 ↔ 分层」对位图（0.6 高光页用）。
  左侧＝断点命中时的 Call Stack（栈顶在上，与 VS Code 一致），
  右侧＝mini 的四层文件；两侧按「层」着色对位，直观呈现
  「栈帧的层次 ＝ 分层的层次」。

  ⚠ 复用说明：第 1 次课 1.5.1 会把这张图升级为正式的「四层依赖方向图」
  （cli → service → repo → models 的依赖箭头）。届时在本组件基础上扩展，
  不要另造一份。frames 可通过 prop 覆盖成第 1 次课的 FastAPI 八层栈。
-->
<script setup lang="ts">
type Layer = 'cli' | 'service' | 'repo' | 'models' | 'entry'
interface Frame { name: string; layer: Layer; note?: string }

withDefaults(defineProps<{ frames?: Frame[] }>(), {
  frames: () => [
    { name: 'JsonTodoRepo.get', layer: 'repo', note: '我在这' },
    { name: 'TodoService.get_todo', layer: 'service' },
    { name: 'TodoService.finish_todo', layer: 'service' },
    { name: 'main', layer: 'cli', note: 'cli.py' },
    { name: '<module>', layer: 'entry', note: '入口' },
  ],
})

const frameBox: Record<Layer, string> = {
  cli: 'border-sky-500/50 bg-sky-500/8',
  service: 'border-teal-500/50 bg-teal-500/8',
  repo: 'border-amber-500/50 bg-amber-500/8',
  models: 'border-purple-500/50 bg-purple-500/8',
  entry: 'border-gray-400/40 bg-gray-500/8',
}
const frameDot: Record<Layer, string> = {
  cli: 'bg-sky-500',
  service: 'bg-teal-500',
  repo: 'bg-amber-500',
  models: 'bg-purple-500',
  entry: 'bg-gray-400',
}

const layerBoxes = [
  { key: 'cli' as Layer, file: 'cli.py', desc: '外部输入翻译层', box: 'border-sky-500/40 bg-sky-500/6', dot: 'bg-sky-500', text: 'text-sky-700 dark:text-sky-300' },
  { key: 'service' as Layer, file: 'service.py', desc: '业务规则层', box: 'border-teal-500/40 bg-teal-500/6', dot: 'bg-teal-500', text: 'text-teal-700 dark:text-teal-300' },
  { key: 'repo' as Layer, file: 'repo.py', desc: '数据访问层', box: 'border-amber-500/40 bg-amber-500/6', dot: 'bg-amber-500', text: 'text-amber-700 dark:text-amber-300' },
]
</script>

<template>
  <div grid="~ cols-[1.05fr_auto_1fr] gap-3 items-center">
    <!-- 左：调用栈 -->
    <div>
      <div class="text-xs tracking-widest opacity-60 mb-2 text-center">Call Stack（栈顶在上）</div>
      <div class="flex flex-col gap-1.5">
        <div
          v-for="(f, i) in frames" :key="i"
          class="flex items-center gap-2 px-2.5 py-1.5 rounded-md border font-mono text-[13px]"
          :class="frameBox[f.layer]"
        >
          <span class="w-2 h-2 rounded-full shrink-0" :class="frameDot[f.layer]" />
          <span class="font-bold truncate">{{ f.name }}</span>
          <span v-if="f.note" class="ml-auto text-[10px] opacity-55 font-sans shrink-0">{{ f.note }}</span>
          <span v-if="i === 0" class="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-700 dark:text-amber-300 font-bold font-sans shrink-0">栈顶</span>
        </div>
      </div>
    </div>

    <!-- 中：对位 -->
    <div class="text-center">
      <div class="text-2xl opacity-40 leading-none">↔</div>
      <div class="mt-1 text-[10px] opacity-50 writing-mode-vertical" style="writing-mode: vertical-rl">同色＝同层</div>
    </div>

    <!-- 右：四层文件 -->
    <div>
      <div class="text-xs tracking-widest opacity-60 mb-2 text-center">mini 的四层</div>
      <div class="flex flex-col gap-1.5">
        <div
          v-for="l in layerBoxes" :key="l.key"
          class="flex items-center gap-2 px-2.5 py-1.5 rounded-md border"
          :class="l.box"
        >
          <span class="w-2 h-2 rounded-full shrink-0" :class="l.dot" />
          <span class="font-mono text-[13px] font-bold truncate" :class="l.text">{{ l.file }}</span>
          <span class="ml-auto text-[11px] opacity-70 shrink-0">{{ l.desc }}</span>
        </div>
        <div class="mt-1 pt-1.5 border-t border-dashed border-gray-400/30 flex items-center gap-2 px-2.5 py-1.5 rounded-md border border-purple-500/30 bg-purple-500/5">
          <span class="w-2 h-2 rounded-full shrink-0 bg-purple-500" />
          <span class="font-mono text-[12px] font-bold text-purple-700 dark:text-purple-300 truncate">models + errors</span>
          <span class="ml-auto text-[11px] opacity-60 shrink-0">被三层用 · 不进栈</span>
        </div>
      </div>
    </div>
  </div>
</template>
