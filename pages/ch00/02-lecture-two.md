---
layout: section
class: lecture-two lecture-opening
---

<div class="eyebrow">讲二 · PYTHON 阅读基础</div>

# 读懂第 1 次课<br>要出现的 <span class="key">Python 写法</span>

<div class="pt-3 text-sm opacity-80 leading-loose">
0.7 类型注解 · 0.8 对象与常见表达式 · 0.9 异常与执行顺序<br>
0.10 装饰器 · 0.11 async 边界 · 0.12 启动与 import · 0.13 阅读边界与自检
</div>

<div class="mt-8 text-sm key">
读懂代码，不要求从零设计框架
</div>

<!--
课前讲二只为读懂第 1 次课的单文件搜索案例。学生已经练过启动程序、读报文和切换栈帧；这一讲补上函数签名、对象访问和执行顺序。
教学预算：讲解约 60 分钟，暂停跟做另计；不是已核对的录播时长。

节奏建议：注解 6 分钟、对象与表达式 14 分钟、异常 8 分钟、装饰器 16 分钟、async 4 分钟、启动与 import 5 分钟、阅读边界与自检 7 分钟。暂停跟做单独计时。

使用第一课真实源码和已有 mini 示例，结构示意明确标注。不预讲依赖注入、分层、统一异常契约，也不提前给出 request-id 的解决方案；把发现问题的过程留给第一课。
-->

---
class: lecture-two
---

# 讲二怎么学：会读，不要求从零写框架

<div grid="~ cols-2 gap-6" class="mt-6 text-sm">
<div class="p-5 rounded-lg border border-teal-500/40 bg-teal-500/5">
<h3 class="key">阅读主线</h3>
<p>读出参数、类型与默认值；认出属性访问、with 与结果转换。</p>
<p>区分函数对象和调用；说明 @ 登记时机、return / raise 后的执行顺序。</p>
<p>async / await 只读形状；0.12 亲手启动搜索服务并发一次请求。</p>
</div>
<div v-click="1" class="p-5 rounded-lg border border-sky-500/40 bg-sky-500/5">
<h3 class="example">教师演示／课后回看</h3>
<p>包装器和 MiniApp 内部实现由教师导读，允许暂停与回看。</p>
<p>不要求手写嵌套装饰器、实现路由器或解释线程池。</p>
<p>分层、依赖注入与统一异常设计，不作为第一课的先修门槛。</p>
</div>
</div>

<div v-click="2" class="mt-5 p-3 rounded-lg bg-amber-500/10 text-sm"><b class="caution">用给定源码和输出解释行为</b>；遇到不熟悉的工具操作，可回看讲一的对应练习。</div>

<!--
教学单元：讲二导读；本页：主线与阅读深度，不另加课时。
讲一已练过的工具不重做整套，把日志关联与四处取证留给第一课。
原有 60 分钟包含教师演示与思路导读，不要求学生同步写完示例。包装器和 MiniApp 是阅读材料，不变成独立编码作业；代码阅读自检仍覆盖装饰器登记时机。

[click] 展示教师导读与课后回看的范围。
[click] 收束到用源码和输出解释行为。
-->

---
class: lecture-two
---

# 0.7 类型注解：不会自动检查实参类型

<div class="text-xs -mt-1 mb-3">写了 <code>x: int</code>，不代表 Python 会自动拒绝其他类型。<b class="caution">注解不是运行时类型检查器。</b></div>

<div grid="~ cols-2 gap-6" class="mt-2">

<div>
<div class="text-xs tracking-widest opacity-75 mb-2">四种写法</div>
<div class="rounded-lg border border-gray-400/25 font-mono text-sm">
  <div class="px-3 py-2 border-b border-gray-400/15"><span class="text-teal-600 dark:text-teal-400">page: int = 1</span><span class="opacity-75 font-sans text-xs">　变量注解</span></div>
  <div class="px-3 py-2 border-b border-gray-400/15"><span class="text-teal-600 dark:text-teal-400">def double(n: int) -&gt; int:</span><span class="opacity-75 font-sans text-xs">　参数与返回</span></div>
  <div class="px-3 py-2 border-b border-gray-400/15"><span class="text-teal-600 dark:text-teal-400">keyword: str | None = None</span><span class="opacity-75 font-sans text-xs">　可能 str 也可能 None</span></div>
  <div class="px-3 py-2"><span class="text-teal-600 dark:text-teal-400">items: list[str]</span><span class="opacity-75 font-sans text-xs">　列表里装什么</span></div>
</div>
<div class="mt-3 text-xs opacity-70"><code>str | None</code> 读作「str 或 None」；<code>list[str]</code> 读作「装字符串的列表」。</div>
</div>

<div>
<div class="text-xs tracking-widest opacity-75 mb-2">现场演示 · <span class="font-bold text-rose-600 dark:text-rose-400">先猜，再看</span></div>

<<< @/snippets/lesson00/annotations_demo.py#double

```python
print(double(3))
print(double("ab"))
print(double([1, 2]))
print(double.__annotations__)
```

<div v-click="1" class="mt-2 text-xs tracking-widest opacity-75 mb-1">实际输出（静态对照）</div>
<div v-click="1" class="result rounded-lg bg-gray-500/10 border border-gray-400/25 px-3 py-2">
6<br>
<span class="text-rose-600 dark:text-rose-400 font-bold">abab</span>　<span class="opacity-75 font-sans text-xs">← 注解写 int，传 str 照样跑出结果</span><br>
[1, 2, 1, 2]<br>
{'n': &lt;class 'int'&gt;, 'return': &lt;class 'int'&gt;}
</div>
</div>

</div>

<!--
类型注解，先做个实验。这个函数 double 写着参数是 int，返回是 int。我传一个字符串 "ab" 进去，你猜会怎样？

先停一下，让学生预测传入字符串的结果。

[click] 输出 abab，因为字符串乘 2 就是重复两遍。传列表也一样。Python 没有因注解而拒绝实参；本例的 __annotations__ 还能读到注解信息。注意这不意味着所有操作都不会报类型错误，只是注解本身不自动强制检查。
-->

---
class: lecture-two
---

# 0.7 注解不检查，那它有什么用？

<div class="text-xs opacity-75 -mt-1 mb-3">区分两件事：直接调用 Python 函数，与让框架处理 HTTP 输入。</div>

<div grid="~ cols-[0.8fr_1.2fr] gap-6" class="mt-2">

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
  <div v-click="1" class="flex items-start gap-3 p-3 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
    <span class="w-6 h-6 rounded-full bg-teal-500/25 text-xs flex items-center justify-center font-bold shrink-0">3</span>
    <span><b class="text-teal-700 dark:text-teal-300">框架读取注解，处理外部输入</b></span>
  </div>
</div>
<div v-click="2" class="mt-3 p-3 rounded-lg bg-amber-500/10 border-l-4 border-amber-500 text-sm">
<b class="caution">Python 不自动检查，不等于框架不会检查。</b>第 10 次课再比较 TypeScript：转译与类型检查也不是同一件事。
</div>
</div>

<div v-click="2">
<div class="text-xs tracking-widest opacity-75 mb-2">第 1 次课真实签名 · v1_ai_raw.py</div>

```python
# 路由装饰器在 0.10 解释
@app.post("/getQuestions")
def get_questions(keyword: str = "", page: int = 1):
    ...
```

<div class="mt-3 text-sm space-y-2">
<div>· <code>keyword</code>、<code>page</code>：<span class="example">参数名</span>。</div>
<div>· <code>str</code>、<code>int</code>：<span class="key">类型注解</span>。</div>
<div>· <code>""</code>、<code>1</code>：省略参数时的<span class="caution">默认值</span>。</div>
<div>· 通过 HTTP 传入 <code>page=abc</code>：FastAPI 会返回 <b class="error">422</b>，<b class="error">不进入函数体</b>。</div>
</div>
<div class="mt-3 text-xs opacity-70">这里只有整数类型要求，尚未限制 page ≥ 1。参数约束与模型在第 3 次课展开。</div>
</div>

</div>

<!--
先看编辑器与静态检查工具的用途。

[click] 框架也会读取注解，并据此处理 HTTP 输入。这不是 Python 自己突然开始检查函数实参。

[click] 对照第一课的真实函数签名，逐个读出参数名、类型和默认值。传 page=abc 的 HTTP 请求会在进入函数体前被拒绝；整数负数却不受这个签名限制。今天先能读懂这种区别，第 3 次课再学校验规则。
-->

---
class: lecture-two
---

# 0.8 对象：点号取属性，括号做调用

<div class="text-sm opacity-70 mb-5">先读懂对象的用法；本节不要求设计类、继承体系或项目分层。</div>

<div grid="~ cols-2 gap-6">
<div>
<div class="text-xs tracking-widest opacity-75 mb-2">教师导读 · MiniApp 初始化节选</div>

```python
class MiniApp:
    def __init__(self):
        self.routes = {}

app = MiniApp()
print(app.routes)  # {}
```

<div v-click="1" class="mt-3 text-sm"><code>MiniApp</code> 是<span class="example">类</span>，<code>app</code> 是<span class="key">实例</span>。创建实例时调用 <code>__init__</code> 初始化；这里的 <code>self</code> 指向该实例。</div>
</div>
<div class="text-sm space-y-3">
<div v-click="2" class="step-row"><code>request.method</code><br><b class="key">读取</b>请求对象的 method 属性。</div>
<div v-click="3" class="step-row"><code>request.headers.get("Accept", "")</code><br>先取 headers，再<b class="key">调用</b>它的 get 方法；没有这个头时返回空字符串。</div>
<div v-click="3" class="step-row"><code>engine.connect()</code><br><b class="key">调用</b> engine 对象的 connect 方法。</div>
<div v-click="3" class="text-xs">调用实例方法时，Python 会把实例传给第一个参数，通常命名为 <code>self</code>。</div>
</div>
</div>

<!--
教学单元：0.8；本页：对象访问。
MiniApp 只取现有演示的初始化部分，完整注册行为在 0.10 阅读。让学生区分 app.routes 和 app.route(...)：属性读取与方法调用。request 和 engine 的内部实现不在这里展开。

[click] 对照初始化代码，区分类与实例，解释 self。
[click] 点号取属性：先看 request.method。
[click] 括号做调用：对照 headers.get 与 engine.connect，再回到 self。
-->

---
class: lecture-two
---

# 0.8 连接代码块与字符串：先读懂形状

<div grid="~ cols-2 gap-6" class="mt-5">
<div>
<div class="text-xs tracking-widest opacity-75 mb-2">连接使用的结构节选</div>

```python
with engine.connect() as conn:
    rows = conn.execute(
        text("SELECT 1")
    ).fetchall()
```

<div v-click="1" class="mt-3 text-sm">进入代码块<b class="key">取得连接</b>，命名为 <code>conn</code>；执行 SQL、取出结果。退出时由上下文管理器<b class="key">清理资源</b>。</div>
<div v-click="1" class="mt-3 text-sm opacity-80">这里不等于每次关闭底层物理连接，也<b class="caution">不等于自动提交</b>；连接池与事务后续再讲。</div>
</div>
<div v-click="2">
<div class="text-xs tracking-widest opacity-80 mb-2">f-string：把表达式结果放进字符串</div>

```python
keyword = "react"
message = f"query keyword={keyword}"
print(message)
# query keyword=react
```

<div class="mt-3 text-sm">前缀 <code>f</code> ＋花括号中的表达式。<b class="key">先计算，再放进字符串</b>。</div>
<div v-click="3" class="mt-3 p-3 rounded-lg bg-amber-500/10 text-sm">第一课反例用它拼 SQL。<b class="caution">读懂语法不代表认可安全性</b>，仅限本地虚构数据；第 3 次用参数化模板，第 6 次解释原理。</div>
</div>
</div>

<!--
教学单元：0.8；本页：with 与 f-string。
代码为形状节选，engine、text 由示例提供。with 的重点是资源使用范围；本例先取完结果，再退出连接上下文。不要把 with 一概解释为自动提交。

[click] 解释进入、使用和退出连接代码块。
[click] 读 f-string 的表达式与结果。
[click] 补充拼接 SQL 的安全边界。
-->

---
class: lecture-two
---

# 0.8 列表推导式与日志参数：拆成小步读

<div grid="~ cols-2 gap-6" class="mt-5">
<div>
<div class="text-xs tracking-widest opacity-75 mb-2">搜索结果转换 · 同一操作的展开</div>

```python {1|4-6|all}
[dict(r._mapping) for r in rows]

# 等价的阅读展开
data = []
for r in rows:
    data.append(dict(r._mapping))
```

<div v-click="1" class="mt-3 text-sm">每次从 rows <b class="key">取一行 → 转成字典 → 收集成列表</b>。<code>r._mapping</code> 是 SQLAlchemy 行对象的映射视图。</div>
</div>
<div v-click="2">
<div class="text-xs tracking-widest opacity-80 mb-2">日志：模板与参数分开给</div>

```python
logger.info("query keyword=%s page=%s",
            keyword, page)
```

<div class="mt-3 text-sm"><code>%s</code> 是<b class="key">占位符</b>，后面的两个参数依次填入；INFO 是日志级别，<b class="caution">不是 HTTP 状态码</b>。</div>
<div v-click="3" class="mt-4 text-sm">遇到 <code>*args</code> / <code>**kwargs</code>：<b class="key">定义处收集</b>其余位置 / 关键字参数；<b class="example">调用处展开转交</b>。先看数据从哪里来、交给谁。</div>
</div>
</div>

<LessonLink v-click="3">先能逐行读懂搜索代码。第一课再问：这些记录足够判断一次请求经历了什么吗？</LessonLink>

<!--
教学单元：0.8；本页：结果转换与日志调用。
列表推导式不是新的数据库查询，而是在遍历已有 rows。日志示意和课堂 plain 模式一致；不在课前提供并发记录关联方案。

[click] 高亮展开后的循环，对照取行、转换、收集三个动作。
[click] 恢复完整代码，转向日志模板与参数。
[click] 补充参数的收集与展开，再连接第一课的观察问题。
-->


---
class: lecture-two
---

# 0.9 异常：先判断哪一行还会执行

<div class="text-sm opacity-70 mb-4">异常会中断当前正常路径，沿调用关系寻找匹配的处理者；不是“报一句错然后自动接着跑”。</div>

<div grid="~ cols-2 gap-6">
<div>
<div class="text-xs tracking-widest opacity-75 mb-2">控制流结构示意</div>

```python {all|all|2,4-5,8-9}
try:
    result = do_something()
    print("调用之后")
except ValueError as exc:
    print("捕获：", exc)
else:
    print("正常完成")
finally:
    print("清理")
```

</div>
<div v-click="1" class="text-sm space-y-3">
<div><b class="example">try</b>：尝试执行；发生异常后，块内剩余语句跳过。</div>
<div><b class="error">except</b>：只处理匹配的异常；<code>as exc</code> 给异常对象起名字。</div>
<div><b class="key">else</b>：try 正常执行完才进入。</div>
<div><b class="caution">finally</b>：离开这段处理结构时执行，常用于清理；不保证进程被强制终止时仍能运行。</div>
</div>
</div>

<div v-click="2" class="mt-4 p-3 rounded-lg bg-amber-500/10 text-sm">若调用抛出 <code>ValueError</code>：<b class="error">不打印“调用之后”</b>，而是执行 <b class="error">except</b>，再执行 <b class="caution">finally</b>。未匹配的异常继续向外传播。</div>

<!--
教学单元：0.9；本页：异常控制流。
这是一份结构示意，do_something 由具体程序提供，不要求四段同时出现。先让学生指出抛错后哪些语句会跳过。
[click] 逐项解释 try、except、else、finally，先不揭示本例路径。
[click] 揭示路径。捕获父类也能接住其子类；今天只读已有异常名称，不设计异常家族。全局处理与统一错误契约留第 4 次课。
-->

---
class: lecture-two
---

# 0.9 return 失败信息，与 raise 不是一回事

<div grid="~ cols-[1.2fr_0.8fr] gap-6" class="mt-5">
<div>
<div class="text-xs tracking-widest key mb-2">第一课 v1 详情接口的分支 · return</div>

```python
if row is None:
    return {"success": False, "message": "not found"}
```

<div v-click="1" class="mt-3 text-sm step-row">函数<b class="key">正常返回</b>了一个字典。<code>False</code> 只是其中的值，<b class="caution">不会自动抛出异常</b>，也不会自动改变 HTTP 状态。</div>
</div>
<div>
<div class="text-xs tracking-widest error mb-2">第一课 v2 的故意失败语句 · raise</div>

```python
raise RuntimeError("故意触发")
```

<div v-click="2" class="mt-3 text-sm p-3 rounded-lg bg-rose-500/8">当前正常路径<b class="error">被中断</b>。如果调用者没有接住异常，调用点后面的普通语句也<b class="error">不会接着执行</b>。</div>
</div>
</div>

<LessonLink v-click="3">第一课观察 /boom：已有记录中，哪些留下了，哪些没有？请根据 return / raise 的执行顺序预测，再与实际输出核对。</LessonLink>

<div v-click="3" class="mt-4 text-sm opacity-80">回想 mini 的退出码：机器也需要可识别的失败信号。HTTP 应怎样表达失败，在第一课用实际报文核对。</div>

<!--
教学单元：0.9；本页：正常返回与异常传播。
课前只提供预测执行顺序的工具，不提前补全异常处理。
先区分语言层面的 return 与 raise，再引出第一课的观察问题。不能把返回值方式一概判错，也不能声称抛异常就自动得到正确的业务状态码。mini 只是运行练习，不承诺第一课把它原封不动改成 Web 分层项目。

[click] return 正常返回字典，False 是数据。
[click] raise 中断正常路径，异常向外传播。
[click] 用两种执行顺序预测 /boom，再联系退出码与 HTTP 失败信号。
-->


---
class: lecture-two
---

# 0.10 装饰器：读懂路由上方的 @

<div class="text-sm opacity-70 mb-3">目标是读懂“把函数交给另一个可调用对象”，不要求独立编写装饰器。</div>

<div grid="~ cols-2 gap-6" class="mt-2 wrap-code">

<div>
<div class="text-xs tracking-widest key mb-2">前提：函数是对象</div>

```python
def hello():
    return "hi"

f = hello              # 不加括号＝把函数本身赋给 f
print(f())             # hi
print(hello.__name__)  # hello → 有属性，说明是对象
```

<div v-click="1" class="mt-3 text-sm">能赋值、能当参数传、能从函数里返回——正因为<b class="key">函数是对象</b>，装饰器才可能存在。</div>
</div>

<div v-click="2">
<div class="text-xs tracking-widest opacity-80 mb-2">教师演示／回看 · 无参装饰器的展开</div>

<<< @/snippets/lesson00/decorator_demo.py#log_call {*}{lines:true}

</div>

</div>

<div v-click="3" class="mt-3 p-3 rounded-lg bg-teal-500/8 border-l-4 border-teal-500 text-sm">
<code>@log_call</code> ＋ 函数定义　<b class="key">完全等价于</b>　定义完再补一行：
<code class="key">greet = log_call(greet)</code><br>
<span class="opacity-80">——一行赋值，没有任何魔法。</span>
</div>

<!--
这一节先区分函数对象与函数调用，再读懂装饰器对函数做了什么。允许暂停回看，不考手写嵌套函数。

[click] 第一个前提：函数是对象。你可以把它赋给变量、传给别的函数、从函数里返回。hello 不加括号赋给 f，f() 照样能调用；hello.__name__ 能取到属性——说明它就是个对象。

[click] 展示右侧源码，先找到接收 func 和返回 wrapper 的位置。

[click] 基于这个，@ 是什么？右边这个 log_call，@log_call 加一个函数定义，完全等价于：函数定义完之后，再写一行 greet = log_call(greet)。就这样，一行赋值的简写，没有任何魔法。
-->

---
clicks: 2
class: lecture-two
---

# 0.10 带参数的装饰器：先取得，再应用

<div class="text-sm mb-3">用第一课 v1 / v2 的旧 POST 路由读两步：<b class="key">执行函数定义时登记</b>，不是收到请求后才登记。</div>

<div grid="~ cols-[0.85fr_1.15fr] gap-6" class="mt-4">

<div>
<div class="text-xs tracking-widest opacity-75 mb-2">你看到的写法</div>

```python
@app.post("/getQuestions")
def get_questions():
    ...
```

<div class="mt-8 text-center text-3xl key">→</div>
<div class="mt-2 text-center text-sm opacity-80">完全等价于右边两步<br><span class="text-xs">先取得，再应用</span></div>
</div>

<div>
<div v-click="1" class="p-4 rounded-lg border-2 border-amber-500/50 bg-amber-500/8">
  <div class="text-xs font-bold text-amber-700 dark:text-amber-300 mb-2">第 1 步 · 调用装饰器工厂</div>
  <code class="text-sm font-mono">decorator = app.post("/getQuestions")</code>
  <div class="text-sm opacity-85 mt-2.5">先计算装饰器表达式，得到 decorator；此时尚未把端点函数交给它。</div>
</div>
<div v-click="2" class="mt-4 p-4 rounded-lg border-2 border-teal-500/50 bg-teal-500/8">
  <div class="text-xs font-bold text-teal-700 dark:text-teal-300 mb-2">第 2 步 · 再把它用到函数上</div>
  <code class="text-sm font-mono">get_questions = decorator(get_questions)</code>
  <div class="text-xs opacity-85 mt-2.5">这一步才把函数交给装饰器——<b class="key">登记 / 改造发生在这里</b>。</div>
</div>
<div v-click="2" class="mt-4 text-sm">两步描述的是调用关系，<b>不要求三层嵌套</b>。下一页的注册型例子只有工厂与 decorator 两层。</div>
</div>

</div>

<!--
教学单元：0.10；本页：带参数的装饰器。为突出两步，省略真实搜索签名中的参数。

[click] 先求值 app.post("/getQuestions")，得到 decorator。

[click] 创建函数对象后，交给 decorator，再用返回值绑定函数名。注意处理函数体此时没有执行；注册型直接返回原函数，包装型可以返回新函数。
-->

---
class: lecture-two
---

# 0.10 先看用途：注册，还是包装？

<div grid="~ cols-2 gap-6" class="mt-6 text-sm">
<div class="p-4 rounded-lg border border-teal-500/40 bg-teal-500/5">
<h3 class="key">注册型：记录以后调用谁</h3>
<p><code>@app.post("/getQuestions")</code></p>
<p>让框架建立方法、路径与端点函数的关联。请求到来后，框架再进行匹配、解析和调用。</p>
</div>
<div v-click="1" class="p-4 rounded-lg border border-amber-500/40 bg-amber-500/5">
<h3 class="caution">包装型：返回另一个函数</h3>
<p><code>@log_call</code></p>
<p>本例返回 wrapper；以后调用 greet 时，先打印，再调用原函数。</p>
</div>
</div>

<div v-click="2" class="mt-5 p-3 rounded-lg bg-gray-500/8 text-sm">仅看 <code>@</code> <b class="caution">不能断定用途</b>。要读装饰器<b class="key">做了什么、返回了什么</b>；两种用途也可以组合。</div>

<LessonLink v-click="2">搜索接口第一行是在声明“这个方法和路径由谁处理”，不是当场执行搜索。路由匹配细节留第 3 次课。</LessonLink>

<!--
教学单元：0.10；本页：注册与包装的区别。
两种用途并列，不宣称其中一种在所有 Web 框架里占多数。
[click] 展示包装型，与已显示的注册型并列比较。
[click] 让学生回看 log_call 的 return wrapper，和后面 MiniApp 的 return func 对比。
-->

---
class: lecture-two compact-code
---

# 0.10 读一个小例子：MiniApp 的注册过程

<div class="text-xs opacity-80 mb-1">教师演示／课后回看：字典保存对应关系，只追登记与调用，不要求复写或设计框架。</div>

<<< @/snippets/lesson00/decorator_demo.py#miniapp {1-3|5-10|12-16|all}{lines:true}

<div v-click="1" class="mt-2 text-xs"><code>route</code> 就是标准两步：外层 <code>route(path, method)</code> 接住参数、返回内层；内层 <code>decorator(func)</code> 接住函数，唯一做的事——<b class="key">往字典里塞一条</b>，然后<b class="key">原样返回</b>函数（一个字节没改）。</div>

<!--
读现成的 MiniApp，只追三个动作：创建字典、登记函数、按键找到并调用。它只模拟路由职责，没有实现 HTTP、参数校验或异步调度。

[click] route 方法就是标准的两步：外层接住路径和方法，返回里面那个 decorator；内层 decorator 接住被装饰的函数，做的唯一一件事就是往 self.routes 这个字典里塞一条——键是方法加路径，值是函数本身。塞完还打印一句“[注册]”，方便你看清它什么时候执行。函数本身原样 return，一个字节没改。

[click] 高亮 handle：按方法、路径找到函数，此时 func() 才调用它。
[click] 恢复完整代码，串起创建字典、登记与调用。
-->

---
class: lecture-two
---

# 0.10 用它登记两个函数：路由表长这样

<div class="text-xs tracking-widest opacity-75 mb-2">教师演示／课后回看 · 对照注释中的两步展开，找到登记时机</div>

<<< @/snippets/lesson00/decorator_demo.py#register {1-3|6-8|all}{lines:true}

<div grid="~ cols-[1.1fr_0.9fr] gap-6" class="mt-3">

<div v-click="2">

<div class="text-xs tracking-widest opacity-80 mb-1.5">跑出来的 <code>app.routes</code>（就是个字典）</div>

<div class="result rounded-lg bg-gray-500/10 border border-gray-400/25 px-3 py-2">
{ (<span class="text-sky-600 dark:text-sky-400">'GET'</span>,&nbsp; '/posts'): &lt;function list_posts&gt;,<br>
&nbsp; (<span class="text-teal-600 dark:text-teal-400">'POST'</span>, '/posts'): &lt;function create_post&gt; }
</div>

</div>

<div v-click="3" class="text-sm">MiniApp 用 <b class="key">(方法, 路径)</b> 元组作键，<b class="key">函数作值</b>。FastAPI 的 <code>app.routes</code> 则是<b class="example">路由对象列表</b>：关联职责相似，<b class="caution">数据结构和匹配机制不同</b>。</div>

</div>

<!--
此页仍是 MiniApp 的 /posts 玩具例子，不是第一课的搜索 API。静态输出省略函数地址，只表达键值关系；真实打印在下一页。第 3 次课再观察 FastAPI 的路由对象列表，不把它说成字典。

[click] 从 GET 的登记切到 POST；路径相同、方法不同。
[click] 恢复完整源码，展示生成的路由字典。
[click] 区分 MiniApp 的字典与 FastAPI 的路由对象列表。
-->

---
layout: default
class: lecture-two
---

<div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/15 border border-amber-500/40 text-amber-700 dark:text-amber-300 font-bold text-sm tracking-wide">
阅读练习 9 · 教师演示／课后回看 MiniApp
</div>

<div class="mt-4 text-left">

<div class="text-xs tracking-widest opacity-75 mb-1.5">要执行的命令</div>

```bash
uv run python snippets/lesson00/decorator_demo.py
```

<div grid="~ cols-[1.25fr_0.75fr] gap-5" class="mt-4">
<div v-click="1">
<div class="text-xs tracking-widest opacity-80 mb-1.5">预期看到（静态对照，注意前两行的时机）</div>

```
[注册] GET /posts -> list_posts
[注册] POST /posts -> create_post
--- 模块顶层已完成注册；尚未调用处理函数 ---
{('GET', '/posts'): <function list_posts at 0x...>,
 ('POST', '/posts'): <function create_post at 0x...>}
(200, '帖子列表')
(200, '已创建')
(404, 'not found')
[调用] greet
hi
```

</div>
<div v-click="2" class="self-center">
<div class="p-4 rounded-lg border-2 border-teal-500/40 bg-teal-500/5 text-sm">
<b>要能回答：</b>为什么两行 <code class="text-xs">[注册]</code> 先出现，<b class="key">而处理函数的结果后出现？</b>
</div>
<div class="mt-4 text-sm key">
能解释登记与调用时机即可；本脚本可自行复演，不要求独立编写
</div>
</div>
</div>
</div>

<!--
（阅读练习 9）教师在课件仓库根目录执行，学生对照源码与输出说明时机；自行复演可选。模块顶层执行到装饰器时，route 和 decorator 已被调用，所以先打印注册；此时尚未调用 list_posts / create_post。随后主入口调用 handle 才得到处理结果。

直接运行脚本与第一次导入模块都可能执行顶层定义，但只有直接运行本文件时进入这里的 __main__ 分支。不能说注册发生在“任何函数调用之前”或“程序运行之前”。

[click] 展示完整输出，先观察两行注册，再读处理结果。
[click] 展示解释时机的问题与阅读目标。
-->


---
class: lecture-two
---

# 0.11 async / await：只要求看懂形状

<div grid="~ cols-2 gap-6" class="mt-5 text-sm">
<div class="space-y-4">
<div class="step-row"><b class="key">async def</b>：本例定义协程函数。调用时得到协程对象，函数体要在<b class="key">被等待或调度后</b>才执行。</div>
<div v-click="1" class="step-row"><b class="key">await</b>：等待结果时<b class="caution">可能挂起</b>，让事件循环处理其他任务；不保证每遇到 await 就切换。</div>
<div v-click="1">普通 Python 文件里，await 写在 async 函数内。</div>
</div>
<div v-click="2">
<div class="text-xs tracking-widest opacity-80 mb-2">v2_traceable.py · 中间件的一行</div>

```python
response = await call_next(request)
```

<div class="mt-4 p-3 rounded-lg bg-teal-500/8">够用的解释：把请求<b class="key">交给下游处理</b>，<b class="key">等待响应对象</b>；如果抛出异常，就转入异常传播路径。</div>
<div class="mt-4">第 5 次课再讨论事件循环、工作线程，以及何时用 def / async def。</div>
</div>
</div>

<LessonLink v-click="3">在函数式 <code>trace_middleware</code> 中认出这行即可。真实栈受线程与异步边界影响，不保证出现某个固定框架帧。</LessonLink>

<!--
教学单元：0.11；本页：async 阅读边界。
暂不讨论异步生成器等其他形态，保持本例协程函数与等待表达式的阅读范围。
只读表达式的作用，不提前给出完整中间件和请求关联方案。同步端点交给工作线程的机制留第 5 次课，第一课通过实际停点认识观察边界。

[click] 从协程函数转向 await：可能挂起，不保证切换。
[click] 展示中间件的这一行，读出交给下游、等待响应。
[click] 提醒真实调用栈的线程与异步边界。
-->

---
class: lecture-two
---

# 0.12 import 与启动：先确认站在哪个目录

<div class="text-sm opacity-70 mb-4">本例的模块是 .py 文件；mini 是带 __init__.py 的普通包。</div>

<table class="w-full">
<thead><tr><th>运行方式</th><th>默认放到搜索路径前面的目录</th><th>本例用途</th></tr></thead>
<tbody>
<tr><td><code>python -m mini.cli</code></td><td><b class="key">当前工作目录</b></td><td>在 lesson00 目录运行包中模块</td></tr>
<tr v-click="1"><td><code>python mini/cli.py</code></td><td><b class="caution">脚本所在的 mini 目录</b></td><td>此目录布局下可能找不到顶层 mini</td></tr>
<tr v-click="2"><td><code>uvicorn v1_ai_raw:app</code></td><td>默认应用目录为<b class="key">当前工作目录</b></td><td>导入 v1_ai_raw 模块，取得 app</td></tr>
</tbody>
</table>

<div v-click="3" class="mt-5 p-3 rounded-lg bg-amber-500/10 text-sm">import 按 <code>sys.path</code> 查找，<b class="caution">不是永远只看当前目录</b>。遇到找不到模块，核对工作目录、解释器、依赖和运行方式。</div>

<!--
教学单元：0.12；本页：运行路径。
只覆盖本例的模块与普通包，其他包形态暂不展开。
使用常规 Python 启动设置解释搜索路径，不展开隔离模式和自定义 PYTHONPATH。mini 仅回收讲一的运行经验；这里不推导依赖方向或要求改架构。

[click] 对比直接运行脚本与 -m 的搜索路径。
[click] 接到 uvicorn 的模块导入与 app 对象。
[click] 总结找不到模块时要核对的四项条件。
-->

---
class: lecture-two
---

# 0.12 环境必做：启动服务，只发一次请求

<div class="text-sm mb-3">进入 <code>snippets/ch01/m0-tracer</code>，使用 <b class="key">Python 3.12</b>；本页检查 v1 的服务启动与搜索结果。</div>

<div class="mb-3 p-3 rounded-lg bg-amber-500/10 text-sm"><b class="caution">环境边界</b>　本步骤使用默认 SQLite 虚构教学数据；先确认没有继承其他 DATABASE_URL。不连接真实业务库，不部署公网。</div>

```bash
uv sync --frozen
uv run python seed.py
uv run uvicorn v1_ai_raw:app --host 127.0.0.1 --port 8000
```

<div v-click="1" class="mt-3 text-sm step-row"><b class="key">检查点</b>　打开 <code>http://127.0.0.1:8000/docs</code>，执行 POST /getQuestions，填 keyword=react、page=1，预期返回 <b class="key">6 条数据</b>。</div>

<div v-click="2" class="mt-3">
<div class="text-sm mb-2">/docs 与 curl <b class="caution">二选一</b>发请求；CDN 不可用时用下方 curl。核对结果后 <b class="key">Ctrl+C 停服务</b>。</div>

```bash
curl -i -X POST "http://127.0.0.1:8000/getQuestions?keyword=react&page=1"
```

</div>

<!--
教学单元：0.12；本页：课前环境跟做。
只发一次请求确认工具能运行，不提前演示日志噪音、关联标识或四处取证。课前材料只发 v1 与必要环境文件，不提前分发 v3 参考答案。完整准备见根 README；不使用 reset 操作已有数据库。
环境边界与启动命令首屏同时可见，先核对数据库配置再运行。

[click] 展示请求参数与 6 条结果的检查点。
[click] 展示 curl 备选方式，明确二选一；核对后停止服务。
-->

---
class: lecture-two
---

# 0.12 配置阅读参考：看 os.getenv

<div grid="~ cols-2 gap-6" class="mt-5">
<div>
<div class="text-xs tracking-widest opacity-75 mb-2">第一课配置 · 等价分行节选</div>

```python
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///./demo.db"
)
```

<div v-click="1" class="mt-3 text-sm">先取<b class="key">进程环境变量</b>；<b class="caution">未设置才用默认值</b>。相对数据库路径与<b class="key">启动时工作目录</b>有关。</div>
</div>
<div v-click="2" class="text-sm space-y-4">
<div class="reading-card"><b class="caution">.env 只是文件</b>，os.getenv <b class="caution">不会自己读它</b>。确需使用时，先复制 .env.example 为 .env，核对为本地教学配置。</div>
<div>显式加载后运行：</div>

```bash
uv run --env-file .env uvicorn v1_ai_raw:app
```

<div v-click="3"><b class="caution">.env 不提交</b>；.env.example 只保留安全占位或本地示例。第 4 次课再做配置管理与启动校验。</div>
</div>
</div>

<!--
教学单元：0.12；本页：配置阅读。
默认 SQLite 路径不需要创建 .env；这一页是自选配置的备查。不要把读取环境变量说成自动加载文件。切换配置要重启，seed 和应用必须使用同一个教学库配置。

[click] 解释环境变量优先、未设置才用默认值。
[click] 区分 .env 文件与进程环境，展示显式加载命令。
[click] 补充不提交 .env 的安全边界。
-->

---
class: lecture-two
---

# 0.13 阅读边界：必须会、会读即可、后续展开

<div grid="~ cols-3 gap-5" class="mt-6 text-sm">
<div class="p-4 rounded-lg border border-teal-500/40 bg-teal-500/5">
<h3 class="key">必须会</h3>
<p>启动与停止程序；发请求、看报文；设置断点、切换栈帧。</p>
<p>读参数与默认值，区分 return / raise，预测下一行是否执行。</p>
</div>
<div v-click="1" class="p-4 rounded-lg border border-sky-500/40 bg-sky-500/5">
<h3 class="example">会读即可</h3>
<p>对象属性、方法、with、列表推导式、日志模板。</p>
<p>@ 登记函数；await 等待下游；request.state 暂存当前请求的数据。</p>
</div>
<div v-click="2" class="p-4 rounded-lg border border-gray-400/40 bg-gray-500/5">
<h3>后续展开</h3>
<p>第 3 次：输入／输出契约与 Pydantic。</p>
<p>第 4 次：保契约重构，再批准错误体迁移。</p>
<p>第 5 次：中间件与异步；第 6 / 7 次：SQL / ORM。</p>
</div>
</div>

<div v-click="3" class="mt-5 text-sm step-row">第一课不是从零设计框架：先用给定单文件，<b class="key">观察输入、执行与输出，再用证据解释</b>。</div>

<!--
教学单元：0.13；本页：分级阅读清单。
request.state 只给用途，不提前定义请求关联方案。后续设计知识不作为第一课的先修考核；遇到不认识的框架内部帧，先标记而非逐层钻源码。

[click] 在必须会的操作之外，列出会读即可的语法。
[click] 展示后续课程展开的内容，划清先修边界。
[click] 收束为观察输入、执行与输出，再用证据解释。
-->

---
layout: center
class: lecture-two text-center
---

# 遇到不懂的代码，先保持阅读主线

<div class="mt-2 text-sm opacity-75 max-w-2xl mx-auto">面对暂时不懂的代码，不必停在第一个疑问上；先用下面三步保持阅读主线。</div>

<div class="mt-8 max-w-3xl mx-auto grid grid-cols-3 gap-4 text-left">
<div class="p-4 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-3xl font-bold text-teal-700 dark:text-teal-300 mb-2">1</div>
  <div class="text-sm">先给它一个<b class="key">够用的近似解释</b></div>
</div>
<div v-click="1" class="p-4 rounded-lg border-2 border-sky-500/40 bg-sky-500/5">
  <div class="text-3xl font-bold example mb-2">2</div>
  <div class="text-sm"><b class="example">标记它</b>，记下「这个我不懂」</div>
</div>
<div v-click="2" class="p-4 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-3xl font-bold key mb-2">3</div>
  <div class="text-sm"><b class="key">继续往下走</b>，不停在这里</div>
</div>
</div>

<div v-click="3" class="mt-6 max-w-3xl mx-auto p-4 rounded-lg bg-amber-500/10 border-l-4 border-amber-500 text-sm text-left">
这个习惯在读 AI 生成代码时会一直用到。AI 一次给你一百行，里面<b>永远</b>有你不认识的东西。<b class="text-amber-700 dark:text-amber-300">能不能带着几个未解决的问号继续往前推进，是能不能用好 AI 的分界线之一。</b>
</div>

<!--
但这张表还有一个更重要的用途，这是我今天想留给你们的最后一句话。它本身就是一次示范：面对不懂的代码，正确反应不是恐慌。

正确反应是三步——先给它一个够用的近似解释，标记一下"这个我不懂"，然后继续往下走。为什么这很重要？因为 AI 一次给你一百行代码，里面永远有你不认识的东西，永远。你要是每次都停在第一个不认识的地方，你一辈子读不完一个文件。能不能带着几个没解决的问号继续往前推进——这是能不能用好 AI 的分界线之一。

[click] 在近似解释之后，标记还不懂的地方。
[click] 继续往下走，保持阅读主线。
[click] 连接阅读 AI 生成代码的习惯。
-->

---
layout: center
class: lecture-two text-center
---

# 课前课到此结束

<div class="mt-2 text-sm opacity-70 max-w-2xl mx-auto">用两类自检找出卡点；可回看、可重测。目标是带着能运行的工具和读代码的基本方法进入第一课。</div>

<div class="mt-8 max-w-3xl mx-auto grid grid-cols-2 gap-5 text-left">
<div class="p-5 rounded-lg border-2 border-teal-500/40 bg-teal-500/5">
  <div class="text-xs tracking-widest opacity-75 mb-2">门槛一</div>
  <div class="text-lg font-bold key mb-1.5">环境验收</div>
  <div class="text-sm opacity-80">Git · 依赖 · 程序运行 · 调试器 · 请求结果。<br><span class="text-xs opacity-70">包含 m0-tracer 搜索成功；调试器能切换栈帧并指出当前帧变量，不用固定层数代替理解。</span></div>
</div>
<div v-click="1" class="p-5 rounded-lg border-2 border-sky-500/40 bg-sky-500/5">
  <div class="text-xs tracking-widest opacity-80 mb-2">门槛二</div>
  <div class="text-lg font-bold example mb-1.5">读代码测试</div>
  <div class="text-sm">按课程发布的读代码题自测，<b class="key">≥80%</b>，可重测。<br><span class="text-xs opacity-70">考签名、对象访问、装饰器时机与异常顺序；不考分层设计、DI 或框架内部实现。</span></div>
</div>
</div>

<div v-click="2" class="mt-8 text-base font-bold key">第 1 次课见。</div>

<!--
好，课前课到这儿。这一讲的东西不少，但核心就两件：把"代码跑在哪、报错怎么读、调试器怎么用"打通（讲一），把"第 1 次课会冒出来的 Python 写法"先见一遍（讲二）。

环境自检包含 0.12 的真实搜索结果；调试器重点是停点与当前帧变量，不强求 Web 同步端点具有固定层数。读代码题按课程实际发布版本执行，本课件没有附带新的题库；不得把旧版分层与 DI 题作为当前先修门槛。第一课继续使用这些工具，判断不同位置留下的证据能否相互印证。

[click] 展示读代码测试，与环境验收并列。
[click] 结束课前课，进入第一课。
-->
