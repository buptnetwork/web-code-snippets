---
layout: section
---

# 讲一 · 协议报文与工具链

<div class="pt-3 text-sm opacity-60">
0.1 跑在哪里 · 0.2 HTML·URL·HTTP 报文 · 0.3 JSON · 0.4 终端与工具链 · 0.5 读报错 · 0.6 调试器（高光）
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

# 0.2 HTML：浏览器眼里的文档

<div class="text-xs opacity-55 -mt-1 mb-2">0.1 说浏览器跑 HTML·CSS·JS——这一页把 HTML 认全。<b class="text-teal-700 dark:text-teal-300">落点：表单提交，就是在发一个 HTTP 请求。</b></div>

<div grid="~ cols-2 gap-6" class="mt-1 text-sm">

<div>
<div class="text-xs tracking-widest opacity-60 mb-1.5">文档基本结构</div>

```html
<!DOCTYPE html>
<html lang="zh">
  <head><!-- 元信息：标题 / 编码 / 样式 --></head>
  <body><!-- 你看到的一切 --></body>
</html>
```

<div class="text-xs tracking-widest opacity-60 mt-3 mb-1.5">常用标签（认脸）</div>
<div class="flex flex-wrap gap-1.5 text-[11px]">
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 font-mono">div</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 font-mono">span</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 font-mono">p</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 font-mono">h1~h6</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 font-mono">ul / li</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 font-mono">a</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 font-mono">img</span>
<span class="px-2 py-0.5 rounded bg-gray-500/8 border border-gray-400/20 font-mono">table</span>
</div>

<div class="text-xs tracking-widest opacity-60 mt-3 mb-1.5">语义标签（结构即含义）</div>
<div class="flex flex-wrap gap-1.5 text-[11px]">
<span class="px-2 py-0.5 rounded bg-teal-500/10 border border-teal-500/25 font-mono">header</span>
<span class="px-2 py-0.5 rounded bg-teal-500/10 border border-teal-500/25 font-mono">nav</span>
<span class="px-2 py-0.5 rounded bg-teal-500/10 border border-teal-500/25 font-mono">main</span>
<span class="px-2 py-0.5 rounded bg-teal-500/10 border border-teal-500/25 font-mono">section</span>
<span class="px-2 py-0.5 rounded bg-teal-500/10 border border-teal-500/25 font-mono">article</span>
<span class="px-2 py-0.5 rounded bg-teal-500/10 border border-teal-500/25 font-mono">footer</span>
</div>
</div>

<div>
<div class="text-xs tracking-widest opacity-60 mb-1.5">表单全套 · 一个发帖表单</div>

```html
<form action="/posts" method="POST">
  <label>标题 <input name="title" required></label>
  <textarea name="body"></textarea>
  <select name="category"><option value="tech">技术</option></select>
  <button type="submit">发布</button>
</form>
```

<div class="mt-1.5 text-[11px] opacity-70"><code>input</code> 的 type：<span class="font-mono">text · password · email · number · checkbox · radio · file · hidden</span></div>

<div class="text-xs tracking-widest opacity-60 mt-3 mb-1.5">五个关键属性</div>
<div class="text-[12px] space-y-1">
<div class="flex gap-2"><code class="w-16 shrink-0 text-amber-600 dark:text-amber-400 font-bold">action</code><span class="opacity-85">提交到哪个 URL</span></div>
<div class="flex gap-2"><code class="w-16 shrink-0 text-amber-600 dark:text-amber-400 font-bold">method</code><span class="opacity-85">GET / POST</span></div>
<div class="flex gap-2"><code class="w-16 shrink-0 text-amber-600 dark:text-amber-400 font-bold">name</code><span class="opacity-85">字段名 → 请求体的键</span></div>
<div class="flex gap-2"><code class="w-16 shrink-0 text-amber-600 dark:text-amber-400 font-bold">value</code><span class="opacity-85">字段值 → 请求体的值</span></div>
<div class="flex gap-2"><code class="w-16 shrink-0 text-amber-600 dark:text-amber-400 font-bold">required</code><span class="opacity-85">空着不让提交</span></div>
</div>
</div>

</div>

<div v-click class="mt-2 p-2.5 rounded-lg bg-teal-500/8 border-l-4 border-teal-500 text-sm">
点「发布」那一刻：浏览器把每个 <code class="text-xs">name=value</code> 拼成请求体，按 <code class="text-xs">method</code> 发到 <code class="text-xs">action</code> 那个 URL——<b>这就是下一页要拆的 HTTP 请求。</b>
</div>

<!--
0.1 我们说浏览器里跑的是 HTML、CSS、JS。这一页把 HTML 认全——不用背，认脸就行。

左边，一个 HTML 文档就这么个骨架：DOCTYPE 声明、html 根、head 放元信息、body 放你看到的一切。常用标签这些 div、span、p、标题、列表、链接、图片、表格，你天天在网页上见到，现在知道它们叫什么。语义标签 header、nav、main、section、article、footer——它们和 div 长得一样，区别是「结构即含义」，浏览器和搜索引擎能读懂这块是页头还是正文。本课不考 CSS 布局，HTML 只要求看得懂、改得动。

右边是重点——表单。你看这个发帖表单：form 标签上有两个关键属性，action 和 method。action 是提交到哪个 URL，method 是用 GET 还是 POST。里面每个输入控件都有 name——title、body、category，这就是将来请求体里的键。required 是浏览器级校验，空着不让你提交。input 还有很多 type，密码、邮箱、数字、复选、单选、文件，今天认脸就行。

[click] 现在把这两页连起来：你点「发布」那一刻，浏览器干了什么？它把所有 name=value 拼成请求体，按 method 指定的方法，发到 action 那个 URL。这就是一个 HTTP 请求。表单，是 HTTP 请求最常见的源头。下一页我们就拆开这个请求看——URL 长什么样、报文长什么样。
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

# 0.2 HTTP 方法与状态码

<div class="text-xs opacity-55 -mt-1 mb-3">报文起始行里的两个关键词。<b class="text-amber-600 dark:text-amber-400">今天认脸，判据与修复留第 1 次课。</b></div>

<div grid="~ cols-2 gap-6" class="mt-2 text-sm">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">五个方法 · 你想对资源做什么</div>
<div class="rounded-lg overflow-hidden border border-gray-400/25 text-[13px]">
<div class="flex gap-2 px-3 py-1.5 border-b border-gray-400/15"><code class="w-16 shrink-0 font-bold text-teal-600 dark:text-teal-400">GET</code><span class="opacity-85">读一个资源（列表、详情）</span></div>
<div class="flex gap-2 px-3 py-1.5 border-b border-gray-400/15"><code class="w-16 shrink-0 font-bold text-teal-600 dark:text-teal-400">POST</code><span class="opacity-85">新建一个资源（发帖、注册）</span></div>
<div class="flex gap-2 px-3 py-1.5 border-b border-gray-400/15"><code class="w-16 shrink-0 font-bold text-amber-600 dark:text-amber-400">PUT</code><span class="opacity-85">整体替换一个资源</span></div>
<div class="flex gap-2 px-3 py-1.5 border-b border-gray-400/15"><code class="w-16 shrink-0 font-bold text-amber-600 dark:text-amber-400">PATCH</code><span class="opacity-85">局部修改一个资源</span></div>
<div class="flex gap-2 px-3 py-1.5"><code class="w-16 shrink-0 font-bold text-rose-600 dark:text-rose-400">DELETE</code><span class="opacity-85">删除一个资源</span></div>
</div>
<div class="mt-2 text-xs opacity-70">第 1 次课的五个接口，正好把这五个方法各用一次。</div>
</div>

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">状态码 · 服务端怎么回话</div>
<div class="space-y-1.5 text-[13px]">
<div class="flex gap-2 items-baseline"><span class="w-9 shrink-0 font-mono font-bold text-teal-700 dark:text-teal-300">2xx</span><span class="opacity-85">成功</span><span class="font-mono text-xs opacity-55">200 · 201 · 204</span></div>
<div class="flex gap-2 items-baseline"><span class="w-9 shrink-0 font-mono font-bold text-sky-600 dark:text-sky-400">3xx</span><span class="opacity-85">重定向</span><span class="font-mono text-xs opacity-55">301 · 302 · 303</span></div>
<div class="flex gap-2 items-baseline"><span class="w-9 shrink-0 font-mono font-bold text-amber-600 dark:text-amber-400">4xx</span><span class="opacity-85">你（客户端）错了</span><span class="font-mono text-xs opacity-55">400 · 401 · 403 · 404 · 409 · 422</span></div>
<div class="flex gap-2 items-baseline"><span class="w-9 shrink-0 font-mono font-bold text-rose-600 dark:text-rose-400">5xx</span><span class="opacity-85">我（服务端）错了</span><span class="font-mono text-xs opacity-55">500</span></div>
</div>
<div class="mt-3 p-2.5 rounded-lg bg-gray-500/8 text-xs">
<b>先记三个</b>：<code>200</code> 成功、<code>404</code> 没找到、<code>500</code> 服务端炸了。其余第 1 次课逐个见到——<code>401</code> 没登录、<code>403</code> 没权限、<code>409</code> 冲突、<code>422</code> 校验失败。
</div>
</div>

</div>

<!--
报文四部分的起始行里，有两个关键词：方法和状态码。这一页把它们认全。

左边五个方法，就是"你想对资源做什么"：GET 读、POST 新建、PUT 整体替换、PATCH 局部改、DELETE 删。第 1 次课那五个接口，正好一个方法用一次，你到时候会一一对上。

右边状态码，是服务端的回话。先记大类：2xx 成功、3xx 重定向、4xx 你错了、5xx 我错了。这个"你错了/我错了"的分法要刻进脑子——4xx 是客户端的问题，5xx 是服务端的问题，排障时第一刀就砍在这里。

具体码今天先认三个：200 成功、404 没找到、500 服务端炸了。剩下的 401 没登录、403 没权限、409 冲突、422 校验失败——第 1 次课会一个个见到，每个都配一个现场复现。今天不抢判据，认脸就够。
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

# 0.2 DevTools Network 面板的五件事

<div class="text-xs opacity-55 -mt-1 mb-3">跟做 2 你已经打开了 Network。这一页把「看什么」系统成五件事——<b class="text-teal-700 dark:text-teal-300">这是你今后排障的主战场。</b></div>

<div class="mt-2 space-y-2 text-sm">

<div class="flex items-start gap-3 p-2.5 rounded-lg border border-gray-400/25 bg-gray-500/5">
<span class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">1</span>
<div><b>看状态码</b><span class="opacity-75">　点开请求，Headers 顶部那个 200 / 404 / 500——第一刀砍在 4xx 还是 5xx</span></div>
</div>

<div class="flex items-start gap-3 p-2.5 rounded-lg border border-gray-400/25 bg-gray-500/5">
<span class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">2</span>
<div><b>看请求头与响应头</b><span class="opacity-75">　Request Headers 里你发了什么（Cookie、Authorization），Response Headers 里服务端回了什么（Set-Cookie、Cache-Control）</span></div>
</div>

<div class="flex items-start gap-3 p-2.5 rounded-lg border border-gray-400/25 bg-gray-500/5">
<span class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">3</span>
<div><b>看请求载荷与响应体</b><span class="opacity-75">　Payload 标签是你发过去的 JSON；Response / Preview 标签是服务端回的数据</span></div>
</div>

<div class="flex items-start gap-3 p-2.5 rounded-lg border border-gray-400/25 bg-gray-500/5">
<span class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">4</span>
<div><b>看耗时</b><span class="opacity-75">　Timing 标签把一次请求拆成 DNS、连接、等待（TTFB）、下载——「慢」慢在哪一段</span></div>
</div>

<div class="flex items-start gap-3 p-2.5 rounded-lg border border-gray-400/25 bg-gray-500/5">
<span class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">5</span>
<div><b>勾 Disable cache，分清缓存与服务器</b><span class="opacity-75">　Size 列显示 (memory cache) / (disk cache) 还是真实大小——排查「改了代码没生效」的第一步</span></div>
</div>

</div>

<div v-click class="mt-3 p-3 rounded-lg bg-amber-500/8 border-l-4 border-amber-500 text-sm">
这五件事就是预习包第 6 章那道必做题的操作清单。第 1 次课起，每次问「失败什么样、在哪观察」，答案都在这五件事里。
</div>

<!--
跟做 2 你们已经打开了 Network 面板，也看到了浏览器发的头比 curl 多得多。这一页我把「在 Network 里到底看什么」系统成五件事，这是你今后排障的主战场。

第一，看状态码。点开任何一个请求，最上面那个数字，200 还是 404 还是 500——排障第一刀就砍在这里：是 4xx 你错了，还是 5xx 我错了。

第二，看请求头和响应头。Request Headers 里是你发过去的，Cookie、Authorization 都在这；Response Headers 里是服务端回过来的，Set-Cookie、Cache-Control 在这。

第三，看请求载荷和响应体。Payload 标签是你发过去的 JSON，Response 或 Preview 标签是服务端回的数据。第 1 次课那个 422 的 errors 数组，就是在这里看到的。

第四，看耗时。Timing 标签把一次请求拆成 DNS、连接、等待、下载几段——用户说"慢"，你要能说出慢在哪一段。

第五，勾上 Disable cache，分清这个资源是从缓存来的还是从服务器来的。Size 列如果显示 memory cache 或 disk cache，说明根本没走网络。你改了代码刷新没生效，十有八九是缓存——这是排查的第一步。

这五件事，就是预习包第 6 章那道必做题的操作清单。从第 1 次课起，我们每节课问"失败什么样、在哪观察"，答案都落在这五件事里。
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
