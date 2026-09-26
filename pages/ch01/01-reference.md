---
class: l01
---

<div class="unit">L01-R01 · 课后查阅 · 常用写法卡 #1（上）</div>

# 从声明到响应，框架替你做了什么？

| 常用写法 | 谁替你做了什么 | 必须记住的边界 |
|---|---|---|
| `app = FastAPI()` | 框架建立应用对象 | 创建对象不等于监听端口 |
| `@app.get("/questions")` | 登记 GET 路径与端点的对应关系 | 函数名不是 URL；请求匹配后才调用 |
| `{qid}` 与 `qid: int` | 框架提取路径值，按声明转换 | 转为整数不代表记录存在 |
| 返回 `dict`／`list` | 框架将本例返回值变为 JSON 响应 | 200 不替你保证业务数据正确 |

<div class="callout">用自己的例子补一条说明；可以直接复用概念三问表，不必再交一张卡。</div>

<!--
教学单元：L01-R01；本页：常用写法卡前半，课后参考，不增加课堂时间。
对应归档底稿七。完整卡片分两页以保证可读性，不删边界。
-->

---
class: l01
---

<div class="unit">L01-R01 · 课后查阅 · 常用写法卡 #1（下）</div>

# 运行、报告失败与观察

| 常用写法 | 谁替你做了什么 | 必须记住的边界 |
|---|---|---|
| `python -m uvicorn main:app` | 服务器接收 HTTP，请求交给应用 | 目录、对象名与端口须对应当前工程 |
| `raise HTTPException(...)` | 框架把 HTTP 异常转换成错误响应 | 缺失资源不能用 200 加空对象代替 |
| Network 查看目标请求 | 浏览器展示请求、状态、响应正文 | 不直接展示服务器内部执行 |

<div class="cols mt-6">
<div><h3>界面备用</h3>

```bash
curl -i http://127.0.0.1:8000/questions
```

</div>
<div><h3>证据边界</h3><p>curl 会新发一次请求，<br>不能冒充刚才浏览器那次记录。</p></div>
</div>
<div class="note">不依赖 /docs 的在线资源；终端输出与浏览器面板是不同形式的观察。</div>

<!--
教学单元：L01-R01；本页：常用写法卡后半。
响应要核对内容、状态、媒体类型，不以打开文档页代替接口正常。
-->

---
class: l01
---

<div class="unit">L01-R02 · 课后查阅 · M0 行为规格</div>

# 自检核对行为，不限定你的查找写法

<div class="contract-table">

| GET 路径 | 状态 | JSON 约定 |
|---|---|---|
| `/questions` | 200 | `items`；3／2／1，每项只有 id、title、body |
| `/questions/3`、`/2`、`/1`¹ | 200 | 对应记录，直接返回对象，不套 items |
| `/questions/999`、`/0`、`/-1`¹ | 404 | `{"detail":"问题不存在"}` |
| `/not-a-route` | 404 | `{"detail":"Not Found"}` |
| `/questions/abc` | 422 | 框架校验响应；不固定版本相关文案 |
| `/healthz` | 200 | `{"status":"ok"}` |

</div>
<div class="note">¹ 表中简写仍以 <code>/questions</code> 为前缀。自检前恢复三条原始虚构数据；键顺序、空白与中文转义不计分。</div>
<div class="callout">qid 只声明整数，没有正数约束：0、负整数在本数据中因不存在而返回 404。</div>

<!--
教学单元：L01-R02；本页：完整M0契约。对应归档底稿八。
自检实际发10条请求。对于abc只固定状态，不固定422的版本相关正文；仍要求JSON响应。
不要声称未实现的keyword参数已经支持搜索。
-->

---
class: l01
---

<div class="unit">L01-R03 · 课后查阅 · 环境与阶段切换</div>

# 同一环境，三个 main.py，分开运行

<div class="cols mt-4">
<div><h3>在 first-api 包根准备环境</h3>

```bash
uv sync --frozen
# macOS / Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

<p class="note">Python 3.12；锁定版本随包提供。<br>教师课前安装，学生课堂不首次下载。</p></div>
<div><h3>激活后，进入当前阶段</h3>

```bash
cd exercise
python -m uvicorn main:app \
  --host 127.0.0.1 --port 8000
```

<p>PowerShell 把启动命令写成一行。</p><p>第二终端也激活相同环境，<br>进入 exercise，再运行：</p>

```bash
python ../check_m0.py
```

</div>
</div>
<div class="note">教师示范用 starter；课后对照用 reference。切换前先 Ctrl+C，不开启 reload。完整说明见代码仓库 README 的 first-api 部分。</div>

<!--
教学单元：L01-R03；本页：安装、工作目录与命令。
包根即 snippets/ch01/first-api。命令不是从Slidev根直接运行；激活解决解释器来源。
自检可用 --base-url http://127.0.0.1:8001 指定自己确认过的另一个本地端口。
-->

---
class: l01
---

<div class="unit">L01-R04 · 课后查阅 · IDE 操作卡</div>

# 先选对启动配置，再看断点

<div class="cols mt-5">
<div><h3>VS Code 准备</h3><ol><li>直接打开 <code>first-api</code> 文件夹。</li><li>安装 Python／Python Debugger 扩展。</li><li>选择本包 <code>.venv</code> 的解释器。</li><li>停止终端中占用相同端口的服务。</li></ol></div>
<div><h3>运行与观察</h3><ol><li>选“第 1 课：我的详情练习”。</li><li>在 <code>print</code> 行下断点，启动调试。</li><li>访问 <code>/questions/3</code>。</li><li>看局部变量与类型，截图后继续。</li></ol></div>
</div>
<div class="callout">PyCharm 使用同样条件：模块 <code>uvicorn</code>，参数 <code>main:app</code>，工作目录为 exercise，本包解释器，无 reload。</div>
<div class="note">端点断点停住时，浏览器仍可能等待响应；继续运行后再看完整响应。调试配置检查不等于真实 IDE 操作已验收。</div>

<!--
教学单元：L01-R04；本页：调试说明，完整本人操作仍需实际完成。
launch.json不写死macOS解释器路径。PyCharm说明是等价配置指引，不冒充已经提供PyCharm项目配置。
-->

---
class: l01
---

<div class="unit">L01-R05 · 课后查阅 · 模板边界与 AI</div>

# 哪些要解释，哪些只要会用？

| 材料 | 本课要求 |
|---|---|
| 应用对象、路由、详情函数与 404 | **要求解释**：作用、位置、触发条件 |
| 固定数据、列表外壳、启动与调试配置 | **要求会用**：按规格读、运行、改值 |
| M0 自检器、教师验证器内部 | **黑盒**：运行、读失败项；不考内部实现 |
| 第 2 课 SQLite 模块（另行提供） | **要求会用**：本课不实现、不验收其内部 |

<div class="cols mt-5">
<div><h3>AI 解释核对</h3><p>选一行路由或参数声明 → 请 AI 解释 → 用自己的运行证据判断。</p></div>
<div><h3>想再往下挖 · 选做</h3><p>手写 socket 收一次本地 HTTP，体会服务器省掉了哪些工作。</p></div>
</div>
<div class="note">正确解释可接受；选做不影响 M0。教师工具开发不转嫁给学生。</div>

<!--
教学单元：L01-R05；本页：理解边界。黑盒不进口试。
socket只作为选做方向，本轮没有制作socket课程包，也不要求学生完成它。
-->

---
class: l01
---

<div class="unit">L01-R06 · 课后查阅 · 下一课交接规格</div>

# 第 2 课起点是教师增量，不是 M0 欠账

<div class="cols mt-5">
<div class="panel"><h3>M0 现在交付</h3><p>固定列表、详情、存活探针。</p><pre class="plain-output">GET /questions
{"items":[...]}</pre><p>记录：id / title / body。</p></div>
<div class="panel"><h3>教师下一阶段提供</h3><p>SQLite＋搜索分页＋同源页面骨架。</p><pre class="plain-output">GET /questions?keyword=react
{"items":[...],"total":1,"page":1}</pre><p>记录的原有三个字段不变。</p></div>
</div>
<div class="note">新增参数：keyword 默认空，page 默认 1，page_size 默认 20（1–50）；page ≥ 1。关键词清洗后匹配标题／正文，按 id 降序后分页；total 为分页前匹配总数。</div>
<div class="callout">第 2 课读取 <code>data.items</code>。页面与 API 同源；数据库内部与故障设施由教师准备。本次起点包尚未制作。</div>

<!--
教学单元：L01-R06；本页：版本交接。对应归档底稿九，详细教师模块与样本规格保留在归档快照。
后续模块为question_store，list/get/search接口；不在本轮实现。无匹配是200空items，不是404。
详情与healthz保持M0响应；不提前引入第4课统一错误体与数据库探针。
-->
