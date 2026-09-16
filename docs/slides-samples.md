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

<img src="/images/ch00/class-qr-code.png" alt="课程 QQ 群二维码 · 458839515" class="h-80 rounded shadow-lg" />

<div class="mt-4 flex items-baseline gap-2">
  <span class="opacity-50 text-sm">课程 QQ 群</span>
  <span class="font-mono font-bold text-lg tracking-wide">458839515</span>
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
layout: center
class: text-center
---

# 归结起来，只有一个结论

<div class="mt-8 mb-6 p-6 rounded-lg border-2 border-rose-500/40 bg-rose-500/5 max-w-4xl mx-auto">

<div class="text-2xl font-bold leading-relaxed">
AI 的代码生成速度<span class="text-rose-600 dark:text-rose-400">远胜</span>人类，<br>代码质量也已<span class="text-rose-600 dark:text-rose-400">超过</span>许多初级甚至中级开发者。
</div>

<div class="mt-3 text-lg opacity-80">
代码生成不再是人类的比较优势。
</div>

</div>

<div v-click class="p-5 rounded-lg border-2 border-teal-500/40 bg-teal-500/5 max-w-4xl mx-auto">

<div class="text-xs tracking-widest opacity-60 mb-2">边　界</div>

<div class="text-xl leading-relaxed">
AI 接管的是「<span class="font-bold">把方案变成代码</span>」，<br>
人该练的是「<span class="font-bold text-teal-700 dark:text-teal-300">把问题变成方案</span>」
</div>

</div>

<!--
从这些事里我只提一个结论：在代码生成这件事上，AI 已经领先——速度远胜人类，代码质量也超过了许多初级甚至中级开发者。这一点上，我不跟你们绕弯子。

[click] 但请你们把第二句话也记住：被 AI 接管的，是"把方案变成代码"这一整段执行工作——从生成到测试、修复；而"把问题变成方案"，才是你们要练的东西。

这两句话中间的差别，就是我今天要讲的全部东西。如果你只记住第一句，你会得出"这门课没用"的结论；把第二句也想清楚，你会得出完全相反的结论。
-->

---

# 「复现」归零，「理解与判断」升值

<div grid="~ cols-2 gap-6" class="mt-6">

<div class="p-5 rounded-lg border border-rose-500/30 bg-rose-500/5 flex flex-col">
  <div class="text-xs tracking-widest opacity-60 mb-3">表述一</div>
  <div class="text-lg leading-relaxed flex-1">
    能背出红黑树 <code>rotateLeft</code> 的 12 行实现
  </div>
  <div class="mt-4 pt-3 border-t border-rose-500/20 text-3xl font-bold text-rose-600 dark:text-rose-400">
    归零
  </div>
</div>

<div v-click class="p-5 rounded-lg border border-teal-500/30 bg-teal-500/5 flex flex-col">
  <div class="text-xs tracking-widest opacity-60 mb-3">表述二</div>
  <div class="text-lg leading-relaxed flex-1">
    知道存在一类结构可在 <span class="font-bold">O(log n)</span> 内维持有序性，并知道它与<span class="font-bold">跳表、B+ 树、哈希表</span>在什么场景下互相替代
  </div>
  <div class="mt-4 pt-3 border-t border-teal-500/20 text-3xl font-bold text-teal-600 dark:text-teal-400">
    升值
  </div>
</div>

</div>

<div v-click class="mt-6 text-center text-lg">

这两条之间的差别，就是<span v-mark.underline.orange="3">本课程内容重构的边界线</span>。

</div>

<!--
刚才说的那条边界，用红黑树看得更清楚——归零的是"复现"，不是红黑树本身。

你看这两句话。第一句：能背出 rotateLeft 那十二行——归零，彻底归零。

[click] 第二句：你知道有这么一类结构，能用 O(log n) 的代价维持有序性，而且你知道它跟跳表、跟 B+ 树、跟哈希表在什么情况下可以互相换——这一句，升值。

[click] 这两句话看起来讲的是同一个东西，其实差别巨大。这条界线，就是我这学期重新排课程内容的依据。

最后补一个口径：归零的是"把复现当本事"；"当练法"，复现没有归零——亲手实现一遍，正是理解与判断的地基。这点澄清二会展开。
-->

---

# 五条理由，说明「理解与判断」为何升值

<div class="mt-8 space-y-3">

<div v-click="1" class="flex items-center gap-5 p-3.5 rounded-lg border border-teal-500/25 bg-teal-500/5">
  <div class="text-2xl font-bold text-teal-600 dark:text-teal-400 w-8">①</div>
  <div class="flex-1"><span class="font-bold">技术史规律</span>　抽象层的知识存亡机制</div>
</div>

<div v-click="2" class="flex items-center gap-5 p-3.5 rounded-lg border border-teal-500/25 bg-teal-500/5">
  <div class="text-2xl font-bold text-teal-600 dark:text-teal-400 w-8">②</div>
  <div class="flex-1"><span class="font-bold">表达精度</span>　概念词汇是与 AI 沟通的接口</div>
</div>

<div v-click="3" class="flex items-center gap-5 p-3.5 rounded-lg border border-teal-500/25 bg-teal-500/5">
  <div class="text-2xl font-bold text-teal-600 dark:text-teal-400 w-8">③</div>
  <div class="flex-1"><span class="font-bold">判断与取舍</span>　AI 的失效模式是「正确但不合适」</div>
</div>

<div v-click="4" class="flex items-center gap-5 p-3.5 rounded-lg border border-teal-500/25 bg-teal-500/5">
  <div class="text-2xl font-bold text-teal-600 dark:text-teal-400 w-8">④</div>
  <div class="flex-1"><span class="font-bold">决策杠杆</span>　产出规模放大骨架决策的代价</div>
</div>

<div v-click="5" class="flex items-center gap-5 p-3.5 rounded-lg border border-teal-500/25 bg-teal-500/5">
  <div class="text-2xl font-bold text-teal-600 dark:text-teal-400 w-8">⑤</div>
  <div class="flex-1"><span class="font-bold">领域事实</span>　AI 系统本身由数据结构构成</div>
</div>

</div>

<!--
接下来我用五条理由来论证。

[click] 第一条是技术史的规律，
[click] 第二条是你怎么跟 AI 说话，
[click] 第三条是我自己项目里踩的一个坑，
[click] 第四条讲为什么 AI 写得越快人的判断越贵，
[click] 第五条讲 AI 系统本身是用什么搭起来的。

走完这五条，我们再回来谈这学期到底怎么上。
-->

---

# 真问题不是「AI 能力有多强？」

<div class="mt-8 max-w-4xl mx-auto">

<div class="p-4 rounded-lg border border-gray-400/25 bg-gray-500/5 opacity-55">
  <div class="text-xs tracking-widest mb-2">不是问题</div>
  <div class="text-xl line-through decoration-2">AI 的能力到底有多强？</div>
  <div class="text-xs mt-2">——它在快速进化：Agent 能力约每 7 个月翻一番（METR · Nature 报道）</div>
</div>

<div class="text-center text-2xl my-4 opacity-30">↓</div>

<div v-click class="p-6 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-3">真问题（一个技术史问题）</div>
  <div class="text-2xl font-bold leading-relaxed">
    抽象层每上升一次，都会消灭一批知识。<br>
    <span class="text-teal-700 dark:text-teal-300">哪些会被吃掉？哪些不会？</span>
  </div>
</div>

<div v-click class="mt-5 text-center text-sm opacity-75">
这个问题有答案——因为它在我们这个专业里，已经发生过至少<span class="font-bold">三次</span>。
</div>

</div>

<UnitNav :active="1" />

<!--
现在网上讨论 AI，绝大多数在争"AI 到底强不强"。我认为这是个假问题——答案的保质期太短。2025 年 3 月，Nature 报道了非营利机构 METR 的"智能体摩尔定律"：Agent 能力大约每 7 个月翻一番。你今天给出的任何答案，几个月后都会过时。

[click] 真问题是一个技术史问题：**抽象层每往上升一次，都会消灭一批知识。哪些会被吃掉，哪些不会？**

[click] 这个问题有答案，因为这件事在我们这个专业里已经发生过至少三次了，而且三次的答案惊人地一致。
-->

---

# 三次历史跃迁的对照

<div class="mt-5 text-sm">

<div class="flex gap-4 pb-2 mb-1 border-b border-gray-400/30 text-xs tracking-wide opacity-60">
  <div class="w-52 shrink-0">抽象层跃迁</div>
  <div class="flex-1">被吃掉的知识</div>
  <div class="flex-1">存活并升值的知识</div>
</div>

<div v-click="1" class="flex gap-4 py-2.5 border-b border-gray-400/15">
  <div class="w-52 shrink-0 font-bold">汇编 → C<span class="opacity-50 font-normal">（编译器）</span></div>
  <div class="flex-1 text-rose-600 dark:text-rose-400">手写汇编、手工分配寄存器</div>
  <div class="flex-1 text-teal-700 dark:text-teal-300">内存布局、cache 局部性、指令代价</div>
</div>

<div v-click="2" class="flex gap-4 py-2.5 border-b border-gray-400/15">
  <div class="w-52 shrink-0 font-bold">手动内存 → GC</div>
  <div class="flex-1 text-rose-600 dark:text-rose-400"><code>malloc/free</code> 配对管理</div>
  <div class="flex-1 text-teal-700 dark:text-teal-300">对象生命周期、GC 停顿调优、泄漏定位</div>
</div>

<div v-click="3" class="flex gap-4 py-2.5 border-b border-gray-400/15">
  <div class="w-52 shrink-0 font-bold">裸写 → 框架</div>
  <div class="flex-1 text-rose-600 dark:text-rose-400">样板代码、胶水代码</div>
  <div class="flex-1 text-teal-700 dark:text-teal-300">数据流边界、状态归属、一致性模型</div>
</div>

<div v-click="4" class="flex gap-4 py-3 mt-1 rounded bg-amber-500/10 border border-amber-500/30">
  <div class="w-52 shrink-0 font-bold pl-2">人写 → AI 生成</div>
  <div class="flex-1 text-3xl font-bold text-amber-600 dark:text-amber-400 leading-none">？</div>
  <div class="flex-1 text-3xl font-bold text-amber-600 dark:text-amber-400 leading-none">？</div>
</div>

</div>

<div v-click="5" class="mt-4 text-center text-sm opacity-70">
每一次跃迁，都是<span class="text-rose-600 dark:text-rose-400 font-bold">一批知识死</span>、<span class="text-teal-700 dark:text-teal-300 font-bold">一批知识变贵</span>
</div>

<UnitNav :active="1" />

<!--
我们一行一行看。

[click] 第一行，编译器。编译器出来之后，绝大多数人不再手写汇编了。今天没人会因为不会手写汇编而找不到工作。**但是**——理解内存布局、理解 cache 局部性、理解一条指令要花多少代价的人，价值反而上去了。为什么？你们想一下：所有的性能问题、所有的并发 bug、所有的内存故障，恰好都发生在抽象漏水的地方。抽象没漏的时候你不用懂，抽象一漏，只有懂的人能救。

[click] 第二行，垃圾回收。GC 出来之后，你不用再手动 free 了，malloc/free 配对这件事从大部分人的日常里消失了。但是 GC 停顿怎么调？内存为什么还在涨？这个对象什么时候该断引用？GC 不替你想，它只在你想错的时候让你的服务卡住两秒。

[click] 第三行，框架。框架出来之后，样板代码没了，胶水代码没了。但"这个状态该归哪个模块""这两个模块之间数据流的边界在哪"——框架给不了你答案。

[click] 现在看第四行。人写代码 → AI 生成代码。两个问号。这是我们今天要填的空。
-->

---
layout: center
class: text-center
---

# 三次跃迁，一条规律

<div class="mt-10 space-y-5 max-w-3xl mx-auto">

<div class="p-6 rounded-lg border-2 border-rose-500/35 bg-rose-500/5">
  <div class="text-3xl font-bold">
    抽象<span class="text-rose-600 dark:text-rose-400">封得住</span>的地方，知识会<span class="text-rose-600 dark:text-rose-400">死</span>。
  </div>
</div>

<div v-click class="p-6 rounded-lg border-2 border-teal-500/35 bg-teal-500/5">
  <div class="text-3xl font-bold">
    抽象<span class="text-teal-600 dark:text-teal-400">漏水</span>的地方，知识不死，<br>而且<span class="text-teal-600 dark:text-teal-400">变贵</span>。
  </div>
</div>

</div>

<div v-click class="mt-5 text-sm opacity-80">
例：<span class="font-mono">0.1 + 0.2 = 0.30000000000000004</span>——连"数字"这层最基础的抽象，也在漏水。
</div>

<div v-click class="mt-4 text-sm opacity-70">
所以要填第四行那两个问号，只需回答一件事：<span class="font-bold">AI 这层抽象，漏不漏？漏在哪儿？</span>
</div>

<UnitNav :active="1" />

<!--
三次跃迁，一条规律：**抽象封得住的地方，知识会死；**

[click] **抽象漏水的地方，知识不死，而且变贵。**

这句话请记一下，今天后面我会至少回到它三次。

[click] 什么叫漏水？举一个你们现在就能亲手验证的例子：在浏览器控制台或者 Python 里输入 0.1 + 0.2——它不等于 0.3，等于 0.30000000000000004。"数字"，我们从小学信到大的这层抽象，也在漏。漏出来的是什么？浮点表示、二进制转换这些底层知识——抽象一漏，只有懂的人能救。

[click] 因为要填第四行那两个问号，唯一的办法就是搞清楚一件事：AI 这层抽象，漏不漏？漏在哪儿？

我不跟你们空谈，接下来我们做实验、看案例。
-->

---

# 第四行的答案

<div class="mt-8 flex gap-6">

<div class="w-38 shrink-0 flex items-center">
  <div class="p-4 rounded bg-amber-500/10 border border-amber-500/30 text-center w-full">
    <div class="text-xs opacity-60 mb-1">抽象层跃迁</div>
    <div class="font-bold">人写<br>↓<br>AI 生成</div>
  </div>
</div>

<div class="flex-1 p-5 rounded-lg border border-rose-500/30 bg-rose-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-4">被吃掉的</div>
  <div class="space-y-3 text-[15px]">
    <div>语法细节</div>
    <div>API 记忆</div>
    <div>样板与模板代码</div>
    <div>标准算法的手写实现</div>
    <div>跨语言翻译</div>
    <div>测试骨架</div>
  </div>
</div>

<div v-click class="flex-1 p-5 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-4">存活并升值的</div>
  <div class="space-y-3 text-[15px]">
    <div><span class="font-bold text-teal-600 dark:text-teal-400">①</span> 把模糊需求翻译成<span class="font-bold">带约束的规格说明</span></div>
    <div><span class="font-bold text-teal-600 dark:text-teal-400">②</span> 数据结构与复杂度<span class="font-bold">选型</span></div>
    <div><span class="font-bold text-teal-600 dark:text-teal-400">③</span> 对 AI 产出做<span class="font-bold">高密度验证</span></div>
    <div><span class="font-bold text-teal-600 dark:text-teal-400">④</span> 系统级<span class="font-bold">取舍</span><span class="block text-xs opacity-70 mt-0.5 pl-5">（时间／空间／一致性／成本／可维护性）</span></div>
    <div><span class="font-bold text-teal-600 dark:text-teal-400">⑤</span> 抽象漏水时的<span class="font-bold">故障定位</span></div>
  </div>
</div>

</div>

<UnitNav :active="1" />

<!--
我先把我的答案摆出来，然后用剩下的时间证明它。

左边这一列，被吃掉的：语法细节、API 记忆、样板代码、标准算法的手写实现、跨语言翻译、测试骨架。这些我认，全部认。

[click] 右边这一列，我认为不但没死，而且变贵了：第一，把一个模糊的需求翻译成带约束的规格说明；第二，数据结构和复杂度的选型；第三，对 AI 产出的高密度验证；第四，系统级的取舍；第五，抽象漏水时候的故障定位。

[click] 接下来我们一条一条地证：先证第一条，再证后面四条。
-->

---
layout: center
class: text-center
---

# 一个命题

<div class="mt-10 p-8 rounded-lg border-2 border-teal-500/40 bg-teal-500/5 max-w-4xl mx-auto">

<div class="text-3xl font-bold leading-relaxed">
你能向 AI 表达的<span class="text-teal-700 dark:text-teal-300">精度上限</span><br>
=<br>
你掌握的<span class="text-teal-700 dark:text-teal-300">概念精度上限</span>
</div>

</div>

<div v-click class="mt-8 text-lg opacity-75">
你没有的概念，一个字也表达不出来。
</div>

<UnitNav :active="2" />

<!--
这一节我要证明一个命题：**你能向 AI 表达的精度上限，等于你自己掌握的概念精度上限。**

[click] 你没有的概念，一个字也表达不出来。
-->

---

# 对照实验：同一需求，两组 prompt

<div class="mt-3 flex items-start gap-2 text-xs leading-relaxed opacity-80">
  <span class="px-2 py-0.5 rounded bg-gray-500/15 font-bold shrink-0">场景</span>
  <div>给网络爬虫做 URL 去重——每次从待抓队列取出 URL，抓之前先判断它是否已经抓过。<br>把已经抓过的当成没抓过，就会重复抓取、甚至陷入死循环；而队列里的 URL 还在源源不断地来。</div>
</div>

<div grid="~ cols-2 gap-6" class="mt-4">

<div class="p-4 rounded-lg border border-gray-400/30 bg-gray-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-3">PROMPT A</div>
  <div class="font-mono text-base leading-relaxed">
    写个函数，判断一个列表里有没有重复元素。
  </div>
  <div class="mt-6 pt-3 border-t border-gray-400/20 text-xs opacity-50">
    约 90% 的人会这样问
  </div>
</div>

<div v-click class="p-4 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-3">PROMPT B</div>
  <div class="font-mono text-sm leading-relaxed">
    判断 <span class="bg-amber-400/25 rounded px-1">10^7 个 64 位整数</span>中是否存在重复。<br>
    约束：数据<span class="bg-amber-400/25 rounded px-1">流式到达，只允许单遍扫描</span>；<br>
    进程<span class="bg-amber-400/25 rounded px-1">内存上限 100MB</span>；<br>
    可容忍 <span class="bg-amber-400/25 rounded px-1">0.1% 假阳性</span>，<br>
    但<span class="bg-amber-400/25 rounded px-1">不允许假阴性</span>。
  </div>
  <div class="mt-3 pt-3 border-t border-teal-500/20 text-xs opacity-60">
    同一个需求，换了一种说法 · 高亮处共 <span class="font-bold">5</span> 个约束成分
  </div>
</div>

</div>

<div v-click class="mt-6 text-center text-xl font-bold">
你们觉得这两个 prompt，AI 会给出<span v-mark.circle.orange="3">同一个答案</span>吗？
</div>

<UnitNav :active="2" />

<!--
先交代这个实验的需求场景：网络爬虫的 URL 去重。爬虫从待抓队列里一条条取出 URL，抓之前先判断：这个 URL 之前是不是已经抓过？把抓过的当成没抓过，就会重复抓取，顺着环状链接还会陷入死循环——而队列里的 URL 是源源不断进来的。

面对同一个场景，我准备了两段 prompt，问的是同一件事：判断有没有重复元素。

第一段，Prompt A，我猜是你们百分之九十的人会写的那种：「写个函数，判断一个列表里有没有重复元素。」——不懂数据结构的人，看到这个爬虫场景，能写出来的也只有这一句。

[click] 第二段，Prompt B，是一位高阶开发者会写出来的。同一个场景，他先把需求提炼成几个问题，再逐条落实：规模多少？——千万级；数据怎么来？——流式到达，只能顺着过一遍；内存给多少？——这个模块的预算是一百兆；判错了会怎样？——抓过的绝不能漏，漏一个就会重复抓取、甚至死循环；没抓过的误判无所谓，不过是少抓一个页面，千分之一以内可以接受。把这五条翻译成约束词，就是这段 prompt：「判断一千万个 64 位整数里有没有重复。约束：数据是流式到达的，只允许单遍扫描；进程内存上限一百兆；可以容忍千分之一的假阳性，但不允许假阴性。」

[click] 先别看答案。我问你们一个问题——你们觉得这两个 prompt，AI 会给出同一个答案吗？

（举手，等 10 秒）好，我们看。
-->

---
layout: full
class: px-10 py-6
---

<div class="flex items-center gap-3 mb-3">
  <div class="text-2xl font-bold">实验结果</div>
  <div class="text-xs opacity-50">同一个 AI · 同一天 · 间隔不到一分钟</div>
</div>

<div grid="~ cols-2 gap-5">

<div>
  <div class="flex items-baseline gap-2 mb-1.5">
    <span class="text-xs px-2 py-0.5 rounded bg-gray-500/15 font-bold">A</span>
    <span class="text-sm font-bold">set 去重比长度</span>
    <span class="text-xs opacity-60">空间约 600 MB</span>
  </div>
  <img src="/images/ch00/demo_prompt_a_response.png" class="rounded border border-gray-400/20 shadow" />
</div>

<div>
  <div class="flex items-baseline gap-2 mb-1.5">
    <span class="text-xs px-2 py-0.5 rounded bg-teal-500/20 text-teal-700 dark:text-teal-300 font-bold">B</span>
    <span class="text-sm font-bold">Bloom filter</span>
    <span class="text-xs opacity-60">空间 17.1 MB</span>
  </div>
  <img src="/images/ch00/demo_prompt_b_response_crop.png" class="rounded border border-teal-500/25 shadow" />
</div>

</div>

<div v-click="1" class="mt-5 text-center">
  <div class="text-2xl font-bold">AI 在这两次里，有哪一次<span v-mark.circle.red="2">答错了</span>吗？</div>
</div>

<div v-click="3" class="mt-4 flex items-center justify-center gap-8">
  <div class="text-3xl font-bold text-teal-600 dark:text-teal-400">没有。两次都对。</div>
  <div class="text-4xl font-black">差别 <span class="text-rose-600 dark:text-rose-400">100%</span> 来自提问的人。</div>
</div>

<UnitNav :active="2" />

<!--
左边，Prompt A 的回答。三行，一个 set，转成集合比长度。干净、正确、可读。

右边，Prompt B 的回答。它给了我一个 Bloom filter，位数组开多大、用几个哈希函数、假阳性率怎么控制，全都算了出来。注意它自己列的方案表——HashSet 那一行，它算的是超过 160 兆。这个数字我们下一页会自己推一遍。

同一个 AI，同一天，间隔不到一分钟。

[click] 现在我问一个关键问题，你们认真想三秒钟：**AI 在这两次里面，有哪一次答错了吗？**

[click] （停，等学生答）

[click] 没有。两次都是对的。Prompt A 那三行代码，在"一个列表、几百个元素"这个语境下，是最优解，我挑不出毛病。

所以差别在哪儿？**百分之百在提问的人身上。**

这一点我希望你们今天带走。你们以为我要讲"AI 不行、所以还得靠你们"——不是。我要讲的是：**AI 全对，问题在你。** 这比"AI 不行"可怕得多，因为"AI 不行"是它的问题，会随着版本迭代解决；"你不知道该问什么"是你的问题，不会随着任何模型升级而自动解决。
-->

---

# 五个约束词，各锁掉了什么

<div class="mt-5 text-sm">

<div class="flex gap-4 pb-2 mb-1 border-b border-gray-400/30 text-xs tracking-wide opacity-60">
  <div class="w-56 shrink-0">约束词</div>
  <div class="flex-1">锁定的技术决策</div>
  <div class="w-40 shrink-0">对应课程内容</div>
</div>

<div v-click="1" class="flex gap-4 py-2.5 border-b border-gray-400/15 items-center">
  <div class="w-56 shrink-0 font-mono text-xs bg-amber-400/20 rounded px-2 py-1">10^7 个 64 位整数</div>
  <div class="flex-1">数据量级 → 排除 <span class="font-bold">O(n²)</span></div>
  <div class="w-40 shrink-0 text-xs opacity-70">复杂度分析</div>
</div>

<div v-click="2" class="flex gap-4 py-2.5 border-b border-gray-400/15 items-center">
  <div class="w-56 shrink-0 font-mono text-xs bg-amber-400/20 rounded px-2 py-1">流式到达、单遍扫描</div>
  <div class="flex-1">访问模式 → 排除排序、排除随机访问</div>
  <div class="w-40 shrink-0 text-xs opacity-70">线性表</div>
</div>

<div v-click="3" class="flex gap-4 py-2.5 border-b border-gray-400/15 items-center">
  <div class="w-56 shrink-0 font-mono text-xs bg-amber-400/20 rounded px-2 py-1">内存上限 100MB</div>
  <div class="flex-1">空间预算 → 排除<span class="font-bold text-rose-600 dark:text-rose-400">全部精确去重结构</span></div>
  <div class="w-40 shrink-0 text-xs opacity-70">空间复杂度、散列</div>
</div>

<div v-click="4" class="flex gap-4 py-2.5 border-b border-gray-400/15 items-center">
  <div class="w-56 shrink-0 font-mono text-xs bg-amber-400/20 rounded px-2 py-1">容忍 0.1% 假阳性</div>
  <div class="flex-1">允许近似 → <span class="font-bold text-teal-700 dark:text-teal-300">打开概率型结构的可行域</span></div>
  <div class="w-40 shrink-0 text-xs opacity-70">散列／Bloom filter</div>
</div>

<div v-click="5" class="flex gap-4 py-2.5 border-b border-gray-400/15 items-center">
  <div class="w-56 shrink-0 font-mono text-xs bg-amber-400/20 rounded px-2 py-1">不允许假阴性</div>
  <div class="flex-1">误差单边 → <span class="font-bold text-teal-700 dark:text-teal-300">精确指向 Bloom filter</span></div>
  <div class="w-40 shrink-0 text-xs opacity-70">散列</div>
</div>

</div>

<div v-click="6" class="mt-5 text-center text-lg">
五个词，<span v-mark.underline.orange="6">全部来自这门课的词汇表</span>。
</div>

<UnitNav :active="2" />

<!--
我们把 Prompt B 拆开，看我到底用了哪些词。

[click] 第一个，"一千万个 64 位整数"。这是数据量级。这个词一说出口，所有 O(n²) 的方案当场出局——双重循环在一千万上要跑十的十四次方次，跑到明年。

[click] 第二个，"流式到达、只允许单遍扫描"。这是访问模式。这个词一出，排序类方案出局了，因为排序要么得把数据全拿到手，要么得多趟 I/O；随机访问的方案也出局了。

[click] 第三个，"内存上限一百兆"。这个我们下一页详细算。

[click] 正因为精确方案全灭，第四个词才有意义——"可以容忍千分之一的假阳性"。这一句话打开了一个全新的可行域：概率型结构。

[click] 第五个词，"不允许假阴性"。这是给误差指方向：允许我把没见过的说成见过，不允许我把见过的说成没见过。这个单边性一说出来，答案就唯一了，就是 Bloom filter。

[click] 现在你回头看这五个词——数据量级、单遍扫描、内存上限、假阳性、假阴性——**五个词，全部来自这门课的词汇表。**
-->

---

# 内存预算核算 · 上限 100MB

<div class="mt-4 space-y-2.5 text-sm">

<div class="flex items-center gap-3 text-xs">
  <div class="w-56 shrink-0" />
  <div class="flex-1 relative h-4">
    <div class="absolute inset-y-0 left-0 border-r-2 border-dashed border-rose-500/60 flex items-end justify-end pr-1" style="width: 16.67%">
      <span class="font-bold text-rose-600 dark:text-rose-400 whitespace-nowrap">100MB 预算线</span>
    </div>
  </div>
  <div class="w-60 shrink-0" />
</div>

<div v-click="1" class="flex items-center gap-3">
  <div class="w-56 shrink-0 text-right">裸数据本身 <span class="text-xs opacity-60">8 B／元素</span></div>
  <div class="flex-1 relative h-7">
    <div class="absolute inset-y-0 left-0 border-r-2 border-dashed border-rose-500/40 bg-rose-500/5" style="width: 16.67%" />
    <div class="absolute inset-y-0 left-0 rounded-r bg-gray-400/50" style="width: 13.3%" />
  </div>
  <div class="w-60 shrink-0 flex items-center gap-2">
    <span class="font-mono">80 MB</span>
    <span class="text-xs px-1.5 py-0.5 rounded bg-gray-500/15 opacity-80">不是可查询结构</span>
  </div>
</div>

<div v-click="2" class="flex items-center gap-3">
  <div class="w-56 shrink-0 text-right">最紧凑的开放地址哈希表 <span class="text-xs opacity-60">16 B</span></div>
  <div class="flex-1 relative h-7">
    <div class="absolute inset-y-0 left-0 border-r-2 border-dashed border-rose-500/40 bg-rose-500/5" style="width: 16.67%" />
    <div class="absolute inset-y-0 left-0 rounded-r bg-rose-500/50" style="width: 26.7%" />
  </div>
  <div class="w-60 shrink-0 flex items-center gap-2">
    <span class="font-mono font-bold">160 MB</span>
    <span class="text-xs px-1.5 py-0.5 rounded bg-rose-500/15 text-rose-700 dark:text-rose-300 font-bold">超 · 已是理论下限</span>
  </div>
</div>

<div v-click="3" class="flex items-center gap-3">
  <div class="w-56 shrink-0 text-right">C++ <code class="text-xs">unordered_set</code> <span class="text-xs opacity-60">≈25 B</span></div>
  <div class="flex-1 relative h-7">
    <div class="absolute inset-y-0 left-0 border-r-2 border-dashed border-rose-500/40 bg-rose-500/5" style="width: 16.67%" />
    <div class="absolute inset-y-0 left-0 rounded-r bg-rose-500/50" style="width: 41.7%" />
  </div>
  <div class="w-60 shrink-0 flex items-center gap-2">
    <span class="font-mono font-bold">250 MB</span>
    <span class="text-xs px-1.5 py-0.5 rounded bg-rose-500/15 text-rose-700 dark:text-rose-300">超</span>
  </div>
</div>

<div v-click="3" class="flex items-center gap-3">
  <div class="w-56 shrink-0 text-right">Python <code class="text-xs">set</code> 存 int 对象 <span class="text-xs opacity-60">≈60 B</span></div>
  <div class="flex-1 relative h-7">
    <div class="absolute inset-y-0 left-0 border-r-2 border-dashed border-rose-500/40 bg-rose-500/5" style="width: 16.67%" />
    <div class="absolute inset-y-0 left-0 rounded-r bg-rose-500/60" style="width: 100%" />
  </div>
  <div class="w-60 shrink-0 flex items-center gap-2">
    <span class="font-mono font-bold">600 MB</span>
    <span class="text-xs px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-700 dark:text-rose-300 font-bold">超 6 倍</span>
  </div>
</div>

<div v-click="4" class="flex items-center gap-3 pt-1">
  <div class="w-56 shrink-0 text-right font-bold">Bloom filter <span class="text-xs opacity-60 font-normal">14.4 bit ≈ 1.8 B</span></div>
  <div class="flex-1 relative h-7">
    <div class="absolute inset-y-0 left-0 border-r-2 border-dashed border-rose-500/40 bg-rose-500/5" style="width: 16.67%" />
    <div class="absolute inset-y-0 left-0 rounded-r bg-teal-500/70" style="width: 3%" />
  </div>
  <div class="w-60 shrink-0 flex items-center gap-2">
    <span class="font-mono font-bold text-teal-700 dark:text-teal-300">18 MB</span>
    <span class="text-xs px-1.5 py-0.5 rounded bg-teal-500/20 text-teal-700 dark:text-teal-300 font-bold">可行 · 用了预算 1/5</span>
  </div>
</div>

</div>

<div v-click="5" class="mt-5 text-center text-sm">
<span class="opacity-70">精确方案全部出局，才轮到</span>「<span class="font-bold">容忍 0.1% 假阳性</span>」<span class="opacity-70">这个词发挥作用</span>
</div>

<UnitNav :active="2" />

<!--
（板书口算）一千万个整数，每个 8 字节，一乘，八千万字节，**80 兆**。一百兆够用啊，老师你是不是搞错了？

[click] 没搞错。80 兆是**裸数据本身**的大小，而裸数据不是一个能做查重的结构。你要判断"来了一个数，之前见过没有"，你得有个可查询的结构。

[click] 我们算最好的情况：一个最紧凑的开放地址哈希表，只存 key、不存别的，装填因子撑到 0.5，那就是每个元素 16 字节——**160 兆**，超了。这已经是理论下限了。刚才那张截图里 AI 自己算的也是 160 兆。

[click] 你要是用 C++ 的 unordered_set，链地址加每节点的 malloc 开销，两百五十兆。你要是用 Python 的 set，每个整数是一个对象，二十多字节额外开销加指针加装填因子，六百兆——超了六倍。

[click] Bloom filter 要多少？千分之一假阳性，每个元素大约 14.4 个比特，一千万个元素，一亿四千四百万比特，**十八兆**。一百兆的预算，用了不到五分之一。

[click] 请注意这个顺序：不是我一开始就想用 Bloom filter，是因为精确方案全部出局，"容忍千分之一假阳性"这个词才有了意义。
-->

---
layout: center
---

# 这一节的结论

<div class="mt-8 space-y-4 max-w-4xl mx-auto">

<div class="p-5 rounded-lg border-2 border-amber-500/40 bg-amber-500/5">
  <div class="text-2xl font-bold leading-relaxed">
    缺少某个概念词，AI 会自动把对应约束<span class="text-amber-600 dark:text-amber-400">设为默认值</span>。
  </div>
</div>

<div v-click class="p-5 rounded-lg border-2 border-rose-500/40 bg-rose-500/5">
  <div class="text-2xl font-bold leading-relaxed">
    被默认掉的约束<span class="text-rose-600 dark:text-rose-400">不会报错</span>，<br>
    会在上线后以 <span class="font-mono">OOM</span>、<span class="font-mono">超时</span>、<span class="font-mono">数据倾斜</span> 的形式返还。
  </div>
</div>

<div v-click class="p-4 rounded-lg bg-gray-500/10 border-l-4 border-gray-400">
  <div class="text-lg">
    这<span class="font-bold">不是</span>提示词技巧问题。<br>
    <span class="opacity-80">提示词技巧解决不了「这个词根本不在你脑子里」。</span>
  </div>
</div>

</div>

<UnitNav :active="2" />

<!--
结论是这样：**你缺哪一个词，AI 就替你把那条约束默认掉。**

[click] 而它默认掉的东西不会报错——它会给你一段能跑、能过测试、看起来还挺漂亮的代码，然后在你上线之后，以 OOM、以超时、以某个分片突然打爆的形式还给你。

这里我要停一下问你们一句：**你们平时用 AI 写代码的时候，有几个人告诉过它「我的数据有多大」？** （等，观察反应）我猜很少。那就意味着，你们过去每一次都在接受它的默认假设。

[click] 最后，请不要把这一节理解成"我去报个提示词课就好了"。提示词技巧能帮你把话说得更清楚，但它解决不了一件事：**那个词根本不在你脑子里。** 你想不到"假阳性"这三个字，任何提示词模板都救不了你。
-->

---

# 课程定位之一：这首先是一门<span class="text-teal-600 dark:text-teal-400">词汇课</span>

<div class="text-sm opacity-70 mt-1 mb-6">它提供一套描述<span class="font-bold">计算成本</span>的语言。</div>

<div grid="~ cols-2 gap-6">

<div class="p-5 rounded-lg border border-rose-500/30 bg-rose-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-3">没有这套语言</div>
  <div class="text-lg leading-relaxed">
    只能说「帮我写个函数」，<br>
    <span class="font-bold text-rose-600 dark:text-rose-400">被动接受 AI 的全部默认假设</span>
  </div>
</div>

<div v-click class="p-5 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-3">有这套语言</div>
  <div class="text-lg leading-relaxed">
    能输出<span class="font-bold text-teal-700 dark:text-teal-300">规格说明</span>（specification），<br>
    而 AI 是极高效的<span class="font-bold">规格执行器</span>
  </div>
</div>

</div>

<div v-click class="mt-8 text-center">
  <div class="inline-flex items-center gap-4 text-2xl font-bold">
    <span class="px-4 py-2 rounded bg-gray-500/10 opacity-60 line-through">实现者</span>
    <span class="text-3xl opacity-40">→</span>
    <span class="px-4 py-2 rounded bg-teal-500/15 text-teal-700 dark:text-teal-300">规格作者</span>
  </div>
  <div class="mt-3 text-sm opacity-60">今天第一个要记住的角色变化</div>
</div>

<UnitNav :active="2" />

<!--
所以这门课的第一重定位，是一门**词汇课**。它给你一套描述"计算成本"的语言。

没有这套语言，你只能说"帮我写个函数"，然后 AI 帮你把所有你没提的事全默认掉。

[click] 有了这套语言，你能写出规格说明——而 AI 恰好是这个世界上执行规格效率最高的东西。

[click] **你的角色从"实现者"上移到"规格作者"。** 这是今天第一个要记的角色变化。
-->

---

# 案例：气象网格数据 → 区县尺度聚合

<div class="text-xs opacity-60 -mt-1 mb-4">案例来源：授课教师实际项目 · 不是教材例题</div>

<div grid="~ cols-[1fr_1.1fr] gap-7">
<div>

**业务需求**

把气象网格数据（如 0.05° 格点的降水、气温）聚合成<span class="font-bold">区县尺度</span>的统计量，用于逐日报表。

<div class="mt-4 space-y-2 text-sm">
  <div class="flex items-center gap-3 p-2 rounded bg-gray-500/8">
    <div class="w-28 opacity-70">网格点数 N</div>
    <div class="font-bold font-mono">数十万级</div>
  </div>
  <div class="flex items-center gap-3 p-2 rounded bg-gray-500/8">
    <div class="w-28 opacity-70">区县数 M</div>
    <div class="font-bold font-mono">约 3,000</div>
  </div>
  <div class="flex items-center gap-3 p-2 rounded bg-amber-500/10">
    <div class="w-28 opacity-70">执行频次</div>
    <div class="font-bold">逐日 × 多要素，反复执行</div>
  </div>
</div>

</div>
<div class="flex items-center justify-center">

<svg viewBox="0 0 400 260" class="w-full max-h-56">
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.25" />
    </pattern>
  </defs>
  <rect width="400" height="260" fill="url(#grid)" />
  <g fill="currentColor" opacity="0.3">
    <template v-for="r in 12" :key="r">
      <circle v-for="c in 19" :key="c" :cx="c * 20" :cy="r * 20" r="1.6" />
    </template>
  </g>
  <path d="M 30 40 L 150 30 L 175 120 L 90 150 L 25 110 Z" fill="rgb(20,184,166)" fill-opacity="0.14" stroke="rgb(13,148,136)" stroke-width="2.5" />
  <path d="M 175 120 L 150 30 L 280 45 L 310 130 L 200 165 Z" fill="rgb(244,63,94)" fill-opacity="0.12" stroke="rgb(225,29,72)" stroke-width="2.5" />
  <path d="M 90 150 L 175 120 L 200 165 L 160 230 L 60 205 Z" fill="rgb(245,158,11)" fill-opacity="0.12" stroke="rgb(217,119,6)" stroke-width="2.5" />
  <text x="70" y="90" style="font-size:18px" fill="rgb(13,148,136)" font-weight="bold">区县 A</text>
  <text x="205" y="100" style="font-size:18px" fill="rgb(225,29,72)" font-weight="bold">区县 B</text>
  <text x="100" y="190" style="font-size:18px" fill="rgb(217,119,6)" font-weight="bold">区县 C</text>
</svg>

</div>
</div>

<div class="mt-4 text-center text-sm opacity-75">
格点与区县是<span class="font-bold">多对一</span>关系；这个归属关系<span class="font-bold">一天都不会变</span>。
</div>

<UnitNav :active="3" />

<!--
下面这个案例是我自己项目里的事，不是教材上的例题。

需求很朴素：气象数据是网格的，比如 0.05 度一个格点，铺满全国。但报表要的是行政单位——每个区县今天平均降水多少、平均气温多少。所以要把网格尺度的数据聚合成区县尺度。

三个数字你们记一下：网格点数十万级，区县数大概三千，而且这个事要**每天**跑、**每个要素**都跑。

我把这个需求丢给 AI。
-->

---

# AI 的初始方案

```python
for 每个区县 c in 全部区县:            # 外层 M 次
    bucket = []
    for 每个网格点 g in 全部网格:       # 内层 N 次
        if g 落在 c 内:                # 空间归属判断
            bucket.append(g.value)
    result[c] = mean(bucket)
```

<div v-click="1" class="mt-4 text-sm">
  <div class="text-xs tracking-widest opacity-60 mb-2">复杂度审计</div>
  <div class="grid grid-cols-4 gap-3">
    <div class="p-3 rounded border border-teal-500/30 bg-teal-500/5">
      <div class="text-xs opacity-60 mb-1">正确性</div>
      <div class="font-bold text-teal-700 dark:text-teal-300">完全正确</div>
    </div>
    <div class="p-3 rounded border border-teal-500/30 bg-teal-500/5">
      <div class="text-xs opacity-60 mb-1">可读性</div>
      <div class="font-bold text-teal-700 dark:text-teal-300">清晰、直观</div>
    </div>
    <div class="p-3 rounded border border-rose-500/40 bg-rose-500/8">
      <div class="text-xs opacity-60 mb-1">时间复杂度</div>
      <div class="font-bold text-rose-600 dark:text-rose-400">O(M × N)</div>
      <div class="text-xs opacity-70 mt-0.5">内层含几何判断，常数极大</div>
    </div>
    <div class="p-3 rounded border border-rose-500/40 bg-rose-500/8">
      <div class="text-xs opacity-60 mb-1">重复成本</div>
      <div class="font-bold text-rose-600 dark:text-rose-400">每日 × 每要素</div>
      <div class="text-xs opacity-70 mt-0.5">完整重跑一遍 M×N</div>
    </div>
  </div>
</div>

<div v-click="2" class="mt-4 p-3 rounded bg-amber-500/10 border-l-4 border-amber-500 text-sm">
这段代码<span class="font-bold">完全正确</span>。逻辑没问题，结果没问题，可读性甚至比我后来的版本还好。<span class="font-bold">它只是慢得离谱。</span>
</div>

<UnitNav :active="3" />

<!--
这是 AI 给我的第一版。我先不说好不好，你们自己读三十秒，然后告诉我这段代码的时间复杂度。

（停 30 秒，点一两个学生回答）

[click] 对，O(M 乘 N)。外层三千个区县，内层几十万个格点，乘出来是十亿次量级。而且注意内层那一句——"g 落在 c 内"，这不是一次整数比较，这是一次几何判断，要做点在多边形内的测试，常数项非常大。

再补一刀：这个东西要**每天跑、每个要素跑**。你今天算了一遍格点属于哪个区县，明天数据换了，你又从头算一遍——而**格点和区县的空间关系一天都没变过**。

[click] 但是我要强调一件事：**这段代码是完全正确的。** 逻辑没问题，结果没问题，可读性甚至比我后来的版本还好。它跑得出来，只是慢得离谱。
-->

---

# 改进方案：展平 → merge → groupby

<div grid="~ cols-2 gap-6" class="mt-3">

<div class="p-4 rounded-lg border border-rose-500/30 bg-rose-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-3">原方案 · 嵌套循环</div>
  <div class="space-y-1.5 text-sm">
    <div class="flex items-center gap-2">
      <div class="w-20 text-xs px-2 py-1 rounded bg-rose-500/15 text-center">区县 1</div>
      <div class="opacity-40">→</div>
      <div class="flex-1 px-2 py-1 rounded bg-gray-500/10 text-xs">扫描全部 N 个格点 + 几何判断</div>
    </div>
    <div class="flex items-center gap-2">
      <div class="w-20 text-xs px-2 py-1 rounded bg-rose-500/15 text-center">区县 2</div>
      <div class="opacity-40">→</div>
      <div class="flex-1 px-2 py-1 rounded bg-gray-500/10 text-xs">扫描全部 N 个格点 + 几何判断</div>
    </div>
    <div class="flex items-center gap-2 opacity-50">
      <div class="w-20 text-xs px-2 py-1 rounded bg-rose-500/15 text-center">⋮</div>
      <div class="opacity-40">→</div>
      <div class="flex-1 px-2 py-1 rounded bg-gray-500/10 text-xs">⋮</div>
    </div>
    <div class="flex items-center gap-2">
      <div class="w-20 text-xs px-2 py-1 rounded bg-rose-500/15 text-center">区县 3000</div>
      <div class="opacity-40">→</div>
      <div class="flex-1 px-2 py-1 rounded bg-gray-500/10 text-xs">扫描全部 N 个格点 + 几何判断</div>
    </div>
  </div>
  <div class="mt-3 pt-2 border-t border-rose-500/20 text-center">
    <span class="font-bold text-rose-600 dark:text-rose-400">同一批格点被扫了 3,000 遍</span>
  </div>
</div>

<div v-click="1" class="p-4 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-3">新方案 · 三步，各一遍</div>
  <div class="space-y-2 text-sm">
    <div class="flex items-center gap-2">
      <div class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">1</div>
      <div class="flex-1"><span class="font-bold">展平</span> 成一维长表 <code class="text-xs">(grid_id, value)</code></div>
      <div class="font-mono text-xs text-teal-700 dark:text-teal-300">O(N)</div>
    </div>
    <div class="flex items-center gap-2">
      <div class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">2</div>
      <div class="flex-1"><span class="font-bold">merge</span> 按编号查对照表</div>
      <div class="font-mono text-xs text-teal-700 dark:text-teal-300">O(N)</div>
    </div>
    <div class="flex items-center gap-2">
      <div class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">3</div>
      <div class="flex-1"><span class="font-bold">groupby</span> 按区县编码聚合</div>
      <div class="font-mono text-xs text-teal-700 dark:text-teal-300">O(N)</div>
    </div>
  </div>
  <div v-click="2" class="mt-3 p-2 rounded bg-amber-500/12 text-xs">
    <span class="font-bold">grid_id → 区县编码</span> 对照表：<span class="font-bold text-amber-700 dark:text-amber-400">预计算，一辈子只算一次</span>
  </div>
</div>

</div>

<div v-click="3" class="mt-5 flex items-center justify-center gap-6">
  <div class="text-2xl font-bold">
    <span class="text-rose-600 dark:text-rose-400">O(M × N)</span>
    <span class="mx-3 opacity-40">→</span>
    <span class="text-teal-600 dark:text-teal-400">O(N)</span>
  </div>
  <div class="text-sm opacity-75">实测提升约 <span class="font-bold text-lg">两个数量级</span>；区县越多、要素越多，收益越大</div>
</div>

<UnitNav :active="3" />

<!--
我给 AI 的提示只有三句话。

[click] 第一，先把网格数据**展平**——从二维数组变成一条长表，每行是「格点编号，数值」，这一步 O(N)。第二，跟一张事先算好的对照表做 **merge**——那张表就一列格点编号、一列区县编码，按编号查一次就对上，O(N)。第三，按区县编码 **groupby** 聚合，O(N)。

[click] 注意那张对照表：它是预计算的，一辈子只算一次。

[click] 三步都是 O(N)，整体从 O(M×N) 掉到 O(N)。实测快了两个数量级，远不止十倍。而且要注意，这个收益是随规模放大的——区县越多、要素越多，差距越大。
-->

---

# 慢动作：6 个格点走完三步

<div class="text-xs opacity-60 -mt-1 mb-2">2×3 网格 · 2 个区县 · 格内为气温值，左上角小字为格点编号（行优先）</div>

<div class="flex items-stretch gap-2.5 min-h-[318px]">

<div class="shrink-0">
  <div class="text-[11px] font-bold opacity-60 mb-1">原始网格</div>
  <div class="grid grid-cols-3 gap-1.5 w-[144px]">
    <div v-for="c in [[1, '7.0', 'A'], [2, '8.0', 'A'], [3, '9.0', 'B'], [4, '4.0', 'A'], [5, '5.0', 'A'], [6, '6.0', 'B']]" :key="c[0]"
         class="relative h-11 rounded-md border flex items-center justify-center"
         :class="c[2] === 'A' ? 'border-teal-500/40 bg-teal-500/12' : 'border-rose-500/35 bg-rose-500/10'">
      <span class="absolute top-0.5 left-1 text-[8px] font-mono opacity-50">{{ c[0] }}</span>
      <span class="text-sm font-mono font-bold">{{ c[1] }}</span>
    </div>
  </div>
  <div class="mt-1.5 flex items-center gap-2.5 text-[10px] opacity-70">
    <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 rounded-sm bg-teal-500/40"></span>区县 A</span>
    <span class="flex items-center gap-1"><span class="inline-block w-2.5 h-2.5 rounded-sm bg-rose-500/40"></span>区县 B</span>
  </div>
</div>

<div v-click="1" class="flex-1 min-w-[70px] flex flex-col items-center justify-center gap-0.5">
  <div class="text-xs font-bold text-teal-600 dark:text-teal-400">① 展平</div>
  <div class="text-[10px] opacity-50">把网格拉直</div>
  <div class="text-xl opacity-25">→</div>
</div>

<div v-click="1" class="shrink-0">
  <div class="text-[11px] font-bold opacity-60 mb-1">一维长表</div>
  <div class="w-[124px] rounded-md border border-gray-500/25 overflow-hidden text-xs font-mono leading-tight">
    <div class="grid grid-cols-2 bg-gray-500/10 text-[10px] font-bold">
      <div class="py-0.5 text-center opacity-70">grid_id</div>
      <div class="py-0.5 text-center opacity-70">value</div>
    </div>
    <div v-for="r in [[1, '7.0'], [2, '8.0'], [3, '9.0'], [4, '4.0'], [5, '5.0'], [6, '6.0']]" :key="r[0]"
         class="grid grid-cols-2 border-t border-gray-500/15">
      <div class="py-[3px] text-center">{{ r[0] }}</div>
      <div class="py-[3px] text-center">{{ r[1] }}</div>
    </div>
  </div>
</div>

<div v-click="2" class="flex-1 min-w-[70px] flex flex-col items-center justify-center gap-0.5">
  <div class="text-xs font-bold text-teal-600 dark:text-teal-400">② merge</div>
  <div class="text-[10px] opacity-50">按编号查对照表</div>
  <div class="text-xl opacity-25">→</div>
</div>

<div v-click="2" class="shrink-0 flex flex-col">
  <div class="text-[11px] font-bold opacity-60 mb-1">合并表</div>
  <div class="w-[156px] rounded-md border border-gray-500/25 overflow-hidden text-xs font-mono leading-tight">
    <div class="grid grid-cols-[52px_52px_52px] bg-gray-500/10 text-[10px] font-bold">
      <div class="py-0.5 text-center opacity-70">grid_id</div>
      <div class="py-0.5 text-center opacity-70">value</div>
      <div class="py-0.5 text-center opacity-70">区县</div>
    </div>
    <div v-for="r in [[1, '7.0', 'A'], [2, '8.0', 'A'], [3, '9.0', 'B'], [4, '4.0', 'A'], [5, '5.0', 'A'], [6, '6.0', 'B']]" :key="r[0]"
         class="grid grid-cols-[52px_52px_52px] border-t border-gray-500/15 items-center">
      <div class="py-[3px] text-center">{{ r[0] }}</div>
      <div class="py-[3px] text-center">{{ r[1] }}</div>
      <div class="py-[3px] flex justify-center">
        <span class="px-1.5 rounded text-[10px] font-bold leading-4" :class="r[2] === 'A' ? 'bg-teal-500/25 text-teal-700 dark:text-teal-300' : 'bg-rose-500/20 text-rose-700 dark:text-rose-300'">{{ r[2] }}</span>
      </div>
    </div>
  </div>
  <div class="mt-1.5 mb-1 text-[11px] font-bold text-amber-600 dark:text-amber-400">对照表 · 预计算</div>
  <div class="w-[124px] rounded-md border border-amber-500/35 overflow-hidden text-xs font-mono leading-tight self-center">
    <div class="grid grid-cols-2 bg-amber-500/10 text-[10px] font-bold">
      <div class="py-0.5 text-center text-amber-700 dark:text-amber-400">grid_id</div>
      <div class="py-0.5 text-center text-amber-700 dark:text-amber-400">区县</div>
    </div>
    <div v-for="r in [[1, 'A'], [2, 'A'], [3, 'B'], [4, 'A'], [5, 'A'], [6, 'B']]" :key="r[0]"
         class="grid grid-cols-2 border-t border-amber-500/20">
      <div class="py-[3px] text-center">{{ r[0] }}</div>
      <div class="py-[3px] text-center font-bold" :class="r[1] === 'A' ? 'text-teal-700 dark:text-teal-300' : 'text-rose-700 dark:text-rose-300'">{{ r[1] }}</div>
    </div>
  </div>
</div>

<div v-click="3" class="flex-1 min-w-[70px] flex flex-col items-center justify-center gap-0.5">
  <div class="text-xs font-bold text-teal-600 dark:text-teal-400">③ groupby</div>
  <div class="text-[10px] opacity-50">分组求平均</div>
  <div class="text-xl opacity-25">→</div>
</div>

<div v-click="3" class="shrink-0">
  <div class="text-[11px] font-bold opacity-60 mb-1">区县尺度结果</div>
  <div class="w-[136px] rounded-md border-2 border-teal-500/40 overflow-hidden text-xs font-mono leading-tight">
    <div class="grid grid-cols-2 bg-teal-500/10 text-[10px] font-bold">
      <div class="py-0.5 text-center text-teal-700 dark:text-teal-300">区县</div>
      <div class="py-0.5 text-center text-teal-700 dark:text-teal-300">均值</div>
    </div>
    <div v-for="r in [['A', '6.0'], ['B', '7.5']]" :key="r[0]"
         class="grid grid-cols-2 border-t border-teal-500/20">
      <div class="py-1 flex justify-center">
        <span class="px-1.5 rounded text-[10px] font-bold leading-4" :class="r[0] === 'A' ? 'bg-teal-500/25 text-teal-700 dark:text-teal-300' : 'bg-rose-500/20 text-rose-700 dark:text-rose-300'">{{ r[0] }}</span>
      </div>
      <div class="py-1 text-center font-bold">{{ r[1] }}</div>
    </div>
  </div>
  <div class="mt-1.5 text-[10px] opacity-60 text-center">6 行 → 2 行</div>
</div>

</div>

<div v-click="4" class="mt-3 p-2 rounded-lg bg-teal-500/8 border-l-4 border-teal-500 text-sm text-center">
  三步全是「把表从头扫到尾」——<span class="font-bold">没有几何判断、没有回头重扫</span>，总代价 3 × O(N)
</div>

<UnitNav :active="3" />

<!--
有些词得停下来抠清楚——"展平、merge、groupby"，光听名字是没画面的。我们用一个 6 个格点的小例子，慢动作走一遍。

看左边：2 乘 3 的网格，格子里是气温值，左上角小字是格点编号，行优先、从 1 数到 6；颜色就是区县的划分——A 区四个格点，B 区两个。

[click] 第一步，展平：把这张二维网格"拉直"，按编号顺序铺成一条长表——每个格点一行，两列：编号、数值。注意，这时候数据里还看不到任何区县信息。这一步就是顺序读一遍内存，O(N)。

[click] 第二步，merge：拿长表跟右边这张对照表做连接。对照表就两列——编号、区县编码，预计算，只算一次。连接的动作很朴素：长表的每一行，拿编号去对照表里查一次，把区县编码贴到行尾。查一次 O(1)，六行就查六次，合并表就出来了。看最后一列，A、A、B——全是查出来的。注意：这一步里没有任何几何计算。

[click] 第三步，groupby：按最后一列分组——A 组四行、B 组两行，每组求平均：A 区 (7+8+4+5)/4 = 6.0，B 区 (9+6)/2 = 7.5。六行变两行，报表要的数就出来了。

[click] 回头看整条流水线：每一站都只是把表从头到尾扫一遍，没有一步回头重扫，也没有一步做几何判断。这就是"三步都是 O(N)"的画面——最贵的那件事，早就被固化进对照表了。
-->

---

# 这个案例底下压着<span class="text-teal-600 dark:text-teal-400">四层</span>知识

<div grid="~ cols-[1.35fr_1fr] gap-6" class="mt-3">

<div class="space-y-2 text-sm">

<div class="p-2 rounded bg-gray-500/8 border-l-4 border-gray-400/50 opacity-70">
  <div class="text-xs tracking-widest mb-0.5">表面</div>
  <div>「改用 merge + groupby 就快了」</div>
</div>

<div v-click="1" class="p-2 rounded bg-teal-500/8 border-l-4 border-teal-500">
  <div class="text-xs tracking-widest opacity-70 mb-0.5">数据结构层</div>
  <div>同一个需求，换一种<span class="font-bold">数据组织方式</span>——「每次都从头翻」变成「查一次对照表」，代价完全不在一个量级。数据库每天都在自动做这种判断。</div>
</div>

<div v-click="2" class="p-2 rounded bg-teal-500/8 border-l-4 border-teal-500">
  <div class="text-xs tracking-widest opacity-70 mb-0.5">算法层</div>
  <div>格点属于哪个区县，跟「今天几号」「算什么要素」无关——既然不变，就<span class="font-bold">别放在循环里天天算</span>，拎出来只算一次。那张对照表就是这么来的。</div>
</div>

<div v-click="3" class="p-2 rounded bg-teal-500/8 border-l-4 border-teal-500">
  <div class="text-xs tracking-widest opacity-70 mb-0.5">内存层</div>
  <div>展平后数据在内存里<span class="font-bold">连续成一条，从头扫到尾</span>——「抽象漏水的地方，知识不死，而且变贵」，说的就是这一层。</div>
</div>

<div v-click="4" class="p-3 rounded bg-rose-500/10 border-l-4 border-rose-500">
  <div class="text-xs tracking-widest opacity-70 mb-0.5">抽象漏水点</div>
  <div class="font-bold">AI 默认了一个我从未说出口的前提：<br>「数据规模不大，而且只跑一次」</div>
</div>

</div>

<div v-click="1" class="flex items-center">
<div class="w-full space-y-3 text-xs">

<div class="p-3 rounded border border-rose-500/30 bg-rose-500/5">
  <div class="font-bold mb-2 text-rose-600 dark:text-rose-400">老办法</div>
  <div class="flex gap-1.5">
    <div class="flex flex-col gap-1">
      <div class="px-2 py-1 rounded bg-rose-500/15 text-center">c₁</div>
      <div class="px-2 py-1 rounded bg-rose-500/15 text-center">c₂</div>
      <div class="px-2 py-1 rounded bg-rose-500/15 text-center">c₃</div>
    </div>
    <div class="flex flex-col justify-around opacity-40 text-[10px]">
      <div>→→→</div><div>→→→</div><div>→→→</div>
    </div>
    <div class="flex-1 p-2 rounded bg-gray-500/10 flex items-center justify-center text-center">
      每次都从头翻一遍<br>N 个格点
    </div>
  </div>
  <div class="mt-2 text-center font-mono font-bold">M × N</div>
</div>

<div class="p-3 rounded border-2 border-teal-500/40 bg-teal-500/5">
  <div class="font-bold mb-2 text-teal-700 dark:text-teal-300">新办法</div>
  <div class="flex items-center gap-1.5">
    <div class="flex-1 p-2 rounded bg-gray-500/10 text-center">格点<br>扫一遍</div>
    <div class="opacity-40">→</div>
    <div class="p-2 rounded bg-teal-500/20 text-center font-bold">查对照表<br>一次就定位</div>
    <div class="opacity-40">→</div>
    <div class="flex-1 p-2 rounded bg-gray-500/10 text-center">区县<br>编码</div>
  </div>
  <div class="mt-2 text-center font-mono font-bold">N</div>
</div>

</div>
</div>

</div>

<UnitNav :active="3" />

<!--
现在最重要的部分来了。如果你们从这个案例里学到的只是"哦，以后用 merge 和 groupby"，那这十分钟就浪费了。这个案例底下压着四层知识。

[click] **第一层，数据结构层。** 右边这两张卡片，是同一个需求的两套数据组织方式：上面是老办法——每一行都从头翻一遍全表；下面是新办法——备一张对照表，查一次就定位。这个变换在行业里有正经名字，今天先不展开——你们先记住这个画面：**数据库每天都在自动做这种判断**。换句话说，学了这门课，你就是你自己的优化器。

[click] **第二层，算法层。** 关键在于看出一个事实：格点属于哪个区县，跟今天几号、跟你算的是气温还是降水，**完全无关**。既然无关，它就不该待在循环里——把它拎出来、算一次、存下来。你们刚才在"慢动作"里看到的那张对照表，就是这个动作的产物。就这一下，几何判断的成本从"每天十亿次"变成"一辈子几十万次"。

[click] **第三层，内存层。** 展平之后，数据在内存里连续成一条，从头扫到尾；老办法是东一块、西一块地翻。你们回想一下前面编译器那一段——编译器吃掉了手写汇编，但懂"数据在内存里怎么摆"的人，反而更值钱了。**就是这一格。** 三十年前的道理，在 2026 年的 pandas 代码里原封不动地生效。

[click] **第四层，也是最要命的一层：抽象漏在哪儿。** AI 默认了一个我从来没说过的前提——**"你的数据不大，而且你只跑一次。"** 它不是猜错了，它是在缺信息的时候必须猜，而它猜的方向永远是最普通的那个方向。

最后收一句：今天不要求你们听懂每一层——只需要看出：一个"就快了"的改动底下，压着这门课要一段一段教给你们的骨架。以后每学一章，都可以回来重看这个案例——它会越来越清楚。
-->

---

# AI 的典型失效模式

<div class="mt-3 p-5 rounded-lg border-2 border-rose-500/40 bg-rose-500/5 text-center">
  <div class="text-xl opacity-80">不是语法错误，也不是逻辑错误，而是</div>
  <div class="text-3xl font-bold mt-2">
    「<span class="text-teal-600 dark:text-teal-400">语义正确</span>、<span class="text-rose-600 dark:text-rose-400">复杂度错误</span>」
  </div>
</div>

<div grid="~ cols-[1fr_1.15fr] gap-6" class="mt-5">

<div>
  <div class="text-xs tracking-widest opacity-60 mb-2">四道防线，三道失效</div>
  <div class="space-y-1.5 text-sm">
    <div v-click="1" class="flex items-center gap-3 p-2 rounded bg-rose-500/8">
      <div class="flex-1">编译器</div>
      <div class="text-rose-600 dark:text-rose-400 font-bold">否</div>
    </div>
    <div v-click="2" class="flex items-center gap-3 p-2 rounded bg-rose-500/8">
      <div class="flex-1">单元测试（小数据）</div>
      <div class="text-rose-600 dark:text-rose-400 font-bold">否</div>
    </div>
    <div v-click="3" class="flex items-center gap-3 p-2 rounded bg-rose-500/8">
      <div class="flex-1">只看可读性的 code review</div>
      <div class="text-rose-600 dark:text-rose-400 font-bold">否</div>
    </div>
    <div v-click="4" class="flex items-center gap-3 p-2.5 rounded bg-teal-500/12 border border-teal-500/40">
      <div class="flex-1 font-bold">有复杂度直觉的人，扫一眼循环嵌套</div>
      <div class="text-teal-700 dark:text-teal-300 font-bold text-lg">是</div>
    </div>
  </div>
</div>

<div>
<svg viewBox="0 0 360 200" class="w-full">
  <rect x="45" y="12" width="52" height="150" fill="rgb(148,163,184)" fill-opacity="0.14" />
  <line x1="45" y1="162" x2="345" y2="162" stroke="currentColor" stroke-width="1.2" opacity="0.5" />
  <line x1="45" y1="162" x2="45" y2="12" stroke="currentColor" stroke-width="1.2" opacity="0.5" />
  <path d="M 45 160 Q 150 150 240 110 T 330 20" fill="none" stroke="rgb(225,29,72)" stroke-width="2.8" />
  <path d="M 45 161 L 330 140" fill="none" stroke="rgb(13,148,136)" stroke-width="2.8" />
  <text x="248" y="42" style="font-size:17px" fill="rgb(225,29,72)" font-weight="bold">O(M × N)</text>
  <text x="272" y="134" style="font-size:17px" fill="rgb(13,148,136)" font-weight="bold">O(N)</text>
  <text fill="rgb(71,85,105)" x="52" y="182" style="font-size:13px">测试数据规模</text>
  <text fill="rgb(71,85,105)" x="52" y="192" style="font-size:13px">两条线几乎重合</text>
  <text fill="rgb(71,85,105)" x="285" y="182" style="font-size:13px">生产规模</text>
  <text fill="rgb(120,133,153)" x="178" y="196" style="font-size:13px">数据规模 N →</text>
  <circle cx="330" cy="20" r="3.5" fill="rgb(225,29,72)" />
  <circle cx="330" cy="140" r="3.5" fill="rgb(13,148,136)" />
  <line x1="336" y1="20" x2="336" y2="140" stroke="currentColor" stroke-width="1" opacity="0.4" stroke-dasharray="3 2" />
  <text fill="rgb(71,85,105)" x="332" y="104" text-anchor="end" style="font-size:14px" font-weight="bold">100×+</text>
</svg>
<div class="text-center text-xs opacity-70 -mt-1">
灰色区间正是<span class="font-bold">单元测试查不出来</span>的原因
</div>
</div>

</div>

<UnitNav :active="3" />

<!--
从这个案例我要提炼出一句话，我认为这是今天整节课最有实用价值的一句：

**AI 的典型失效模式，不是语法错误，也不是逻辑错误，而是"语义正确、复杂度错误"。**

你们体会一下这有多难防。

[click] 语法错了，编译器报——这里编译器不报，因为语法完全合法。
[click] 逻辑错了，测试报——这里测试也不报，因为测试数据就一百行，跑得飞快。你看右边这张图，小数据那一段，两条曲线几乎是重合的。
[click] code review 呢？也不报，因为代码可读性甚至比正确答案还好。

[click] 四道防线，三道失效。剩下唯一一道，是**有复杂度直觉的人，扫一眼循环嵌套结构就知道不对**。

这个直觉，就是这门课要给你们的东西。
-->

---

# 他们不写代码，但<span class="text-teal-600 dark:text-teal-400">定义骨架</span>

<div class="mt-3 grid grid-cols-2 gap-4 text-sm">
  <div class="p-3 rounded bg-gray-500/8 opacity-60">
    <div class="text-xs tracking-widest mb-1">常见误读</div>
    <div class="line-through">三到七个人对 AI 说「给我写个系统」，然后等结果</div>
  </div>
  <div class="p-3 rounded bg-amber-500/10 border-l-4 border-amber-500">
    <div class="text-xs tracking-widest opacity-70 mb-1">事实</div>
    <div class="font-bold">他们是整个项目中最累、脑力密度最高的人</div>
  </div>
</div>

<div class="mt-5 text-xs tracking-widest opacity-60 mb-2">100 万行代码必须回答的结构性问题</div>

<div class="space-y-2 text-sm">

<div v-click="1" class="flex items-center gap-4 p-2.5 rounded border border-teal-500/25 bg-teal-500/5">
  <div class="flex-1">核心数据流用什么<span class="font-bold">数据结构</span>组织</div>
  <div class="w-64 text-xs opacity-75">线性表、树、图、散列</div>
</div>

<div v-click="2" class="flex items-center gap-4 p-2.5 rounded border border-teal-500/25 bg-teal-500/5">
  <div class="flex-1">缓存策略选 <span class="font-bold">LRU</span> 还是 <span class="font-bold">LFU</span>，容量多大，怎么失效</div>
  <div class="w-64 text-xs opacity-75">哈希表 + 双向链表、优先队列</div>
</div>

<div v-click="3" class="flex items-center gap-4 p-2.5 rounded border border-teal-500/25 bg-teal-500/5">
  <div class="flex-1">并发控制用<span class="font-bold">锁</span>还是<span class="font-bold">无锁队列</span></div>
  <div class="w-64 text-xs opacity-75">队列、原子操作</div>
</div>

<div v-click="4" class="flex items-center gap-4 p-2.5 rounded border border-teal-500/25 bg-teal-500/5">
  <div class="flex-1">索引建在哪一列，用 <span class="font-bold">B+ 树</span>还是<span class="font-bold">哈希</span></div>
  <div class="w-64 text-xs opacity-75">树、散列、范围查询</div>
</div>

</div>

<div v-click="5" class="mt-4 text-center">
右边这一列，<span v-mark.underline.orange="5">没有一项在这门课之外</span>。
</div>

<UnitNav :active="4" />

<!--
我们回到开头 OpenAI 那个案例。很多人看完那篇文章的第一反应是：那三到七个人肯定爽得不行，对 AI 说一句"给我写个系统"，然后喝咖啡等结果。

恰恰相反。那篇文章通篇在讲的是：他们是整个项目里最累、脑力密度最高的人。他们的累法变了，不是手累，是脑子累。

他们不写代码，但他们定义骨架。AI 生成了一百万行代码，但这一百万行代码——

[click] 核心数据流用什么结构组织？
[click] 缓存策略选 LRU 还是 LFU、容量开多大、怎么失效？
[click] 并发控制用锁还是无锁队列？
[click] 索引建在哪一列、用 B+ 树还是哈希？

这些决定系统生死的骨架，全部由人类工程师基于数据结构功底做出。

[click] 你看右边这一列——LRU 是哈希表加双向链表，LFU 要用优先队列，索引选型是树和散列的取舍。**没有一项在这门课之外。**
-->

---

# 角色转变

<div class="mt-6 flex items-center justify-center gap-6">
  <div class="px-5 py-3 rounded-lg bg-gray-500/10 text-xl opacity-60 line-through">代码编写者</div>
  <div class="text-3xl opacity-40">→</div>
  <div class="px-5 py-3 rounded-lg bg-teal-500/15 text-teal-700 dark:text-teal-300 text-xl font-bold">高密度的技术决策者与验证者</div>
</div>

<div grid="~ cols-[1fr_1.2fr] gap-8" class="mt-8 items-center">

<div class="space-y-3">
  <div class="p-4 rounded-lg border-2 border-teal-500/40 bg-teal-500/8">
    <div class="text-xs tracking-widest opacity-60 mb-1">人</div>
    <div class="text-xl font-bold text-teal-700 dark:text-teal-300">数据结构与算法策略</div>
    <div class="text-sm mt-1">＝ 这 100 万行代码的<span class="font-bold">灵魂</span></div>
  </div>
  <div class="p-4 rounded-lg border border-gray-400/30 bg-gray-500/8">
    <div class="text-xs tracking-widest opacity-60 mb-1">AI</div>
    <div class="text-xl font-bold">肌肉与手脚</div>
    <div class="text-sm mt-1 opacity-75">效率极高，永不疲倦</div>
  </div>
</div>

<div>

<div class="w-[62%] mx-auto py-2 rounded-lg border-2 border-teal-500/50 bg-teal-500/15 text-center font-bold text-teal-700 dark:text-teal-300">
  人类决策层 · 数据结构与算法策略
</div>

<div class="text-center text-2xl leading-none text-teal-600 dark:text-teal-400 py-1">↓</div>

<div class="w-[80%] mx-auto py-3 rounded-lg border border-gray-400/40 bg-gray-500/12 text-center font-bold">
  AI 生成层
</div>

<div class="text-center text-2xl leading-none opacity-40 py-1">↓</div>

<div class="w-full py-5 rounded-lg border border-gray-400/30 bg-gray-500/8 text-center text-xl font-bold opacity-75">
  100 万行代码
</div>

<div class="text-center text-xs opacity-65 mt-3">上层薄、下层厚，但方向自上而下决定</div>
</div>

</div>

<UnitNav :active="4" />

<!--
所以本质的转变是：从"代码编写者"变成"高密度的技术决策者与验证者"。

AI 是肌肉和手脚，效率极高，永不疲倦。而人提供的数据结构与算法策略，才是这一百万行代码的灵魂。

你看右边这张图：人类决策层很薄，AI 生成层厚一些，产出的一百万行代码最厚。但箭头方向是自上而下的——最薄的那一层决定了最厚那一层长什么样。
-->

---

# 杠杆效应：实现越便宜，决策错误越贵

<div grid="~ cols-[1.25fr_1fr] gap-7" class="mt-5">

<div class="space-y-3">

<div class="p-4 rounded-lg border border-gray-400/30 bg-gray-500/8">
  <div class="text-xs tracking-widest opacity-60 mb-2">AI 之前 · 架构选错</div>
  <div class="text-sm">手写<span class="font-bold">三个月</span>才发现问题</div>
  <div class="mt-2 pt-2 border-t border-gray-400/20 text-sm">
    沉没成本 ＝ <span class="font-bold">三个月人力</span>
    <span class="text-xs opacity-60 ml-1">很痛，但可控</span>
  </div>
</div>

<div v-click="1" class="p-4 rounded-lg border-2 border-rose-500/40 bg-rose-500/8">
  <div class="text-xs tracking-widest opacity-60 mb-2">AI 之后 · 架构选错</div>
  <div class="text-sm"><span class="font-bold">三天</span>生成 10 万行基于错误架构的代码，<span class="opacity-80">而且全都能跑、能过测试</span></div>
  <div class="mt-2 pt-2 border-t border-rose-500/20 text-sm">
    沉没成本 ＝ <span class="font-bold text-rose-600 dark:text-rose-400">10 万行代码 + 已建立在其上的全部依赖</span>
  </div>
</div>

</div>

<div class="flex items-center">
<svg viewBox="0 0 300 200" class="w-full">
  <line x1="40" y1="170" x2="285" y2="170" stroke="currentColor" stroke-width="1.2" opacity="0.5" />
  <line x1="40" y1="170" x2="40" y2="15" stroke="currentColor" stroke-width="1.2" opacity="0.5" />
  <path d="M 40 165 Q 150 155 210 95 T 275 20" fill="none" stroke="rgb(225,29,72)" stroke-width="3" />
  <circle cx="105" cy="158" r="4.5" fill="rgb(148,163,184)" />
  <text fill="rgb(71,85,105)" x="112" y="154" style="font-size:14px">AI 之前</text>
  <circle cx="258" cy="35" r="4.5" fill="rgb(225,29,72)" />
  <text x="196" y="30" style="font-size:14px" fill="rgb(225,29,72)" font-weight="bold">AI 之后</text>
  <text fill="rgb(71,85,105)" x="95" y="188" style="font-size:14px">实现速度 →</text>
  <text fill="rgb(71,85,105)" x="-158" y="15" style="font-size:12px" transform="rotate(-90)">决策错误的沉没成本</text>
</svg>
</div>

</div>

<div v-click="2" class="mt-5 p-4 rounded-lg border-2 border-amber-500/40 bg-amber-500/8 text-center">
  <div class="text-2xl font-bold">写得越快，选错的代价越高。</div>
  <div class="text-sm mt-1.5 opacity-80">这是「选型与验证」在 AI 时代<span class="font-bold">升值而非降值</span>的根本原因。</div>
</div>

<UnitNav :active="4" />

<!--
最后这一点，我希望你们想清楚，因为它反直觉。

AI 之前，架构选错了怎么样？你手写三个月，写到一半发现不对，回头改。损失三个月，很痛，但可控。

[click] AI 之后，架构选错了怎么样？三天之内，AI 帮你把这个错误架构生成了十万行代码，而且这十万行全都能跑、能过测试。等你发现不对的时候，已经有一堆东西建在它上面了。

[click] **实现变得几乎免费，于是决策错误的代价被放大了。写得越快，选错的代价越高。**

这就是为什么在 AI 时代，"选型"和"验证"这两件事的价值是上升的，不是下降的。这跟很多人的直觉相反，但这是杠杆的基本性质：杠杆放大的是你推的方向，方向错了它一样放大。
-->

---
layout: center
class: text-center
---

# 最后一条理由

<div class="mt-10 p-8 rounded-lg border-2 border-teal-500/40 bg-teal-500/5 max-w-4xl mx-auto">

<div class="text-2xl font-bold leading-relaxed">
LLM 训练与推理栈的每一次关键性能突破，<br>背后都站着一个<span class="text-teal-700 dark:text-teal-300">经典数据结构问题</span>。
</div>

</div>

<div v-click class="mt-6 text-xl">
数据结构在 AI 领域不是<span class="line-through decoration-rose-500 decoration-2 opacity-60">外围课程</span>，而是<span class="font-bold text-teal-700 dark:text-teal-300">核心课程</span>。
</div>

<UnitNav :active="5" />

<!--
最后一条理由。有同学觉得，数据结构是一门很老的课，跟 AI 是两个世界的事——AI 那边是矩阵、是梯度、是 Transformer，跟树跟图有什么关系。

[click] 我这一节就讲一件事：**大模型训练与推理栈的每一次关键性能突破，背后都站着一个经典数据结构问题。** 你想做 AI，数据结构不是外围，是核心。
-->

---

# 推理侧 · 新闻里的名词，背后都是<span class="text-teal-600 dark:text-teal-400">经典问题</span>

<div grid="~ cols-2 gap-x-5 gap-y-2.5" class="mt-4 text-sm">

<div v-click="1" class="p-2.5 rounded border border-gray-400/25 bg-gray-500/5">
  <div class="font-bold">KV Cache 分页管理<span class="text-xs opacity-60 font-normal"> · PagedAttention / vLLM</span></div>
  <div class="text-xs mt-1 text-teal-700 dark:text-teal-300">分页 + 间接索引表　<span class="opacity-70">与内存分配器、OS 页表同源</span></div>
</div>

<div v-click="2" class="p-2.5 rounded border border-gray-400/25 bg-gray-500/5">
  <div class="font-bold">前缀复用<span class="text-xs opacity-60 font-normal"> · Prefix Caching</span></div>
  <div class="text-xs mt-1 text-teal-700 dark:text-teal-300">Trie／压缩基数树 + 引用计数 + LRU</div>
</div>

<div v-click="3" class="p-2.5 rounded border border-gray-400/25 bg-gray-500/5">
  <div class="font-bold">向量检索 / RAG<span class="text-xs opacity-60 font-normal"> · 亿级 top-k</span></div>
  <div class="text-xs mt-1 text-teal-700 dark:text-teal-300">HNSW（多层图，跳表式分层导航）、IVF 倒排、乘积量化</div>
</div>

<div v-click="4" class="p-2.5 rounded border border-gray-400/25 bg-gray-500/5">
  <div class="font-bold">采样<span class="text-xs opacity-60 font-normal"> · top-k / top-p</span></div>
  <div class="text-xs mt-1 text-teal-700 dark:text-teal-300">全排序 O(V log V) ｜ 堆 O(V log k) ｜ 快速选择 O(V)</div>
</div>

<div v-click="5" class="p-2.5 rounded border border-gray-400/25 bg-gray-500/5">
  <div class="font-bold">投机解码 / Beam Search</div>
  <div class="text-xs mt-1 text-teal-700 dark:text-teal-300">优先队列；草稿构成 token 树，验证是树上批量匹配</div>
</div>

<div v-click="5" class="p-2.5 rounded border border-gray-400/25 bg-gray-500/5">
  <div class="font-bold">连续批处理<span class="text-xs opacity-60 font-normal"> · continuous batching</span></div>
  <div class="text-xs mt-1 text-teal-700 dark:text-teal-300">调度队列、优先级队列、抢占与公平性</div>
</div>

<div v-click="5" class="p-2.5 rounded border border-gray-400/25 bg-gray-500/5">
  <div class="font-bold">结构化解码<span class="text-xs opacity-60 font-normal"> · JSON／正则约束</span></div>
  <div class="text-xs mt-1 text-teal-700 dark:text-teal-300">有限状态自动机 + Trie，在词表上生成掩码</div>
</div>

<div v-click="6" class="p-2.5 rounded border-2 border-amber-500/45 bg-amber-500/10">
  <div class="font-bold">FlashAttention</div>
  <div class="text-xs mt-1 text-amber-700 dark:text-amber-300">分块 tiling + cache／SRAM 局部性 —— <span class="font-bold">即「知识不死，而且变贵」的又一次应验</span></div>
</div>

</div>

<div v-click="7" class="mt-4 text-center text-sm opacity-80">
2022 年的顶级论文，用的是 <span class="font-bold">1980 年代</span>的道理。
</div>

<UnitNav :active="5" />

<!--
快速看一眼，因为这些内容不是几分钟内能讲清楚的。

[click] 第一条，KV Cache 分页。大模型推理最吃显存的就是 KV cache，而且每个请求长度不一样，显存会碎掉。vLLM 的解法叫 PagedAttention——把 KV cache 切成固定大小的块，用一张块表把逻辑上的序列映射到物理块上。听着熟悉吗？这就是操作系统的页表，就是内存分配器解决碎片的老办法，原封不动地搬到显存上。（此处可板书手画：逻辑块 → 块表 → 物理块）

[click] 第二条，前缀复用。很多请求前面挂着同一段 system prompt，几千个 token 一模一样，重复算就是浪费。解法是把所有请求的 token 序列组织成一棵压缩基数树，共同前缀共享同一份 KV，加引用计数，加 LRU 淘汰。一棵 Trie 加一个 LRU——两个都是这门课的内容。

[click] 第三条，向量检索。RAG 要在上亿个向量里找最近邻，主流方案叫 HNSW，全称 Hierarchical Navigable Small World。它是一个多层图，上层稀疏、下层密集，从上往下逐层缩小搜索范围。它的分层导航思想，跟跳表是一回事。

[click] 第四条，采样。top-k 采样，从几万个词里挑前 k 个。你要是全排序，O(V log V)；用堆，O(V log k)；用快速选择，O(V)。这三个复杂度我们在排序和选择那一章讲。大模型每生成一个 token 都要做这个决定，一秒钟做几十次。

[click] 中间这三条你们自己看，投机解码是优先队列加 token 树，连续批处理是调度队列，结构化解码是自动机加 Trie。

[click] 最后一条，FlashAttention——这个是近几年最有名的推理优化之一，它的核心思想就是分块，让数据待在 SRAM 里别来回搬。**这就是 cache 局部性。**

[click] 我在前面说过，编译器吃掉了手写汇编，但 cache 局部性反而变贵了。这是 2022 年的顶级论文，用的是 1980 年代的道理。
-->

---

# 训练侧 · 流水线上的每一步，背后都是<span class="text-teal-600 dark:text-teal-400">经典问题</span>

<div class="mt-4 text-sm">

<div class="flex gap-4 pb-1.5 mb-1 border-b border-gray-400/30 text-xs tracking-wide opacity-55">
  <div class="w-64 shrink-0">AI 系统技术</div>
  <div class="flex-1">底层数据结构与算法</div>
</div>

<div class="flex gap-4 py-2 rounded border-2 border-amber-500/45 bg-amber-500/10 my-1">
  <div class="w-64 shrink-0 font-bold pl-2">训练语料去重<span class="text-xs opacity-60 font-normal"> · 万亿 token 级</span></div>
  <div class="flex-1 text-amber-700 dark:text-amber-300 font-bold">MinHash + LSH、<span v-mark.circle.orange="1">Bloom filter</span>、SimHash</div>
</div>

<div class="flex gap-4 py-1.5 border-b border-gray-400/15 opacity-65">
  <div class="w-64 shrink-0">Tokenizer / BPE 训练与编码</div>
  <div class="flex-1">优先队列 + 双向链表；Trie／Aho-Corasick 最长匹配</div>
</div>

<div class="flex gap-4 py-2 rounded border-2 border-amber-500/45 bg-amber-500/10 my-1">
  <div class="w-64 shrink-0 font-bold pl-2">自动微分 / 反向传播</div>
  <div class="flex-1 text-amber-700 dark:text-amber-300 font-bold">计算图是 <span v-mark.circle.orange="2">DAG</span>；反向传播 = 拓扑排序的逆序遍历</div>
</div>

<div class="flex gap-4 py-1.5 border-b border-gray-400/15 opacity-65">
  <div class="w-64 shrink-0">梯度检查点</div>
  <div class="flex-1">典型时间-空间权衡；最优重算策略可用动态规划求解</div>
</div>

<div class="flex gap-4 py-1.5 border-b border-gray-400/15 opacity-65">
  <div class="w-64 shrink-0">稀疏张量 / 图神经网络</div>
  <div class="flex-1">CSR／CSC 稀疏格式、邻接表、图遍历</div>
</div>

<div class="flex gap-4 py-1.5 border-b border-gray-400/15 opacity-65">
  <div class="w-64 shrink-0">MoE 路由</div>
  <div class="flex-1">top-k 选择 + 负载均衡（分配／装箱问题）</div>
</div>

<div class="flex gap-4 py-1.5 border-b border-gray-400/15 opacity-65">
  <div class="w-64 shrink-0">分布式 All-Reduce</div>
  <div class="flex-1">Ring／树形归约；通信复杂度由树结构决定</div>
</div>

<div class="flex gap-4 py-1.5 opacity-65">
  <div class="w-64 shrink-0">Embedding 表 / 特征哈希</div>
  <div class="flex-1">哈希函数设计、冲突处理、hash trick</div>
</div>

</div>

<UnitNav :active="5" />

<!--
训练这一侧我快速扫过，你们回去自己看，我只点两行。

[click] **第一行，训练语料去重。** 万亿 token 级的语料，要判断这段文本之前有没有见过。用什么？MinHash 加 LSH、SimHash，还有——Bloom filter。请你们回想一下前面那次对照实验，Prompt B 的答案是什么？就是这个东西。

[click] **自动微分那一行。** 反向传播是怎么实现的？前向的时候把所有运算记成一张有向无环图，反向的时候按拓扑排序的逆序遍历这张图，逐个节点传梯度。所以你每次调 loss.backward()，PyTorch 在底下做的就是一次图的拓扑遍历。DAG 和拓扑排序，我们图那一章讲。（可板书手画：计算图 DAG + 拓扑逆序回传）

[click] 我当时出那道题不是编的，那是大模型训练流水线里每天在跑的真实生产问题。你们今天已经会问这道题了。其余几行你们自己对着课程目录看。
-->

---
layout: center
class: text-center
---

# 一句话收

<div class="mt-8 space-y-4 max-w-4xl mx-auto">

<div class="p-5 rounded-lg border border-gray-400/30 bg-gray-500/5">
  <div class="text-xl">
    大模型的<span class="font-bold">能力上限</span>　←　由<span class="font-bold">算法研究</span>决定
  </div>
</div>

<div v-click class="p-6 rounded-lg border-2 border-teal-500/45 bg-teal-500/8">
  <div class="text-xl leading-relaxed">
    它能否<span class="font-bold">跑得起来、跑得便宜、跑得稳定</span><br>
    ←　几乎完全由<span class="font-bold text-teal-700 dark:text-teal-300">数据结构与系统实现</span>决定
  </div>
</div>

</div>

<div v-click class="mt-6 text-sm opacity-75">
今天这个行业里工资最高的一批工程师，做的就是<span class="font-bold">后面这件事</span>。
</div>

<UnitNav :active="5" />

<!--
一句话收：大模型的能力上限，由算法研究决定；

[click] 但它能不能跑起来、跑得便不便宜、稳不稳定，几乎完全由数据结构和系统实现决定。

[click] 今天这个行业里工资最高的一批工程师，做的就是后面这件事。

（如现场有时间，可对着课程目录点几个结构名，说明本课覆盖率；不必逐条展开。）
-->

---
layout: section
---

# 那么这学期，我到底该练什么

<div class="pt-4 text-sm opacity-60">
五条理由走完，回答最实际的那个问题
</div>

<!--
走完五条理由，现在回答那个最实际的问题：既然有的贬值有的升值，这学期我到底该把时间花在哪儿？

我用布鲁姆教育目标分类法来说。这是教育学里描述认知层次的经典框架，六层，从记忆、理解、应用，到分析、评价、创造。
-->

---
layout: full
---

<div class="h-full flex flex-col px-10 py-6">

<div class="text-center shrink-0">
  <div class="text-2xl font-bold">布鲁姆六层能力 · AI 前后的权重变化</div>
  <div class="text-xs opacity-55 mt-1">下三层缩，上三层涨</div>
</div>

<div class="flex-1 flex mt-4 min-h-0">

<div class="flex-1 text-sm min-h-0 flex flex-col justify-center gap-2">

<div class="flex gap-3 px-1 pb-1 border-b border-gray-400/30 text-xs tracking-wide opacity-55">
  <div class="w-14 shrink-0">层次</div>
  <div class="flex-1">典型行为</div>
  <div class="w-28 shrink-0 text-center">权重</div>
</div>

<div v-click="1" class="flex gap-3 items-center px-1 py-2">
  <div class="w-14 shrink-0 font-bold">6 创造</div>
  <div class="flex-1">把模糊业务问题形式化成带约束的规格；设计组合型结构</div>
  <div class="w-28 shrink-0 text-center text-xs"><span class="opacity-45">★</span> <span class="text-teal-600 dark:text-teal-400 font-bold">→ ★★★★★</span></div>
</div>

<div v-click="1" class="flex gap-3 items-center px-1 py-2">
  <div class="w-14 shrink-0 font-bold">5 评价</div>
  <div class="flex-1">在多个可行方案间取舍：时间／空间／精度／一致性／成本</div>
  <div class="w-28 shrink-0 text-center text-xs"><span class="opacity-45">★</span> <span class="text-teal-600 dark:text-teal-400 font-bold">→ ★★★★★</span></div>
</div>

<div v-click="1" class="flex gap-3 items-center px-1 py-2">
  <div class="w-14 shrink-0 font-bold">4 分析</div>
  <div class="flex-1">复杂度分析、瓶颈定位、识别 AI 方案中的 O(n²)</div>
  <div class="w-28 shrink-0 text-center text-xs"><span class="opacity-45">★★</span> <span class="text-teal-600 dark:text-teal-400 font-bold">→ ★★★★★</span></div>
</div>

<div v-click="2" class="flex gap-3 items-center px-1 py-2 rounded bg-amber-500/10 border border-amber-500/30">
  <div class="w-14 shrink-0 font-bold">3 应用</div>
  <div class="flex-1">从「照实现写代码」转为「选型 + 委托 + 验证」</div>
  <div class="w-28 shrink-0 text-center text-xs"><span class="opacity-45">★★★★</span> <span class="text-rose-600 dark:text-rose-400 font-bold">→ ★★</span></div>
</div>

<div v-click="3" class="flex gap-3 items-center px-1 py-2 rounded bg-teal-500/12 border border-teal-500/35">
  <div class="w-14 shrink-0 font-bold">2 理解</div>
  <div class="flex-1">解释不变量、解释复杂度成因 —— <span class="font-bold">不降反升</span></div>
  <div class="w-28 shrink-0 text-center text-xs"><span class="opacity-45">★★★</span> <span class="text-teal-600 dark:text-teal-400 font-bold">→ ★★★★</span></div>
</div>

<div v-click="2" class="flex gap-3 items-center px-1 py-2 rounded bg-amber-500/10 border border-amber-500/30">
  <div class="w-14 shrink-0 font-bold">1 记忆</div>
  <div class="flex-1">背 API、背旋转代码 —— 但保留最小集：<span class="font-bold">概念名词表</span></div>
  <div class="w-28 shrink-0 text-center text-xs"><span class="opacity-45">★★★★</span> <span class="text-rose-600 dark:text-rose-400 font-bold">→ ★</span></div>
</div>

<div v-click="4" class="mt-2 p-2.5 rounded-lg bg-teal-500/12 border-2 border-teal-500/40 text-center">
  <div class="text-lg font-bold">从「熟练工」往「决策者」转型</div>
  <div class="text-xs mt-0.5 opacity-80">理论联系实践，在课后实践中培养判断能力</div>
</div>

</div>
</div>
</div>

<!--
（对着权重列讲：箭头左边是 AI 之前的星级，右边是 AI 之后。）

[click] **上面三层，涨，而且是大涨。** 分析从两星涨到五星，评价从一星涨到五星，创造从一星涨到五星。

[click] **下面三层，缩。** 记忆从四星掉到一星，应用从四星掉到两星。为什么？因为 AI 就是干这个的。你花二十个小时练手写红黑树，练出来的能力，AI 三秒钟给你。

[click] 理解那一层我要单独说：它从三星涨到四星，**不降反升**。为什么？因为你不理解，你就没法审计 AI。你不知道 O(M×N) 是怎么来的，你就永远看不出那段区县循环有问题。理解是分析的地基，地基不能拆。

[click] 我把这张表的意思说白了：**这学期，从"熟练工"往"决策者"转型——理论联系实践，在课后实践中培养判断能力。**
-->

---

# 澄清一 · 记忆层不归零，是换内容

<div grid="~ cols-2 gap-6" class="mt-6">

<div class="p-5 rounded-lg border border-rose-500/30 bg-rose-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-2">归零的记忆</div>
  <div class="text-base">代码怎么写</div>
  <div class="text-xs mt-2 opacity-70 font-mono">rotateLeft 的 12 行<br>std::lower_bound 的参数顺序</div>
  <div class="mt-3 pt-2 border-t border-rose-500/20 text-sm font-bold text-rose-600 dark:text-rose-400">可完全外包给 AI</div>
</div>

<div v-click="1" class="p-5 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-2">升值的记忆</div>
  <div class="text-base font-bold">概念名词及其适用条件</div>
  <div class="text-xs mt-2 opacity-70">「有这么个东西，它在什么情况下该用」</div>
  <div class="mt-3 pt-2 border-t border-teal-500/20 text-sm font-bold text-teal-600 dark:text-teal-400">不可外包</div>
</div>

</div>

<div v-click="2" class="mt-6 p-4 rounded-lg bg-amber-500/10 border-l-4 border-amber-500">

<div class="text-xs tracking-widest opacity-60 mb-2">为什么不可外包 —— 回到那次对照实验</div>

<div class="text-lg leading-relaxed">
认知库里没有 <span class="font-mono font-bold">Bloom filter</span> 这个词，就<span class="font-bold">不可能提出 Prompt B</span>。<br>
<span class="text-base opacity-85">AI 能给答案，但不能替你想到「应该提这个问题」。</span>
</div>

</div>

<!--
这里有个地方极容易被误读，我必须澄清：**我说的不是"记忆没用了"，我说的是"要记的东西换了"。**

归零的是"代码怎么写"——rotateLeft 那十二行，lower_bound 的参数顺序，忘了就忘了，问 AI。

[click] 升值的是"概念名词，以及它的适用条件"。这个不能外包。

[click] 理由回到那次对照实验：**你脑子里没有 Bloom filter 这个词，你就永远问不出 Prompt B。** AI 能给你答案，但它不能替你想到"我应该问这个问题"。想到问题是你的活。
-->

---

# 我们要理解的知识，长这个样子

<div class="mt-3 text-sm">

<div class="flex gap-4 pb-1.5 mb-1 border-b border-gray-400/30 text-xs tracking-wide opacity-55">
  <div class="flex-[1.5]">需求特征</div>
  <div class="w-52 shrink-0">首选结构</div>
  <div class="flex-1">关键代价</div>
</div>

<div v-click="1" class="flex gap-4 py-2 rounded border-2 border-amber-500/40 bg-amber-500/10 my-1">
  <div class="flex-[1.5] pl-2">只判断存在性，允许极小误判，内存紧张</div>
  <div class="w-52 shrink-0 font-bold">Bloom filter</div>
  <div class="flex-1 text-rose-600 dark:text-rose-400">假阳性；不支持删除</div>
</div>

<div v-click="2" class="flex gap-4 py-2 border-b border-gray-400/15">
  <div class="flex-[1.5] pl-2">需要有序 + 范围查询</div>
  <div class="w-52 shrink-0 font-bold">平衡树／跳表／B+ 树</div>
  <div class="flex-1 text-rose-600 dark:text-rose-400">O(log n)；常数大于哈希</div>
</div>

<div v-click="3" class="flex gap-4 py-2 rounded border-2 border-amber-500/40 bg-amber-500/10 my-1">
  <div class="flex-[1.5] pl-2">只按 key 精确查找</div>
  <div class="w-52 shrink-0 font-bold">哈希表</div>
  <div class="flex-1 text-rose-600 dark:text-rose-400">无序；最坏 O(n)；扩容抖动</div>
</div>

<div v-click="4" class="flex gap-4 py-2 border-b border-gray-400/15">
  <div class="flex-[1.5] pl-2">反复取极值 + 动态插入</div>
  <div class="w-52 shrink-0 font-bold">堆／优先队列</div>
  <div class="flex-1 text-rose-600 dark:text-rose-400">不支持高效查找任意元素</div>
</div>

<div v-click="4" class="flex gap-4 py-2 border-b border-gray-400/15">
  <div class="flex-[1.5] pl-2">大量前缀共享的字符串集合</div>
  <div class="w-52 shrink-0 font-bold">Trie／基数树</div>
  <div class="flex-1 text-rose-600 dark:text-rose-400">内存开销大；指针跳转不利于 cache</div>
</div>

<div v-click="4" class="flex gap-4 py-2 border-b border-gray-400/15">
  <div class="flex-[1.5] pl-2">数据超出内存、只能顺序读</div>
  <div class="w-52 shrink-0 font-bold">外部排序／流式算法</div>
  <div class="flex-1 text-rose-600 dark:text-rose-400">多趟 I/O</div>
</div>

<div v-click="4" class="flex gap-4 py-2">
  <div class="flex-[1.5] pl-2">关系是多对多连接</div>
  <div class="w-52 shrink-0 font-bold">图 + 邻接表</div>
  <div class="flex-1 text-rose-600 dark:text-rose-400">遍历顺序决定复杂度</div>
</div>

</div>

<div v-click="5" class="mt-3 p-3 rounded-lg bg-teal-500/12 border-2 border-teal-500/40 flex items-center gap-4">
  <div class="text-lg font-bold flex-1">这张表就是你和 AI 对话的<span class="text-teal-700 dark:text-teal-300">接口协议</span>。</div>
  <div class="text-sm opacity-80 shrink-0">期末考这张表，<span class="font-bold">不考任何一行具体代码</span>。</div>
</div>

<!--
所以这学期我们要理解的知识，长这个样子——你们看这张表。左边是需求的特征，中间是首选结构，右边是它的代价。

[click] 我举一行：第一行，只要判断存在性、允许极小误判、内存紧——你脑子里就要立刻蹦出 Bloom filter，同时立刻想到它的代价：有假阳性、而且不能删除。

[click] 第二行，要有序、要范围查询，平衡树、跳表、B+ 树。

[click] 第三行，只按 key 精确查——哈希表，代价是无序、最坏 O(n)、还有扩容抖动。

[click] 剩下四行你们自己看。这张表会跟着课程一章一章加行，每讲完一章我们就往上补。

[click] **这张表就是你跟 AI 对话的接口协议。** 你手上有这张表，你才能给出规格；你没有，你只能说"帮我写个函数"。期末我考这张表，不考任何一行具体代码。
-->

---

# 澄清二 · 那我一行都不写行不行？

<div class="mt-4 p-4 rounded-lg bg-rose-500/8 border-l-4 border-rose-500">

<div class="text-base leading-relaxed">
未经亲手实现，对复杂度的判断只是<span class="font-bold">背下来的字符串</span>，无法转化为可用直觉。<br>
由此产生<span class="font-bold text-rose-600 dark:text-rose-400">能力幻觉</span>（illusion of competence）：<span class="font-bold">读得懂，但判断不了。</span>
</div>

</div>

<div class="mt-5 text-sm">

<div class="flex items-baseline gap-3 mb-2">
  <div class="font-bold text-base">最小必要手写清单</div>
  <div class="text-xs opacity-65">四项，每项只做一次 · 目标是建立体感，不追求熟练度</div>
</div>

<div class="flex gap-4 pb-1.5 mb-1 border-b border-gray-400/30 text-xs tracking-wide opacity-55">
  <div class="w-6 shrink-0">#</div>
  <div class="flex-1">手写内容</div>
  <div class="flex-1">要获得的体感</div>
</div>

<div v-click="1" class="flex gap-4 py-2.5 border-b border-gray-400/15">
  <div class="w-6 shrink-0 font-bold opacity-45">1</div>
  <div class="flex-1 font-bold">链表<span class="font-normal opacity-70">（插入、删除、反转）</span></div>
  <div class="flex-1 text-teal-700 dark:text-teal-300">「O(1) 插入」的代价：随机访存与边界处理</div>
</div>

<div v-click="2" class="flex gap-4 py-2.5 border-b border-gray-400/15">
  <div class="w-6 shrink-0 font-bold opacity-45">2</div>
  <div class="flex-1 font-bold">递归在二叉树中的应用</div>
  <div class="flex-1 text-teal-700 dark:text-teal-300">树的问题 = 左子树 + 右子树 + 一步</div>
</div>

<div v-click="3" class="flex gap-4 py-2.5 border-b border-gray-400/15">
  <div class="w-6 shrink-0 font-bold opacity-45">3</div>
  <div class="flex-1 font-bold">哈希表<span class="font-normal opacity-70">（含冲突处理与扩容）</span></div>
  <div class="flex-1 text-teal-700 dark:text-teal-300">「O(1) 平均」背后的代价与最坏情况</div>
</div>

<div v-click="4" class="flex gap-4 py-2.5 border-b border-gray-400/15">
  <div class="w-6 shrink-0 font-bold opacity-45">4</div>
  <div class="flex-1 font-bold">堆／优先队列 + top-k 应用</div>
  <div class="flex-1 text-teal-700 dark:text-teal-300">O(n log n) 与 O(n log k) 的实际差距</div>
</div>

</div>

<div v-click="5" class="mt-4 p-3 rounded bg-amber-500/10 border-l-4 border-amber-500 text-sm">
<span class="font-bold">平衡树：旋转不用写，但要理解。</span>　重点是它维持什么不变量、为什么长成这样。
</div>

<!--
有同学听到这里会问：既然不考代码，那我一行都不写行不行？

不行。理由不是"传统上就得这么练"，是认知规律：**你没亲手实现过，你对复杂度的判断只是一串背下来的字符串，不是能用的直觉。** 你会得到一种很危险的状态，教育心理学叫"能力幻觉"——你读代码觉得都懂，一到要你判断这段代码在千万级数据下会不会崩，你答不出来。

所以我保留一个**很短**的手写清单，四项，每项只做一次，我不追求你熟练，我追求你有体感。

[click] 链表，先把手感找回来：指针怎么重连、边界条件是怎么冒出来的。

[click] 二叉树的递归——任何树的问题，都能拆成"左子树、右子树、合一步"；复杂度，顺着递归式就出来了。

[click] 哈希表，你要亲手感受一下"平均 O(1)"背后压着什么代价、最坏情况长什么样。

[click] 堆加 top-k，亲手对比一下 n log n 和 n log k 差多少。

[click] **注意：平衡树，旋转不用写，但要理解。** 我们会讲它的不变量、讲它为什么长成这样、讲它跟 B 树的关系——把"它在维持什么"说清楚，比写得出来重要。
-->

---
layout: center
class: text-center
---

# 这门课的目标

<div class="mt-6 p-6 rounded-lg border-2 border-teal-500/45 bg-teal-500/8 max-w-4xl mx-auto">

<div class="text-xs tracking-widest opacity-60 mb-3">AI 时代的能力分水岭下移了</div>

<div class="text-3xl font-bold leading-relaxed">
<span class="text-teal-700 dark:text-teal-300">判断的准确性</span>，<br>取代了<span class="opacity-60 line-through decoration-rose-500 decoration-2">实现的熟练度</span>。
</div>

</div>

<div v-click="1" class="mt-6 text-xl font-bold">
不做被 AI 替代的程序员，做<span v-mark.circle.orange="2">驾驭 AI 的构建者</span>。
</div>

<div grid="~ cols-2 gap-5" class="mt-6 max-w-4xl mx-auto text-left">

<div v-click="3" class="p-4 rounded-lg border border-rose-500/30 bg-rose-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-2">被替代的角色</div>
  <div class="text-base">把明确规格<span class="font-bold">翻译成代码</span>的人</div>
</div>

<div v-click="4" class="p-4 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-2">不可替代的角色</div>
  <div class="text-base">定义规格、选择骨架、验证产出、<span class="font-bold text-teal-700 dark:text-teal-300">承担后果</span>的人</div>
</div>

</div>

<div v-click="5" class="mt-5 text-base">
后者的全部判断依据，<span class="font-bold">就是这门课的内容</span>。
</div>

<!--
这一节收一句：**AI 时代的能力分水岭下移了。不再是"你会不会写"，而是"你判断得准不准"。**

[click] 所以这门课的目标，我用一句话讲清楚：**不要做被 AI 替代的程序员，要做驾驭 AI 的构建者。**

[click] 我把这两种人的界线划清楚。

[click] 被替代的是谁？是把明确规格翻译成代码的人——因为这件事 AI 做得比你好，而且更便宜。

[click] 不可替代的是谁？是定义规格、选择骨架、验证产出、并且**为结果承担后果**的人。最后这四个字很重要：承担后果。AI 不承担后果。系统崩了，是你去救。

[click] 而你能不能救，取决于你脑子里有没有这门课的东西。

————————————————
【教师口袋问题｜时间富余或学生质疑时口头抛出，不翻页】

Q1　三次跃迁表第四行"人写 → AI 生成"，五年后回看还会有哪些内容被吃掉？
　→ 设计模式？部分系统设计经验？引导学生自己把这张表往前推。

Q2　如果 AI 强到能自行判断"此处应用 Bloom filter"，"概念名词不可外包"的论证是否还成立？
　→ 仍成立：内存预算与误判容忍度属**业务事实**而非技术推理，AI 无法自行获取。这个问题很好，值得当场表扬。

Q3　网格聚合案例里，如果区县只有 5 个、只跑一次，原方案有问题吗？
　→ 没有问题。"更优"永远相对于约束而言——这正是"评价"层能力的核心。
-->

---

# 课程参考教材

<div v-click="1" class="mt-6 flex items-baseline gap-4 p-3.5 rounded-lg border-2 border-teal-500/40 bg-teal-500/8">
  <div class="w-20 shrink-0 text-xs tracking-widest opacity-60">教材</div>
  <div class="text-xl font-bold">自编讲义</div>
</div>

<div v-click="2" class="mt-5">

<div class="mb-1 text-xs tracking-widest opacity-55">参考教材</div>

<div class="flex items-baseline gap-4 py-2.5 border-b border-gray-400/15">
  <div class="flex-1 font-bold">《数据结构（C语言版）》</div>
  <div class="w-72 shrink-0 text-sm opacity-70">严蔚敏 · 清华大学出版社</div>
</div>

<div class="flex items-baseline gap-4 py-2.5 border-b border-gray-400/15">
  <div class="flex-1 font-bold">《数据结构与算法之美》</div>
  <div class="w-72 shrink-0 text-sm opacity-70">王争 · 人民邮电出版社</div>
</div>

<div class="flex items-baseline gap-4 py-2.5 border-b border-gray-400/15">
  <div class="flex-1 font-bold">《数据结构与算法分析——C语言描述》</div>
  <div class="w-72 shrink-0 text-sm opacity-70">马克·艾伦·维斯 · 机械工业出版社</div>
</div>

<div class="flex items-baseline gap-4 py-2.5">
  <div class="flex-1 font-bold">《算法》</div>
  <div class="w-72 shrink-0 text-sm opacity-70">Robert Sedgewick · 人民邮电出版社</div>
</div>

</div>

<!--
最后把教材交代两句。

[click] 主教材是我的**自编讲义**，跟着课程进度走。

[click] 下面四本是参考教材——不用每本都从头读，挑一本对你胃口的跟着翻；哪一章卡住了，回来对着查。
-->

---

# 考核方式

<div class="mt-6 flex items-stretch gap-5">

<div v-click="1" class="w-[60%] shrink-0 p-4 rounded-lg border-2 border-teal-500/40 bg-teal-500/8">
  <div class="flex items-baseline justify-between px-0.5">
    <div class="text-lg font-bold text-teal-700 dark:text-teal-300">平时成绩</div>
    <div class="text-3xl font-bold text-teal-600 dark:text-teal-400">60%</div>
  </div>
  <div class="mt-3">
    <div class="flex items-baseline gap-3 py-1.5 border-b border-gray-400/15">
      <div class="w-28 shrink-0 text-sm font-bold">考勤</div>
    </div>
    <div class="flex items-baseline gap-3 py-1.5 border-b border-gray-400/15">
      <div class="w-28 shrink-0 text-sm font-bold">作业 <span class="text-teal-600 dark:text-teal-400">10%</span></div>
      <div class="flex-1 text-xs opacity-65">教学云平台提交，开放性作业为主</div>
    </div>
    <div class="flex items-baseline gap-3 py-1.5 border-b border-gray-400/15">
      <div class="w-28 shrink-0 text-sm font-bold">综合实践 <span class="text-teal-600 dark:text-teal-400">40%</span></div>
    </div>
    <div class="flex items-baseline gap-3 py-1 pl-7 border-b border-gray-400/15">
      <div class="w-16 shrink-0 text-xs font-bold opacity-80">独立 ×2</div>
      <div class="flex-1 text-xs opacity-65">各 10 分 · 单独完成 · 提交答辩讲解视频到云平台</div>
    </div>
    <div class="flex items-baseline gap-3 py-1 pl-7 border-b border-gray-400/15">
      <div class="w-16 shrink-0 text-xs font-bold opacity-80">团队 ×1</div>
      <div class="flex-1 text-xs opacity-65">20 分 · 3 人 1 组 · 线下答辩验收</div>
    </div>
    <div class="flex items-baseline gap-3 py-1.5">
      <div class="w-28 shrink-0 text-sm font-bold">期中 <span class="text-teal-600 dark:text-teal-400">10%</span></div>
      <div class="flex-1 text-xs opacity-65">闭卷考试</div>
    </div>
  </div>
</div>

<div v-click="2" class="flex-1 flex flex-col p-4 rounded-lg border-2 border-gray-400/25 bg-gray-500/5">
  <div class="flex items-baseline justify-between px-0.5">
    <div class="text-lg font-bold">期末考试</div>
    <div class="text-3xl font-bold opacity-80">40%</div>
  </div>
  <div class="mt-3 flex-1 flex flex-col justify-center gap-4">
    <div class="flex items-baseline gap-3">
      <div class="w-14 shrink-0 text-sm font-bold opacity-80">形式</div>
      <div class="flex-1 text-sm">闭卷考试</div>
    </div>
    <div class="flex items-baseline gap-3">
      <div class="w-14 shrink-0 text-sm font-bold text-teal-700 dark:text-teal-300">强化</div>
      <div class="flex-1 text-sm font-medium">算法思想和解决问题的能力</div>
    </div>
    <div class="flex items-baseline gap-3">
      <div class="w-14 shrink-0 text-sm font-bold opacity-55">弱化</div>
      <div class="flex-1 text-sm opacity-70">知识点考核</div>
    </div>
  </div>
</div>

</div>

<!--
考核方式，也说清楚——免得期末有人觉得意外。

[click] 大头在平时：平时成绩占 60%。构成呢——考勤，不单列比例；作业 10%，教学云平台提交，以开放性作业为主；综合实践占 40%，两次独立实践各 10 分，单独完成，答辩讲解视频提交到云平台，加一次团队实践 20 分，3 人 1 组完成，线下答辩验收；期中占 10%，闭卷。

[click] 期末考试占 40%，闭卷。注意它的口径——强化算法思想和解决问题的能力，弱化知识点考核。这跟前面讲的是一路话：这门课不测你背了多少，测你能不能想清楚、做对取舍。所以别等到期末，平时这 60% 都是能一点点挣回来的。

导论到这里就收尾了。下次课，我们正式进数据结构。
-->
