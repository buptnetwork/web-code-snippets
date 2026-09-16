---
layout: section
---

# 讲二 · 读懂第 1 次课要出现的 Python 写法

<div class="pt-3 text-sm opacity-60">
0.7 类型注解 · 0.8 类 · 0.9 异常 · 0.10 装饰器（高光） · 0.11 async 边界 · 0.12 包与 import · 0.13 允许不懂清单
</div>

<div class="mt-8 text-xs opacity-50">
本讲 60 分钟 · 每个语法点都标「对应第 1 次课」
</div>

<!--
课前课第二讲。这一讲不教"怎么写 Python"，只教一件事：把第 1 次课会突然冒出来的那些写法，先在这儿见一遍。

有一条通用要求贯穿整讲：所有例子都直接取自第 1 次课的真实代码或我们的 mini 程序，不造 class Animal / class Dog 那种教科书例子。每个语法点后面都跟一条"对应第 1 次课"，明确告诉你"你会在第 1 次课的哪个文件见到它"。

这是课前课最大的杠杆——第 1 次课你看到 class Settings(BaseSettings) 时，认知负载就从"陌生语法 + 陌生结构"降成"只有结构是新的"。这条绑定装置，我一讲都会带着。
-->

---

# 0.7 类型注解：给人和框架看，不给机器执行

<div class="text-xs opacity-55 -mt-1 mb-3">打掉一个具体误解：以为写了 <code>x: int</code>，Python 就会检查类型。<b class="text-amber-600 dark:text-amber-400">不会，一行都不检查。</b></div>

<div grid="~ cols-2 gap-6" class="mt-2">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">四种写法</div>
<div class="rounded-lg overflow-hidden border border-gray-400/25 font-mono text-[13px]">
  <div class="px-3 py-2 border-b border-gray-400/15"><span class="text-teal-600 dark:text-teal-400">page: int = 1</span><span class="opacity-50 font-sans text-xs">　变量注解</span></div>
  <div class="px-3 py-2 border-b border-gray-400/15"><span class="text-teal-600 dark:text-teal-400">def double(n: int) -&gt; int:</span><span class="opacity-50 font-sans text-xs">　参数与返回</span></div>
  <div class="px-3 py-2 border-b border-gray-400/15"><span class="text-teal-600 dark:text-teal-400">keyword: str | None = None</span><span class="opacity-50 font-sans text-xs">　可能 str 也可能 None</span></div>
  <div class="px-3 py-2"><span class="text-teal-600 dark:text-teal-400">items: list[Todo]</span><span class="opacity-50 font-sans text-xs">　列表里装什么</span></div>
</div>
<div class="mt-3 text-xs opacity-70"><code>str | None</code> 读作「str 或 None」；<code>list[Todo]</code> 读作「装 Todo 的列表」。</div>
</div>

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">现场演示 · <span class="font-bold text-rose-600 dark:text-rose-400">先猜，再看</span></div>

<<< @/snippets/lesson00/annotations_demo.py {lines:true,all:2}

<div v-click="3" class="mt-2 text-xs tracking-widest opacity-55 mb-1">实际输出（静态对照）</div>
<div v-click="3" class="rounded-lg bg-gray-500/10 border border-gray-400/25 font-mono text-[13px] px-3 py-2 leading-relaxed">
6<br>
<span class="text-rose-600 dark:text-rose-400 font-bold">abab</span>　<span class="opacity-55 font-sans text-xs">← 注解写 int，传 str 照样跑出结果</span><br>
[1, 2, 1, 2]<br>
{'n': &lt;class 'int'&gt;, 'return': &lt;class 'int'&gt;}
</div>
</div>

</div>

<!--
类型注解，先做个实验。这个函数 double 写着参数是 int，返回是 int。我传一个字符串 "ab" 进去，你猜会怎样？

[click] 停一下，你先在心里猜。报错？……没有。它输出了 abab。因为字符串乘 2 就是重复两遍。传列表也一样，[1,2] 乘 2 变成 [1,2,1,2]。

[click] 最后这行 double.__annotations__ 说明：注解只是被 Python 存起来了，谁想读谁读，它自己不参与任何运行时检查。这一点你现在就要接受：Python 的类型注解一行都不检查。
-->

---

# 0.7 注解不检查，那它有什么用？

<div class="text-xs opacity-55 -mt-1 mb-3">三个用途，<b class="text-teal-700 dark:text-teal-300">第三个才是关键</b>——它是第 1 次课几乎所有「魔法」的来源。</div>

<div grid="~ cols-2 gap-6" class="mt-2">

<div>
<div class="space-y-2.5 text-sm">
  <div class="flex items-start gap-3 p-3 rounded-lg border border-gray-400/25 bg-gray-500/5">
    <span class="w-6 h-6 rounded-full bg-gray-500/20 text-xs flex items-center justify-center font-bold shrink-0">1</span>
    <span>编辑器的<b>补全和跳转</b></span>
  </div>
  <div class="flex items-start gap-3 p-3 rounded-lg border border-gray-400/25 bg-gray-500/5">
    <span class="w-6 h-6 rounded-full bg-gray-500/20 text-xs flex items-center justify-center font-bold shrink-0">2</span>
    <span>静态检查工具（mypy 等）在<b>运行前</b>报错</span>
  </div>
  <div v-click class="flex items-start gap-3 p-3 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
    <span class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">3</span>
    <span><b class="text-teal-700 dark:text-teal-300">框架在运行时读取注解，据此决定行为</b> ← 一切「魔法」的来源</span>
  </div>
</div>
<div v-click="2" class="mt-3 p-3 rounded-lg bg-amber-500/10 border-l-4 border-amber-500 text-sm">
一句话：<b>注解本身不做事，但有人在读它。</b>第 9 次课讲 TypeScript 会回收这个演示——「类型错了为什么还能打包成功」，同一个道理。
</div>
</div>

<div v-click="2">
<div class="rounded-lg border-l-4 border-sky-500/70 bg-sky-500/6 overflow-hidden">
  <div class="px-3 py-1.5 bg-sky-500/12 text-xs font-bold text-sky-700 dark:text-sky-300 tracking-wide">对应第 1 次课 · 框架读了注解之后做了什么</div>
  <div class="text-[13px]">
    <div class="flex gap-3 px-3 py-2 border-t border-sky-500/15">
      <code class="w-52 shrink-0 text-xs text-sky-700 dark:text-sky-300">page: int = Query(1, ge=1)</code>
      <span class="flex-1 opacity-85">从查询串取 <code class="text-xs">page</code>，转 int，检查 ≥1，不合格返回 <b>422</b></span>
    </div>
    <div class="flex gap-3 px-3 py-2 border-t border-sky-500/15">
      <code class="w-52 shrink-0 text-xs text-sky-700 dark:text-sky-300">payload: PostCreate</code>
      <span class="flex-1 opacity-85">把请求体 JSON 按 <code class="text-xs">PostCreate</code> 的字段逐个校验并构造成对象</span>
    </div>
    <div class="flex gap-3 px-3 py-2 border-t border-sky-500/15">
      <code class="w-52 shrink-0 text-xs text-sky-700 dark:text-sky-300">secret_key: str</code>
      <span class="flex-1 opacity-85">没给默认值 → 环境变量里没有它就<b class="text-rose-600 dark:text-rose-400">启动失败</b></span>
    </div>
    <div class="flex gap-3 px-3 py-2 border-t border-sky-500/15">
      <code class="w-52 shrink-0 text-xs text-sky-700 dark:text-sky-300">response_model=PostOut</code>
      <span class="flex-1 opacity-85">只把 <code class="text-xs">PostOut</code> 列出的字段序列化出去</span>
    </div>
  </div>
</div>
</div>

</div>

<!--
那注解有什么用？三个。前两个是编辑器补全、静态检查工具，都不神秘。

[click] 第三个才是重点：框架会在运行的时候把这些注解读出来，然后决定自己该干什么。

[click] 你看第 1 次课这几行。page: int = Query(1, ge=1)——FastAPI 读到这个注解，就知道要从查询串里取 page、转成整数、检查是不是大于等于 1，不合格直接返回 422，你一行 if 都不用写。payload: PostCreate——它读到这个，就知道把请求体的 JSON 按这个类的字段一个个校验。secret_key: str 没给默认值，环境变量里找不到它，程序直接启动失败。

所以第 1 次课那些看起来像魔法的东西，来源就是这里：注解本身不做事，但有人在读它。最后提一句，第 9 次课讲 TypeScript 也是同一个道理——类型只在编译前起作用，编译完就没了。那节课我会问你们：类型错了为什么代码还能打包成功？答案跟今天这个演示一模一样。
-->

---

# 0.8 类：把数据和规则装在一起

<div class="text-xs opacity-55 -mt-1 mb-3">本节是<b class="text-teal-700 dark:text-teal-300">重点</b>，涵盖第 1 次课 <code>config.py</code> / <code>schemas/</code> / <code>repositories/</code> / <code>services/</code> / <code>errors.py</code> 五个文件的共同基础。学完这一节，那五个文件的骨架你就全见过了。</div>

<div grid="~ cols-[0.95fr_1.05fr] gap-6" class="mt-2">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">类＝图纸，实例＝照图纸造出来的东西</div>
<div grid="~ cols-[1fr_auto_1fr] gap-2 items-center">
  <div class="p-3 rounded-lg border-2 border-teal-500/40 bg-teal-500/5 text-center">
    <div class="font-mono text-[13px] font-bold">TodoService</div>
    <div class="text-[11px] opacity-60 mt-1">一张图纸（类）</div>
    <div class="mt-2 pt-2 border-t border-teal-500/20 text-[11px] text-left opacity-80">
      <div><b>类属性</b>：写在类体</div>
      <div class="opacity-60">所有实例<b>共享</b></div>
      <div class="mt-1"><code>__init__</code> 方法</div>
    </div>
  </div>
  <div class="text-xl opacity-40">→</div>
  <div class="space-y-2">
    <div class="p-2 rounded border border-sky-500/40 bg-sky-500/5 text-[11px]">
      <div class="font-mono font-bold text-xs">svc1</div>
      <div class="opacity-75">实例属性 <code>self.repo = repoA</code></div>
    </div>
    <div class="p-2 rounded border border-sky-500/40 bg-sky-500/5 text-[11px]">
      <div class="font-mono font-bold text-xs">svc2</div>
      <div class="opacity-75">实例属性 <code>self.repo = repoB</code></div>
    </div>
    <div class="text-[10px] opacity-55">实例属性：<b>每个实例各自一份</b></div>
  </div>
</div>
<div class="mt-3 text-xs opacity-75">你调 <code>svc1.list_todos()</code>，Python 悄悄把 <code>svc1</code> 当第一个参数（就是 <code>self</code>）传进去。</div>
</div>

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">最小骨架：<code>__init__</code> 与 <code>self</code></div>

```python
class TodoService:
    def __init__(self, repo):   # 创建实例时自动调用
        self.repo = repo        # self 就是「这个实例自己」

svc = TodoService(repo=JsonTodoRepo())  # 这行去执行 __init__
svc.list_todos()                # 等价 TodoService.list_todos(svc)
```

<div class="mt-3 p-3 rounded-lg bg-gray-500/8 text-sm">
<code>__init__</code> 不是「构造」实例，是实例被造出来后<b>自动跑一次的初始化</b>；<code>self</code> 永远指向「当前这个实例」。
</div>
</div>

</div>

<!--
这一节讲完，第 1 次课那五个文件的骨架你就全见过了。

先是最基本的：类是图纸，实例是照图纸造出来的东西。你看左边这张图，TodoService 是图纸，svc1、svc2 是照它造出来的两个实例。图纸上的东西——类属性——所有实例共享；每个实例自己身上的东西——实例属性——各自一份。

__init__ 在创建实例时自动跑。self 就是"这个实例自己"。你调 svc 点某个方法，Python 悄悄把 svc 当第一个参数传进去了，那个参数就叫 self。
-->

---

# 0.8 第 1 次课最高频的三种「类写法」

<div class="text-xs opacity-55 -mt-1 mb-3">这三种你在第 1 次课会反复撞见，先认脸。</div>

<div grid="~ cols-3 gap-4" class="mt-2 text-sm">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">① 声明式：类属性＋注解</div>

```python {all:0}
class PostCreate(BaseModel):
    title: str
    body: str
    author: str

class Settings(BaseSettings):
    env: str = "dev"
    debug: bool = False
    secret_key: str   # 无默认→必填
```

<div class="mt-2 text-xs opacity-80">类体里<b>只有字段名和类型，没有方法</b>。它在说「我有这些字段，各是什么类型，哪些有默认值」——<b class="text-teal-700 dark:text-teal-300">是声明，不是逻辑</b>。父类会读它，替你生成校验 / 去环境变量取值。</div>
</div>

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">② 继承与属性覆盖</div>

<<< @/snippets/lesson00/mini/errors.py#family {lines:true,maxHeight:'210px'}

<div class="mt-2 text-xs opacity-80"><code>NotFoundError</code> 只改了两个类属性，其余全继承。<b class="text-amber-600 dark:text-amber-400">门槛测试会问：它有没有 <code>__init__</code>？</b> 有——继承来的。</div>
</div>

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">③ <code>@dataclass</code> 省掉手写</div>

<<< @/snippets/lesson00/mini/models.py#todo {lines:true,maxHeight:'210px'}

<div class="mt-2 text-xs opacity-80">它自动生成了 <code>__init__</code>、<code>__repr__</code>、<code>__eq__</code>。<b>不神秘</b>，就是省掉手写这三样的工具。</div>
</div>

</div>

<div v-click class="mt-4 p-3 rounded-lg bg-teal-500/8 border-l-4 border-teal-500 text-sm">
换个眼光看①：<b>它不是在写逻辑，是在填一张表格给框架看。</b><code class="text-xs">created_by</code> 是内部字段——存起来，但展示给用户时不输出（对应第 1 次课的 <code class="text-xs">response_model</code> 出站白名单）。
</div>

<!--
然后是第二种写法，这个你们最陌生，也是第 1 次课最常见的——类体里只有字段名和类型，没有方法。

你看这个 PostCreate，就三行，全是"名字：类型"。它在说什么？它在说"我这个类有这几个字段，各是什么类型"。这是一种声明，不是代码。那谁来用这个声明？父类。BaseModel 会把这些声明读出来，替你生成校验逻辑；BaseSettings 会读出来，去环境变量里挨个找值。所以这类写法你要换个眼光看：它不是在写逻辑，它是在填一张表格给框架看。

[click] 中间这个是继承。NotFoundError 就两行，改了两个类属性，其他全从父类继承。我问你们一个问题：NotFoundError 有没有 __init__ 方法？有，继承来的。这个门槛测试会考。

右边 dataclass 就是省掉手写 __init__ 的工具，不神秘。注意 Todo 里那个 created_by，它是内部字段，存起来但展示时不输出——这正好对应第 1 次课的 response_model，出站白名单。
-->

---

# 0.8 构造器接收依赖（隐藏重点）

<div class="text-xs opacity-55 -mt-1 mb-3">这条是第 1 次课 1.2.5「依赖注入」和第 8 次课测试替换的伏笔。今天只点出问题的<b>形状</b>，答案第 1 次课给。</div>

<div grid="~ cols-2 gap-6" class="mt-2">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">✓ mini 的写法：仓储从外面传进来</div>

<<< @/snippets/lesson00/mini/service.py#init {lines:true}

<div class="mt-2 text-xs opacity-80"><code>repo</code> 是<b class="text-teal-700 dark:text-teal-300">从外面传进来</b>的 → 想换成别的实现（测试用的假仓储）随时能换。</div>
</div>

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">✗ 反例：自己在里面创建</div>

```python
class TodoService:
    def __init__(self):
        self.repo = JsonTodoRepo()  # 自己 new → 换不掉了
```

<div class="mt-2 p-3 rounded-lg bg-rose-500/8 border-l-4 border-rose-500 text-sm">
<b>问题在哪：</b>想测这个类的业务规则，就<b>必须真的读写文件</b>。测得慢、测得脏、还测不稳。
</div>
</div>

</div>

<div grid="~ cols-2 gap-6" class="mt-5">
<div class="p-3 rounded-lg border border-gray-400/25 bg-gray-500/5 text-sm">
<div class="text-xs tracking-widest opacity-60 mb-1.5">参数写法三件事</div>
<div class="text-xs space-y-1 opacity-85">
<div>· 关键字参数 <code>f(title="x")</code> 比位置参数可读</div>
<div>· 默认值：<code>created_by="local"</code></div>
<div>· <b class="text-amber-600 dark:text-amber-400">keyword-only</b>：<code>def add(self, *, title, created_by)</code> 里那个 <code>*</code> ＝ 它后面的参数<b>必须用名字传</b>。第 1 次课仓储方法全用这个写法。</div>
</div>
</div>
<div class="rounded-lg border-l-4 border-sky-500/70 bg-sky-500/6 overflow-hidden text-sm">
<div class="px-3 py-1.5 bg-sky-500/12 text-xs font-bold text-sky-700 dark:text-sky-300 tracking-wide">对应第 1 次课</div>
<div class="px-3 py-2 text-xs space-y-1 opacity-90">
<div>· 声明式类属性 → <code>Settings</code>、<code>PostCreate</code> / <code>PostOut</code></div>
<div>· 继承覆盖 → <code>NotFoundError</code> / <code>ConflictError</code> / <code>RuleViolation</code></div>
<div>· <code>@dataclass</code> → <code>PostRecord</code></div>
<div>· 构造器接收依赖 → <code>PostService(repo=...)</code>、<code>deps.py</code></div>
<div>· keyword-only <code>*</code> → <code>repo.add(*, title, body, author, client_ip)</code></div>
</div>
</div>
</div>

<!--
最后这一条是重点，你们先记住这个问题的形状，答案第 1 次课给。

看这个 TodoService，它的仓储是从外面传进来的，不是自己在里面创建的。如果自己在里面 new 一个会怎样？你就换不掉了。想测这个类的业务规则，就必须真的去读写文件。第 1 次课我会给出正式答案，那个东西叫依赖注入。

下面这块是参数写法三件事，尤其那个星号——keyword-only，星号后面的参数必须用名字传，不能靠位置。第 1 次课仓储方法全用这个写法，你现在认得它就行。

右边这张"对应第 1 次课"的表你扫一眼：今天讲的每种类写法，第 1 次课都会在哪个文件出现，我都标好了。
-->


---

# 0.9 异常：跨层传递信息的手段

<div class="text-xs opacity-55 -mt-1 mb-3"><b class="text-teal-700 dark:text-teal-300">换视角</b>：不要把异常讲成「错误处理」。它是——内层想告诉外层一件事，但中间隔了好几层，<b>异常是唯一能一次穿透过去的方式</b>。</div>

<div grid="~ cols-2 gap-6" class="mt-3">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">完整四段形态（第 1 次课中间件正好用满）</div>

```python
try:
    result = do_something()
except SomeError:
    ...     # 出错了做什么
else:
    ...     # 没出错才做什么
finally:
    ...     # 不管出没出错都做（清理、reset）
```

</div>

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">捕获父类，能接住所有子类</div>

```python
try:
    svc.add_todo("x")
except AppError as exc:   # 接住 NotFound/Conflict/RuleViolation
    print(exc.code, exc.detail)
```

<div class="mt-3 p-3 rounded-lg bg-gray-500/8 text-sm">
因为异常有<b>继承关系</b>（0.8 的 <code>AppError</code> 家族）。所以最外层只写一个 <code>except AppError</code>，就能兜住业务层抛出的<b>所有</b>领域异常。
</div>
</div>

</div>

<!--
异常这个东西，我想换个说法讲。你们以前学的可能是"异常用来处理错误"。我换一个说法：异常是内层想告诉外层一件事，但中间隔了好几层，异常是唯一能一次穿透过去的方式。

先认两个形态。完整四段：try、except、else、finally——第 1 次课的中间件正好把这四段用满了，你到时候能对得上。

另一个更重要的性质：异常有继承关系，捕获父类能接住所有子类。add_todo 可能抛 NotFoundError、ConflictError、RuleViolation 三种，但它们都是 AppError 的孩子。所以最外层只写一个 except AppError，就把三种全兜住了。这就是为什么 mini 的 cli 里只有一个 except。
-->

---

# 0.9 异常怎么穿层（板书）

<div class="text-xs opacity-55 -mt-1 mb-2">看 mini 的真实代码：<code>repo</code> 返回 <code>None</code> → <code>service</code> 抛异常 → <b class="text-teal-700 dark:text-teal-300">中间层什么都不用写</b> → 最外层 <code>cli.main</code> 接住。</div>

<div grid="~ cols-[1fr_1.25fr] gap-5" class="mt-1">

<div class="text-sm">
<div class="text-xs tracking-widest opacity-60 mb-1.5">service.py · 抛出</div>

<<< @/snippets/lesson00/mini/service.py#get_todo {lines:true,maxHeight:'130px'}

<div class="text-xs tracking-widest opacity-60 mt-3 mb-1.5">cli.py · 全程序<b class="text-amber-600 dark:text-amber-400">唯一</b>的翻译点</div>

```python {6-8}
except AppError as exc:
    print(f"错误[{exc.code}]：{exc.detail}",
          file=sys.stderr)
    return exc.exit_code
```

</div>

<div>
<div grid="~ cols-2 gap-4">
<!-- 左：raise 穿透 -->
<div>
<div class="text-xs text-center font-bold text-teal-700 dark:text-teal-300 mb-2">① raise：一路穿透</div>
<div class="px-2 py-1.5 rounded border-2 border-teal-500/50 bg-teal-500/8 text-[11px] font-mono text-center">cli · except<b class="block opacity-60 font-sans">翻译点</b></div>
<div class="relative h-8 flex items-center justify-center">
  <div class="absolute left-1/2 top-0 bottom-0 w-0.5 bg-teal-500/60" />
  <div class="absolute left-1/2 -translate-x-1/2 top-0 text-teal-600 dark:text-teal-400 text-xs">▲</div>
  <span class="relative bg-white dark:bg-[#1b1b1b] px-1 text-[10px] opacity-70">零代码</span>
</div>
<div class="px-2 py-1.5 rounded border border-amber-500/50 bg-amber-500/8 text-[11px] font-mono text-center">service · raise</div>
<div class="h-4 flex items-center justify-center text-xs opacity-40">▲</div>
<div class="px-2 py-1.5 rounded border border-gray-400/40 bg-gray-500/8 text-[11px] font-mono text-center">repo · return None</div>
</div>
<!-- 右：返回码逐层检查 -->
<div>
<div class="text-xs text-center font-bold text-rose-600 dark:text-rose-400 mb-2">② 返回码：逐层检查</div>
<div class="px-2 py-1.5 rounded border border-gray-400/40 bg-gray-500/8 text-[11px] font-mono text-center">cli</div>
<div class="h-4 flex items-center justify-center text-[10px] opacity-60">▲ 检查</div>
<div class="px-2 py-1.5 rounded border border-rose-500/40 bg-rose-500/8 text-[11px] font-mono text-center">service<b class="block opacity-70 font-sans">if err: return err</b></div>
<div class="h-4 flex items-center justify-center text-[10px] opacity-60">▲ 检查</div>
<div class="px-2 py-1.5 rounded border border-rose-500/40 bg-rose-500/8 text-[11px] font-mono text-center">repo<b class="block opacity-70 font-sans">return None, 404</b></div>
</div>
</div>
<div v-click class="mt-3 p-2.5 rounded-lg bg-rose-500/8 border-l-4 border-rose-500 text-xs">
② 每一层都要记得检查返回值并往上传——<b>忘一层，故障就消失了</b>，程序继续跑，最后你在数据里看到一堆脏东西，根本不知道哪儿出的事。
</div>
</div>

</div>

<!--
看 mini 的实际代码。repo 查不到，返回 None。service 发现是 None，抛一个 NotFoundError。然后呢？中间什么都不用写，这个异常自己一路冒到最外面的 cli，cli 那里有一个 except，接住它，翻译成一句人话和一个退出码。整个程序只有这一处在做翻译。

[click] 现在看右边第二种写法，就是 AI 特别爱生成的那种：service 自己返回一个错误码或者一个 success 字段。区别在哪？第一种，异常一路穿透，中间层零代码；第二种，每一层调用它的人都得记得检查返回值，然后再往上传。忘一层，故障就消失了，程序继续跑，最后你在数据库里看到一堆脏数据，根本不知道哪儿出的事。
-->

---

# 0.9 两种写法的正面对比

<div class="mt-2 text-sm">

<div class="flex gap-4 pb-2 mb-1 border-b border-gray-400/30 text-xs tracking-wide opacity-60">
  <div class="w-52 shrink-0"></div>
  <div class="flex-1 text-teal-700 dark:text-teal-300 font-bold">① 服务层 raise，最外层统一翻译</div>
  <div class="flex-1 text-rose-600 dark:text-rose-400 font-bold">② 服务层自己返回错误码</div>
</div>

<div v-click="1" class="flex gap-4 py-2.5 border-b border-gray-400/15 items-center">
  <div class="w-52 shrink-0 font-bold opacity-80">服务层代码</div>
  <div class="flex-1 font-mono text-xs">raise NotFoundError(...)</div>
  <div class="flex-1 font-mono text-xs opacity-80">return None, 4</div>
</div>
<div v-click="2" class="flex gap-4 py-2.5 border-b border-gray-400/15 items-center">
  <div class="w-52 shrink-0 font-bold opacity-80">每个调用点</div>
  <div class="flex-1 text-xs">什么都不用写，异常自己往上冒</div>
  <div class="flex-1 text-xs text-rose-600 dark:text-rose-400"><b>每一层都要检查返回值并往上传</b></div>
</div>
<div v-click="3" class="flex gap-4 py-2.5 border-b border-gray-400/15 items-center">
  <div class="w-52 shrink-0 font-bold opacity-80">换输出形式<br><span class="font-normal opacity-60 text-xs">命令行 → HTTP</span></div>
  <div class="flex-1 text-xs">只改翻译那一处</div>
  <div class="flex-1 text-xs text-rose-600 dark:text-rose-400">服务层里的错误码<b>全要改</b></div>
</div>
<div v-click="4" class="flex gap-4 py-2.5 border-b border-gray-400/15 items-center">
  <div class="w-52 shrink-0 font-bold opacity-80">忘了处理</div>
  <div class="flex-1 text-xs">冒到最外层，<b class="text-teal-700 dark:text-teal-300">一定会被发现</b></div>
  <div class="flex-1 text-xs text-rose-600 dark:text-rose-400">静默继续，<b>故障消失</b></div>
</div>

</div>

<LessonLink v-click="5">
第 1 次课 <code class="text-xs">errors.py</code> 的 <code class="text-xs">AppError</code> 家族与 mini <b>完全同构</b>，只是 <code class="text-xs">exit_code</code> 换成 <code class="text-xs">status_code</code>；服务层三种失败 → 三种领域异常 → 三种状态码（<b>404 / 409 / 422</b>）；最外层用 <code class="text-xs">@app.exception_handler(AppError)</code> 注册翻译函数，一处翻译、全站统一。解剖台那个反例正是写法②：五个接口五种错误格式。
</LessonLink>

<!--
把两种写法摆在一起对比，四行。

[click] 服务层代码：一个是 raise，一个是 return 错误码。

[click] 每个调用点：第一种什么都不用写，异常自己往上冒；第二种每一层都要检查返回值再往上传。

[click] 换输出形式：mini 是命令行，翻译成退出码；第 1 次课是 HTTP，翻译成状态码。第一种我只改翻译那一处，服务层一行不动；第二种服务层里的错误码全得改。

[click] 忘了处理：第一种异常一定冒到最外层被发现；第二种静默继续，故障消失。

[click] 所以异常不只是"处理错误"，它是一种架构手段。第 1 次课的 errors.py 跟 mini 这个是同构的，只是 exit_code 换成 status_code，服务层三种失败对应 404、409、422 三种状态码，最外层用 exception_handler 一处翻译。你现在看懂了 mini 这个，下周那个直接就能读。
-->


---

# 0.10 装饰器：读懂 <code style="font-size:0.9em">@app.post("/posts")</code>

<div class="text-xs opacity-55 -mt-1 mb-3"><b class="text-amber-600 dark:text-amber-400">本讲高光，也是讲二最难的一节。</b>目标<b>不是</b>会写装饰器，而是能说出「这个 @ 让某件事在后台发生了」。</div>

<div grid="~ cols-2 gap-6" class="mt-2">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">前提：函数是对象</div>

```python
def hello():
    return "hi"

f = hello              # 不加括号＝把函数本身赋给 f
print(f())             # hi
print(hello.__name__)  # hello → 有属性，说明是对象
```

<div class="mt-3 text-xs opacity-75">能赋值、能当参数传、能从函数里返回——正因为<b>函数是对象</b>，装饰器才可能存在。</div>
</div>

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">无参装饰器：<code>@</code> 就是一行赋值的简写</div>

<<< @/snippets/lesson00/decorator_demo.py#log_call {lines:true,maxHeight:'235px'}

<div class="mt-2 p-2.5 rounded-lg bg-teal-500/8 border-l-4 border-teal-500 text-sm">
<code>@log_call</code> ＋ 函数定义　<b>完全等价于</b>　定义完再补一行：<br>
<code class="text-xs font-bold">greet = log_call(greet)</code>　——一行赋值，没有任何魔法。
</div>
</div>

</div>

<!--
这一节最难，你们可能要看两遍。但它值得，因为 @ 这个符号是你看 AI 生成的 Web 代码时第一眼就撞上的东西，而百分之九十的人对它的理解是"这是框架的魔法"。今天我们把魔法拆开。

第一个前提：函数是对象。你可以把它赋给变量、传给别的函数、从函数里返回。hello 不加括号赋给 f，f() 照样能调用；hello.__name__ 能取到属性——说明它就是个对象。

基于这个，@ 是什么？右边这个 log_call，@log_call 加一个函数定义，完全等价于：函数定义完之后，再写一行 greet = log_call(greet)。就这样，一行赋值的简写，没有任何魔法。
-->

---
clicks: 2
---

# 0.10 高光 · 带参数的装饰器是「两步」

<div class="text-xs opacity-55 -mt-1 mb-3">全课程<b>唯一一次</b>把「带参数的装饰器是两步」讲干净的机会，<b class="text-amber-600 dark:text-amber-400">两步之间必须停</b>——一次给全就没有效果了。</div>

<div grid="~ cols-[0.85fr_1.15fr] gap-6" class="mt-4">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">你看到的写法</div>

```python
@app.post("/posts")
def create_post():
    ...
```

<div class="mt-8 text-center text-2xl opacity-40">⇓</div>
<div class="mt-2 text-center text-sm opacity-70">完全等价于右边两步<br><span class="text-xs opacity-60">一步一步来，别急 →</span></div>
</div>

<div>
<div v-click="1" class="p-4 rounded-lg border-2 border-amber-500/50 bg-amber-500/8">
  <div class="text-xs font-bold text-amber-700 dark:text-amber-300 mb-2">第 1 步 · 先执行括号里的东西</div>
  <code class="text-base font-mono">decorator = app.post("/posts")</code>
  <div class="text-xs opacity-85 mt-2.5">括号里的 <code>app.post("/posts")</code> <b>先被执行</b>，返回一个「装饰器」。<b class="text-rose-600 dark:text-rose-400">此刻你的函数还没被碰过。</b></div>
</div>
<div v-click="2" class="mt-4 p-4 rounded-lg border-2 border-teal-500/50 bg-teal-500/8">
  <div class="text-xs font-bold text-teal-700 dark:text-teal-300 mb-2">第 2 步 · 再把它用到函数上</div>
  <code class="text-base font-mono">create_post = decorator(create_post)</code>
  <div class="text-xs opacity-85 mt-2.5">这一步才把函数交给装饰器——<b>登记 / 改造发生在这里</b>。</div>
</div>
<div v-click="2" class="mt-4 text-sm">所以带参数的装饰器要写成 <b class="text-amber-600 dark:text-amber-400">三层嵌套函数</b>，这正是它看起来那么难读的原因。</div>
</div>

</div>

<!--
现在看带参数的，这个是重点。@app.post("/posts")——

[click] 第一步，先停在这里。先看括号。括号里的东西先被执行了，app.post("/posts") 跑了一遍，返回了一个东西，我们叫它 decorator。注意：此时你的函数 create_post 还没被碰过。

[click] 第二步，然后，这个 decorator 才被用到你的函数上：create_post = decorator(create_post)。两步，不是一步。这就是为什么带参数的装饰器要写三层嵌套函数，为什么它那么难读。你们把这个"先执行括号、再套到函数上"的两步看明白，@ 就不神秘了。
-->

---

# 0.10 关键认知：装饰器多半在「登记」，不是「改造」

<div class="text-xs opacity-55 -mt-1 mb-3">你的直觉是「装饰器给函数加了功能」。但第 1 次课见到的装饰器几乎全是另一类用途：<b class="text-teal-700 dark:text-teal-300">把函数登记到某张表里，函数本身一个字节都没变。</b></div>

<div class="mt-3 text-sm">
<div class="flex gap-4 pb-2 mb-1 border-b border-gray-400/30 text-xs tracking-wide opacity-60">
  <div class="w-72 shrink-0">第 1 次课的装饰器</div>
  <div class="flex-1">它把函数登记到了哪里</div>
</div>
<div v-click="1" class="flex gap-4 py-2.5 border-b border-gray-400/15 items-center">
  <div class="w-72 shrink-0 font-mono text-xs text-teal-600 dark:text-teal-400">@router.get("/posts")</div>
  <div class="flex-1 text-xs">路由表：<code>("GET", "/api/posts") → list_posts</code></div>
</div>
<div v-click="2" class="flex gap-4 py-2.5 border-b border-gray-400/15 items-center">
  <div class="w-72 shrink-0 font-mono text-xs text-teal-600 dark:text-teal-400">@router.post("")</div>
  <div class="flex-1 text-xs">路由表：<code>("POST", "/api/posts") → create_post</code></div>
</div>
<div v-click="3" class="flex gap-4 py-2.5 border-b border-gray-400/15 items-center">
  <div class="w-72 shrink-0 font-mono text-xs text-teal-600 dark:text-teal-400">@app.exception_handler(AppError)</div>
  <div class="flex-1 text-xs">异常处理表：<code>AppError → 那个翻译函数</code>　<span class="opacity-60">（登记的不是路由）</span></div>
</div>
<div v-click="4" class="flex gap-4 py-2.5 border-b border-gray-400/15 items-center">
  <div class="w-72 shrink-0 font-mono text-xs text-amber-600 dark:text-amber-400">@lru_cache</div>
  <div class="flex-1 text-xs"><b class="text-amber-600 dark:text-amber-400">这个才是真的改造函数</b>（加了缓存）——是少数派</div>
</div>
</div>

<LessonLink v-click="5">
解剖台第一行就是 <code class="text-xs">@app.post("/getPosts")</code>（1.1.2 三问法的第一个示范对象）；1.2.6 的 <code class="text-xs">@router.get("")</code> / <code class="text-xs">@router.post("")</code>；1.3.1 的 <code class="text-xs">@app.exception_handler(AppError)</code>。<b>第 3 次课</b>会让你 <code class="text-xs">print(app.routes)</code> 把 FastAPI 真实路由表打出来——你会发现它和你下一页要写的 MiniApp 是<b>同一个东西</b>，只是字段更多。
</LessonLink>

<!--
好，现在讲最重要的一件事，这一句你们记住：你在 Web 框架里见到的装饰器，大部分不是在改造函数，是在登记函数。

[click] @router.get("/posts") 干了什么？它把你的函数塞进了一张表，键是方法加路径。

[click] @router.post("") 同理，塞进路由表另一个键。

[click] @app.exception_handler(AppError) 也一样，它把你的函数塞进另一张表，说"以后遇到 AppError 就调这个"。注意这里登记的不是路由，是错误翻译函数——接上了 0.9。

[click] 那有没有真改造函数的？有，@lru_cache，它给函数加了缓存。但这是少数派。

[click] 函数本身一个字节都没变，变的只是"它被记在了哪张表上"。下一页我们自己写一个，你就彻底信了。
-->

---

# 0.10 自己实现一个：15 行的 MiniApp

<div class="text-xs opacity-55 -mt-1 mb-2">不信装饰器只是「登记」？我们自己写一个。一个字典当路由表，两层嵌套函数就够了。</div>

<<< @/snippets/lesson00/decorator_demo.py#miniapp {lines:true}

<div class="mt-2 text-xs opacity-80"><code>route</code> 就是标准两步：外层 <code>route(path, method)</code> 接住参数、返回内层；内层 <code>decorator(func)</code> 接住函数，唯一做的事——<b class="text-teal-700 dark:text-teal-300">往字典里塞一条</b>，然后<b>原样返回</b>函数（一个字节没改）。</div>

<!--
不信？我们自己写一个。看这个 MiniApp，十五行，一个字典当路由表。

route 方法就是标准的两步：外层接住路径和方法，返回里面那个 decorator；内层 decorator 接住被装饰的函数，做的唯一一件事就是往 self.routes 这个字典里塞一条——键是方法加路径，值是函数本身。塞完还打印一句“[注册]”，方便你看清它什么时候执行。函数本身原样 return，一个字节没改。
-->

---

# 0.10 用它登记两个函数：路由表长这样

<div class="text-xs tracking-widest opacity-60 mb-2">登记两个函数（注意 <code>@app.route(...)</code> 的两步展开，就写在右边注释里）</div>

<<< @/snippets/lesson00/decorator_demo.py#register {lines:true}

<div grid="~ cols-2 gap-6" class="mt-3">

<div>

<div class="text-xs tracking-widest opacity-60 mb-1.5">跑出来的 <code>app.routes</code>（就是个字典）</div>

<div class="rounded-lg bg-gray-500/10 border border-gray-400/25 font-mono text-[13px] px-3 py-2 leading-relaxed">
{ (<span class="text-sky-600 dark:text-sky-400">'GET'</span>,&nbsp; '/posts'): &lt;function list_posts&gt;,<br>
&nbsp; (<span class="text-teal-600 dark:text-teal-400">'POST'</span>, '/posts'): &lt;function create_post&gt; }
</div>

</div>

<div class="text-xs opacity-80">键是 <b>(方法, 路径)</b> 元组，值是<b>函数对象</b>。跟第 3 次课 FastAPI 真实的 <code>app.routes</code> 对照——<b class="text-teal-700 dark:text-teal-300">同一个东西</b>，只是它每条记录带的字段更多。框架到这儿就不神秘了。</div>

</div>

<!--
下面 @app.route 登记两个函数，跑出来的 app.routes 就是这么个字典。你把它跟第 3 次课 FastAPI 真实的 app.routes 对照，会发现是同一个东西，只是 FastAPI 那个字典里每条记录带的字段更多。这时候框架就不神秘了。
-->

---
layout: center
class: text-center
---

<div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-700 dark:text-amber-300 font-bold text-sm tracking-wide">
⏸ 暂停跟做 9 · 跑一遍 MiniApp，看到路由表
</div>

<div class="mt-5 max-w-3xl mx-auto text-left">

<div class="text-xs tracking-widest opacity-55 mb-1.5">要执行的命令</div>

```bash
uv run python snippets/lesson00/decorator_demo.py
```

<div class="text-xs tracking-widest opacity-55 mt-3 mb-1.5">预期看到（静态对照，注意前两行的时机）</div>

```
[注册] GET /posts -> list_posts
[注册] POST /posts -> create_post
--- 上面两行 [注册] 是在 import 阶段就打印的，此刻我还没调用任何函数 ---
{('GET', '/posts'): <function list_posts at 0x...>,
 ('POST', '/posts'): <function create_post at 0x...>}
(200, '帖子列表')
(200, '已创建')
(404, 'not found')
[调用] greet
hi
```

<div class="mt-3 p-3 rounded-lg border-2 border-teal-500/40 bg-teal-500/5 text-sm">
<b>要能回答：</b>那两行 <code class="text-xs">[注册]</code> 是什么时候打印的？<b class="text-teal-700 dark:text-teal-300">为什么在我调用任何函数之前？</b>
</div>

</div>

<div class="mt-4 inline-flex items-center gap-2 text-teal-700 dark:text-teal-300 font-bold">
✓ 做完再继续
</div>

<!--
（跟做 9）你们跑一下这个文件。看输出——注意那两行"[注册]"，它们排在最前面，是在 import 这个文件的时候就打印出来的，我此刻还一个函数都没调用。

这说明什么？说明装饰器在"定义函数的那一刻"就执行了，登记这件事早在程序正式跑之前就做完了。这正是第 1 次课 FastAPI 启动时就已经知道所有路由的原因——路由表在 import 阶段就填好了。你能亲眼看到这两行排在最前面，这个认知就扎实了。
-->


---

# 0.11 async / await：只要求看懂形状

<div class="text-xs opacity-55 -mt-1 mb-3">本节核心是<b class="text-amber-600 dark:text-amber-400">划边界</b>，不是教内容。目标：看到 <code>async def</code> 不恐慌，并明确知道「第 4 次课整节课讲这件事」。</div>

<div grid="~ cols-[1.05fr_0.95fr] gap-6" class="mt-2">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">只讲三条，仅此三条</div>
<div class="space-y-2 text-sm">
  <div class="p-2.5 rounded-lg border border-teal-500/30 bg-teal-500/5"><b>1</b> · <code>async def</code> 定义的函数，<b class="text-rose-600 dark:text-rose-400">调用它不会执行</b>，会返回一个「协程对象」</div>
  <div class="p-2.5 rounded-lg border border-teal-500/30 bg-teal-500/5"><b>2</b> · <code>await</code> 只能写在 <code>async def</code> 里面，含义是「这里可能要等一会儿，先让别人干活」</div>
  <div class="p-2.5 rounded-lg border border-teal-500/30 bg-teal-500/5"><b>3</b> · 第 1 次课你只会在<b>一个地方</b>见到它 ↓</div>
</div>

```python
response = await call_next(request)
```

<div class="text-xs opacity-75 -mt-1">现在只需理解成：<b class="text-teal-700 dark:text-teal-300">把请求交给内层去处理，等它回来。</b>够了。</div>
</div>

<div>
<div class="rounded-lg border-2 border-dashed border-gray-400/50 bg-gray-500/6 overflow-hidden">
  <div class="px-3 py-1.5 bg-gray-500/12 text-xs font-bold tracking-wide flex items-center gap-2">🔒 明确不讲 · 整块留给第 4 次课</div>
  <div class="p-3 text-xs space-y-1.5 opacity-70">
    <div>· 事件循环是什么</div>
    <div>· 为什么 <code>async def</code> 里不能写阻塞代码</div>
    <div>· 什么时候用 <code>def</code>、什么时候用 <code>async def</code>，选错的后果</div>
    <div>· 为什么第 1 次课路由函数是 <code>def</code> 不是 <code>async def</code><span class="opacity-65">（届时调用栈里会看到 <code>run_in_threadpool</code> 这一帧，教师会说「这是第 4 次课的内容」）</span></div>
  </div>
  <div class="px-3 py-2 border-t border-gray-400/25 bg-amber-500/10 text-xs text-amber-700 dark:text-amber-300 font-bold">到此为止 —— 半懂比不懂更难纠正，所以今天一句都不展开。</div>
</div>
</div>

</div>

<LessonLink>
<code class="text-xs">middleware.py</code> 的 <code class="text-xs">async def dispatch(...)</code> 与那一行 <code class="text-xs">await call_next(request)</code>。第 1 次课 1.4.4 的调用栈里可能出现 <code class="text-xs">run_in_threadpool</code> / anyio 的帧，教师会明确告知「这是第 4 次课的内容，今天不展开」。
</LessonLink>

<!--
这一节很短，因为我今天故意不讲它。你在第 1 次课会见到一个 async def，就一个，在中间件里。你只需要知道三件事。

第一，async def 定义的函数，你调用它不会执行，它返回一个协程对象。第二，await 只能写在 async def 里面，意思是"这儿可能要等一会儿，我先让出去，让别人干活"。第三，第 1 次课你只会见到这一行：response = await call_next(request)。你把它理解成"把请求交给内层处理，然后等它回来"，就够用了。

到此为止。右边这一整块——事件循环是什么、为什么有的函数要写 async 有的不用、写错了会怎样——这些是第 4 次课整节课的内容，我今天一句都不讲。为什么不讲？因为半懂比不懂更麻烦。你现在建立一个错误的印象，第 4 次课我还得先把它拆掉。所以你在第 1 次课看到 async 的时候，就想"哦，这个第 4 次课讲"，然后继续往下听。这就是正确反应。
-->

---

# 0.12 包与模块：import 是怎么找到文件的

<div class="text-xs opacity-55 -mt-1 mb-3"><b class="text-teal-700 dark:text-teal-300">重点。</b>它是第 1 次课「依赖方向」能被讨论的物理前提，也是你实操卡住频率最高的地方（0.4 跟做 6 已经撞过一次）。</div>

<div grid="~ cols-2 gap-6" class="mt-2">

<div>
<div class="space-y-2 text-sm">
  <div class="p-2.5 rounded-lg border border-gray-400/25 bg-gray-500/5"><b>模块</b> ＝ 一个 <code>.py</code> 文件</div>
  <div class="p-2.5 rounded-lg border border-gray-400/25 bg-gray-500/5"><b>包</b> ＝ 一个含 <code>__init__.py</code> 的目录</div>
  <div class="p-2.5 rounded-lg border border-teal-500/30 bg-teal-500/5"><code class="text-xs">from mini.service import TodoService</code><br><span class="text-xs opacity-80">→ 去找 <code>mini/service.py</code>，从里面取出 <code>TodoService</code></span></div>
</div>
<div class="mt-3 p-3 rounded-lg bg-amber-500/8 border-l-4 border-amber-500 text-xs">
Python 从<b>「当前工作目录 ＋ 已安装的包目录」</b>里找 <code>mini</code> 这个名字。所以跟做 6 里你 <code>cd ..</code> 之后就找不到了——<b>不是代码的问题，是你站错了地方</b>。
</div>
</div>

<div>
<div class="text-xs tracking-widest opacity-60 mb-2"><code>python -m mini.cli</code> vs <code>python mini/cli.py</code></div>
<div class="rounded-lg overflow-hidden border border-gray-400/25 text-xs">
  <div class="flex gap-2 px-3 py-1.5 bg-gray-500/10 tracking-wide"><div class="w-24 shrink-0"></div><div class="flex-1 text-teal-700 dark:text-teal-300 font-bold">-m mini.cli</div><div class="flex-1 text-rose-600 dark:text-rose-400 font-bold">mini/cli.py</div></div>
  <div class="flex gap-2 px-3 py-2 border-t border-gray-400/15"><div class="w-24 shrink-0 opacity-70">Python 眼里</div><div class="flex-1">运行 mini 包里的 cli 模块</div><div class="flex-1 opacity-80">运行一个孤立脚本文件</div></div>
  <div class="flex gap-2 px-3 py-2 border-t border-gray-400/15"><div class="w-24 shrink-0 opacity-70">搜索起点</div><div class="flex-1 text-teal-700 dark:text-teal-300 font-bold">当前工作目录</div><div class="flex-1 text-rose-600 dark:text-rose-400 font-bold">mini/ 目录本身</div></div>
  <div class="flex gap-2 px-3 py-2 border-t border-gray-400/15"><div class="w-24 shrink-0 opacity-70">from mini.errors</div><div class="flex-1 text-teal-700 dark:text-teal-300">找得到</div><div class="flex-1 text-rose-600 dark:text-rose-400">ModuleNotFoundError</div></div>
</div>
<div class="mt-3 p-3 rounded-lg bg-teal-500/8 border-l-4 border-teal-500 text-sm">结论：<b>运行包里的模块，用 <code>-m</code>。</b>这条规则记住，能省你好几个小时。</div>
</div>

</div>

<!--
这一节讲两件事：import 怎么找文件，以及为什么依赖必须有方向。

先说找文件。模块就是一个 py 文件，包就是一个带 __init__.py 的目录。from mini.service import TodoService 就是去找 mini 目录下的 service.py，从里面取出 TodoService。

从哪儿开始找？从你的当前工作目录开始找。所以刚才跟做 6 里你 cd 到上一层就找不到了，那不是代码坏了，是你站错了地方。

然后一个很实用的规则：跑包里的模块要用 -m。python -m mini.cli 和 python mini/cli.py 是两回事，后者会让 Python 以为你在跑一个孤立脚本，搜索路径变成 mini 目录本身，于是 from mini.errors import 就找不到 mini 了。这条规则记住，能省你好几个小时。
-->

---
layout: center
class: text-center
---

<div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-700 dark:text-amber-300 font-bold text-sm tracking-wide">
⏸ 现场实验 · 亲手把 mini 弄坏一次
</div>

<div class="mt-5 max-w-3xl mx-auto text-left">

<div class="text-xs tracking-widest opacity-55 mb-1.5">① 在 <code>mini/service.py</code> 最上面加一行（看完立刻删）</div>

```python
from mini.cli import main          # ← 故意加的
```

<div class="text-xs tracking-widest opacity-55 mt-3 mb-1.5">② 运行，预期看到</div>

```bash
uv run python -m mini.cli list
```

```
ImportError: cannot import name 'main' from partially initialized
module 'mini.cli' (most likely due to a circular import)
```

<div class="mt-3 p-3 rounded-lg bg-gray-500/8 text-sm text-left">
<b>发生了什么：</b><code class="text-xs">cli</code> 开始加载 → 要 import <code class="text-xs">service</code> → <code class="text-xs">service</code> 又要 import <code class="text-xs">cli</code> → 但 <code class="text-xs">cli</code> 才加载到一半，<code class="text-xs">main</code> 还没定义出来 → 报错。<b class="text-amber-600 dark:text-amber-400">这不是 Python 的缺陷，是它在替你指出一个架构问题。</b>
</div>

</div>

<div class="mt-4 inline-flex items-center gap-2 text-teal-700 dark:text-teal-300 font-bold">
✓ 看完报错，把那行删掉改回来，再继续
</div>

<!--
现在做实验，我们把 mini 弄坏。你去 service.py 最上面加一行，import cli 里的 main。然后运行 list。

看这个报错：cannot import name main from partially initialized module，后面还贴心地告诉你 most likely due to a circular import。发生了什么？cli 开始加载，它要 import service。service 又要 import cli。但 cli 才加载到一半，main 还没定义出来，于是就炸了。

我要你们换个角度看这个报错：这不是 Python 的缺陷，这是它在替你指出一个架构问题。cli 依赖 service，这是对的，外层用内层。但 service 反过来依赖 cli，这说不通——业务规则凭什么要知道命令行怎么打印东西？只讲"不要循环导入"没用，你必须亲手弄坏一次、看到这句报错，这个痛感才是第 1 次课讲"依赖必须有方向"时唯一能依靠的具体经验。现在把那行删掉，改回去。
-->

---

# 0.12 依赖必须有方向

<div class="text-xs opacity-55 -mt-1 mb-3">箭头<b class="text-rose-600 dark:text-rose-400">只能单向</b>。<code>service</code> 里没有一处 import <code>cli</code>，所以第 1 次课把 <code>cli</code> 换成 HTTP 路由时，<code>service</code> / <code>repo</code> <b>一行都不用改</b>。</div>

<div grid="~ cols-2 gap-6" class="mt-2">

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">mini 的依赖箭头</div>
<div class="p-4 rounded-lg bg-gray-500/6 border border-gray-400/25">
  <div class="flex justify-center"><div class="px-5 py-1.5 rounded border-2 border-sky-500/50 bg-sky-500/8 font-mono text-sm font-bold">cli</div></div>
  <div class="text-center text-base opacity-40 leading-tight my-0.5">↓</div>
  <div class="flex justify-center"><div class="px-5 py-1.5 rounded border-2 border-teal-500/50 bg-teal-500/8 font-mono text-sm font-bold">service</div></div>
  <div class="text-center text-base opacity-40 leading-tight my-0.5">↓</div>
  <div class="flex justify-center"><div class="px-5 py-1.5 rounded border-2 border-amber-500/50 bg-amber-500/8 font-mono text-sm font-bold">repo</div></div>
  <div class="text-center text-base opacity-40 leading-tight my-0.5">↓　↙　↘</div>
  <div class="flex justify-center"><div class="px-4 py-1.5 rounded border border-purple-500/40 bg-purple-500/8 font-mono text-sm">models / errors</div></div>
  <div class="mt-3 pt-3 border-t border-dashed border-gray-400/30 flex items-center justify-center gap-2">
    <div class="px-3 py-1 rounded border border-rose-500/40 bg-rose-500/8 font-mono text-xs text-rose-600 dark:text-rose-400 line-through">service → cli</div>
    <span class="text-xs text-rose-600 dark:text-rose-400 font-bold">✗ 禁止（刚才那个报错）</span>
  </div>
</div>
</div>

<div>
<div class="text-xs tracking-widest opacity-60 mb-2">架构约束＝一条能跑出结果的命令</div>

```bash
grep -rn "from mini.cli" mini/service.py mini/repo.py
# 应当无输出
```

<div class="text-xs tracking-widest opacity-60 mt-4 mb-2">对应第 1 次课的两条自查命令</div>

```bash
grep -rn "from app.repositories" app/routers/   # 应无输出
grep -rn "fastapi\|starlette"   app/services/   # 应无输出
```

<div class="mt-3 p-3 rounded-lg bg-teal-500/8 border-l-4 border-teal-500 text-sm font-bold text-center">架构约束不是一句口号，<br>它是一条能跑出结果的命令。</div>
</div>

</div>

<LessonLink>
1.5.1 的四层依赖方向图与本节的 mini 依赖图<b>同构</b>；1.5.1 的两条 <code class="text-xs">grep</code> 自查命令也一模一样。第 1 次课开场会直接说：「你们上次让 service 去 import cli，那个报错就是<b>依赖方向反了的物理表现</b>。」
</LessonLink>

<!--
所以依赖必须有方向，看这张图，箭头只能单向：cli 到 service 到 repo，再到 models 和 errors。下面那条 service 到 cli 的红箭头，是被禁止的，就是你刚才亲手制造的那个报错。

service 里一处都没 import cli，所以第 1 次课我把 cli 换成 HTTP 路由，service 和 repo 一行不动。

最后一件事。你可能觉得"依赖方向"是句空话，怎么检查？一条命令就能查：grep 一下，service 里有没有 import cli，有输出就是违反了。第 1 次课我会给你们两条一模一样的命令，用来查那个项目的架构违规——routers 里不许直接 import repositories，services 里不许出现 fastapi 或 starlette。记住这句话：架构约束不是口号，它是一条能跑出结果的命令。
-->

---

# 0.13 允许暂时不懂的清单

<div class="text-xs opacity-55 -mt-1 mb-2">心理建设，<b class="text-amber-600 dark:text-amber-400">不能省</b>。第 1 次课你会撞见一堆没讲过的东西，提前给你一张白名单，免得你在课堂上分神纠结、误判「我完全跟不上」——这是这门课最主要的流失原因。</div>

<div class="mt-1 text-[13px]">
<div class="flex gap-3 pb-1.5 mb-1 border-b border-gray-400/30 text-xs tracking-wide opacity-60">
  <div class="w-64 shrink-0">你会在第 1 次课见到</div>
  <div class="flex-1">现在只需理解成</div>
  <div class="w-28 shrink-0 text-center">什么时候真正讲</div>
</div>
<div class="flex gap-3 py-1.5 border-b border-amber-500/20 bg-amber-500/8 items-center">
  <div class="w-64 shrink-0 font-mono text-xs"><b class="text-amber-600 dark:text-amber-400">★</b> Depends(get_post_service)</div>
  <div class="flex-1">「帮我把这东西准备好、传进来」</div>
  <div class="w-28 shrink-0 text-center text-xs opacity-70">第 3 次课</div>
</div>
<div class="flex gap-3 py-1.5 border-b border-amber-500/20 bg-amber-500/8 items-center">
  <div class="w-64 shrink-0 font-mono text-xs"><b class="text-amber-600 dark:text-amber-400">★</b> async def / await call_next</div>
  <div class="flex-1">「交给内层，等它回来」</div>
  <div class="w-28 shrink-0 text-center text-xs opacity-70">第 4 次课</div>
</div>
<div class="flex gap-3 py-1.5 border-b border-amber-500/20 bg-amber-500/8 items-center">
  <div class="w-64 shrink-0 font-mono text-xs"><b class="text-amber-600 dark:text-amber-400">★</b> BaseHTTPMiddleware</div>
  <div class="flex-1">「包在所有请求外面的一层」</div>
  <div class="w-28 shrink-0 text-center text-xs opacity-70">第 4 次课</div>
</div>
<div class="flex gap-3 py-1.5 border-b border-amber-500/20 bg-amber-500/8 items-center">
  <div class="w-64 shrink-0 font-mono text-xs"><b class="text-amber-600 dark:text-amber-400">★</b> ContextVar</div>
  <div class="flex-1">「每个请求各自一份的全局变量」</div>
  <div class="w-28 shrink-0 text-center text-xs opacity-70">第 4 次课</div>
</div>
<div class="flex gap-3 py-1 border-b border-gray-400/12 items-center opacity-45">
  <div class="w-64 shrink-0 font-mono text-xs">BaseSettings</div><div class="flex-1 text-xs">「会自动从环境变量读值的类」</div><div class="w-28 shrink-0 text-center text-xs">第 1 次课够用</div>
</div>
<div class="flex gap-3 py-1 border-b border-gray-400/12 items-center opacity-45">
  <div class="w-64 shrink-0 font-mono text-xs">response_model=PostOut</div><div class="flex-1 text-xs">「只允许这些字段出去」</div><div class="w-28 shrink-0 text-center text-xs">第 1、8 次课</div>
</div>
<div class="flex gap-3 py-1 border-b border-gray-400/12 items-center opacity-45">
  <div class="w-64 shrink-0 font-mono text-xs">@dataclass</div><div class="flex-1 text-xs">0.8 已讲，省掉手写 <code>__init__</code></div><div class="w-28 shrink-0 text-center text-xs">已讲</div>
</div>
<div class="flex gap-3 py-1 border-b border-gray-400/12 items-center opacity-45">
  <div class="w-64 shrink-0 font-mono text-xs">request.scope</div><div class="flex-1 text-xs">「一个装着请求信息的字典」</div><div class="w-28 shrink-0 text-center text-xs">第 3 次课</div>
</div>
<div class="flex gap-3 py-1 items-center opacity-45">
  <div class="w-64 shrink-0 font-mono text-xs">Mapped / mapped_column</div><div class="flex-1 text-xs">第 1 次课不会出现，别提前查</div><div class="w-28 shrink-0 text-center text-xs">第 6 次课</div>
</div>
</div>

<div class="mt-2 text-xs opacity-60"><b class="text-amber-600 dark:text-amber-400">★</b> 这四个是第 1 次课出现频率最高、最容易卡住的，重点看；其余整屏扫一眼即可，不逐行念。<span class="opacity-70">（本清单是复用素材：之后每次课讲掉一个，就划掉一行。）</span></div>

<!--
最后五分钟，讲一件跟语法无关的事。第 1 次课你会撞见一堆我没教过的东西。我现在提前把它们列出来，告诉你：允许不懂。

比如这个 Depends，你看到它，就想"哦，帮我把这个东西准备好传进来"，够了，第 3 次课讲。async 和 await，"交给内层，等它回来"，够了，第 4 次课讲。ContextVar，"每个请求各自一份的全局变量"，够了，第 4 次课讲。这四个是你最容易卡住的，我标了星。剩下的你扫一眼就行，我不逐行念。
-->

---
layout: center
class: text-center
---

# 这张表的另一个用途

<div class="mt-2 text-sm opacity-75 max-w-2xl mx-auto">这才是本节真正的落点——它本身就是一次示范：<b>面对不懂的代码，正确反应不是恐慌</b>，而是三步。</div>

<div class="mt-8 max-w-3xl mx-auto grid grid-cols-3 gap-4 text-left">
<div class="p-4 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-3xl font-bold text-teal-700 dark:text-teal-300 mb-2">1</div>
  <div class="text-sm">先给它一个<b>够用的近似解释</b></div>
</div>
<div class="p-4 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-3xl font-bold text-teal-700 dark:text-teal-300 mb-2">2</div>
  <div class="text-sm"><b>标记它</b>，记下「这个我不懂」</div>
</div>
<div class="p-4 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-3xl font-bold text-teal-700 dark:text-teal-300 mb-2">3</div>
  <div class="text-sm"><b>继续往下走</b>，不停在这里</div>
</div>
</div>

<div class="mt-8 max-w-3xl mx-auto p-4 rounded-lg bg-amber-500/10 border-l-4 border-amber-500 text-sm text-left">
这个习惯在读 AI 生成代码时会一直用到。AI 一次给你一百行，里面<b>永远</b>有你不认识的东西。<b class="text-amber-700 dark:text-amber-300">能不能带着几个未解决的问号继续往前推进，是能不能用好 AI 的分界线之一。</b>
</div>

<!--
但这张表还有一个更重要的用途，这是我今天想留给你们的最后一句话。它本身就是一次示范：面对不懂的代码，正确反应不是恐慌。

正确反应是三步——先给它一个够用的近似解释，标记一下"这个我不懂"，然后继续往下走。为什么这很重要？因为 AI 一次给你一百行代码，里面永远有你不认识的东西，永远。你要是每次都停在第一个不认识的地方，你一辈子读不完一个文件。能不能带着几个没解决的问号继续往前推进——这是能不能用好 AI 的分界线之一。
-->

---
layout: center
class: text-center
---

# 课前课到此结束

<div class="mt-2 text-sm opacity-70 max-w-2xl mx-auto">建议把 <b>0.6 调用栈</b>和 <b>0.10 装饰器</b>两段高光各看两遍，然后去把<b>两道门槛</b>过掉。<span class="opacity-60">（详细验收清单随堂发布，这里只点名。）</span></div>

<div class="mt-8 max-w-3xl mx-auto grid grid-cols-2 gap-5 text-left">
<div class="p-5 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-2">门槛一</div>
  <div class="text-lg font-bold mb-1.5">环境验收</div>
  <div class="text-sm opacity-80">5 张截图：Git · 依赖 · mini 程序 · <b class="text-amber-600 dark:text-amber-400">调试器</b> · curl。<br><span class="text-xs opacity-70">调试器那条是重点：必须看到<b>展开的 Call Stack、≥4 层帧</b>，只看到断点变黄不算过。</span></div>
</div>
<div class="p-5 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-xs tracking-widest opacity-60 mb-2">门槛二</div>
  <div class="text-lg font-bold mb-1.5">读代码测试</div>
  <div class="text-sm opacity-80">20 题，<b>≥80%</b> 通过，可重测。<br><span class="text-xs opacity-70">题型全是「读懂」而非「记忆」。</span></div>
</div>
</div>

<div class="mt-8 text-base font-bold text-teal-700 dark:text-teal-300">第 1 次课见。</div>

<!--
好，课前课到这儿。这一讲的东西不少，但核心就两件：把"代码跑在哪、报错怎么读、调试器怎么用"打通（讲一），把"第 1 次课会冒出来的 Python 写法"先见一遍（讲二）。

现在去把两道门槛过掉。门槛一是环境验收，交五张截图，其中调试器那张是重点——我要看到你展开的 Call Stack 面板、至少四层帧，光断点变黄不算。门槛二是读代码测试，二十题，八十分通过，可以重测，考的全是"读懂"不是"背"。详细清单我随堂发。第 1 次课见。
-->
