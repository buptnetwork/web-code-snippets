<script setup lang="ts">
import { computed } from 'vue'

// 第一课的五框逻辑链，不表示当前线程调用栈或所有 Web 系统的部署结构。
const props = withDefaults(defineProps<{ active?: number; qid?: number; missing?: boolean }>(), {
  active: 0,
  qid: 3,
  missing: false,
})
const stages = computed(() => [
  { title: '浏览器', action: '发请求、显示响应', input: `GET /questions/${props.qid}` },
  { title: 'Uvicorn', action: '监听端口、接收 HTTP', input: '交给 ASGI 应用' },
  { title: 'FastAPI', action: '匹配路由、处理参数', input: `qid = ${props.qid}（int）` },
  { title: '端点函数', action: '按编号查找记录', input: '读取 QUESTIONS' },
  { title: '固定列表', action: '本课的数据来源', input: 'id：3、2、1' },
])
</script>

<template>
  <figure class="first-request-flow" aria-label="浏览器、Uvicorn、FastAPI、端点函数、固定列表的请求与响应双向链路">
    <div class="flow-direction">请求向右 <span>→</span></div>
    <div class="flow-nodes">
      <div v-for="(stage, index) in stages" :key="stage.title" class="flow-node" :class="{ selected: active === index + 1 }">
        <span class="flow-number">0{{ index + 1 }}</span>
        <strong>{{ stage.title }}</strong>
        <span class="flow-action">{{ stage.action }}</span>
        <span v-if="index < 4" class="flow-arrow" aria-hidden="true">→</span>
        <span v-if="stage.input" class="flow-input">{{ stage.input }}</span>
      </div>
    </div>
    <div class="flow-response">
      <span>显示 JSON</span><b>←</b><span>{{ missing ? 'HTTP 404' : 'HTTP 200' }}</span><b>←</b><span>{{ missing ? '错误 JSON' : '生成 JSON' }}</span><b>←</b><span>{{ missing ? 'HTTP 异常' : 'Python dict' }}</span><b>←</b><span>{{ missing ? '无匹配' : '记录' }}</span>
    </div>
    <figcaption v-if="missing">响应向左：端点抛出 HTTPException，框架生成 404 错误响应，经服务器送回。</figcaption>
    <figcaption v-else>响应向左：Python 返回值由框架处理，经服务器送回浏览器。</figcaption>
  </figure>
</template>

<style scoped>
.first-request-flow { margin: 26px 0 20px; color: #173344; }
.flow-direction { font-size: 16px; font-weight: 650; margin-bottom: 12px; color: #087b76; }
.flow-direction span { margin-left: 10px; }
.flow-nodes { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 24px; }
.flow-node { position: relative; padding: 14px 10px; min-height: 172px; background: #eff5f7; border: 1px solid #cfdee4; border-top: 3px solid #7898a5; border-radius: 8px; }
.flow-node.selected { background: #dff4ee; border-color: #0d8c80; }
.flow-number { display: block; color: #657f8b; font: 14px/1.4 monospace; margin-bottom: 8px; }
.flow-node strong { display: block; font-size: 20px; line-height: 1.4; color: #173344; }
.flow-action { display: block; font-size: 16px; line-height: 1.6; margin-top: 8px; }
.flow-input { display: block; font-size: 13px; line-height: 1.5; margin-top: 12px; color: #086f69; overflow-wrap: anywhere; }
.flow-arrow { position: absolute; right: -23px; top: 58px; font-size: 22px; color: #087b76; }
.flow-response { display: grid; grid-template-columns: 1fr 24px 1fr 24px 1fr 24px 1fr 24px 1fr; align-items: center; margin-top: 16px; padding: 12px 0; border-top: 1px solid #b9d5d4; border-bottom: 1px solid #b9d5d4; text-align: center; font-size: 15px; }
.flow-response b { color: #087b76; }
figcaption { font-size: 16px; line-height: 1.6; margin-top: 12px; color: #46616c; }
</style>
