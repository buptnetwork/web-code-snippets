<script setup lang="ts">
import evidence from '../public/images/ch01/evidence.json'
withDefaults(defineProps<{
  view?: 'noise' | 'compare' | 'stack' | 'joined' | 'sql'
  progressive?: boolean
}>(), { view: 'joined', progressive: false })
// 仅去掉时间与级别前缀以放大正文；原始记录完整保存在 evidence.json。
const clean = (text: string) => text.trim().split('\n').map(line => line.replace(/^\d{4}-\d\d-\d\d \S+ INFO /, ''))
const plainLines = clean(evidence.plain.log)
const noiseStart = Math.max(0, plainLines.findIndex(line => line.includes('sql:done')) - 4)
const noise = plainLines.slice(noiseStart, noiseStart + 12)
const filtered = clean(evidence.filtered)
const joined = clean(evidence.joined.log)
const app = joined.filter(line => line.includes('[stu-demo-01]') && (line.includes('-->') || line.includes('<--')))
const sqlStart = joined.findIndex(line => line.includes('sql:begin'))
const sqlEnd = joined.findIndex(line => line.includes('sql:done'))
const sql = joined.slice(sqlStart, sqlEnd + 1)
const rid = evidence.joined.rid
const segments = (line: string) => line.split(rid)
</script>

<template>
  <div class="trace-evidence" :class="view">
    <template v-if="view === 'noise' || view === 'compare'">
      <div class="evidence-columns" :class="{ single: view === 'noise' }">
        <section class="evidence-box">
          <h3>无关联标记 <small>真实并发日志 · 连续节选</small></h3>
          <pre><div v-for="(line, i) in (view === 'compare' ? noise.slice(0, 8) : noise)" :key="i">{{ line }}</div></pre>
        </section>
        <section v-if="view === 'compare'" v-click="progressive ? 1 : 0" class="evidence-box">
          <h3>同一 id 过滤 <small>另一次带标记实验</small></h3>
          <pre><div v-for="(line, i) in filtered" :key="i"><template v-for="(part, j) in segments(line)" :key="j"><mark v-if="j">{{ rid }}</mark>{{ part }}</template></div></pre>
          <p>从进入到离开，六条记录属于同一次请求，不靠相邻位置猜。</p>
        </section>
      </div>
      <div class="evidence-source">真实输出重排，非终端截图；10 个噪音请求＋1 个目标请求，人为延迟 80ms。左侧省略时间前缀，完整记录见素材文件。</div>
    </template>

    <template v-else-if="view === 'stack'">
      <div class="evidence-columns">
        <section class="evidence-box">
          <h3>实际断点栈 <small>栈顶在上 / debugpy DAP</small></h3>
          <div v-for="(frame, i) in evidence.joined.stack" :key="i" class="frame" :class="{ current: i === 0 }">
            <b>{{ frame.name }}</b><small>{{ frame.file }}:{{ frame.line }}</small>
          </div>
          <pre class="vars">rid = <mark>{{ evidence.joined.variables.rid }}</mark>
keyword = {{ evidence.joined.variables.keyword }}
page = {{ evidence.joined.variables.page }}</pre>
        </section>
        <section class="stack-explanation">
          <div v-click="progressive ? 1 : 0">
            <h3>对应链路中的“应用代码”</h3>
            <p><b>get_questions</b>：正在执行的端点。</p>
            <p><b>run</b>：AnyIO 工作线程入口。</p>
            <p><b>threading</b>：线程启动路径。</p>
          </div>
          <div v-click="progressive ? 2 : 0" class="boundary">同步端点在线程池中运行，不能在这个栈里硬找 uvicorn 和中间件。用 <b>rid</b> 把跨线程的事实接起来。</div>
        </section>
      </div>
      <div class="evidence-source">实际停点输出重排，不是 IDE 界面。Python {{ evidence.python }} / FastAPI {{ evidence.versions.fastapi }} / debugpy {{ evidence.versions.debugpy }}。</div>
    </template>

    <template v-else-if="view === 'sql'">
      <section class="evidence-box">
        <h3>查询前后与 SQL echo <small>真实单次请求节选</small></h3>
        <pre><div v-for="(line, i) in sql" :key="i"><template v-for="(part, j) in segments(line)" :key="j"><mark v-if="j">{{ rid }}</mark>{{ part }}</template></div></pre>
      </section>
      <div class="evidence-source">本次是 1 条业务 SELECT；BEGIN / ROLLBACK 是事务边界记录。generated in 是 SQL 编译时间，不是数据库执行耗时。</div>
    </template>

    <template v-else>
      <div class="evidence-columns four">
        <section class="evidence-box">
          <h3>① 客户端响应 <small>HTTPX 实收，非 DevTools 截图</small></h3>
          <pre>{{ evidence.joined.http_version }} {{ evidence.joined.status }}
content-type: {{ evidence.joined.headers['content-type'] }}
x-request-id: <mark>{{ rid }}</mark></pre>
        </section>
        <section v-click="progressive ? 1 : 0" class="evidence-box">
          <h3>② 应用日志 <small>进入 / 离开</small></h3>
          <pre><div v-for="(line, i) in app" :key="i"><template v-for="(part, j) in segments(line)" :key="j"><mark v-if="j">{{ rid }}</mark>{{ part }}</template></div></pre>
        </section>
        <section v-click="progressive ? 2 : 0" class="evidence-box">
          <h3>③ 断点状态 <small>DAP 实测，栈节选</small></h3>
          <pre>{{ evidence.joined.stack[0].name }}
← {{ evidence.joined.stack[1].name }} (AnyIO worker)
rid = <mark>{{ evidence.joined.variables.rid }}</mark></pre>
        </section>
        <section v-click="progressive ? 3 : 0" class="evidence-box">
          <h3>④ SQL 调用 <small>前后日志关联，已暂停并发</small></h3>
          <pre><mark>{{ rid }}</mark> sql:begin
SELECT * FROM questions …
<mark>{{ rid }}</mark> sql:done rows=6</pre>
        </section>
      </div>
      <div class="evidence-source">同一次请求实采；④省略 SQL 中段，完整语句见 SQL 页。耗时含调试暂停，不能用于性能比较。此页不是“四张 IDE / 终端截图”的替代交付。</div>
    </template>
  </div>
</template>

<style scoped>
.trace-evidence { color: #193b4b; }
.evidence-columns { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; align-items: start; }
.evidence-columns.single { grid-template-columns: 1fr; }
.evidence-box { background: #132f40; border-radius: 7px; padding: 14px 17px; color: #e1edf1; }
.evidence-box h3 { color: #f1f8fa !important; font-size: 16px !important; margin: 0 0 12px !important; font-weight: 650; }
.evidence-box h3 small { display: block; color: #c1d9e2; font-size: 13px; font-weight: 400; margin-top: 4px; }
.trace-evidence pre { font: 14px/1.55 'SFMono-Regular', Consolas, monospace; margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; color: #daecf0; }
.trace-evidence mark { background: #9cedd5; color: #103e3c; border-radius: 2px; padding: 0 2px; }
.evidence-box p { font-size: 15px; line-height: 1.6; color: #bed6df; margin: 16px 0 0; }
.evidence-source { font-size: 13px; line-height: 1.5; margin-top: 12px; color: #546b78; }
.compare pre { font-size: 15px; line-height: 1.5; }
.compare .evidence-box p { font-size: 16px; line-height: 1.55; margin: 12px 0 0; }
.compare .evidence-box:first-child pre { color: #afc4ce; }
.noise pre { font-size: 17px; line-height: 1.45; }
.noise .evidence-box { column-count: 2; column-gap: 30px; }
.noise .evidence-box h3 { column-span: all; }
.frame { display: flex; justify-content: space-between; padding: 10px 7px; border-bottom: 1px solid #34505f; font: 16px/1.5 monospace; }
.frame small { font-size: 13px; color: #a4c5d1; }
.frame.current { background: #1b514f; color: #b1f5df; }
.vars { margin-top: 18px !important; font-size: 16px !important; }
.stack-explanation p { font-size: 18px; margin: 14px 0; }
.boundary { border-left: 3px solid #14998d; background: #e6f4ee; padding: 12px 15px; font-size: 17px; line-height: 1.6; }
.sql pre { font-size: 16px; line-height: 1.8; }
.four { gap: 14px; }
.four .evidence-box { padding: 13px 15px; height: 100%; }
.stack-explanation b { color: #087b76; }
.four pre { font-size: 16px; line-height: 1.55; }
</style>
