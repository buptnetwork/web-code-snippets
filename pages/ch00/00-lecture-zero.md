# 授课人与联系方式

<div grid="~ cols-[1.1fr_1fr] gap-8" class="mt-5 items-center">
<div>

<div class="text-xs tracking-widest opacity-45 mb-2">授课教师</div>

<div class="text-3xl font-bold mb-6">王尊亮</div>

<div class="space-y-3 text-sm">
  <div class="flex items-baseline gap-3">
    <span class="opacity-50 w-10 shrink-0">邮箱</span>
    <span class="font-mono">wangzl@bupt.edu.cn</span>
  </div>
  <div class="flex items-baseline gap-3">
    <span class="opacity-50 w-10 shrink-0">电话</span>
    <span class="font-mono">138-1092-4936</span>
  </div>
</div>

<div class="mt-7 p-4 rounded border border-teal-500/30 bg-teal-500/5 text-sm leading-relaxed">

课程通知、作业发布、实验说明均通过 **QQ 群** 发布，请课后完成入群。

</div>

</div>
<div class="flex flex-col items-center">

<img src="/images/ch00/class-qr-code.png" alt="课程 QQ 群二维码 · 416478017" class="h-80 rounded shadow-lg" />

<div class="mt-4 flex items-baseline gap-2">
  <span class="opacity-50 text-sm">课程 QQ 群</span>
  <span class="font-mono font-bold text-lg tracking-wide">416478017</span>
</div>

</div>
</div>

<!--
开场不寒暄，直接进两则事实。这一节的目的不是讲新闻，是把"AI 在代码生成上已经领先人类"这个前提立住。
-->

---

# 事件一 · OpenAI 的 Harness Engineering 实验

<div class="text-xs opacity-55 -mt-2 mb-4">
《Harness Engineering: Leveraging Codex in an Agent-First World》· OpenAI · 2026 年 2 月
</div>

<div grid="~ cols-[1.05fr_1fr] gap-8">
<div>

| 维度 | 事实 |
|---|---|
| 团队规模 | 3 人起步，后扩至 7 人 |
| 硬性约束 | **全程禁止人工手写代码** |
| 周期 | 5 个月 |
| 产出 | **100 万行以上**代码，1,500 个 PR |
| 效率变化 | 约 **10 倍** |

</div>
<div class="flex items-center justify-center">

<img src="/images/ch00/news-openai-harness-engineering.png" class="rounded shadow-lg max-h-80" />

</div>
</div>

<div class="absolute bottom-10 left-14 right-14 flex items-center gap-3 text-xs">
  <div class="flex-1 h-px bg-gray-400/30" />
  <div class="px-3 py-1 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold whitespace-nowrap">2026.02 · Harness Engineering</div>
  <div class="w-20 h-px bg-gray-400/30" />
  <div class="px-3 py-1 rounded-full border border-gray-400/30 opacity-35 whitespace-nowrap">2026.09 · ?</div>
  <div class="flex-1 h-px bg-gray-400/30" />
</div>

<!--
今年二月，OpenAI 发了一篇工程博客。一个团队，最开始三个人，后来扩到七个人，给自己定了一条硬规矩：**一行代码都不许人手写**，全部交给 AI Agent。

五个月，一百万行代码，合并了一千五百个 PR，他们自己估算效率提升大概十倍。

我先不评价这件事好不好，我们只把它当一个事实记下来。
-->

---

# 事件二 · GPT-6 Astra 发布

<div class="text-xs opacity-55 -mt-2 mb-4">
OpenAI · 2026 年 9 月 3 日
</div>

<div grid="~ cols-[1fr_1.05fr] gap-8">
<div class="pt-2">

<div class="p-4 rounded border border-amber-500/30 bg-amber-500/5">

总裁 **Greg Brockman** 在发布前媒体简报会上：

<div class="pt-2 text-xl font-bold">
「我个人认为，我们已经到了 AGI」
</div>

</div>

<div v-click class="mt-4 p-4 rounded border border-amber-500/30 bg-amber-500/5">

发布会结语：

<div class="pt-2 text-xl font-bold">
「Welcome to the AGI era.」
</div>

</div>

</div>
<div class="flex items-center justify-center">

<img src="/images/ch00/news-gpt6-agi-era.png" class="rounded shadow-lg max-h-64" />

</div>
</div>

<div class="absolute bottom-10 left-14 right-14 flex items-center gap-3 text-xs">
  <div class="flex-1 h-px bg-gray-400/30" />
  <div class="px-3 py-1 rounded-full border border-gray-400/30 opacity-35 whitespace-nowrap">2026.02 · Harness Engineering</div>
  <div class="w-20 h-px bg-gray-400/30" />
  <div class="px-3 py-1 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold whitespace-nowrap">2026.09 · GPT-6 Astra</div>
  <div class="flex-1 h-px bg-gray-400/30" />
</div>

<!--
七个月之后，九月三号，OpenAI 发布新一代模型 Astra。他们的总裁 Greg Brockman 在媒体会上说了一句话，说他个人认为我们已经到了 AGI，

[click] 然后用一句 Welcome to the AGI era 结束了整场发布。

这句话争议很大，我不打算在这里下判断。但你们要注意，说这话的人，是掌握全部内部数据的人。
-->

---

# 我自己的 AI Coding 经历

<div class="text-xs opacity-55 -mt-2 mb-4">
2023 年底 → 2026 下半年
</div>

<div grid="~ cols-4 gap-4 items-start" class="mt-14">
<div class="mt-24 p-5 rounded border border-gray-400/25 bg-gray-400/5">
<div class="text-xs font-bold tracking-wide opacity-45">2023 年底</div>
<div class="mt-2 text-lg font-bold opacity-70">插件辅助</div>
<div class="mt-2 text-sm leading-relaxed opacity-60">通义灵码等 IDE 插件；AI 做片段级代码推荐与补全</div>
</div>
<div class="mt-16 p-5 rounded border border-gray-400/25 bg-gray-400/5">
<div class="text-xs font-bold tracking-wide opacity-45">2025 下半年</div>
<div class="mt-2 text-lg font-bold opacity-70">AI IDE</div>
<div class="mt-2 text-sm leading-relaxed opacity-60">Cursor、Qoder：<br>AI 做多文件级编辑与修改</div>
</div>
<div class="mt-8 p-5 rounded border border-gray-400/25 bg-gray-400/5">
<div class="text-xs font-bold tracking-wide opacity-45">2026 上半年</div>
<div class="mt-2 text-lg font-bold opacity-70">SPEC 驱动</div>
<div class="mt-2 text-sm leading-relaxed opacity-60">编制 SPEC，AI 执行，<br>人机协同 review</div>
</div>
<div class="p-5 rounded border border-teal-500/40 bg-teal-500/10">
<div class="flex items-center justify-between gap-2">
<div class="text-xs font-bold tracking-wide text-teal-700 dark:text-teal-300">2026 下半年</div>
<div class="text-[10px] px-1.5 py-0.5 rounded bg-teal-500/15 text-teal-700 dark:text-teal-300">现在</div>
</div>
<div class="mt-2 text-lg font-bold">设计主导</div>
<div class="mt-2 text-sm leading-relaxed opacity-80">人基本不再 review 代码，重心转向确认设计方案</div>
</div>
</div>

<div class="absolute bottom-10 left-14 right-14 text-center text-sm">
<span class="opacity-55">这几年，我的重心逐级上移：</span>从<b>「写代码」</b>，到<b class="text-teal-700 dark:text-teal-300">「定方案」</b>。
</div>

---

# SPEC 样例 · 一份可执行的规格

<div class="-mt-2 mb-4 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">SPEC 驱动</span>
<span class="opacity-55">一次真实会话：澄清问题 → 实施顺序 → 验证方案</span>
</div>

<img src="/images/ch00/spec-driven-coding-sample.png" class="block mx-auto max-h-96 rounded shadow-lg" />

---

# 设计文档样例 · 后端

<div class="-mt-2 mb-4 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">设计主导</span>
<span class="opacity-55">编号、关联文档、定位对比——先写成可评审的文档，再动手</span>
</div>

<img src="/images/ch00/backend-design-document-sample.png" class="block mx-auto max-h-96 rounded shadow-lg" />

---

# 设计文档样例 · 前端

<div class="-mt-2 mb-4 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">设计主导</span>
<span class="opacity-55">页面定位、布局分区、组件与接口字段，逐项定稿</span>
</div>

<img src="/images/ch00/frontend-design-document-sample-1.png" class="block mx-auto max-h-96 rounded shadow-lg" />

---

# 从文档到实现

<div class="-mt-2 mb-4 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">设计主导</span>
<span class="opacity-55">把前端设计文档交给 AI 执行，界面与方案逐条对应</span>
</div>

<img src="/images/ch00/frontend-design-document-sample-2.png" class="block mx-auto max-h-96 rounded shadow-lg" />

---

# 代码的<b class="text-teal-700 dark:text-teal-300">生成方式与生命周期</b>正在重塑

<div class="text-xs opacity-55 -mt-2 mb-6">
从人工编写到 AI 生成，从静态维护到动态演化——软件开发范式迎来历史性转折
</div>

<div grid="~ cols-3 gap-4">

<div class="p-6 rounded border border-gray-400/25 bg-gray-400/5">
<div class="text-xs tracking-widest opacity-50">核心覆盖</div>
<div class="mt-2 text-4xl font-bold text-teal-700 dark:text-teal-300">100%</div>
<div class="mt-2 text-sm opacity-60">一切皆代码</div>
</div>

<div class="p-6 rounded border border-gray-400/25 bg-gray-400/5">
<div class="text-xs tracking-widest opacity-50">生成变革</div>
<div class="mt-2 text-4xl font-bold text-teal-700 dark:text-teal-300">AI First</div>
<div class="mt-2 text-sm opacity-60">智能驱动创作</div>
</div>

<div class="p-6 rounded border border-gray-400/25 bg-gray-400/5">
<div class="text-xs tracking-widest opacity-50">生命周期</div>
<div class="mt-2 text-4xl font-bold text-teal-700 dark:text-teal-300">Dynamic</div>
<div class="mt-2 text-sm opacity-60">持续自我演化</div>
</div>

</div>

<div grid="~ cols-2 gap-4" class="mt-5">

<div class="py-6 px-5 rounded border border-gray-400/25 bg-gray-400/5">
<div class="text-xl font-bold mb-4">代码生成方式的革命</div>
<div class="space-y-3">
<div class="flex items-center gap-2 text-sm">
<span class="px-1.5 py-1 rounded text-[10px] font-bold bg-teal-500/15 text-teal-700 dark:text-teal-300 shrink-0">过去</span>
<span class="opacity-75">开发者逐行编写，依赖经验与记忆</span>
</div>
<div class="flex items-center gap-2 text-sm">
<span class="px-1.5 py-1 rounded text-[10px] font-bold bg-teal-500/15 text-teal-700 dark:text-teal-300 shrink-0">现在</span>
<span class="opacity-75">AI 理解意图，自动生成高质量代码</span>
</div>
<div class="flex items-center gap-2 text-sm">
<span class="px-1.5 py-1 rounded text-[10px] font-bold bg-teal-500/15 text-teal-700 dark:text-teal-300 shrink-0">未来</span>
<span class="opacity-75" v-mark.underline.orange="3">自然语言即代码，想法瞬间实现</span>
</div>
</div>
</div>

<div class="py-6 px-5 rounded border border-gray-400/25 bg-gray-400/5">
<div class="text-xl font-bold mb-4">代码生命周期的重构</div>
<div class="space-y-3">
<div class="flex items-center gap-2 text-sm">
<span class="px-1.5 py-1 rounded text-[10px] font-bold bg-teal-500/15 text-teal-700 dark:text-teal-300 shrink-0">过去</span>
<span class="opacity-75">编写 → 测试 → 部署 → 维护（线性流程）</span>
</div>
<div class="flex items-center gap-2 text-sm">
<span class="px-1.5 py-1 rounded text-[10px] font-bold bg-teal-500/15 text-teal-700 dark:text-teal-300 shrink-0">现在</span>
<span class="opacity-75">AI 生成 → 自动测试 → 智能修复 → 持续优化</span>
</div>
<div class="flex items-center gap-2 text-sm">
<span class="px-1.5 py-1 rounded text-[10px] font-bold bg-teal-500/15 text-teal-700 dark:text-teal-300 shrink-0">未来</span>
<span class="opacity-75">代码自主进化，系统自我完善</span>
</div>
</div>
</div>

</div>

---

# 数据结构课程设计中的 Web 样例 · 找搭子

<div class="-mt-2 mb-4 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">前序课程</span>
<span class="opacity-55">个性化旅游系统——真实路网 + 哈希匹配 + TopK，你们已经做过这样的 Web 应用</span>
</div>

<img src="/images/ch00/course-work-example-a.png" class="block mx-auto max-h-96 rounded shadow-lg" />

<!--
讲完结论，先看几份东西——数据结构课程设计里的作业。注意，这不是别人的故事，就是你们已经做过的事。

这一份是个性化旅游系统。右侧「算法说明」暴露了它的内核：HashTable 加权匹配 + 自制 TopK，在 17142 条真实路网上为每位用户挑出 12 个候选搭子。地图是真的，路网是真的，算法是同学自己写的。

它由什么组成？一个前端页面、一张交互地图、若干表单、一组请求、一个算法服务。合起来就是 Web 开发——你们已经做过了，只是还没人把它系统地讲给你们听。
-->


---

# 数据结构课程设计中的 Web 样例 · 旅游日记

<div class="-mt-2 mb-4 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">前序课程</span>
<span class="opacity-55">TravelSys——导航、表单、发布、检索，多模块协作的 Web 应用</span>
</div>

<img src="/images/ch00/course-work-example-b.png" class="block mx-auto max-h-96 rounded shadow-lg" />

<!--
再看这份：TravelSys 的旅游日记模块。左侧导航把七八个模块串在一起；中间日记广场 126 篇按热度排序，还能按标题、按目的地检索——按标题查找用的就是哈希表。

导航、表单、列表、发布、检索——一个多模块协作的完整应用，全是 Web 开发的基本功。
-->

---

# 数据结构课程设计中的 Web 样例 · 路线探索

<div class="-mt-2 mb-4 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">前序课程</span>
<span class="opacity-55">TourSim——多途经点 + 最短距离策略，图算法变成看得见的路线</span>
</div>

<img src="/images/ch00/course-work-example-c.png" class="block mx-auto max-h-96 rounded shadow-lg" />

<!--
最后这份：TourSim 路线探索。多途经点规划，最短距离策略——这是图算法；从公共卫生学院影像中心到校区医务室，4653 米、四段路程拆得清清楚楚。

图算法最后变成了什么？变成地图上一条看得见的路线。算法是内核，界面是外壳——这两样合起来，就是 Web 应用。
-->

---

# 为什么需要学习这门课程

<div class="-mt-2 mb-4 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">开课导引</span>
</div>

<div class="mt-6 space-y-4">

<div class="flex items-start gap-4 p-4 rounded-lg border border-gray-400/25 bg-gray-400/5">
<span class="w-7 h-7 rounded-full bg-teal-500/25 flex items-center justify-center font-bold shrink-0">1</span>
<div class="text-base leading-relaxed">没学过Web开发也已经能让 AI 生成一个能跑的 Web 项目</div>
</div>

<div class="flex items-start gap-4 p-4 rounded-lg border border-gray-400/25 bg-gray-400/5">
<span class="w-7 h-7 rounded-full bg-teal-500/25 flex items-center justify-center font-bold shrink-0">2</span>
<div class="text-base leading-relaxed">但使用 AI 实现从 0-1 非常简单，但从 1~100，可能会觉得指挥 AI 越来越困难。</div>
</div>

<div class="flex items-start gap-4 p-4 rounded-lg border border-gray-400/25 bg-gray-400/5">
<span class="w-7 h-7 rounded-full bg-teal-500/25 flex items-center justify-center font-bold shrink-0">3</span>
<div class="text-base leading-relaxed">这门课我们教<b>半衰期长的 Web 基本原理 + 当前主流框架（FastAPI / React）的正确用法</b>，目标是能<b class="text-teal-700 dark:text-teal-300">清晰、可控地驾驭 AI 开发一般复杂度的单体 Web 应用</b>。</div>
</div>

</div>

<div v-click class="mt-7 p-5 rounded-lg border-2 border-teal-500/40 bg-teal-500/5 text-center">

<div class="text-xl font-bold leading-relaxed">生成不再是瓶颈，<span class="text-teal-700 dark:text-teal-300">驾驭成了瓶颈</span>。</div>
</div>

<!--
刚才那三份作业都是你们自己做的——找搭子、旅游日记、路线探索，货真价实的 Web 应用。那为什么还要专门开一门课？这一页我先说三句实话，不评价任何人。

第一句：没学过 Web 开发，你们也已经能让 AI 生成一个能跑的 Web 项目——这个起点是真的，我不打算贬低它。

第二句：使用 AI 实现从 0-1 非常简单；但从 1~100，可能会觉得指挥 AI 越来越困难。"能跑"和"能交付"之间，还隔着一批你现在还没有词汇去描述的东西——这句话现在听起来抽象，等会儿你们会亲眼看到。

第三句：这门课我们教什么？第一，教半衰期长的 Web 基本原理——十年后还成立的那些东西：协议、分层、数据、状态。第二，教当前主流框架 FastAPI 和 React 的正确用法。目标只有一个：让你们能清晰、可控地驾驭 AI，去开发一个一般复杂度的单体 Web 应用。

[click] 三句话压缩成一句板书：生成不再是瓶颈，驾驭成了瓶颈。这门课站在瓶颈的另一侧。接下来五十分钟，我要让你们亲眼看到这个瓶颈在哪儿。
-->

---

# 一个你大概已经经历过的场景

<div class="text-xs opacity-55 -mt-2 mb-5">
你向 AI 描述了一个需求，它给了你一个能跑的项目。你部署给同学用——然后遇到下面某一种：
</div>

<div grid="~ cols-3 gap-4" class="text-sm">

<div class="p-4 rounded-lg border border-gray-400/25 bg-gray-400/5 leading-relaxed">
页面上「提交」点两次，<b>帖子发了两条</b>
</div>

<div class="p-4 rounded-lg border border-gray-400/25 bg-gray-400/5 leading-relaxed">
你改了代码，自己看是新的，<b>别人打开还是旧的</b>
</div>

<div class="p-4 rounded-lg border border-gray-400/25 bg-gray-400/5 leading-relaxed">
列表页数据一多就卡，<b>但你不知道慢在哪一层</b>
</div>

<div class="p-4 rounded-lg border border-gray-400/25 bg-gray-400/5 leading-relaxed">
有人把 URL 里的 <code class="text-xs">id</code> 改成别人的，<b>就看到 / 改掉了别人的数据</b>
</div>

<div class="p-4 rounded-lg border border-gray-400/25 bg-gray-400/5 leading-relaxed">
报错只有一句 <code class="text-xs">Internal Server Error</code>，<b>你不知道去哪里看</b>
</div>

<div class="p-4 rounded-lg border border-gray-400/25 bg-gray-400/5 leading-relaxed">
你让 AI「修一下这个 bug」，它改了三个文件，<b>其中两个把别的功能弄坏了</b>
</div>

</div>

<div v-click class="mt-5 p-4 rounded-lg bg-amber-500/10 border-l-4 border-amber-500 text-sm leading-relaxed">
这些问题的共同点是：<b>它们都不是「生成代码」能力不足造成的</b>。AI 生成的代码语法正确、结构像样、甚至比你手写得漂亮。问题出在——<b>没有人向它提出这些方面的要求，也没有人有能力检查它是否满足</b>。
</div>

<!--
这一段我说的每一件事，你们要么自己经历过，要么见同学经历过。我一件一件念，你们对号入座。

（念六条）提交点两次，帖子发两条；改了代码，别人看到旧页面；列表页一多就卡，不知道慢在哪一层；URL 里改个 id 就看到别人的数据；报错只有一句 Internal Server Error；让 AI 修 bug，它把别的地方改坏了。

[click] 这六个问题有一个共同点：它们全都不是"AI 不会写代码"造成的。刚才那三段代码你们也看到了，语法正确、结构像样、甚至比你手写得好看。问题出在——没有人向它提过这些方面的要求，也没有人有能力检查它做没做到。

接下来这个环节，我给你们一个机会，亲眼看一看这句话是什么意思。
-->

---

# 案例 A · 5 分钟找错

<div class="-mt-2 mb-3 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-rose-500/15 text-rose-700 dark:text-rose-300 font-bold">AI 生成 · 能跑 · 无语法错误</span>
<span class="opacity-55">独立完成：找出你认为有问题的地方 + 为什么。</span>
</div>

<style>
h1 {
  font-size: 26px !important;
  margin-bottom: 8px !important;
}
pre {
  font-size: 12px !important;
  line-height: 1.2 !important;
}
pre code,
pre span {
  line-height: 1.2 !important;
}
</style>

```python {lines:true}
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Post

app = FastAPI()

OPENAI_API_KEY = "sk-proj-4f9c2a17bd3e8a55c1"
DB_PASSWORD = "postgres123"

@app.post("/getUserPosts")
def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    result = []
    for post in user.posts:
        author = db.query(User).filter(User.id == post.author_id).first()
        result.append({"id": post.id, "title": post.title,
                       "content": post.content, "author": author})
    return {"success": True, "data": result}

@app.post("/deletePost")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    db.delete(post)
    db.commit()
    return {"success": True}
```

<!--
这是一段 AI 生成的代码，一个问答社区的两个接口：取帖子和删帖子。我先把话说死——它没有语法错误，能跑。

现在轮到你们：找出你认为有问题的地方，每一条写出"为什么"。给你 5 分钟，独立完成，不要问同学，也不要问 AI——问 AI 它就直接改了，你什么都学不到。

（留时间，走动）

时间到。下面公布答案，对着你的清单划勾。
-->

---

# 案例 A · 答案卡

<div class="-mt-2 mb-3 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">公布答案</span>
<span class="opacity-55">九条，对着你的清单划勾——最要命的是第 1、3、7 条</span>
</div>

<div class="mt-1 text-[13px]">

<div class="flex gap-4 pb-1.5 mb-1 border-b border-gray-400/30 text-xs tracking-wide opacity-55">
<div class="w-6 shrink-0">#</div>
<div class="w-[300px] shrink-0">缺陷</div>
<div class="flex-1">后果</div>
</div>

<div class="flex gap-4 py-1.5 border-b border-gray-400/12 items-baseline">
<div class="w-6 shrink-0 font-mono text-rose-600 dark:text-rose-400 font-bold">1</div>
<div class="w-[300px] shrink-0 font-bold text-rose-600 dark:text-rose-400">密钥硬编码在源码</div>
<div class="flex-1 opacity-85">一旦推到仓库即泄漏，且无法分环境</div>
</div>

<div class="flex gap-4 py-1.5 border-b border-gray-400/12 items-baseline">
<div class="w-6 shrink-0 font-mono opacity-45">2</div>
<div class="w-[300px] shrink-0 font-bold">读操作用 POST，URI 用动词</div>
<div class="flex-1 opacity-85">不可缓存、不可分享链接、语义错误</div>
</div>

<div class="flex gap-4 py-1.5 border-b border-gray-400/12 items-baseline">
<div class="w-6 shrink-0 font-mono text-rose-600 dark:text-rose-400 font-bold">3</div>
<div class="w-[300px] shrink-0 font-bold text-rose-600 dark:text-rose-400">返回整个 author 对象</div>
<div class="flex-1 opacity-85"><b>密码哈希、邮箱随响应泄漏</b></div>
</div>

<div class="flex gap-4 py-1.5 border-b border-gray-400/12 items-baseline">
<div class="w-6 shrink-0 font-mono opacity-45">4</div>
<div class="w-[300px] shrink-0 font-bold">无 response_model，返回裸 dict</div>
<div class="flex-1 opacity-85">契约不可知，前端无法生成类型，改坏无感</div>
</div>

<div class="flex gap-4 py-1.5 border-b border-gray-400/12 items-baseline">
<div class="w-6 shrink-0 font-mono opacity-45">5</div>
<div class="w-[300px] shrink-0 font-bold">循环内查询（N+1）</div>
<div class="flex-1 opacity-85">100 条帖子发 101 条 SQL，列表页越用越慢</div>
</div>

<div class="flex gap-4 py-1.5 border-b border-gray-400/12 items-baseline">
<div class="w-6 shrink-0 font-mono opacity-45">6</div>
<div class="w-[300px] shrink-0 font-bold">user 可能为 None 未判断</div>
<div class="flex-1 opacity-85">500 崩栈，且异常直接暴露给用户</div>
</div>

<div class="flex gap-4 py-1.5 border-b border-gray-400/12 items-baseline">
<div class="w-6 shrink-0 font-mono text-rose-600 dark:text-rose-400 font-bold">7</div>
<div class="w-[300px] shrink-0 font-bold text-rose-600 dark:text-rose-400">两个接口都没有鉴权与归属校验</div>
<div class="flex-1 opacity-85"><b>任何人传 post_id 就能删别人的帖（IDOR）</b></div>
</div>

<div class="flex gap-4 py-1.5 border-b border-gray-400/12 items-baseline">
<div class="w-6 shrink-0 font-mono opacity-45">8</div>
<div class="w-[300px] shrink-0 font-bold">错误也返回 200 + success:false</div>
<div class="flex-1 opacity-85">前端、日志、监控、重试全部失效</div>
</div>

<div class="flex gap-4 py-1.5 border-b border-gray-400/12 items-baseline">
<div class="w-6 shrink-0 font-mono opacity-45">9</div>
<div class="w-[300px] shrink-0 font-bold">删除无幂等考虑、无软删除、无审计</div>
<div class="flex-1 opacity-85">重试与误操作不可挽回、无法追责</div>
</div>

</div>

<!--
（公布）九条。你们对照一下自己找到几条。

第 1 条，密钥直接写死在源码里——推到仓库那天就泄漏了，而且没法分环境。
第 2 条，读操作用了 POST，接口名还是个动词——缓存、分享链接、语义全都错了。
第 3 条，返回整个 author 对象——密码哈希、邮箱跟着响应发给了前端。这条最隐蔽。
第 5 条，循环里查数据库——100 条帖子发 101 条 SQL，列表越用越慢。
第 6 条，user 可能是 None 没判断——直接 500。
第 7 条，两个接口都没有鉴权、没有归属校验——任何人传一个 post_id，就能删别人的帖子。

九条里头，最要命的是 1、3、7。我们统计一下全班平均找到几条。（统计）

这九条是怎么来的？它们有没有共同点？下一页说。
-->

---

# 案例 B · 同一个需求，两个提示词

<div class="-mt-2 mb-4 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">现场演示</span>
<span class="opacity-55">同一个模型，同一个需求，跑两次——差距不在模型，在提示词</span>
</div>

<div grid="~ cols-[0.72fr_1.28fr] gap-5" class="mt-2">

<div>
<div class="text-xs tracking-widest opacity-50 mb-2">提示词 1 · 典型写法</div>
<div class="p-4 rounded-lg border border-gray-400/25 bg-gray-400/5 text-sm leading-relaxed">
「帮我写一个问答社区的发帖接口，用 FastAPI。」
</div>
<div class="mt-3 p-3 rounded-lg bg-gray-500/8 text-xs leading-relaxed opacity-75">
产出的代码你们刚见过：能跑。但分层、契约、错误码、授权、边界——全部交给默认。
</div>
</div>

<div v-click>
<div class="text-xs tracking-widest opacity-50 mb-2">提示词 2 · 本课程结业时应该能写出</div>
<div class="p-4 rounded-lg border-2 border-teal-500/40 bg-teal-500/5 text-xs leading-relaxed">
用 FastAPI 实现「发布提问」接口，遵守以下约束：
<div class="mt-1.5 space-y-1">
<div><b class="text-teal-700 dark:text-teal-300">1 分层</b>　路由只做参数绑定与响应，业务逻辑放 <code>services/</code>，数据访问放 <code>repositories/</code>；禁止在路由中直接使用 Session</div>
<div><b class="text-teal-700 dark:text-teal-300">2 契约</b>　定义 <code>QuestionCreate</code> / <code>QuestionOut</code> 两个 Pydantic 模型，端点声明 <code>response_model</code>；输出模型不得包含作者的邮箱与密码字段</div>
<div><b class="text-teal-700 dark:text-teal-300">3 错误</b>　校验失败 422，未登录 401，无权限 403，标题重复 409；错误响应统一为 <code>{code, message, request_id}</code></div>
<div><b class="text-teal-700 dark:text-teal-300">4 授权</b>　必须通过 <code>get_current_user</code> 依赖取得当前用户，作者取自会话而非请求体</div>
<div><b class="text-teal-700 dark:text-teal-300">5 数据</b>　标题非空且 ≤ 200 字符，标签数 ≤ 5；数据库层需有相应约束</div>
<div><b class="text-teal-700 dark:text-teal-300">6 事务</b>　一次请求一个事务；不得在循环内查询数据库</div>
<div><b class="text-teal-700 dark:text-teal-300">7 依赖</b>　不引入新的第三方依赖</div>
</div>
<div class="mt-2 pt-2 border-t border-teal-500/20"><b class="text-teal-700 dark:text-teal-300">验收标准</b>　附 3 条 pytest 用例，分别覆盖成功、未登录、标题超长；<code>tsc</code> / <code>ruff</code> 无警告</div>
</div>
</div>

</div>

<!--
第二个案例，我做一个对比。同一个模型、同一个需求，用两个不同的提示词跑两次。

第一个提示词是这样的——"帮我写一个问答社区的发帖接口，用 FastAPI。"一句话。你们平时是不是都这么写？它出来的产物，就是你们刚才找错的那种代码：能跑，语法也对，但分层、契约、错误码、授权、边界，全部交给模型默认。

[click] 第二个提示词，是本课程结业时你们应该能写出来的水平。你们看：分层怎么分、契约怎么定、错误码哪个是哪个、授权从哪里拿、数据约束写在哪、事务边界、验收标准——七条约束加一条验收标准。

这两个提示词，等会儿我现场跑给你们看输出对比。
-->

---

# AI 时代 Web开发所需的能力结构发生了变化

<div class="-mt-2 mb-2 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">能力结构</span>
</div>

<div class="mt-3 text-[13px]">

<div class="flex gap-3 pb-1.5 mb-0.5 border-b border-gray-400/30 text-xs tracking-wide opacity-55">
<div class="w-28 shrink-0">能力</div>
<div class="flex-1">它要回答的问题</div>
<div class="flex-1">AI 单独做不好的原因</div>
<div class="flex-1">本课程中的训练与考核</div>
</div>

<div v-click="1" class="flex gap-3 py-2 border-b border-gray-400/12 items-start">
<div class="w-28 shrink-0 font-bold text-teal-700 dark:text-teal-300">需求规格化</div>
<div class="flex-1 opacity-90">这个功能「做完了」的标准是什么？边界情况怎么算？</div>
<div class="flex-1 opacity-80">你不说，它就按最常见路径猜</div>
<div class="flex-1 opacity-65">每次作业先写规格再生成</div>
</div>

<div v-click="2" class="flex gap-3 py-2 border-b border-gray-400/12 items-start">
<div class="w-28 shrink-0 font-bold text-teal-700 dark:text-teal-300">约束表达</div>
<div class="flex-1 opacity-90">分层、错误契约、事务边界、授权要求怎么写成它能执行的话？</div>
<div class="flex-1 opacity-80">约束来自你的项目语境，不在它的训练分布里</div>
<div class="flex-1 opacity-65">每课末的「提示词约束骨架」；仓库级 AI 规约文件</div>
</div>

<div v-click="3" class="flex gap-3 py-2 border-b border-gray-400/12 items-start">
<div class="w-28 shrink-0 font-bold text-teal-700 dark:text-teal-300">验收判据</div>
<div class="flex-1 opacity-90">怎么判断它交的东西合格？靠肉眼还是靠机器？</div>
<div class="flex-1 opacity-80">它不会主动为自己设关卡</div>
<div class="flex-1 opacity-65">每课「评审清单」</div>
</div>

<div v-click="4" class="flex gap-3 py-2 border-b border-gray-400/12 items-start">
<div class="w-28 shrink-0 font-bold text-teal-700 dark:text-teal-300">缺陷定位</div>
<div class="flex-1 opacity-90">出问题了，在链路的哪一层？怎么最快缩小范围？</div>
<div class="flex-1 opacity-80">它看不到你的运行时、日志和数据</div>
<div class="flex-1 opacity-65">请求全链路追踪；故障定位四步法；植入 bug 实验</div>
</div>

<div v-click="5" class="flex gap-3 py-2 border-b border-gray-400/12 items-start">
<div class="w-28 shrink-0 font-bold text-teal-700 dark:text-teal-300">方案取舍</div>
<div class="flex-1 opacity-90">Session 还是 JWT？SSR 还是 SPA？加不加索引？</div>
<div class="flex-1 opacity-80">取舍依赖你的约束条件与代价承受度</div>
<div class="flex-1 opacity-65">每个技术决策写 ADR；口试要求辩护</div>
</div>

</div>

<!--
[click] 第一项，需求规格化。这个功能"做完了"的标准是什么？边界情况怎么算？你不说，它就按最常见路径猜。所以每次作业都要先写规格，再让 AI 生成；第 9 次课专门讲"规格先行"。

[click] 第二项，约束表达。分层、错误契约、事务边界、授权要求——这些怎么写成 AI 能执行的话？注意，这些约束来自你的项目语境，不在它的训练分布里。每课末我们沉淀一个"提示词约束骨架"，学期末形成仓库级的 AI 规约文件。

[click] 第三项，验收判据。它交的东西合不合格，靠肉眼还是靠机器？它不会主动为自己设关卡。每课有评审清单；第 9 次课把 CI 四道门禁架起来，让不合格的产出根本进不来。

[click] 第四项，缺陷定位。出了问题，在链路的哪一层？怎么最快缩小范围？AI 看不到你的运行时、日志和数据，这一层只能靠你。我们会练请求全链路追踪、故障定位四步法，做植入 bug 的实验。

[click] 第五项，方案取舍。Session 还是 JWT？SSR 还是 SPA？加不加索引？取舍依赖你的约束条件和代价承受度。每个技术决策写一条 ADR，口试的时候你要为自己的选择辩护。

这五项不是背出来的——期末考试会给你真实的代码和场景，看你当场能不能做。
-->

---

# 学习关注点的六个转变

<div class="-mt-2 mb-3 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">怎么学</span>
<span class="opacity-55">这门课与去年的「Web 开发技术基础」课程，内容重叠不到一半</span>
</div>

<div class="mt-2 text-[13px]">

<div class="flex gap-3 py-2 border-b border-gray-400/12 items-baseline">
<div class="w-60 shrink-0 opacity-55">记住框架 API 怎么写</div>
<div class="shrink-0 text-teal-600 dark:text-teal-400 font-bold px-1">→</div>
<div class="flex-1">建立<b class="text-teal-700 dark:text-teal-300">心智模型</b>：一个请求经过哪些环节，每个环节谁负责、失败什么样、在哪观察</div>
</div>

<div class="flex gap-3 py-2 border-b border-gray-400/12 items-baseline">
<div class="w-60 shrink-0 opacity-55">追求「能跑」</div>
<div class="shrink-0 text-teal-600 dark:text-teal-400 font-bold px-1">→</div>
<div class="flex-1">追求<b class="text-teal-700 dark:text-teal-300">可解释、可验收、可回滚</b>——你要能说出每一行为什么这样写</div>
</div>

<div class="flex gap-3 py-2 border-b border-gray-400/12 items-baseline">
<div class="w-60 shrink-0 opacity-55">从零手写代码</div>
<div class="shrink-0 text-teal-600 dark:text-teal-400 font-bold px-1">→</div>
<div class="flex-1"><b class="text-teal-700 dark:text-teal-300">读、改、诊断、决策</b>：课堂上大量时间用来读别人（包括 AI）写的代码</div>
</div>

<div class="flex gap-3 py-2 border-b border-gray-400/12 items-baseline">
<div class="w-60 shrink-0 opacity-55">遇到报错就换写法 / 问 AI 重写</div>
<div class="shrink-0 text-teal-600 dark:text-teal-400 font-bold px-1">→</div>
<div class="flex-1">用<b class="text-teal-700 dark:text-teal-300">方法</b>定位：复现 → 最小化 → 二分 → 假设验证</div>
</div>

<div class="flex gap-3 py-2 border-b border-gray-400/12 items-baseline">
<div class="w-60 shrink-0 opacity-55">靠自己肉眼审查 AI</div>
<div class="shrink-0 text-teal-600 dark:text-teal-400 font-bold px-1">→</div>
<div class="flex-1">靠<b class="text-teal-700 dark:text-teal-300">机器把关</b>：类型检查、lint、测试、契约校验进 CI，让不合格的产出根本进不来</div>
</div>

<div class="flex gap-3 py-2 border-b border-gray-400/12 items-baseline">
<div class="w-60 shrink-0 opacity-55">学具体技术栈</div>
<div class="shrink-0 text-teal-600 dark:text-teal-400 font-bold px-1">→</div>
<div class="flex-1">学<b class="text-teal-700 dark:text-teal-300">长半衰期的原理</b>，框架只是载体（本课用 FastAPI / React，换栈仍成立）</div>
</div>

</div>

<!--
最后，这门课跟你们印象里的 Web 课很不一样——它跟去年的"Web 开发技术基础"内容重叠不到一半。我列了六个转变，你们预习和上课的时候带着它。

从"记住 API 怎么写"变成"建立心智模型"——不考你背没背 API，考你知不知道一个请求经过哪些环节，每个环节谁负责、失败什么样、在哪观察。

从"追求能跑"变成"追求可解释、可验收、可回滚"——你要能说出每一行为什么这样写。

从"从零手写代码"变成"读、改、诊断、决策"——课堂上大量时间在读代码，读别人写的，包括 AI 写的。

从"报错就换写法或问 AI 重写"变成"用方法定位"——复现、最小化、二分、假设验证。这是方法，不是玄学。

从"靠自己肉眼审查 AI"变成"靠机器把关"——类型检查、lint、测试、契约校验进 CI，让不合格的产出根本进不来。

从"学具体技术栈"变成"学长半衰期的原理"——本课用 FastAPI 和 React，但那只是载体，换个栈这些原理照样成立。
-->

---

# 教学内容 · 一条主线，四次长大

<div class="-mt-2 mb-4 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">项目主线</span>
</div>

<div class="grid grid-cols-2 gap-4 text-sm">

<div class="p-4 rounded-lg border border-gray-400/25 bg-gray-500/5">
<div class="flex items-center gap-2 mb-2">
<span class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">1</span>
<span class="font-bold">第 1–5 课 · 单文件 → SSR 版</span>
<span class="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300 font-bold shrink-0">M0 · M1</span>
</div>
<div class="text-xs opacity-80 leading-relaxed">让一个请求从头走到尾：单文件起步 → 路由与校验 → 分层与依赖注入 → 模板表单闭环。</div>
</div>

<div class="p-4 rounded-lg border border-gray-400/25 bg-gray-500/5">
<div class="flex items-center gap-2 mb-2">
<span class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">2</span>
<span class="font-bold">第 6–9 课 · 契约化 API</span>
<span class="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300 font-bold shrink-0">M2 · M3</span>
</div>
<div class="text-xs opacity-80 leading-relaxed">打开持久层黑盒：SQL 建模与约束 → ORM 与迁移 → 契约化 API → 测试与 CI 四道门禁。</div>
</div>

<div class="p-4 rounded-lg border border-gray-400/25 bg-gray-500/5">
<div class="flex items-center gap-2 mb-2">
<span class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">3</span>
<span class="font-bold">第 10–13 课 · React SPA</span>
<span class="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300 font-bold shrink-0">M4</span>
</div>
<div class="text-xs opacity-80 leading-relaxed">前端工程化重写：构建与类型护栏 → 组件与渲染机制 → 数据获取与服务端状态 → 状态归属与路由。</div>
</div>

<div class="p-4 rounded-lg border border-gray-400/25 bg-gray-500/5">
<div class="flex items-center gap-2 mb-2">
<span class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">4</span>
<span class="font-bold">第 14–16 课 · 加固与上线</span>
<span class="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300 font-bold shrink-0">M5 · M6</span>
</div>
<div class="text-xs opacity-80 leading-relaxed">让它经得起真实世界：认证与对象级授权 → 安全基线与攻防 → AI 集成与上线交付。</div>
</div>

</div>


<!--
先说地图，细节后面几页再展开。

这门课的主线是一个「问答社区」——提问、回答、标签、投票、搜索，最后再加一个 AI 摘要。16 次课里它长大四次，所有课的代码都长在这一个项目上。

第 1 到 5 课，它从单文件起步，长成一个服务端渲染的问答墙——这是 M0 和 M1。第 6 到 9 课，我们把持久层黑盒打开，自己写 SQL 和 ORM，把接口契约化，架上 CI 门禁——M2、M3。第 10 到 13 课，前端工程化，重写为 React 单页应用——M4。最后三课：认证授权、安全加固、AI 集成，然后上线——M5、M6。

-->

---

# 教学内容 · 后端九课（历史路线待同步）

<div class="-mt-2 mb-3 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">后端主线</span>
<span class="opacity-55">从「一个请求怎么走」到「质量怎么守」——九次课铺出后端工程的完整链路</span>
</div>

<div class="text-[12.5px]">

<div class="flex gap-3 pb-1.5 border-b border-gray-400/30 text-xs tracking-wide opacity-55">
<div class="w-10 shrink-0">课次</div>
<div class="w-[135px] shrink-0">学什么</div>
<div class="flex-1">内容摘要</div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">1</div>
<div class="w-[135px] shrink-0 font-bold">第一个 Web 接口</div>
<div class="flex-1 opacity-85">新版：固定列表 → 补详情 → 参数断点 → 五框图；不要求四处取证</div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">2</div>
<div class="w-[135px] shrink-0 font-bold">HTTP 语义</div>
<div class="flex-1 opacity-85">「改了代码，用户还看到旧页面」——缓存翻车复现与文件名指纹修复</div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">3</div>
<div class="w-[135px] shrink-0 font-bold">路由与校验</div>
<div class="flex-1 opacity-85">缺 response_model → 密码哈希跟着响应泄漏，现场复现</div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">4</div>
<div class="w-[135px] shrink-0 font-bold">依赖与分层</div>
<div class="flex-1 opacity-85">先看到路由臃肿，再抽 Depends 与 services——痛感先于命名</div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12 bg-amber-500/5">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">5</div>
<div class="w-[135px] shrink-0 font-bold">中间件与并发</div>
<div class="flex-1 opacity-85">同步阻塞塞进 async → 并发崩塌，吞吐前后定量对照<span class="ml-1.5 text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300 font-bold">M1</span></div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">6</div>
<div class="w-[135px] shrink-0 font-bold">建模与 SQL</div>
<div class="flex-1 opacity-85">NULL 三值逻辑导致漏行（!= / NOT IN）复现与修复</div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12 bg-amber-500/5">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">7</div>
<div class="w-[135px] shrink-0 font-bold">ORM 与迁移</div>
<div class="flex-1 opacity-85">遍历关系刷出 N+1 → selectinload 修复，SQL 条数与耗时前后对照<span class="ml-1.5 text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300 font-bold">M2</span></div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">8</div>
<div class="w-[135px] shrink-0 font-bold">契约与并发写</div>
<div class="flex-1 opacity-85">两个并发投票请求 → 丢失更新 → 乐观锁返回 409</div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12 bg-amber-500/5">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">9</div>
<div class="w-[135px] shrink-0 font-bold">测试与 CI</div>
<div class="flex-1 opacity-85">AI 的「能跑」提交被四道门禁挡下，逐条修绿<span class="ml-1.5 text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300 font-bold">M3</span></div>
</div>

</div>

<!--
本页除第一课交接外仍是旧路线，仅作历史参考；不按右栏旧故障顺序布置v4任务。当前七章映射见course-conventions，第一课以ch01成稿为准。

新版第1课先建立正常列表，由学生补详情，再观察参数断点和五框链路，不接数据库。以下第2课起为历史讲法，待另行同步。第 2 课把协议变成判据：你改了代码，用户还看到旧页面——不是代码的问题，是哪一层缓存在作怪。第 3 课看一个最典型的 AI 事故：少了 response_model，密码哈希跟着响应就漏出去了。第 4 课先让你痛——路由里到处是重复的会话、分页、异常处理——痛完再抽依赖注入和分层。第 5 课，一个同步阻塞调用塞进 async 端点，并发一上来吞吐直接塌方，我们用数据说话——这里交付 M1。

下半段进数据层。第 6 课：一个 NULL 就能让你的查询静默地少几行数据。第 7 课：遍历关系刷出 N+1，几十条 SQL 变一条，条数和耗时前后对照——交付 M2。第 8 课两个并发请求同时投票，丢失更新，上乐观锁返回 409。第 9 课是这门课的总闸：CI 架起四道门禁，拿一段 AI 的「能跑」提交去撞——被挡下，再逐条修绿——交付 M3。

为什么用「翻车」的方式上课？因为 AI 生成的代码最爱犯的错，几乎全在这些现场里——密钥泄漏、缓存、N+1、丢失更新。它们都「能跑」，但迟早出事。亲眼见过一次，你以后看 AI 的代码，眼睛就不一样了。
-->

---

# 教学内容 · 前端与交付七课（第 10–16 次）

<div class="-mt-2 mb-3 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">前端与交付</span>
<span class="opacity-55">后半程：前端工程化 + 安全加固 + 上线——把项目送到真实世界门口</span>
</div>

<div class="text-[12.5px]">

<div class="flex gap-3 pb-1.5 border-b border-gray-400/30 text-xs tracking-wide opacity-55">
<div class="w-10 shrink-0">课次</div>
<div class="w-[135px] shrink-0">学什么</div>
<div class="flex-1">内容摘要</div>
</div>

<div class="flex gap-3 py-[9px] border-b border-gray-400/12">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">10</div>
<div class="w-[135px] shrink-0 font-bold">前端工程化</div>
<div class="flex-1 opacity-85">在 dist/ 里 grep 出前端 .env 里的 API 密钥</div>
</div>

<div class="flex gap-3 py-[9px] border-b border-gray-400/12">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">11</div>
<div class="w-[135px] shrink-0 font-bold">React 渲染机制</div>
<div class="flex-1 opacity-85">key=index + 受控输入导致内容错位 → 现场修复</div>
</div>

<div class="flex gap-3 py-[9px] border-b border-gray-400/12">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">12</div>
<div class="w-[135px] shrink-0 font-bold">数据获取</div>
<div class="flex-1 opacity-85">人为随机延迟复现请求竞态（旧响应盖新）→ query 层修复</div>
</div>

<div class="flex gap-3 py-[9px] border-b border-gray-400/12 bg-amber-500/5">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">13</div>
<div class="w-[135px] shrink-0 font-bold">状态与路由</div>
<div class="flex-1 opacity-85">筛选条件从 useState 迁到 URL 态：刷新不丢、链接可分享<span class="ml-1.5 text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300 font-bold">M4</span></div>
</div>

<div class="flex gap-3 py-[9px] border-b border-gray-400/12">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">14</div>
<div class="w-[135px] shrink-0 font-bold">认证与授权</div>
<div class="flex-1 opacity-85">现场解出 JWT payload；越权改帖（IDOR）复现 → 对象级授权修复</div>
</div>

<div class="flex gap-3 py-[9px] border-b border-gray-400/12 bg-amber-500/5">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">15</div>
<div class="w-[135px] shrink-0 font-bold">安全基线</div>
<div class="flex-1 opacity-85">存储型 XSS 偷 Cookie 冒充登录 → 修复后复测失败<span class="ml-1.5 text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300 font-bold">M5</span></div>
</div>

<div class="flex gap-3 py-[9px] border-b border-gray-400/12 bg-amber-500/5">
<div class="w-10 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">16</div>
<div class="w-[135px] shrink-0 font-bold">AI 与上线</div>
<div class="flex-1 opacity-85">请求内同步等 LLM 30 秒 → 超时 / 降级 / 流式改造<span class="ml-1.5 text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300 font-bold">M6</span></div>
</div>

</div>

<!--
后半程七次课，同样的结构，我再过一遍。

第 10 课，你们第一次看懂 npm run build 到底干了什么——然后把打出来的 dist 拆开，在里面 grep 出前端 .env 里的密钥。对，前端的环境变量必然泄漏，这个结论你要会用实验证明。第 11 课 React 渲染机制：把 key 写成 index，再加一个受控输入，列表内容就错位——现场复现，现场修。第 12 课：加一个随机延迟，请求竞态就出现了——旧响应把新响应盖掉，用 AbortController 和 query 层修掉它。第 13 课：筛选条件放在 useState 里，一刷新就丢、链接分享不出去——迁移到 URL 态。M4 交付。

第 14 课安全入场：现场把一个 JWT 的 payload 解出来给你们看——Base64 不是加密。然后越权改别人的帖子，复现 IDOR，加对象级授权。第 15 课攻防日：存储型 XSS 偷走 Cookie 冒充登录，修完再测——打不进来了。M5 交付。

第 16 课收尾：AI 集成——请求里同步等大模型 30 秒是什么体验？超时、降级、流式改造。然后上线：一键起容器，把它部署到服务器上。M6 交付——期末它得活着。
-->

---

# 教学内容 · 环境与框架

<div class="-mt-2 mb-4 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">装备清单</span>
<span class="opacity-55">全课程用到的全部工具——每一项都会在用到它的那一课里亲手装、亲手用一遍</span>
</div>

<div class="text-sm">

<div class="flex gap-3 py-2 border-b border-gray-400/12 items-start">
<div class="w-20 shrink-0 font-bold text-teal-700 dark:text-teal-300 pt-0.5">后端</div>
<div class="flex-1 flex flex-wrap gap-1.5">
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">Python 3.12+</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">uv</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">FastAPI</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">Pydantic v2</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">pydantic-settings</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">Jinja2</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">SQLAlchemy 2.0</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">Alembic</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">httpx</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">pytest</span>
</div>
</div>

<div class="flex gap-3 py-2 border-b border-gray-400/12 items-start">
<div class="w-20 shrink-0 font-bold text-teal-700 dark:text-teal-300 pt-0.5">数据</div>
<div class="flex-1 flex flex-wrap gap-1.5">
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">PostgreSQL / MySQL</span>
</div>
</div>

<div class="flex gap-3 py-2 border-b border-gray-400/12 items-start">
<div class="w-20 shrink-0 font-bold text-teal-700 dark:text-teal-300 pt-0.5">前端</div>
<div class="flex-1 flex flex-wrap gap-1.5">
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">Node 20+</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">Vite</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">React 18+</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">TypeScript（最小集）</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">React Router</span>
</div>
</div>

<div class="flex gap-3 py-2 border-b border-gray-400/12 items-start">
<div class="w-20 shrink-0 font-bold text-teal-700 dark:text-teal-300 pt-0.5">质量门禁</div>
<div class="flex-1 flex flex-wrap gap-1.5">
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">ruff</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">ESLint</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">tsc --noEmit</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">pytest</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">Playwright</span>
</div>
</div>

<div class="flex gap-3 py-2 border-b border-gray-400/12 items-start">
<div class="w-20 shrink-0 font-bold text-teal-700 dark:text-teal-300 pt-0.5">观察</div>
<div class="flex-1 flex flex-wrap gap-1.5 items-center">
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">Chrome DevTools</span>
<span class="text-[11px] opacity-50 font-mono">Network / Elements / Application / Performance</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">React DevTools</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">psql</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">curl</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">SQLAlchemy echo</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">rollup-plugin-visualizer</span>
</div>
</div>

<div class="flex gap-3 py-2 border-b border-gray-400/12 items-start">
<div class="w-20 shrink-0 font-bold text-teal-700 dark:text-teal-300 pt-0.5">AI</div>
<div class="flex-1 flex flex-wrap gap-1.5">
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">Qoder</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">Codex</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">Claude Code</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 text-xs font-mono">OpenCode</span>
</div>
</div>

</div>

<div class="mt-4 p-3 rounded-lg bg-teal-500/8 border-l-4 border-teal-500 text-xs">
三件套 <b>Python · Node · PostgreSQL</b> 在 Week 0 预习包里已备好；其余工具不提前背——都会在用到它的那一课里亲手装、亲手用一遍。
</div>

<!--
最后看一页很实在的——装备清单。这个学期用到的所有工具都在这上面。

后端一行：Python 3.12 打底，包管理 uv，框架 FastAPI，数据校验 Pydantic v2，配置管理 pydantic-settings，模板 Jinja2，ORM 是 SQLAlchemy 2.0，迁移 Alembic，HTTP 客户端 httpx，测试 pytest。名字现在陌生很正常——从第 3 课起，你会一个一个亲手用上。

数据一行就一样东西：PostgreSQL 或 MySQL，二选一。

前端一行：Node 20 起步，构建工具 Vite，React 18；TypeScript 只学能当护栏的最小一部分，路由用 React Router。

质量门禁一行是第 9 课的主角：ruff、ESLint、tsc --noEmit、pytest，四道检查由 GitHub Actions 串起来自动跑；再加一条 Playwright 冒烟测试，还有 pip-audit 和 npm audit 查依赖漏洞。

观察一行我建议你们现在就看熟。我们每节课都在问两件事——失败什么样、在哪观察，答案就藏在这行里：Chrome DevTools 看网络和页面、React DevTools 看组件、VS Code 调试器看栈帧、psql 直接查库、curl 发原始请求、SQLAlchemy 的 echo 打印每一条 SQL，还有一个产物可视化插件。

AI 一行：Qoder、Codex、Claude Code、OpenCode，任选顺手的。这门课不教哪个工具怎么用——教的是怎么让它们听你的。

Python、Node、PostgreSQL 这三件套，Week 0 预习包里已经装好了；还没跑通自检脚本的同学，这周之内必须补上，上课现场就要用。其余工具不用提前背——用到哪一课，装哪一课。
-->

---

# 学完这门课，你能做到什么

<div class="-mt-2 mb-3 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">结业能力</span>
<span class="opacity-55">七条能力标准</span>
</div>

<div class="text-[12.5px]">

<div class="flex gap-3 pb-1.5 border-b border-gray-400/30 text-xs tracking-wide opacity-55">
<div class="w-[130px] shrink-0">能力</div>
<div class="flex-1">可测量的标准</div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12">
<div class="w-[130px] shrink-0 font-bold">Web 系统工作原理</div>
<div class="flex-1 opacity-85">徒手画出请求全链路，对任一环节说清「谁负责 / 失败什么样 / 在哪观察」</div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12">
<div class="w-[130px] shrink-0 font-bold">后端框架机制</div>
<div class="flex-1 opacity-85">说清装饰器如何变成路由表、依赖如何求值；把「接口慢 / 报错」定位到某一层</div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12">
<div class="w-[130px] shrink-0 font-bold">数据层</div>
<div class="flex-1 opacity-85">画 ER、写出带约束的 DDL；读懂 ORM 生成的 SQL；修 N+1 与丢失更新</div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12">
<div class="w-[130px] shrink-0 font-bold">React 与状态</div>
<div class="flex-1 opacity-85">说清重渲染触发条件与 key 的后果；对任一状态给出归属判定并辩护</div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12">
<div class="w-[130px] shrink-0 font-bold">前端构建</div>
<div class="flex-1 opacity-85">拆开 dist/ 产物；解释「类型错了为什么还能跑」「前端 env 为什么必然泄漏」</div>
</div>

<div class="flex gap-3 py-[7px] border-b border-gray-400/12">
<div class="w-[130px] shrink-0 font-bold">安全与认证</div>
<div class="flex-1 opacity-85">实现会话认证与对象级授权；复现并修复 XSS / CSRF / 注入 / IDOR 各一例</div>
</div>

<div class="flex gap-3 py-[7px] items-baseline bg-teal-500/5">
<div class="w-[130px] shrink-0 font-bold text-teal-700 dark:text-teal-300">驾驭 AI</div>
<div class="flex-1 opacity-85">方案决策；拦住不合格产出；bug定位修复</div>
</div>

</div>


<!--
最后把这个学期给你们什么列清楚——七条能力标准，全部可测量。期末不考你背 API、背定义，看你能做到什么。

Web 系统工作原理：徒手画出请求全链路，对任一环节说得清「谁负责、失败什么样、在哪观察」。后端框架机制：说清装饰器怎么变成路由表、依赖怎么求值；一句「接口慢」，你能定位到某一层。数据层：画 ER、写带约束的 DDL；读懂 ORM 生成的 SQL；N+1 和丢失更新，你能识别也能修。React 与状态：说清重渲染什么时候发生、key 写错的后果；任一状态，你都能给出归属判定，并且辩护。前端构建：拆得开 dist/；能解释「类型错了为什么还能跑」「前端 env 为什么必然泄漏」。安全与认证：会话认证和对象级授权你能实现；XSS、CSRF、注入、IDOR，每样你都能复现并修复。

最后一条——驾驭 AI：十分钟内，在一段 AI 生成的代码里定位缺陷、给出修复 diff；写出带约束的提示词；用 CI 门禁让不合格的产出根本进不来。前面六条，都是为了最后这一条。

具体怎么考、分数怎么算——下一页说。
-->


---

# 本课程的考核方式

<div class="-mt-2 mb-4 flex items-center gap-2 text-xs">
<span class="px-2 py-0.5 rounded-full bg-teal-500/15 text-teal-700 dark:text-teal-300 font-bold">成绩构成</span>
<span class="opacity-55">总评 = 平时 50% ＋ 期末 50%；分值细则开课后公布</span>
</div>

<div class="flex h-12 rounded-lg overflow-hidden text-xs font-bold">
<div class="basis-[10%] bg-teal-500/25 flex items-center justify-center">作业 10%</div>
<div class="basis-[40%] bg-teal-500/45 dark:bg-teal-500/35 flex items-center justify-center">项目实验 40%</div>
<div class="basis-[50%] bg-gray-500/15 flex items-center justify-center">期末 50% · 开卷</div>
</div>


<div class="mt-5 p-4 rounded-lg border-l-4 border-amber-500 bg-amber-500/8">
<div class="flex items-center flex-wrap gap-2">
<span class="font-bold text-sm text-amber-700 dark:text-amber-300">AI 使用政策</span>
<span class="px-2 py-0.5 rounded bg-amber-500/15 text-xs font-bold">鼓励使用</span>
<span class="px-2 py-0.5 rounded bg-amber-500/15 text-xs font-bold">必须留痕</span>
<span class="px-2 py-0.5 rounded bg-amber-500/15 text-xs font-bold">必须能解释</span>
</div>
<div class="mt-2 text-xs opacity-65">三条同时成立，才算驾驭 AI——从第一次作业开始执行。</div>
</div>

<!--
好，说考核。结构先交代：总评 = 平时 50 + 期末 50。

平时这 50 拆两块：作业 10，项目实验 40。看这个比例——项目实验是整个考核里占比最大的单块，就是你从 M1 走到 M6 的问答社区项目。这门课的成绩，大头是随课长出来的，期末前突击补不回来。作业那块不用多讲，就是每节课后的「规格 → 生成 → 审查 → 修复」闭环——评分重点从来不是"能跑"，是你会不会审查、能不能修对。

期末 50，开卷。具体形式和评分细则开课后公布——你们不需要现在记数字，记住结构就行。

最后是一条政策——AI 使用政策，三个词：鼓励使用、必须留痕、必须能解释。再说一遍：这门课不禁止 AI，反而鼓励你用；但用要留痕，产出要能解释。这两条，就是我前面反复说的"驾驭"的验收标准——从第一次作业就开始执行。
-->
