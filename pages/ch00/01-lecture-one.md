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

# 教学内容 · 后端九课（第 1–9 次）

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
<div class="w-[135px] shrink-0 font-bold">请求全链路</div>
<div class="flex-1 opacity-85">同一个 request-id，在 DevTools / 日志 / 栈帧 / SQL 四处串起一个请求</div>
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
这九次课全在后端，我按课次过一遍。注意右边这一列——每节课都有一个「翻车现场」，你亲眼看着它发生，再亲手把它修好。

第 1 课建立坐标系：一个请求从浏览器到数据库再回来，经过哪些环节，每个环节谁负责、失败什么样、在哪观察——以后所有定位问题都从这张图出发。第 2 课把协议变成判据：你改了代码，用户还看到旧页面——不是代码的问题，是哪一层缓存在作怪。第 3 课看一个最典型的 AI 事故：少了 response_model，密码哈希跟着响应就漏出去了。第 4 课先让你痛——路由里到处是重复的会话、分页、异常处理——痛完再抽依赖注入和分层。第 5 课，一个同步阻塞调用塞进 async 端点，并发一上来吞吐直接塌方，我们用数据说话——这里交付 M1。

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


---
layout: section
---

# 讲一 · 协议报文与工具链

<div class="pt-3 text-sm opacity-60">
0.1 跑在哪里 · 0.2 URL 与 HTTP 报文 · 0.3 JSON · 0.4 终端与工具链 · 0.5 读报错 · 0.6 调试器（高光）
</div>

<div class="mt-8 text-xs opacity-50">
本讲 85 分钟 · 录播 · 标「暂停跟做」处务必动手
</div>

<!--
课前课第一讲。这一讲不讲任何框架，只干一件事：把"你写的代码到底跑在哪儿、报错怎么读、调试器怎么用"这三件高风险的前置项打通。

这一讲有六节，其中 0.6 调试器是高光，二十五分钟，不可压缩。中间有六处"暂停跟做"，录播课最大的失败模式是你一路看完什么都没动手，所以那几页是专门用来打断你的。
-->

---

# 0.1 你以前写的东西跑在哪里

<div class="text-xs opacity-55 -mt-1 mb-3">纠正一个极常见的错误心智模型：「我写的代码就是在浏览器里跑的」</div>

<div grid="~ cols-[1fr_auto_1fr] gap-4 items-center" class="mt-6">

<div class="p-5 rounded-lg border-2 border-teal-500/40 bg-teal-500/5 text-center">
  <div class="text-xs tracking-widest opacity-60 mb-2">客户端进程</div>
  <div class="text-lg font-bold">浏览器</div>
  <div class="text-xs opacity-70 mt-1">（你的电脑）</div>
  <div class="mt-3 pt-3 border-t border-teal-500/20 text-sm font-mono">HTML · CSS · JavaScript</div>
</div>

<div class="flex flex-col items-center gap-3 px-2">
  <div class="flex items-center gap-1 text-xs">
    <span class="px-2 py-0.5 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300 font-bold">请求报文</span>
    <span class="text-lg opacity-50">→</span>
  </div>
  <div class="flex items-center gap-1 text-xs">
    <span class="text-lg opacity-50">←</span>
    <span class="px-2 py-0.5 rounded bg-sky-500/15 text-sky-700 dark:text-sky-300 font-bold">响应报文</span>
  </div>
  <div class="mt-1 text-[11px] opacity-45 text-center max-w-[120px]">中间<b>只有报文</b><br>没有共享内存<br>没有共享变量</div>
</div>

<div class="p-5 rounded-lg border-2 border-rose-500/40 bg-rose-500/5 text-center">
  <div class="text-xs tracking-widest opacity-60 mb-2">服务端进程</div>
  <div class="text-lg font-bold">服务器</div>
  <div class="text-xs opacity-70 mt-1">（可能在另一台机器）</div>
  <div class="mt-3 pt-3 border-t border-rose-500/20 text-sm font-mono">Python · Node · Java</div>
</div>

</div>

<div v-click class="mt-6 p-3.5 rounded-lg bg-amber-500/10 border-l-4 border-amber-500 text-sm">
这是<span class="font-bold">两个进程</span>，通常在两台机器上；它们之间<span class="font-bold">只有报文往来</span>，没有别的联系。这门课接下来十六次，一大半时间在讲右边那个方框里的事。
</div>

<!--
先问一个问题：你以前用 AI 写的那个网页，代码到底在哪儿跑？很多人的印象是"就在浏览器里跑"。这个印象是错的，而且错得很关键。

你看这张图，左边浏览器，右边服务端，这是两个进程，很可能在两台不同的机器上。它们之间只有一件事——发报文。没有共享内存，没有共享变量，什么都没有，只有报文。

[click] 这门课接下来十六次，一大半时间在讲右边那个方框里面的事。
-->

---

# 0.1 三种形态 ＋ 一个现场演示

<div grid="~ cols-2 gap-6" class="mt-4">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">先建立轮廓（第 12 次课正式比较）</div>
<div class="space-y-2.5 text-sm">
  <div class="p-3 rounded border border-gray-400/25 bg-gray-500/5">
    <span class="font-bold">纯静态页面</span><span class="opacity-70">　只有客户端，没有服务端逻辑</span>
  </div>
  <div class="p-3 rounded border border-gray-400/25 bg-gray-500/5">
    <span class="font-bold">服务端渲染</span><span class="opacity-70">　服务端拼好完整 HTML 发过来</span><span class="text-xs opacity-50">（第 4 次课做）</span>
  </div>
  <div class="p-3 rounded border-2 border-teal-500/40 bg-teal-500/5">
    <span class="font-bold text-teal-700 dark:text-teal-300">前后端分离</span><span class="opacity-70">　服务端只发数据，浏览器自己画</span><span class="text-xs opacity-50">（第 12 次课做）</span>
  </div>
</div>
<div class="mt-3 text-xs opacity-70">你以前用 AI 生成的项目，大概率是<span class="font-bold">第三种</span>。</div>
</div>

<div v-click>
<div class="text-xs tracking-widest opacity-60 mb-2">现场演示 · 杀掉后端</div>
<div class="space-y-2 text-sm">
  <div class="flex items-center gap-2 p-2 rounded bg-gray-500/8">
    <span class="w-5 h-5 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">1</span>
    <span>打开一个前后端分离的小页面 → 正常显示数据</span>
  </div>
  <div class="flex items-center gap-2 p-2 rounded bg-gray-500/8">
    <span class="w-5 h-5 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">2</span>
    <span>在终端 <kbd>Ctrl+C</kbd> 杀掉后端进程</span>
  </div>
  <div class="flex items-center gap-2 p-2 rounded bg-rose-500/10 border border-rose-500/30">
    <span class="w-5 h-5 rounded-full bg-rose-500/25 text-xs flex items-center justify-center font-bold shrink-0">3</span>
    <span>刷新页面</span>
  </div>
</div>
<div class="mt-3 p-3 rounded-lg bg-rose-500/8 border-l-4 border-rose-500 text-sm">
<b>预期：</b>页面框架、按钮、样式<span class="font-bold">都还在</span>，但数据区域空了或报错；控制台出现网络请求失败。
</div>
</div>

</div>

<!--
[click] 我现在演示一下。这个页面现在好好的，有数据。我去终端把后端进程杀掉。（杀掉，刷新）

你看，页面还在，按钮还在，样式还在，但数据没了。为什么？因为页面这些东西是浏览器手里的，后端死了不影响它。但数据是要去问后端的，后端死了就问不到。

这就是"两个进程"的直接证据。这一节不要引入任何术语层级，你只要建立"两个进程"这一个概念就够了。
-->

---

# 0.2 URL 解剖

<div class="text-xs opacity-55 -mt-1 mb-4">URL 你们每天在用，但可能没拆过。看这一行，六段。</div>

<div class="p-5 rounded-lg bg-gray-500/8 border border-gray-400/25 font-mono text-center">
  <div class="text-base tracking-wide">
    <span class="text-rose-600 dark:text-rose-400">http://</span><span class="text-amber-600 dark:text-amber-400">127.0.0.1</span><span class="text-sky-600 dark:text-sky-400">:8000</span><span class="text-teal-600 dark:text-teal-400">/hello/world</span><span class="text-purple-600 dark:text-purple-400">?page=2&size=10</span><span class="opacity-50">#top</span>
  </div>
  <div class="flex justify-center gap-1 mt-3 text-[11px]">
    <span class="px-2 py-0.5 rounded bg-rose-500/15 text-rose-700 dark:text-rose-300">协议</span>
    <span class="px-2 py-0.5 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300">主机</span>
    <span class="px-2 py-0.5 rounded bg-sky-500/15 text-sky-700 dark:text-sky-300">端口</span>
    <span class="px-2 py-0.5 rounded bg-teal-500/15 text-teal-700 dark:text-teal-300">路径</span>
    <span class="px-2 py-0.5 rounded bg-purple-500/15 text-purple-700 dark:text-purple-300">查询串</span>
    <span class="px-2 py-0.5 rounded bg-gray-500/15 opacity-70">片段</span>
  </div>
</div>

<div grid="~ cols-2 gap-5" class="mt-6">

<div class="p-4 rounded-lg border border-teal-500/30 bg-teal-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-2">会被发到服务端</div>
  <div class="text-sm space-y-1">
    <div>· <span class="font-bold text-teal-700 dark:text-teal-300">路径</span> <code class="text-xs">/hello/world</code></div>
    <div>· <span class="font-bold text-teal-700 dark:text-teal-300">查询串</span> <code class="text-xs">?page=2&size=10</code></div>
  </div>
</div>

<div v-click class="p-4 rounded-lg border border-rose-500/30 bg-rose-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-2">不会被发到服务端</div>
  <div class="text-sm">
    · <span class="font-bold text-rose-600 dark:text-rose-400">片段</span> <code class="text-xs">#top</code>
    <div class="mt-1.5 text-xs opacity-75">只有浏览器自己用——服务端永远看不到井号后面的东西。</div>
  </div>
</div>

</div>

<!--
URL 你们每天在用，但可能没拆过。看这一行，六段：协议、主机、端口、路径、查询串、片段。

重点记两件事：路径和查询串会发给服务端；

[click] 井号后面那个片段不会，那个只有浏览器自己用。你点一个锚点链接跳到页面某个位置，服务端根本不知道你跳哪儿了。
-->

---

# 0.2 HTTP 报文四部分

<div class="text-xs opacity-55 -mt-1 mb-3">请求和响应都是这四样：起始行 · 头 · 空行 · 体。<span class="font-bold text-amber-600 dark:text-amber-400">空行是头与体的唯一分界</span>。</div>

<div grid="~ cols-2 gap-5" class="mt-2 text-[13px]">

<div>
<div class="text-xs tracking-widest opacity-60 mb-1.5">请求报文</div>
<div class="rounded-lg overflow-hidden border border-gray-400/25 font-mono leading-relaxed">
  <div class="px-3 py-1.5 bg-amber-500/12 border-l-4 border-amber-500">GET /hello?page=2 HTTP/1.1<span class="opacity-50 text-xs">　← 起始行：方法＋路径＋版本</span></div>
  <div class="px-3 py-1.5 bg-sky-500/8 border-l-4 border-sky-500">host: 127.0.0.1:8000</div>
  <div class="px-3 py-0.5 bg-sky-500/8 border-l-4 border-sky-500 opacity-80">user-agent: curl/8.4.0</div>
  <div class="px-3 py-0.5 bg-sky-500/8 border-l-4 border-sky-500 opacity-80">accept: */*<span class="opacity-50 text-xs">　← 请求头（可多行）</span></div>
  <div class="px-3 py-1.5 bg-rose-500/15 border-l-4 border-rose-500 font-bold text-center tracking-widest">（空行）</div>
  <div class="px-3 py-1.5 bg-teal-500/8 border-l-4 border-teal-500 opacity-70">（请求体，GET 通常没有）</div>
</div>
</div>

<div>
<div class="text-xs tracking-widest opacity-60 mb-1.5">响应报文</div>
<div class="rounded-lg overflow-hidden border border-gray-400/25 font-mono leading-relaxed">
  <div class="px-3 py-1.5 bg-amber-500/12 border-l-4 border-amber-500">HTTP/1.1 200 OK<span class="opacity-50 text-xs">　← 状态行：版本＋状态码＋原因</span></div>
  <div class="px-3 py-1.5 bg-sky-500/8 border-l-4 border-sky-500">Content-Type: application/json</div>
  <div class="px-3 py-0.5 bg-sky-500/8 border-l-4 border-sky-500 opacity-80">Content-Length: 214</div>
  <div class="px-3 py-0.5 bg-sky-500/8 border-l-4 border-sky-500 opacity-80">X-Demo-Server: lesson00<span class="opacity-50 text-xs">　← 响应头</span></div>
  <div class="px-3 py-1.5 bg-rose-500/15 border-l-4 border-rose-500 font-bold text-center tracking-widest">（空行）</div>
  <div class="px-3 py-1.5 bg-teal-500/8 border-l-4 border-teal-500">{"message":"hello", ...}<span class="opacity-50 text-xs">　← 响应体</span></div>
</div>
</div>

</div>

<div v-click class="mt-4 grid grid-cols-2 gap-4 text-sm">
<div class="p-3 rounded bg-gray-500/8">
  <div class="text-xs tracking-widest opacity-60 mb-1.5">先认脸、不求深解的四个头</div>
  <code class="text-xs">content-type</code>（体是什么格式）· <code class="text-xs">content-length</code>（体多长）· <code class="text-xs">location</code>（新资源在哪）· <code class="text-xs">cookie</code>（第 13 次课正题）
</div>
<div class="p-3 rounded bg-gray-500/8">
  <div class="text-xs tracking-widest opacity-60 mb-1.5">方法与状态码只记轮廓</div>
  <span class="font-bold">GET</span> 读 · <span class="font-bold">POST</span> 提交　｜　<span class="text-teal-700 dark:text-teal-300 font-bold">2xx</span> 成功 · <span class="text-amber-600 dark:text-amber-400 font-bold">4xx</span> 你错了 · <span class="text-rose-600 dark:text-rose-400 font-bold">5xx</span> 我错了
</div>
</div>

<!--
现在看报文。HTTP 报文长什么样？四部分：起始行、头、空行、体。就这四样，请求响应都一样。

注意中间这个空行——它是头和体的唯一分界，没有它服务端不知道头到哪儿结束。学生最容易忽略它，所以我把它标红。

[click] 下面这两块你扫一眼就行。四个头先认脸不求深解；方法和状态码只记轮廓——GET 读、POST 提交，2xx 成功、4xx 你错了、5xx 我错了。判据留给第 1 次课，今天不抢。
-->

---
layout: center
class: text-center
---

<div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-700 dark:text-amber-300 font-bold text-sm tracking-wide">
⏸ 暂停跟做 1 · 起服务端并发第一个请求
</div>

<div class="mt-6 max-w-3xl mx-auto text-left">

<div class="text-xs tracking-widest opacity-55 mb-1.5">要执行的命令</div>

```bash
uv run python snippets/lesson00/demo_server.py       # 终端 A，会一直占着
curl -i "http://127.0.0.1:8000/hello?page=2"         # 终端 B
```

<div class="text-xs tracking-widest opacity-55 mt-4 mb-1.5">预期看到</div>

```
HTTP/1.1 200 OK
Server: demo/0.1 Python/3.12.0
Content-Type: application/json; charset=utf-8
X-Demo-Server: lesson00

{"message": "hello", "path": "/hello?page=2",
 "your_headers": {"Host": "127.0.0.1:8000", "User-Agent": "curl/8.4.0", ...}}
```

</div>

<div class="mt-6 inline-flex items-center gap-2 text-teal-700 dark:text-teal-300 font-bold">
✓ 做完再继续
</div>

<!--
现在跟我做。我给了你们一个四十行的小服务端，纯标准库，没有任何框架。你先把它跑起来——终端 A 会一直占着。

然后终端 B 用 curl 请求它。看这个 -i 参数，意思是"把响应头也打出来"。第一行 200 OK，然后一堆头，然后一个空行，然后是体。四部分都在。

注意响应体里这个 your_headers——这是我故意设计的，它把你发过来的请求头原样退回给你。你看，你只敲了一个 curl，它替你发了 host、user-agent、accept 三个头。
-->

---
layout: center
class: text-center
---

<div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-700 dark:text-amber-300 font-bold text-sm tracking-wide">
⏸ 暂停跟做 2 · 换成浏览器，对比请求头
</div>

<div class="mt-7 max-w-3xl mx-auto text-left space-y-4">

<div class="p-4 rounded-lg bg-gray-500/8 text-sm">
用浏览器访问同一个地址 <code class="text-xs">http://127.0.0.1:8000/hello?page=2</code>，打开 DevTools 的 <span class="font-bold">Network</span> 面板，找到这个请求，看 <span class="font-bold">Headers</span> 标签里的 Request Headers 与 Response Headers。
</div>

<div class="p-4 rounded-lg border-2 border-teal-500/40 bg-teal-500/5 text-sm">
<b class="text-teal-700 dark:text-teal-300">对比 <code class="text-xs">your_headers</code> 的内容：</b>浏览器发的头比 curl <span class="font-bold">多很多</span>——十几个。这些头都在干什么？<span class="font-bold">第二次课整节课讲。</span>
</div>

</div>

<div class="mt-7 inline-flex items-center gap-2 text-teal-700 dark:text-teal-300 font-bold">
✓ 做完再继续
</div>

<!--
[click] 现在用浏览器访问同一个地址，打开 F12 看 Network。你会发现浏览器发的头比 curl 多得多——十几个。

这些头都在干什么？第二次课整节课讲。今天你只要建立一个认知：每次请求都是一段有固定格式的文本，你能看到它的每一个字节。Web 开发里没有魔法，出问题的时候你总能把报文抓出来看。
-->

---
layout: center
class: text-center
---

<div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-700 dark:text-amber-300 font-bold text-sm tracking-wide">
⏸ 暂停跟做 3 · 让它返回一个 404 和一个 400
</div>

<div class="mt-6 max-w-3xl mx-auto text-left">

<div class="text-xs tracking-widest opacity-55 mb-1.5">要执行的命令</div>

```bash
curl -i http://127.0.0.1:8000/nothing-here
curl -i -X POST http://127.0.0.1:8000/echo -H 'content-type: application/json' -d '{坏JSON'
```

<div class="text-xs tracking-widest opacity-55 mt-4 mb-1.5">预期看到</div>

<div class="grid grid-cols-2 gap-4 text-sm">
<div class="p-3 rounded border border-amber-500/30 bg-amber-500/5">
<div class="font-mono font-bold text-amber-700 dark:text-amber-300">404 Not Found</div>
<div class="text-xs opacity-70 mt-1">路径不存在 → 服务端找不到资源</div>
</div>
<div class="p-3 rounded border border-rose-500/30 bg-rose-500/5">
<div class="font-mono font-bold text-rose-600 dark:text-rose-400">400 Bad Request</div>
<div class="text-xs opacity-70 mt-1">体不是合法 JSON → 服务端读不懂你发的</div>
</div>
</div>

</div>

<div class="mt-6 inline-flex items-center gap-2 text-teal-700 dark:text-teal-300 font-bold">
✓ 做完再继续
</div>

<!--
最后让它返回一个 404 和一个 400。第一个请求一个不存在的路径，第二个发一段坏掉的 JSON。

你看状态行：404 是"你请求的东西我这儿没有"，400 是"你发的东西我读不懂"。这两个状态码第 1 次课会反复见到，今天先混个脸熟。
-->

---

# 0.3 JSON 的形状

<div class="text-xs opacity-55 -mt-1 mb-3">快讲。重点只有一件事：看着一段嵌套 JSON 说出「这是对象，里面有个数组，数组里是对象」。</div>

<div grid="~ cols-[1fr_1.1fr] gap-6" class="mt-2">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">JSON 只有六种值</div>
<div class="flex flex-wrap gap-2 text-sm">
  <span class="px-2.5 py-1 rounded bg-teal-500/10 border border-teal-500/25">对象 <code class="text-xs">{}</code></span>
  <span class="px-2.5 py-1 rounded bg-teal-500/10 border border-teal-500/25">数组 <code class="text-xs">[]</code></span>
  <span class="px-2.5 py-1 rounded bg-teal-500/10 border border-teal-500/25">字符串 <code class="text-xs">""</code></span>
  <span class="px-2.5 py-1 rounded bg-teal-500/10 border border-teal-500/25">数字</span>
  <span class="px-2.5 py-1 rounded bg-teal-500/10 border border-teal-500/25">布尔 <code class="text-xs">true/false</code></span>
  <span class="px-2.5 py-1 rounded bg-teal-500/10 border border-teal-500/25"><code class="text-xs">null</code></span>
</div>

<div class="text-xs tracking-widest opacity-60 mt-5 mb-2">与 Python 的三处差异（必踩）</div>
<div class="text-sm">
<div class="flex gap-3 py-1.5 border-b border-gray-400/15">
  <div class="flex-1 font-mono text-xs">JSON</div><div class="flex-1 font-mono text-xs opacity-70">Python</div>
</div>
<div class="flex gap-3 py-1.5 border-b border-gray-400/15">
  <div class="flex-1 font-mono text-xs text-rose-600 dark:text-rose-400">true / false</div><div class="flex-1 font-mono text-xs">True / False</div>
</div>
<div class="flex gap-3 py-1.5 border-b border-gray-400/15">
  <div class="flex-1 font-mono text-xs text-rose-600 dark:text-rose-400">null</div><div class="flex-1 font-mono text-xs">None</div>
</div>
<div class="flex gap-3 py-1.5">
  <div class="flex-1 font-mono text-xs text-rose-600 dark:text-rose-400">键必须双引号</div><div class="flex-1 font-mono text-xs">单引号也行</div>
</div>
</div>
</div>

<div v-click>
<div class="text-xs tracking-widest opacity-60 mb-2">三层嵌套结构树</div>
<div class="p-4 rounded-lg bg-gray-500/8 border border-gray-400/25 font-mono text-xs leading-relaxed">
<div><span class="text-teal-700 dark:text-teal-300 font-bold">对象</span> {</div>
<div class="pl-4">"type": "...", "status": 422,</div>
<div class="pl-4"><span class="text-amber-600 dark:text-amber-400 font-bold">"errors": 数组</span> [</div>
<div class="pl-8"><span class="text-sky-600 dark:text-sky-400 font-bold">对象</span> {"field": "title", "msg": "..."},</div>
<div class="pl-8"><span class="text-sky-600 dark:text-sky-400 font-bold">对象</span> {"field": "body",  "msg": "..."}</div>
<div class="pl-4">],</div>
<div class="pl-4">"request_id": "9f2c1a4b7e30"</div>
<div>}</div>
</div>
<div class="mt-2 text-xs opacity-75">最外层是<b>对象</b> → <code>errors</code> 是<b>数组</b> → 每个元素又是<b>对象</b>，各有 <code>field</code> 和 <code>msg</code> 两个键。</div>
</div>

</div>

<!--
JSON 就六种值，对象、数组、字符串、数字、布尔、null。没别的了。

三个坑，你们写的时候一定会踩：JSON 里是小写的 true false null，Python 里是大写的 True False None。还有键必须用双引号，单引号 JSON 不认。

[click] 现在看右边这段——这是第 1 次课我演示校验失败时你们会看到的真实响应。你们现在就要能读它。最外面是一个对象，里面 errors 这个键它的值是一个数组，数组里每个元素又是一个对象，每个对象有 field 和 msg 两个键。三层。

为什么要专门练这个？因为第十次课我们做前端表单，就是要把这个数组里的每一项，按 field 的值找到对应的输入框，把 msg 显示在它下面。你读不懂这个结构，那节课就没法做。
-->


---

# 0.4 终端、进程与项目工具链

<div class="text-xs opacity-55 -mt-1 mb-3">纯操作节，必须逐条跟做。直接预防第 1 次课的四类现场事故：工作目录不对、端口被占、虚拟环境没激活、<code>.env</code> 被误提交。</div>

<div grid="~ cols-2 gap-x-6 gap-y-3" class="mt-2 text-sm">

<div class="p-3 rounded border border-gray-400/25 bg-gray-500/5">
  <div class="font-bold mb-1">① 路径与工作目录</div>
  <div class="text-xs opacity-80 space-y-1">
    <div><code>pwd</code> 看我在哪 · <code>cd</code> 换地方 · <code>ls</code> 看有什么</div>
    <div>相对路径相对<b>当前工作目录</b>，不是文件所在目录</div>
    <div class="text-rose-600 dark:text-rose-400">必须在项目根启动：配置里 <code>env_file=".env"</code> 是相对路径，站错地方它<b>不报错</b>、默默用默认值</div>
  </div>
</div>

<div class="p-3 rounded border border-gray-400/25 bg-gray-500/5">
  <div class="font-bold mb-1">② 进程与端口</div>
  <div class="text-xs opacity-80 space-y-1">
    <div>启动服务 ＝ 起一个进程，一直占着终端；<kbd>Ctrl+C</kbd> 结束</div>
    <div>端口是进程<b>独占</b>的资源，一个端口同时只能被一个进程监听</div>
    <div>占用报错两个解法：换端口 / 找到旧进程杀掉</div>
  </div>
</div>

<div class="p-3 rounded border border-gray-400/25 bg-gray-500/5">
  <div class="font-bold mb-1">③ 环境变量与 <code>.env</code></div>
  <div class="text-xs opacity-80 space-y-1">
    <div>环境变量是操作系统给进程的一组键值对，程序启动时能读到</div>
    <div><code>.env</code> <b>不是 Python 语法</b>，只是约定格式的文本，由库去读</div>
    <div>为什么用它：密钥、数据库地址不能写进代码（第 1 次课 1.5.3 讲原理）</div>
  </div>
</div>

<div class="p-3 rounded border border-gray-400/25 bg-gray-500/5">
  <div class="font-bold mb-1">④ 包管理与虚拟环境</div>
  <div class="text-xs opacity-80 space-y-1">
    <div><code>uv sync</code> 按 <code>pyproject.toml</code> 装依赖；<code>uv run &lt;命令&gt;</code> 在项目环境里执行</div>
    <div>虚拟环境为什么存在：不同项目要不同版本的同一个库</div>
    <div>锁文件：让你的机器和我的机器装出<b>完全一样</b>的版本</div>
  </div>
</div>

<div class="p-3 rounded border border-gray-400/25 bg-gray-500/5">
  <div class="font-bold mb-1">⑤ Git 最小闭环</div>
  <div class="text-xs opacity-80 space-y-1">
    <div><code>git clone / status / add / commit -m / push</code></div>
    <div class="text-rose-600 dark:text-rose-400"><code>.gitignore</code> 必须含 <code>.env</code>：<b>提交过一次的密钥删不掉</b>，只能吊销重发</div>
  </div>
</div>

<div class="p-3 rounded border-2 border-teal-500/40 bg-teal-500/5">
  <div class="font-bold mb-1 text-teal-700 dark:text-teal-300">⑥ 三条会反复用到的命令</div>
  <div class="text-xs space-y-1">
    <div><code>curl -i URL</code> 看完整响应含头 <span class="opacity-60">· 第 1、8、11 次课</span></div>
    <div><code>grep -rn "词" 目录/</code> 全项目搜字符串 <span class="opacity-60">· 查架构违规</span></div>
    <div><code>python -m 包.模块</code> 以模块方式运行 <span class="opacity-60">· 第 0、1 次课</span></div>
  </div>
</div>

</div>

<!--
这一节全是操作，你们必须跟着做，光看没用。它直接预防第 1 次课教案里记录的四类现场事故。

先说工作目录。这个东西每年都有人栽。第一次课我们的配置文件里写的是 env_file 等于点 env，这是个相对路径，相对的是你启动命令时所在的目录，不是代码文件所在的目录。你在别的地方启动，它找不到这个文件，然后——注意——它不报错，它默默用默认值。你调试半小时才发现配置根本没生效。所以规则很简单：永远在项目根目录启动。

再说端口。端口是独占的，一个端口同一时刻只能一个进程听。

然后是 .env 这个文件。它不是 Python 代码，就是一个约定格式的文本。现在你只要记住一条铁律：.env 绝对不能提交到 Git。密钥进过一次 Git 历史，你就删不掉了，只能去把那个密钥吊销掉重新申请。这种事故每年都在真实公司里发生。

最后那三条命令——curl -i、grep -rn、python -m——会反复用到，尤其 python -m，下一节跟做你们就会撞到。
-->

---
layout: center
class: text-center
---

<div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-700 dark:text-amber-300 font-bold text-sm tracking-wide">
⏸ 暂停跟做 4 · 制造并解决端口占用
</div>

<div class="mt-6 max-w-3xl mx-auto text-left">

<div class="text-xs tracking-widest opacity-55 mb-1.5">要执行的命令</div>

```bash
# 终端 A 里 demo_server 还在跑，现在在终端 B 再起一个
uv run python snippets/lesson00/demo_server.py
```

<div class="text-xs tracking-widest opacity-55 mt-4 mb-1.5">预期看到</div>

```
OSError: [Errno 48] Address already in use
```

<div class="mt-3 p-3 rounded-lg bg-teal-500/8 border-l-4 border-teal-500 text-sm text-left">
<b>处理：</b>回终端 A 按 <kbd>Ctrl+C</kbd>，再在终端 B 启动。端口是独占的，看到这句就换端口或关掉旧的。
</div>

</div>

<div class="mt-5 inline-flex items-center gap-2 text-teal-700 dark:text-teal-300 font-bold">
✓ 做完再继续
</div>

<!--
跟着做一下，我让 demo_server 跑着，再起一个。看这个报错，Address already in use。

端口是独占的，一个端口同一时刻只能一个进程听。第一次课我们的服务用 8000 端口，你要是之前有个东西没关，就会看到这句话。看到就换端口或者关掉旧的。
-->

---
layout: center
class: text-center
---

<div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-700 dark:text-amber-300 font-bold text-sm tracking-wide">
⏸ 暂停跟做 5 · 第一次跑通 mini 程序
</div>

<div class="mt-1 max-w-4xl mx-auto text-left">
<div class="text-[11px] opacity-60 mb-1.5 text-center">必须在 <code>snippets/lesson00</code> 目录执行 · 这个程序贯穿讲一讲二，现在必须跑通</div>

```bash
cd snippets/lesson00
uv run python -m mini.cli add "写第一次课作业"
uv run python -m mini.cli add "看完课前课"
uv run python -m mini.cli list
uv run python -m mini.cli done 1
uv run python -m mini.cli list
uv run python -m mini.cli delete 99
```

<div class="text-xs tracking-widest opacity-55 mt-3 mb-1.5">预期看到（节选）</div>

```
INFO  mini.repo    READ todos.json -> 0 rows
INFO  mini.repo    INSERT -> id=1
已添加：[ ] #1 写第一次课作业
...
INFO  mini.repo    UPDATE id=1 done=True
已完成：[x] #1 写第一次课作业
...
错误[not_found]：待办 99 不存在        ← 这一行走的是 stderr（退出码 4）
```

</div>

<div class="mt-4 inline-flex items-center gap-2 text-teal-700 dark:text-teal-300 font-bold">
✓ 做完再继续
</div>

<!--
最后跑通我们的 mini 程序。这个程序你们接下来两讲会反复见到，而且第一次课我还会提它，所以现在必须跑通。

看这些 INFO 开头的行——这是数据访问日志，它告诉你这次操作读了几次、写了几次。你数一下 add 那次：读一次、写一次。这个"数一下"的习惯，第六课能救你的命。

最后看那条 delete 99，它返回了一个错误，而且走的是 stderr 不是 stdout，退出码是 4 不是 0。一个正经的命令行程序要这样。这一点跟第一次课的"错误必须用正确的状态码"是同一回事。
-->

---
layout: center
class: text-center
---

<div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-700 dark:text-amber-300 font-bold text-sm tracking-wide">
⏸ 暂停跟做 6 · 体会「工作目录」这个坑
</div>

<div class="mt-6 max-w-3xl mx-auto text-left">

<div class="text-xs tracking-widest opacity-55 mb-1.5">要执行的命令</div>

```bash
cd ..                                   # 故意退到上一层
uv run python -m mini.cli list          # 观察发生什么
```

<div class="text-xs tracking-widest opacity-55 mt-4 mb-1.5">预期看到</div>

```
ModuleNotFoundError: No module named 'mini'
```

<div class="mt-3 p-3 rounded-lg bg-amber-500/10 border-l-4 border-amber-500 text-sm text-left">
不是代码坏了，是<b>你站错了地方</b>。为什么？<span class="font-bold">0.12 会解释</span>——先记住这个现象。
</div>

</div>

<div class="mt-5 inline-flex items-center gap-2 text-teal-700 dark:text-teal-300 font-bold">
✓ 做完再继续
</div>

<!--
再做最后一个实验，体会工作目录这个坑。你 cd 到上一层，再跑同样的命令。

看，ModuleNotFoundError，找不到 mini 了。注意——这不是代码的问题，是你站错了地方。为什么会这样？0.12 那一节我会解释 import 到底从哪儿开始找文件。今天你先记住这个现象。
-->


---

# 0.5 报错怎么读

<div class="text-xs opacity-55 -mt-1 mb-3">被严重低估的技能。零基础的第一反应是<b class="text-rose-600 dark:text-rose-400">滚到最上面看</b>，正确读法是<b class="text-teal-700 dark:text-teal-300">从最下面往上看</b>。</div>

<div grid="~ cols-[1fr_1.15fr] gap-6" class="mt-2">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">读 traceback 的三步法</div>
<div class="space-y-2.5 text-sm">
  <div class="flex items-start gap-3 p-3 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
    <span class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">1</span>
    <span>看<b>最后一行</b>：异常类型＋消息 → 告诉你「发生了什么」</span>
  </div>
  <div class="flex items-start gap-3 p-3 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
    <span class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">2</span>
    <span>从下往上找<b>第一个属于你自己代码的文件</b> → 告诉你「从哪儿开始查」</span>
  </div>
  <div class="flex items-start gap-3 p-3 rounded-lg border border-gray-400/25 bg-gray-500/5 opacity-75">
    <span class="w-6 h-6 rounded-full bg-gray-500/20 text-xs flex items-center justify-center font-bold shrink-0">3</span>
    <span>中间那些库文件的帧<b>先跳过</b>——它们通常只是传递者，不是原因</span>
  </div>
</div>
</div>

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">板书 · 阅读顺序</div>
<div class="rounded-lg overflow-hidden border border-gray-400/25 font-mono text-[11px] leading-relaxed">
  <div class="px-3 py-1 bg-gray-500/8 opacity-45">Traceback (most recent call last):</div>
  <div class="px-3 py-1 bg-gray-500/8 opacity-45">　File ".../fastapi/routing.py", line 812　<span class="opacity-60">← 库帧，跳过</span></div>
  <div class="px-3 py-1 bg-gray-500/8 opacity-45">　File ".../starlette/middleware.py", line 88　<span class="opacity-60">← 库帧，跳过</span></div>
  <div class="relative px-3 py-1 bg-teal-500/12 border-l-4 border-teal-500 font-bold">　File "app/services/post_service.py", line 18
    <span class="absolute right-2 top-0.5 text-[10px] px-1.5 py-0.5 rounded bg-teal-500/20 text-teal-700 dark:text-teal-300">② 再找这里 ↑</span>
  </div>
  <div class="px-3 py-1 bg-teal-500/8 border-l-4 border-teal-500/50">　　1 / 0</div>
  <div class="relative px-3 py-1.5 bg-rose-500/15 border-l-4 border-rose-500 font-bold">ZeroDivisionError: division by zero
    <span class="absolute right-2 top-1 text-[10px] px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-700 dark:text-rose-300">① 先看这里</span>
  </div>
</div>
<div class="mt-2 text-xs opacity-75">最后一行说「除零」，往上第一个自己的文件是 <code>post_service.py:18</code> → <b class="text-teal-700 dark:text-teal-300">错误产生在服务层</b>。</div>
</div>

</div>

<!--
读报错这件事，我要专门花十分钟，因为几乎所有人第一次都读错方向。

你看到一大段红字，本能反应是滚到最上面开始读。错的。从最下面开始读。

最后一行告诉你发生了什么——除零了、找不到模块了、字段缺了。这是结论。然后你从下往上找，找到第一个是你自己写的文件。中间那些一堆库里的文件，它们绝大多数情况只是传递者，不是原因，先跳过。

三步：看最后一行，往上找自己的文件，然后去那一行。就这样。你看右边这段，最后一行 ZeroDivisionError，往上第一个自己的文件是 post_service.py 第 18 行——错误产生在服务层。说得出来，你就已经在做"定位"这件事了，而定位是第十六课的正题。
-->

---

# 0.5 三种最常见报错的形状

<div class="mt-4 text-sm">

<div class="flex gap-4 pb-2 mb-1 border-b border-gray-400/30 text-xs tracking-wide opacity-60">
  <div class="w-72 shrink-0">报错</div>
  <div class="flex-1">通常的真实原因</div>
  <div class="w-56 shrink-0">先检查什么</div>
</div>

<div v-click="1" class="flex gap-4 py-3 border-b border-gray-400/15 items-center">
  <div class="w-72 shrink-0 font-mono text-xs text-rose-600 dark:text-rose-400">ModuleNotFoundError:<br>No module named 'x'</div>
  <div class="flex-1">依赖没装 / 工作目录不对 / 少了 <code class="text-xs">__init__.py</code></div>
  <div class="w-56 shrink-0 text-xs opacity-80">我在哪个目录？<br>我用 <code>uv run</code> 了吗？</div>
</div>

<div v-click="2" class="flex gap-4 py-3 border-b border-gray-400/15 items-center">
  <div class="w-72 shrink-0 font-mono text-xs text-rose-600 dark:text-rose-400">ImportError: cannot import name 'y' from partially initialized module</div>
  <div class="flex-1"><b class="text-amber-600 dark:text-amber-400">循环导入</b>（0.12 现场制造）</div>
  <div class="w-56 shrink-0 text-xs opacity-80">两个文件是不是<br>互相 import 了？</div>
</div>

<div v-click="3" class="flex gap-4 py-3 border-b border-gray-400/15 items-center">
  <div class="w-72 shrink-0 font-mono text-xs text-rose-600 dark:text-rose-400">ValidationError:<br>field required</div>
  <div class="flex-1">配置或请求数据缺字段</div>
  <div class="w-56 shrink-0 text-xs opacity-80">看它说的是哪个字段<br>（第 1 次课开场就见）</div>
</div>

</div>

<div v-click="4" class="mt-5 p-3.5 rounded-lg bg-sky-500/8 border-l-4 border-sky-500 text-sm">
<span class="font-bold text-sky-700 dark:text-sky-300">对应第 1 次课：</span>我会故意在服务层插一行 <code class="text-xs">1 / 0</code>，让你看到「栈只进日志、不进响应体」。那时你要能一眼读出：错误产生在 <code class="text-xs">post_service.py</code>，<b>在服务层</b>。
</div>

<!--
这三种报错你们会反复见到，我把形状和真实原因列出来。

[click] 第一种 ModuleNotFoundError，找不到模块。十有八九不是代码问题，是你站错了目录，或者没用 uv run。

[click] 第二种 ImportError，partially initialized module，后面还跟着 circular import。这是循环导入，0.12 那一节我会让你们亲手把 mini 弄坏，制造出这个报错。

[click] 第三种 ValidationError，field required，配置或者请求数据缺字段。第 1 次课开场你们就会见到。

[click] 这一节直接支撑第 1 次课的 500 演示，以及第 16 次课的定位四步法。第一次课我会故意写一个除零错误，你们要能一眼说出"这是服务层的问题"。
-->

---
layout: center
class: text-center
---

<div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-700 dark:text-amber-300 font-bold text-sm tracking-wide">
⏸ 暂停跟做 7 · 读三段真实报错
</div>

<div class="mt-6 max-w-3xl mx-auto text-left">

<div class="p-4 rounded-lg bg-gray-500/8 text-sm">
打开 <code class="text-xs">snippets/lesson00/traceback_samples.md</code>，里面有<b>三段真实报错</b>。每段回答两个问题：
<div class="mt-3 grid grid-cols-2 gap-3">
  <div class="p-2.5 rounded border border-teal-500/30 bg-teal-500/5 text-center font-bold text-teal-700 dark:text-teal-300">① 哪个文件、哪一行？</div>
  <div class="p-2.5 rounded border border-teal-500/30 bg-teal-500/5 text-center font-bold text-teal-700 dark:text-teal-300">② 我该先去改什么？</div>
</div>
</div>

<div class="mt-4 p-3 rounded-lg bg-amber-500/10 border-l-4 border-amber-500 text-sm text-left">
提示：用刚学的<b>三步法</b>——先看最后一行，再从下往上找第一个自己的文件，中间库帧跳过。
</div>

</div>

<div class="mt-5 inline-flex items-center gap-2 text-teal-700 dark:text-teal-300 font-bold">
✓ 做完再继续
</div>

<!--
现在你们自己读三段，我给了文件，每段回答两个问题：哪个文件哪一行，我该先改什么。用刚学的三步法。

（跟做 7，留时间）三段的答案：第一段不是代码问题，是工作目录不对或没用 -m；第二段是循环导入，service.py 那句 import 要删掉；第三段是 repo.py 拼错了 title，注意错误产生在仓储层，但报错是从 cli 一路传上来的——这就是异常穿层，0.9 会讲。
-->

---

# 0.6 调试器：为什么不用 print

<div class="text-xs opacity-55 -mt-1 mb-3">本讲<b class="text-amber-600 dark:text-amber-400">高光</b>，25 分钟不可压缩。先解决态度问题——否则学完你还是会退回去用 print。</div>

<div grid="~ cols-2 gap-6" class="mt-2">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">print 调试为什么不行</div>
<div class="space-y-2.5 text-sm">
  <div class="p-3 rounded-lg border border-rose-500/30 bg-rose-500/5">
    <b class="text-rose-600 dark:text-rose-400">只能看到你事先想到</b>要看的那一个值——可 bug 恰恰出在你<b>没想到</b>的地方
  </div>
  <div class="p-3 rounded-lg border border-rose-500/30 bg-rose-500/5">
    要改代码、要记得删；删漏一行就跟着上线了
  </div>
  <div class="p-3 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
    <b class="text-teal-700 dark:text-teal-300">断点停下的那一刻</b>：当前所有变量、整条调用链，全摊在你面前——<b>包括你没想到要看的</b>
  </div>
</div>
</div>

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">VS Code 五个动作（就这五个）</div>
<div class="rounded-lg overflow-hidden border border-gray-400/25 text-sm">
  <div class="flex gap-3 px-3 py-1.5 bg-gray-500/10 text-xs tracking-wide opacity-60">
    <div class="w-28 shrink-0">动作</div><div class="flex-1">干什么</div>
  </div>
  <div class="flex gap-3 px-3 py-2 border-t border-gray-400/15">
    <div class="w-28 shrink-0 font-bold">行号左边点一下</div><div class="flex-1 opacity-85">设断点</div>
  </div>
  <div class="flex gap-3 px-3 py-2 border-t border-gray-400/15">
    <div class="w-28 shrink-0 font-bold"><kbd>F5</kbd></div><div class="flex-1 opacity-85">启动调试，跑到断点处停住</div>
  </div>
  <div class="flex gap-3 px-3 py-2 border-t border-gray-400/15">
    <div class="w-28 shrink-0 font-bold"><kbd>F10</kbd> 单步跳过</div><div class="flex-1 opacity-85">执行这行，<b>不</b>进函数内部</div>
  </div>
  <div class="flex gap-3 px-3 py-2 border-t border-gray-400/15 bg-teal-500/5">
    <div class="w-28 shrink-0 font-bold"><kbd>F11</kbd> 单步进入</div><div class="flex-1">执行这行，<b class="text-teal-700 dark:text-teal-300">进入被调用的函数里面</b></div>
  </div>
  <div class="flex gap-3 px-3 py-2 border-t border-gray-400/15">
    <div class="w-28 shrink-0 font-bold"><kbd>F5</kbd> 继续</div><div class="flex-1 opacity-85">跑到下一个断点或结束</div>
  </div>
</div>
<div class="mt-2 text-xs opacity-70"><kbd>F10</kbd> vs <kbd>F11</kbd> 记牢：F10「这行执行掉别带我进去」，F11「带我进这个函数里面看」。</div>
</div>

</div>

<!--
这二十五分钟是这一讲最重要的，我建议你们看两遍。

先回答一个问题：为什么不用 print 调试？因为 print 只能看到你事先想到要看的那个值。但 bug 之所以是 bug，就是因为出在你没想到的地方。断点停下那一刻，所有变量、整条调用链，全摊在你眼前。

好，五个动作：点行号设断点，F5 启动，F10 单步跳过，F11 单步进入，F5 继续。就这五个。F10 和 F11 的区别要记牢：F10 是「这行执行掉，别带我进去」，F11 是「带我进这个函数里面看」。
-->

---

# 0.6 四个面板 ＋「栈」是什么

<div grid="~ cols-[0.9fr_1.1fr] gap-6" class="mt-5">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">停下后看四个面板</div>
<div class="space-y-2 text-sm">
  <div class="p-2.5 rounded border border-gray-400/25 bg-gray-500/5"><b>Variables</b><span class="opacity-75">　此刻所有变量的值</span></div>
  <div class="p-2.5 rounded border-2 border-amber-500/50 bg-amber-500/8"><b class="text-amber-700 dark:text-amber-300">Call Stack</b><span class="opacity-80">　我在哪、被谁调进来的</span><span class="ml-1.5 text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-700 dark:text-amber-300 font-bold align-middle">本节重点</span></div>
  <div class="p-2.5 rounded border border-gray-400/25 bg-gray-500/5"><b>Watch</b><span class="opacity-75">　盯住某个表达式</span></div>
  <div class="p-2.5 rounded border border-gray-400/25 bg-gray-500/5"><b>Debug Console</b><span class="opacity-75">　在断点处直接执行代码试试</span></div>
</div>
</div>

<div v-click>
<div class="text-xs tracking-widest opacity-60 mb-2">今天最重要的概念：栈</div>
<div class="space-y-2.5 text-sm">
  <div class="p-3 rounded-lg bg-gray-500/8">函数被<b class="text-teal-700 dark:text-teal-300">调用</b>时，一个「帧」被<b>压</b>到栈上；函数<b class="text-rose-600 dark:text-rose-400">返回</b>时，这个帧被<b>弹</b>掉。</div>
  <div class="p-3 rounded-lg bg-gray-500/8"><b>栈底</b>是程序入口，<b class="text-amber-600 dark:text-amber-400">栈顶是你现在停的位置</b>。</div>
  <div class="p-3 rounded-lg border-2 border-teal-500/40 bg-teal-500/5 font-bold text-center">读调用栈 ＝ 回答两个问题：<br>我在哪？我是怎么来的？</div>
</div>
</div>

</div>

<!--
停在断点后，看四个面板。Variables 是此刻所有变量的值；Call Stack 是重点——我在哪、我是被谁调进来的；Watch 盯住某个表达式；Debug Console 可以在断点处直接敲代码试试。

[click] 现在讲今天最重要的概念——栈。函数被调用时，一个「帧」被压到栈上；函数返回时，这个帧被弹掉。栈底是程序入口，栈顶是你现在停的位置。所以读调用栈就是在回答两个问题：我在哪？我是怎么来的？就这两个。下一页我用一个最干净的例子，把压栈弹栈一步步放给你看。
-->

---
clicks: 5
---

# 0.6 高光 · 三层嵌套的压栈弹栈

<div class="text-xs opacity-55 -mt-1 mb-1">跟着点 <b>5</b> 下，盯住右边栈的高度怎么变。断点打在 <code>return total</code>。</div>

<div grid="~ cols-[0.85fr_1.15fr] gap-6" class="mt-1">

<div>

<<< @/snippets/lesson00/stack_demo.py#levels {lines:true}

<div class="mt-2 text-xs opacity-70">level1(3) → level2(3×10=<b>30</b>) → level3(30+1=<b>31</b>)，total=31×2=<b class="text-teal-700 dark:text-teal-300">62</b></div>
</div>

<div>
<div class="flex items-center justify-between mb-2">
  <div class="text-xs tracking-widest opacity-60">调用栈（栈顶在上）</div>
  <div class="text-xs font-bold px-2 py-0.5 rounded bg-gray-500/12">栈高 {{ $clicks >= 5 ? 1 : $clicks }}</div>
</div>
<div class="flex flex-col gap-1.5 justify-end min-h-[196px]">
  <div v-show="$clicks === 4" class="px-3 py-2 rounded-md border-2 border-amber-500/60 bg-amber-500/10 font-mono text-[13px] flex items-center gap-2">
    <span class="font-bold">level3</span><span class="opacity-70">n=31, total=62</span>
    <span class="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-amber-500/25 text-amber-700 dark:text-amber-300 font-bold font-sans">栈顶 · 断点命中</span>
  </div>
  <div v-show="$clicks === 3 || $clicks === 4" class="px-3 py-2 rounded-md border border-teal-500/50 bg-teal-500/8 font-mono text-[13px] flex items-center gap-2">
    <span class="font-bold">level2</span><span class="opacity-70">n=30</span>
  </div>
  <div v-show="$clicks >= 2 && $clicks <= 4" class="px-3 py-2 rounded-md border border-sky-500/50 bg-sky-500/8 font-mono text-[13px] flex items-center gap-2">
    <span class="font-bold">level1</span><span class="opacity-70">n=3</span>
  </div>
  <div v-show="$clicks >= 1" class="px-3 py-2 rounded-md border border-gray-400/40 bg-gray-500/8 font-mono text-[13px] flex items-center gap-2">
    <span class="font-bold">&lt;module&gt;</span><span class="opacity-70">程序入口</span>
    <span class="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-gray-500/15 opacity-70 font-sans">栈底</span>
  </div>
</div>
<div v-show="$clicks >= 5" class="mt-2 p-2.5 rounded-lg bg-teal-500/10 border-l-4 border-teal-500 text-sm">
  <b class="text-teal-700 dark:text-teal-300">level3 返回 62 ↑</b> 帧弹出交回 level2；再逐层弹出，栈回到只剩 <code class="text-xs">&lt;module&gt;</code>。
</div>
<div class="mt-2 min-h-[42px] text-sm leading-snug">
  <span v-show="$clicks === 0" class="opacity-60">点一下开始：程序从入口 <code>&lt;module&gt;</code> 启动。</span>
  <span v-show="$clicks === 1"><b>第 1 步</b> · <code>&lt;module&gt;</code> 入栈（栈底＝入口），调用 level1(3)。</span>
  <span v-show="$clicks === 2"><b>第 2 步</b> · level1 帧压上，n=3；它调用 level2(3×10)。</span>
  <span v-show="$clicks === 3"><b>第 3 步</b> · level2 帧压上，n=30；它调用 level3(30+1)。</span>
  <span v-show="$clicks === 4"><b>第 4 步</b> · level3 帧压上，n=31，<b class="text-amber-600 dark:text-amber-400">断点命中，停在栈顶</b>（栈高 4）。</span>
  <span v-show="$clicks === 5"><b>第 5 步</b> · level3 弹出返回 62，逐层弹回，只剩 <code>&lt;module&gt;</code>。</span>
</div>
</div>

</div>

<!--
现在讲今天最重要的概念——栈。我用一个跟业务毫无关系的例子，就三层函数，把它讲干净。（分步演示，点五下）

[click] 程序从入口开始，<module> 这一帧在栈底，它调用 level1，level1 这一帧被压到栈上。

[click] level1 里 n 是 3，它调用 level2，传进去的是 n 乘 10，也就是 30。level2 帧压上去。

[click] level2 里 n 是 30，它调用 level3，传进去 n 加 1，也就是 31。level3 帧压上去。

[click] 现在栈上有四层，栈高 4。断点在 level3 里，所以我停在栈顶。往下看，就能知道我是怎么被一层层调进来的。

[click] 然后 level3 算出 total 等于 62，返回，它这一帧被弹掉，62 交给 level2；level2 再返回，弹掉……逐层弹回去，最后栈回到只剩 <module>。所以调用栈回答两个问题：我在哪？我是怎么来的？
-->

---
layout: center
class: text-center
---

<div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-700 dark:text-amber-300 font-bold text-sm tracking-wide">
⏸ 暂停跟做 8 · 亲手看一次调用栈
</div>

<div class="mt-6 max-w-3xl mx-auto text-left">

<div class="text-xs tracking-widest opacity-55 mb-1.5">怎么做</div>
<div class="p-4 rounded-lg bg-gray-500/8 text-sm space-y-1.5">
  <div>① 打开 <code class="text-xs">snippets/lesson00/stack_demo.py</code>，在 <code class="text-xs">return total</code> 那行<b>行号左边点一下</b>设断点</div>
  <div>② 按 <kbd>F5</kbd> 启动调试（选 <span class="opacity-70">Python File</span>）</div>
  <div>③ 停在断点后看 <b>Call Stack</b> 面板，<b>点击每一帧</b>，观察 <b>Variables</b> 面板跟着变</div>
</div>

<div class="text-xs tracking-widest opacity-55 mt-4 mb-1.5">回答这个问题</div>
<div class="p-4 rounded-lg border-2 border-teal-500/40 bg-teal-500/5 text-sm">
  <code class="text-xs font-bold">level2</code> 那一帧里，<code class="text-xs font-bold">n</code> 等于几？<b class="text-teal-700 dark:text-teal-300">为什么不是 3？</b>
</div>

</div>

<div class="mt-6 inline-flex items-center gap-2 text-teal-700 dark:text-teal-300 font-bold">
✓ 做完再继续
</div>

<!--
（跟做 8）你们自己试一下，在 return total 打断点，F5 启动，点每一帧，看变量面板跟着变。

答案是：level2 那一帧里 n 是 30，不是 3——因为 level1 传进去的是 n 乘 10。每一帧有自己独立的变量，这也正是「帧」这个说法的意思。你能亲眼看到这个 30，比你听我讲十遍都管用。
-->

---

# 0.6 切到 mini：栈帧的层次就是分层的层次

<div class="text-xs opacity-55 -mt-1 mb-2">在 <code>mini/repo.py</code> 的 <code>get()</code> 首行打断点，跑 <code>uv run python -m mini.cli done 1</code>，命中时的栈：</div>

<CallStackLayers />

<div v-click class="mt-5 p-3.5 rounded-lg bg-teal-500/8 border-l-4 border-teal-500 text-sm">
<b class="text-teal-700 dark:text-teal-300">对照着看：栈的层次，就是右边分层的层次。</b>这句话你现在可能觉得平淡，但它是第 1 次课的核心。
</div>

<div v-click="2" class="mt-3 p-3 rounded-lg bg-sky-500/8 border-l-4 border-sky-500 text-sm">
<span class="font-bold text-sky-700 dark:text-sky-300">对应第 1 次课：</span>1.4.4 高光页的栈有<b>八层</b>——<code class="text-xs">uvicorn → FastAPI → 中间件 → 路由匹配 → 校验 → 路由函数 → 服务层 → 仓储层</code>。比 mini 多的<b class="text-amber-600 dark:text-amber-400">前五层全是框架替你做的事</b>。今天先在没框架的干净环境把「栈＝分层」看明白，第 1 次课就能把 6 分钟全花在「框架多做了什么」上。
</div>

<!--
现在换到 mini 程序，这一段是重点。我在 repo 的 get 方法里打断点，跑一个 done 命令。看栈：最上面 repo.get，下面 service.get_todo，再下面 service.finish_todo，再下面 cli 的 main。

[click] 你们对照右边那张四个方框的图看——栈的层次，就是我画的分层的层次。

[click] 这句话你们现在可能觉得平淡，但它是第一次课的核心。第一次课我会在 FastAPI 里做同样的事，那时候栈上会有八层，前面五层全是框架替你干的活。今天你先在没有框架的干净环境里把这件事看明白，下周你就能把注意力全放在「框架到底多做了什么」上面。
-->
