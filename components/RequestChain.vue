<script setup lang="ts">
withDefaults(defineProps<{ active?: number; compact?: boolean }>(), { active: 0, compact: false })
const stages = [
  { title: '浏览器', sub: '构造请求 / 渲染', point: 1, observation: '报文' },
  { title: '解析与连接', sub: 'DNS / TCP / TLS', point: 0 },
  { title: '反向代理', sub: '第 16 次课填', point: 0 },
  { title: 'ASGI 服务器', sub: 'uvicorn', point: 0 },
  { title: '中间件链', sub: '进入 / 离开', point: 2, observation: '应用日志' },
  { title: '路由与参数', sub: '匹配 / 校验', point: 0 },
  { title: '应用代码', sub: '端点函数', point: 3, observation: '断点栈帧' },
  { title: '数据库', sub: 'SQL 调用处', point: 4, observation: 'SQL 日志' },
]
const numbers = ['', '①', '②', '③', '④']
</script>

<template>
  <div class="request-chain" :class="{ compact }" aria-label="请求八环节与四处观察点">
    <div class="chain-heading">请求方向 <span>→</span><small>逻辑链路，不是单线程调用栈</small></div>
    <div class="chain-stages">
      <div v-for="(stage, i) in stages" :key="stage.title" class="chain-stage"
        :class="{ proxy: i === 2, selected: active > 0 && active === stage.point, observed: stage.point > 0 }">
        <div class="chain-order">{{ String(i + 1).padStart(2, '0') }}</div>
        <strong>{{ stage.title }}</strong>
        <small>{{ stage.sub }}</small>
        <div v-if="stage.point" class="chain-point">{{ numbers[stage.point] }} {{ stage.observation }}</div>
        <span v-if="i < 7" class="chain-arrow">→</span>
      </div>
    </div>
    <div class="chain-return"><span>←</span> 响应回到客户端，再由前端处理与渲染</div>
    <div v-if="!compact" class="chain-caption">本地 HTTP 开发直连 uvicorn，不经过反向代理或 TLS；连接可能复用，数据库也不一定每次都访问。</div>
  </div>
</template>

<style scoped>
.request-chain { margin: 18px 0; color: #17394a; }
.chain-heading { display: flex; gap: 12px; align-items: center; font-size: 16px; font-weight: 650; margin-bottom: 12px; }
.chain-heading small { margin-left: auto; font-size: 14px; font-weight: 400; color: #526577; }
.chain-stages { display: grid; grid-template-columns: repeat(8, minmax(0, 1fr)); gap: 12px; }
.chain-stage { position: relative; min-height: 133px; padding: 10px 3px; text-align: center; background: #eef3f7; border-top: 3px solid #90a4b5; border-radius: 3px; }
.chain-order { font-family: monospace; font-size: 14px; color: #627d8b; margin-bottom: 10px; }
.request-chain .chain-stage strong { display: block; color: inherit; font-size: 15px; line-height: 1.5; white-space: nowrap; }
.chain-stage small { display: block; font-size: 13px; line-height: 1.6; margin-top: 6px; }
.chain-stage.observed { border-top-color: #0f8d86; }
.chain-stage.proxy { background: #f4f4f4; border-top-style: dashed; color: #6b7280; }
.chain-stage.selected { background: #cff4eb; outline: 2px solid #0f8d86; }
.chain-point { margin-top: 12px; font-size: 14px; color: #086d68; font-weight: 700; }
.chain-arrow { position: absolute; right: -13px; top: 47px; width: 13px; color: #526577; }
.chain-return { border-bottom: 2px solid #79aaa9; border-left: 2px solid #79aaa9; border-right: 2px solid #79aaa9; margin: 8px 40px 0; padding: 4px 0 7px; text-align: center; font-size: 14px; color: #176b70; }
.chain-return span { font-size: 19px; margin-right: 8px; }
.chain-caption { font-size: 15px; line-height: 1.55; margin-top: 16px; color: #526577; }
.compact { margin: 8px 0 18px; }
.compact .chain-heading, .compact .chain-order, .compact .chain-stage small, .compact .chain-return { display: none; }
.compact .chain-stage { min-height: 62px; padding: 8px 2px; }
.request-chain.compact .chain-stage strong { font-size: 13px; }
.compact .chain-point { font-size: 12px; margin-top: 5px; }
.compact .chain-arrow { top: 21px; }
</style>
