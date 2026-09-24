# 第 5 次课教学底稿（第四版）
## SSR 表单闭环 ｜ 交付 M1

> **备课基线**：[第四版大纲](../syllabus-v4.md)第 5 课与[新版第 4 课交接](lesson-04.md)。本稿彻底重写课堂路线、参考实现、验收与后续交接，尚未移交归档。独立工程、模板任务包、并发脚本和课件需随后制作，不从旧工程反推本课要求。

## 〇、这次课要建立什么

**讲给学生的目标句**：你能让同一套业务规则同时服务 HTML 表单和 JSON 接口，并说出这个请求占用了服务器的什么。

核心解释目标是：**表单提交的完整闭环——校验失败怎样带着原输入回到页面，成功后为什么要跳转。** 同步／异步执行方式是支撑机制，由教师引导固定对照，不作为学生现场开发压测工具的任务。

课堂路线：**正常模板 → 教师做通创建与回填 → 学生完成列表／详情及三字段非法输入 → 预测 PRG → 教师并发对照 → M1 验收**。沿用第 4 课已正确的中间件和事务边界，不重新开一堂中间件调度课，不从混合故障工程开始。

### 95 分钟教学 + 5 分钟缓冲

| 分钟 | 教学单元 | 当场产出 |
|---|---|---|
| 5 | 回顾与目标 | 看到相同业务的 JSON 与 HTML 两种入口 |
| 15 | 模板渲染与自动转义正例 | 能修改模板变量，解释继承与文本输出 |
| 18 | 教师构建创建表单 | 校验失败回填，提交完成后 303 |
| 25 | 学生完成列表／详情页 | 模板、三字段同时非法证据与失败回填函数 |
| 20 | 教师引导三种执行方式对照 | 单 worker、并发 1／10 的六组记录 |
| 12 | 执行判据、M1 与收尾 | 一条调用链的选择理由和作业范围 |
| **95** | **合计** | **另留 5 分钟缓冲，无课内小测** |

前置是第 3 课的 QuestionCreate、基本异常处理，以及第 2 课的 form/label/提交事件概念。不要求先会 React、CSS 布局或压力测试。课内未完成的模板在同一个 M1 作业包中补齐；超时先压缩参考处理器逐行讲解，不削减正常正例、学生独立实践和失败回填。

### 教师提供与学生负责

| 提供物 | 标注 | 学生要求 |
|---|---|---|
| Jinja2Templates、base.html 与给定样式 | 要求会用 | 会传 context、继承和插值，不解释模板编译或设计 CSS |
| HTML 路由接线、现有 SQLite 数据层和连接依赖 | 要求会用，保留前课已经建立的解释要求 | 不重写数据库，按签名调用；知道服务显式提交、依赖只清理 |
| Form 文本适配、创建路径和 HTML 错误适配骨架 | 要求解释 | 区分解析、校验、业务与表现；理解保留原值和状态码 |
| 列表／详情模板、失败回填函数 | 学生完成并要求解释 | 自主组织继承与错误位置，按固定字段和文案实现 |
| 三种等待端点、并发脚本、故障开关 | 工具内部黑盒；三种端点的执行差异要求解释 | 先预测、运行既有设施、记录并解释，不开发测量工具 |

## 一、起点：换表现形式，不复制业务规则

**课堂 5 分钟。先展示已有 JSON 创建，再展示教师完成版的“填表 → 发布 → 详情”，不分析故障开场。**

### 1.1 继续沿用的契约

- 数据仍为 sqlite3 单表，标签存 tags_json；没有 ORM、作者关联或用户表。第 6 课才由教师迁往 PostgreSQL 并建立关联表。
- JSON 保留 `GET /questions`、`GET /questions/{qid}`、`POST /questions`。列表外壳 items/total/page，查询 keyword/page/page_size 默认空字符串／1／20；page≥1，page_size 为 1–50。
- 搜索先去关键词首尾空白，标题或正文做字面子串匹配；样本英文字母不区分大小写，`%`／`_` 不作通配符；按 id 降序后分页，total 为分页前总数。
- 记录保留 id/title/body/tags/created_at。详情整数 id 不加正数限制，缺失（包括 0、负数）404，非整数 422。
- QuestionCreate 保持 title 清洗后 5–200 字符、body 清洗后 10–20000 字符；tags 最多 5 个字符串、默认空列表，不额外排序／去重；JSON 拒绝 id、created_at 等额外字段。
- JSON 创建仍为 201 + Location。服务显式 commit 后返回 DTO，已知精确标题重复为 409；依赖仍只提供连接并关闭。
- JSON 错误沿用 code/message/detail/request_id。`/healthz` 正常 200、`{"status":"ok"}`，预期数据库故障 503、`{"status":"degraded"}`，不增加 db 字段。
- 第 4 课 request-id、配对结构化日志和普通未知异常补头继续有效；本课只增加 HTML 表现，不再安装第二份中间件。

### 1.2 本课新增的 HTML 路由

| 方法与路径 | 正常结果 | 主要异常 |
|---|---|---|
| `GET /ui/questions` | 200 列表页，支持相同搜索／分页参数 | 非法参数 422 HTML；空结果仍为 200 |
| `GET /ui/questions/new` | 200 创建表单，三项输入为空 | 非预期错误 500 HTML |
| `GET /ui/questions/{qid}` | 200 详情页，显示五个公开字段 | 不存在整数 404 HTML，非整数 422 HTML |
| `POST /ui/questions` | 提交成功后 303，Location 指向 HTML 详情 | 输入 422 回填，标题冲突 409 回填，未知失败 500 HTML |

HTML 三页指列表、详情、创建表单，不是要求再做一个错误页任务。教师提供安全错误页。JSON 路径不因浏览器的 Accept 请求头变成 HTML；本课按 `/ui` 和 `/ui/…` 的路径边界区分表现，不做完整内容协商。

第 2 课最小页面作为对照保留在教师副本；本课课堂主入口为 `/ui/questions`，旧 `/` 和静态挂载不因新增 SSR 被误删。不把 `.mount("/", …)` 放在所有 API 之前截走请求。此时同源，不引入 CORS。

```text
JSON 正文 → JSON 端点 ─────────┐
                              ├→ 同一 QuestionCreate → 同一创建服务 → SQLite
表单文本 → 表单适配 → HTML 端点 ┘                         显式 commit
       JSON 入口 ← 201 + JSON           HTML 入口 ← 303 → GET 详情 HTML
```

SSR 是服务器先把模板和数据生成 HTML，浏览器再解析显示；不需要在此页面再用 fetch 拼列表。页面实现换了，第 2 课建立的 HTTP、失败阶段和安全显示判断仍然适用。

## 二、必要铺垫：一个能正常显示的模板

**课堂 15 分钟。约 5 分钟模板调用，5 分钟继承与表单元素，5 分钟同一文本的自动转义。**

### 2.1 运行条件与模板入口

教师包须预装 Jinja2 与 python-multipart，锁定与 FastAPI/Starlette 匹配的版本。缺少前者无法使用模板集成；缺少后者使用 Form 时可能在注册路由阶段报错，不把安装排错交给学生。

以下代码按职责分段构成最终参考，需先定义所有函数再装配应用。QuestionCreate、QuestionOut、QuestionListOut、ConnDep、查询／服务函数与第 4 课应用工厂来自教师基线；不在本文复制模型或改写事务服务。

```python
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from typing import Annotated

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
ui = APIRouter(prefix="/ui", include_in_schema=False)


def render_form(request, values, errors, status_code=200):
    return templates.TemplateResponse(
        request=request, name="question_form.html",
        context={"values": values, "errors": errors}, status_code=status_code,
    )


@ui.get("/questions/new", response_class=HTMLResponse)
def new_question_page(request: Request):
    return render_form(request, {"title": "", "body": "", "tags": ""}, {})
```

`templates` 目录相对于教师入口模块定位，不依赖学生从哪个工作目录启动。request、模板名与 context 是不同参数；使用当前集成的关键字调用，不混用旧的位置参数顺序。

### 2.2 base.html 与创建表单（教师提供）

以下注释标明将来模板文件名，不表示本轮已经生成独立工程文件。

```html
<!-- base.html -->
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}问答墙{% endblock %}</title>
  <style>.body { white-space: pre-wrap; }</style>
</head>
<body>
  <nav aria-label="主导航">
    <a href="/ui/questions">问题列表</a>
    <a href="/ui/questions/new">发布问题</a>
  </nav>
  <main>{% block content %}{% endblock %}</main>
</body>
</html>
```

```html
<!-- question_form.html -->
{% extends "base.html" %}
{% block title %}发布问题{% endblock %}
{% block content %}
<h1>发布问题</h1>
{% if errors %}<p role="alert">发布未完成，请检查下方提示。</p>{% endif %}
{% if errors.form %}<p role="alert">{{ errors.form }}</p>{% endif %}
<form method="post" action="/ui/questions" novalidate>
  <label for="title">标题</label>
  <input id="title" name="title" value="{{ values.title }}" aria-describedby="title-error">
  <p id="title-error">{{ errors.get('title', '') }}</p>
  <label for="body">正文</label>
  <textarea id="body" name="body" aria-describedby="body-error">
{{ values.body }}</textarea>
  <p id="body-error">{{ errors.get('body', '') }}</p>
  <label for="tags">标签（用英文逗号分隔）</label>
  <input id="tags" name="tags" value="{{ values.tags }}" aria-describedby="tags-error">
  <p id="tags-error">{{ errors.get('tags', '') }}</p>
  <button type="submit">发布</button>
</form>
{% endblock %}
```

让学生指出：base 提供共同导航，子模板替换 title/content；input 的 value 与 textarea 的内容位置不同；name 是提交字段，id 用于 label 和页面定位。这里是原生表单导航，**没有第 2 课的 preventDefault 或 fetch 监听器**，不得把旧监听器再挂上去。

textarea 开始标签后固定多放一个换行，再紧接插值且不缩进：HTML 解析会忽略这里的第一个换行，因此不会吞掉正文自身的首个换行。不要把插值挪回标签同一行；回填保留文本内容与换行，但浏览器会把 CRLF／CR 规范化为 LF，不承诺请求字节原样重现。

教学页固定 `novalidate`，不设阻止边界输入的 maxlength，便于观察服务器同时拒绝三个字段；实际产品可增加浏览器约束改善体验，但服务端规则仍须保留。样式由教师提供，不以照抄 DOM 或页面美观作为本课唯一达标标准。

### 2.3 正常的安全输出

教师在隔离模板预览的 values.title 中放入无害文本 `<strong>用户标题</strong>`。使用当前 Jinja2Templates 的 HTML 环境，`{{ values.title }}` 会将它转义；浏览器显示文本，响应源码可见实体，不生成 strong 节点。创建任务先用普通合法数据，不为了这个预览写入共享库。

- 本课从正例开始，正式模板不使用 `|safe`、Markup 或拼接用户 HTML。换行可用 CSS `white-space: pre-wrap`，无需关闭转义。
- 这里是 Jinja2Templates 的 HTML 集成；裸 Jinja2 Environment 不必然开启同样配置。
- 自动 HTML 转义不等于任意脚本、样式或 URL 协议上下文安全。本课的用户数据放进文本或带引号的普通表单属性；链接 id 来自整数记录，查询串另做 URL 编码。
- 不展示弹窗脚本或以“没弹窗”证明安全。第 15 课再进入专用 XSS 靶场。

## 三、教师构建：保留原值，校验成功后才调用服务

**课堂 18 分钟。约 5 分钟表单编码与模型，7 分钟回填，6 分钟正常创建与 PRG。先用普通输入做通提交，再逐段回看失败路径。**

### 3.1 三个字段怎样进入同一个模型

原生表单默认发送 `application/x-www-form-urlencoded`，不是 JSON。Form 负责取得文本，QuestionCreate 负责业务输入校验；不再手写一套标题／正文长度判断。

本课固定的表单编码规则：

| 控件 | 原始回填值 | 传给 QuestionCreate 的值 |
|---|---|---|
| title | 解析后的原始文本，保留首尾空白 | 原文本交模型；模型先 strip 再限制长度 |
| body | 解析后的原始文本，保留正文与换行 | 原文本交模型；模型先 strip 再限制长度 |
| tags | 一个逗号分隔的文本串 | 整栏为空为 `[]`；否则按英文逗号 split，不额外 trim／去重 |

例如 `python,FastAPI` 变为两个字符串，`a,a` 保留重复，空栏不变成一个空标签。逗号是**本表单的编码分隔符**；JSON 入口仍可传包含逗号的单个标签，本页不宣称能无损表达所有可能的字符串列表。标签数量仍由同一个模型检查，不在适配器偷偷截成前五个。

下面是教师提供的文本适配器。命名 Form 参数本身可能忽略额外表单键，所以另外检查未知键和同名控件重复提交，不能仅把已挑选的三项交给 extra="forbid" 就声称拒绝了全部原请求字段。

```python
async def read_question_form(
    request: Request,
    title: str = Form(""),
    body: str = Form(""),
    tags: str = Form(""),
):
    raw = await request.form()
    values = {"title": title, "body": body, "tags": tags}
    errors = {}
    if any(name not in values for name in raw):
        errors["form"] = "表单只接受标题、正文和标签字段。"
    elif any(len(raw.getlist(name)) > 1 for name in values):
        errors["form"] = "同一字段不能重复提交。"
    request.state.form_values = values
    return values, errors


FormDep = Annotated[tuple, Depends(read_question_form)]
```

这个异步依赖只等待框架解析／取得表单，不执行 sqlite3 操作；同步创建端点随后由框架在线程池执行。当前 Form 解析可复用同一 Request 已缓存的表单结果，不是再次消费网络正文。文件上传或无法按声明解析的正文不在普通文本回填承诺内：它们由教师 HTML 请求错误处理器返回安全错误页，不把任意原始请求体塞回页面。

### 3.2 创建端点只做输入适配和 HTTP 翻译

```python
@ui.post("/questions", response_class=HTMLResponse)
def submit_question_page(request: Request, form: FormDep, conn: ConnDep):
    values, errors = form
    if errors:
        return render_form(request, values, errors, 422)
    incoming = {
        "title": values["title"], "body": values["body"],
        "tags": values["tags"].split(",") if values["tags"] else [],
    }
    try:
        payload = QuestionCreate.model_validate(incoming)
    except ValidationError as exc:
        return render_validation_failure(request, values, exc)
    question = create_question_service(conn, payload)
    return RedirectResponse(f"/ui/questions/{question.id}", status_code=303)
```

`render_validation_failure` 是下一单元的学生局部任务；教师演示副本提供行为正确的版本，先展示失败时原值与各字段提示，函数实现留到学生练习后对照。

必须能解释：

1. values 留给回填，payload 才传入服务。不能拿清洗后的模型倒填原始输入，也不能在 except 中统一换成空字符串。
2. 这里只捕获紧贴输入模型调用的 ValidationError。服务内部输出模型校验失败仍是 500，不被这个 except 改成客户端 422。
3. DuplicateTitle 向表现层传播；服务已先 rollback。不能在依赖里提交，也不在 HTML 端点另加 commit；JSON 与 HTML 使用同一服务入口。
4. 默认 request 作用域依赖仍负责最后关闭。服务返回成功已确认提交，303 的发送不依赖清理阶段完成写入。
5. 资源依赖可能先于输入校验执行；数据库获取失败与非法输入同时出现时可能先返回 500。422 回填的课堂对照固定在数据库正常的条件下，不承诺多故障优先级。

### 3.3 业务失败与未知失败各放哪里

教师提供并讲解 §七 的 HTML 适配：标题冲突返回 409 的表单，回填三项；详情缺失返回 404 错误页；请求解析／路径参数错误返回 422 错误页；响应启动前未知错误返回 500 错误页。JSON 仍由第 4 课原处理器生成四字段，不复制业务冲突规则。

普通 500 只显示“服务器内部错误”及 request-id，不回传异常文本、SQL 或原始正文。不能把所有 500 说成没有保存，也不自动重试提交。第 4 课两组故障回归继续使用：commit 前失败无本次记录，确认提交后失败记录仍在；同样不能发送 303，但数据结论不同。

### 3.4 PRG：先预测，再观察刷新

固定正常数据和已成功的服务调用：

```text
POST 表单 → 模型校验 → 服务写入并提交 → 303 Location: /ui/questions/新id
          → 浏览器 GET 详情 → 200 HTML → F5 再 GET 详情
```

先问：成功跳转后 F5 会发哪个方法、哪个 URL？若成功后直接返回 200 HTML 呢？

- PRG 完成后的当前页面来自 GET 详情，刷新再次 GET，不重发创建 POST。JSON 客户端的 201 行为没有因此变成 303。
- 教师隔离副本只把成功返回改成 POST 200 HTML，再刷新，浏览器可能提示确认重发；记录实际行为。若重发相同标题，当前唯一约束应拒绝并返回 409，不要求产生重复记录才能证明重放。
- RedirectResponse 默认是 307，必须显式写 303。307／308 保留方法和正文，不是本课需要的“改为读取详情”。
- **PRG 只处理成功结果页刷新重放的问题，不等于幂等，不防双击、并发重发或 CSRF。** 422／409 的失败页面仍是 POST 响应，刷新可能再次提交，不能笼统说任何页面 F5 都是 GET。

教师请求工具关闭自动跟随，先核对 303 与 Location，再发 GET；浏览器在 Network 保留日志查看真实导航与刷新。手工重发 POST 不是 F5 的替代证据，不把进程内重定向测试称为已验收浏览器行为。

## 四、学生任务：两页模板与一次完整回填

**课堂 25 分钟。建议 4 分钟独立写失败回填函数，7 分钟列表模板，6 分钟详情模板，5 分钟三字段非法输入，3 分钟互查和保存结果。AI 对照可在课后补齐，不要求再独立写整个创建端点。**

### 4.1 自己先写这一个函数，再和 AI 比较

教师给 `render_validation_failure(request, values, exc)` 签名和已有 render_form；学生按以下规则完成：返回 422、原 values 不变、按 loc 第一项把提示放到 title/body/tags、只展示固定安全文案，不回显完整错误对象。可以选提示组织方式，但三项错误不能互相覆盖。

完成后才给出核对参考：

```python
FIELD_MESSAGES = {
    "title": "标题去除首尾空白后须为 5–200 个字符。",
    "body": "正文去除首尾空白后须为 10–20000 个字符。",
    "tags": "标签须为字符串列表，最多 5 项。",
}


def render_validation_failure(request, values, exc):
    errors = {}
    for error in exc.errors():
        field = error["loc"][0] if error["loc"] else "form"
        if field in FIELD_MESSAGES:
            errors.setdefault(field, FIELD_MESSAGES[field])
        else:
            errors.setdefault("form", "表单内容不符合接口约束。")
    return render_form(request, values, errors, 422)
```

固定文案是表现层提示，不重新实施长度校验；模型规则变化时同步提示文本。JSON 的安全 loc/type 与 HTML 的字段文案可以不同，但使用同一输入模型作裁决。

AI 协作限定在**这一个失败回填函数**：保存自己的版本，再让 AI 写一版，用三字段失败样本比较错误位置、输入保留、状态码和安全性。记录采纳／未采纳的理由，正确建议可保留，不要求找出错误。模板和回归结果可复用同一作业材料。

### 4.2 读取路由由教师提供，学生完成表现

```python
@ui.get("/questions", response_class=HTMLResponse)
def question_list_page(
    request: Request, conn: ConnDep,
    keyword: str = Query(""), page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    result = QuestionListOut.model_validate(
        search_questions(conn, keyword, page, page_size)
    )
    return templates.TemplateResponse(
        request=request, name="question_list.html",
        context={"result": result, "keyword": keyword, "page_size": page_size},
    )


@ui.get("/questions/{qid}", response_class=HTMLResponse)
def question_detail_page(request: Request, qid: int, conn: ConnDep):
    question = get_question_service(conn, qid)
    return templates.TemplateResponse(
        request=request, name="question_detail.html", context={"q": question},
    )
```

先注册静态 `/questions/new`，再注册动态 `/questions/{qid}`，防止把 new 当作整数编号解析；这是教师接线核对，不以分析路由内部对象作为学生任务。

HTMLResponse 不受 JSON 的 response_model 自动处理，所以这里显式使用既有读模型检查数据，不把数据库行随意交给模板。错误与业务缺失继续通过同一服务／处理器分流，输出模型不替代业务核对。

### 4.3 列表页的固定规格与参考

应显示：查询关键词、当前页及总数、问题标题链接与正文、空结果说明；列表 id 顺序和查询行为与 JSON 对齐。分页链接由教师提供可用写法，学生不开发分页库或另设计参数规范。无匹配是 200 和“没有找到相关问题”，不是异常。

```html
<!-- question_list.html -->
{% extends "base.html" %}
{% block title %}问题列表{% endblock %}
{% block content %}
<h1>问题列表</h1>
<form method="get" action="/ui/questions">
  <label for="keyword">关键词</label>
  <input id="keyword" name="keyword" value="{{ keyword }}">
  <input type="hidden" name="page" value="1">
  <input type="hidden" name="page_size" value="{{ page_size }}">
  <button type="submit">搜索</button>
</form>
<p>共 {{ result.total }} 条，第 {{ result.page }} 页</p>
<ul>
{% for q in result.items %}
  <li><a href="/ui/questions/{{ q.id }}">{{ q.title }}</a><p class="body">{{ q.body }}</p></li>
{% else %}
  <li>没有找到相关问题</li>
{% endfor %}
</ul>
<nav aria-label="分页">
{% if result.page > 1 %}
  <a href="/ui/questions?{{ {'keyword': keyword, 'page': result.page - 1, 'page_size': page_size} | urlencode }}">上一页</a>
{% endif %}
{% if result.page * page_size < result.total %}
  <a href="/ui/questions?{{ {'keyword': keyword, 'page': result.page + 1, 'page_size': page_size} | urlencode }}">下一页</a>
{% endif %}
</nav>
{% endblock %}
```

result 是 QuestionListOut 模型对象，此处 result.items 是声明的列表字段；若改成字典，应使用 `result['items']`，避免 Jinja 属性查找取得字典的 items 方法。查询串用 urlencode，再由 HTML 自动转义处理属性，不把关键词手拼进 href。

### 4.4 详情页的固定规格与参考

显示同一记录的 id、标题、完整正文、标签与带时区创建时间；标签为空给“暂无标签”。模板自主选择继承结构和布局，但不能漏掉正文或重新引入作者字段。

```html
<!-- question_detail.html -->
{% extends "base.html" %}
{% block title %}{{ q.title }}{% endblock %}
{% block content %}
<article>
  <h1>{{ q.title }}</h1>
  <p>问题编号：{{ q.id }}</p>
  <p class="body">{{ q.body }}</p>
  <ul aria-label="标签">
  {% for tag in q.tags %}<li>{{ tag }}</li>
  {% else %}<li>暂无标签</li>{% endfor %}
  </ul>
  <time datetime="{{ q.created_at.isoformat() }}">{{ q.created_at.isoformat() }}</time>
</article>
{% endblock %}
```

继承和链接可使用等价组织方式；不能用固定一条问题冒充详情查询。时间验收比较实际含义，不因 `Z` 和 `+00:00` 的等价表示判错。

### 4.5 必做的一次“三个字段同时非法”

固定数据库可用，表单不被浏览器校验拦截。学生自选值，同时满足：title 清洗后少于 5、body 清洗后少于 10、tags 按逗号切分后超过 5。示例：title=`"  x  "`，body=`"  short  "`，tags=`"a,b,c,d,e,f"`。

核对一份响应即可：422 HTML，三个字段各有错误提示；title/body 的原始空白及 tags 全串仍在对应控件中；没有重定向，独立连接确认无新增。不能只回填第一个错误，也不能为了消除报错静默截断标签。

然后把输入修正为合法值，正常提交得到 303，详情显示清洗后的标题正文及全部标签。再提交相同清洗标题，409 回填，行数不增加。缺失／空白、长度上下界、特殊文本和 JSON 同规则回归由教师脚本帮助课后核对，不追加多份截图。

## 五、教师引导：一个请求占用了什么

**课堂 20 分钟。建议 4 分钟说明调度与固定条件，3 分钟预测，8 分钟运行六组并记录，5 分钟解释结果。压测脚本为黑盒，学生记录即可。**

### 5.1 先给最小执行规则

- 由 FastAPI 调用的普通 `def` 端点／同步依赖在线程池执行；等待会占用线程容量。
- `async def` 在事件循环上运行，可挂起的异步等待让其他任务前进；写了 async 不会把内部阻塞调用变成异步。
- 在异步端点中直接调用普通同步函数，仍在当前执行位置运行，不会因辅助函数写成 def 自动卸载到线程池。

先把这些位置画在已有服务器框里，不要求新交一张完整架构图。一个进程仍可以处理多个并发请求，不能把 worker、线程池和协程都说成“一个请求开一个进程”。

### 5.2 固定的三种对照

下列端点只注册在教师本地隔离实验应用，不挂到 M1 公开工程。它们都没有数据库、没有模板、没有真实外部服务，仅等待 1 秒并返回相同数据。

```python
import asyncio
import time
from fastapi import FastAPI


def make_wait_lab():
    lab = FastAPI(debug=False)

    @lab.get("/lab/blocking")
    async def blocking_wait():
        time.sleep(1)
        return {"ok": True}

    @lab.get("/lab/awaiting")
    async def awaiting_wait():
        await asyncio.sleep(1)
        return {"ok": True}

    @lab.get("/lab/threaded")
    def threaded_wait():
        time.sleep(1)
        return {"ok": True}

    return lab
```

第一条是隔离反例，不是要求学生把合格 M1 改坏。`time.sleep` 模拟阻塞等待，不证明真实数据库、CPU 或网络调用具有相同成本；第三条释放事件循环但仍占用线程。

教师包的实验模块约定为 wait_lab.py，`app = make_wait_lab()`；发包后实际验收的启动形式：

```bash
python -m uvicorn wait_lab:app --host 127.0.0.1 --port 8001 --workers 1
```

它不是本仓库已经存在的命令入口。不启用 reload；与 M1 的端口区分，先核对当前请求确实发给实验服务。线程池可用容量至少为 10，无其他同步任务争抢；实际配置及版本随记录附上，不把常见默认值说成固定线程数量。

### 5.3 预测条件与测量口径

固定每组**总请求数为 10**，并发上限分别为 1 与 10，共三种端点 × 两种并发。单 worker、每次等待 1 秒、客户端允许至少 10 个连接，所有请求完整读完 JSON 才结束计时。并发 10 时客户端在同一批次发起十个任务；并发 1 是顺序处理相同的十个请求，不是仅发一次。

先问：并发 10 时总时长大致是多少，哪个更长？忽略开销、资源足够时的解释模型：

| 端点 | 并发 1、总数 10 | 并发 10、总数 10 | 原因 |
|---|---|---|---|
| blocking | 约 10 秒 | 约 10 秒 | 阻塞事件循环，等待无法在该循环上重叠 |
| awaiting | 约 10 秒 | 约 1 秒 | 可挂起等待重叠 |
| threaded | 约 10 秒 | 约 1 秒 | 多个线程中的等待重叠，须有足够容量 |

上表是条件明确的预测，不是实测数据、硬性通过阈值或“异步永远更快”的承诺。不能把每组请求数从 10 改成 20，却继续照抄这张总时长答案。

教师脚本统一复用异步客户端和连接池，先预热、后测量；客户端超时至少 30 秒。每组报告总数／并发、成功／HTTP失败／超时／其他失败、总时长及单请求延迟；等待并发名额的时间不计入单请求服务延迟，但整批总时长包含它。

| 模式 | 并发 | 请求总数 | 成功／失败／超时 | 总时长 | 解释 |
|---|---|---|---|---|---|
| blocking／awaiting／threaded | 1／10 | 10 | 实测 | 实测 | 按条件填写 |

课堂六组记录可以直接复用教师数据，注明来源。不得删除超时请求后宣称延迟很低；少量样本不作为生产吞吐或容量报告。若结果不符，先核对单 worker、客户端并发、等待代码、线程容量与目标端口，不以偏离固定倍数直接扣分。

## 六、执行判据、M1 验收与后续交接

**课堂 12 分钟。约 4 分钟回到调用链，5 分钟 M1 验收，3 分钟收束与后续任务。**

### 6.1 回到本课为什么用 def

HTML 的读写路径使用同步 sqlite3，所以路由采用 def，直接调用相同的同步服务。不能只给端点加 async 就宣称提速，也不把同步连接传进多个并行任务共享。继续使用第 4 课教师工厂的 `check_same_thread=False`、每请求独立连接、非自动提交写事务；取消线程亲和检查并不保证共享连接并发安全。

| 调用链 | 本课判据 | 边界 |
|---|---|---|
| 同步 sqlite3 或阻塞 SDK | def 端点，框架放入线程池 | 线程容量、连接与数据库仍可能成为限制 |
| 真正的异步 I/O | async def + await | 排查内部隐藏的同步调用或长计算 |
| 异步入口必须调用同步工作 | 教师参考：显式卸载完整同步工作单元 | 资源在有效生命周期内使用，不并发共享连接 |
| 长时间 CPU 工作 | 另行评估算法、进程或任务系统 | 不是加 async 或线程池就必然提高吞吐 |

本课不增加多 worker、CPU 压测或连接池调优的必交任务。表单依赖中的 await 仅服务异步解析；真正阻塞的数据操作仍在同步端点调用链内。

### 常用写法卡 #5

| 写法 | 替我们做什么 | 必须知道的边界 |
|---|---|---|
| Jinja2Templates + extends/block | 把 context 渲染进共享页面骨架 | 不是再次执行前端 fetch；模板不承担数据库业务规则 |
| HTML 模板自动转义 | 将用户内容安全地用于本课文本／普通属性位置 | 不是任意上下文都安全，不用 safe 绕过 |
| Form 文本 → QuestionCreate | 解析传输格式，再复用输入规则 | CSV 标签是表单编码，不改变 JSON 列表规则 |
| 原 values + errors 回填 | 告诉用户哪里错，同时保留输入 | 清洗后的 payload 不等于原输入；不能只保留首个字段 |
| 服务返回后 303 → GET | 成功结果停留在读取页面 | PRG 不是幂等或 CSRF 防护，失败 POST 页仍可能被重发 |
| def／async def | 框架选择线程池或事件循环 | 直接调用普通函数不会自动卸载 |

### 6.2 M1 固定验收

| 范围 | 达标结果 |
|---|---|
| HTML 三页 | 列表／详情／创建表单可导航；new 不误匹配动态路由；列表空结果 200，详情缺失 404 |
| 搜索与输出 | 查询规则、分页参数不改名；标题正文对应真实记录；详情显示标签与时间，用户文本转义 |
| 三字段失败 | title/body/tags 同时非法时 422，三个提示和原值都在，无新增记录 |
| 其他输入边界 | 缺失／空白／长度上下界、5／6 标签；未知表单键和重复标量键拒绝；JSON 原有严格输入规则保留 |
| 标题冲突 | 409 HTML 回填三项，独立连接确认没有第二条；JSON 仍为 409 四字段 |
| 成功 PRG | 303 + HTML Location，独立连接可读到已提交数据；后续 GET 成功，实际浏览器刷新 GET |
| 错误与事务 | HTML 404／422／500 不误发 JSON，API 不因 Accept 变 HTML；未知错误安全，request-id 保留；提交前／确认后故障分别核对数据，不将所有 500 当无写入 |
| JSON 与探针 | 三端点成功与错误契约保留；healthz 200／503 仍仅 status 字段；没有提前加入作者或 ORM |
| 执行方式 | 六组教师并发记录及解释；能沿一个实际路由指到 sqlite3 等阻塞点并说明 def 的理由 |

这是本地虚构数据教学站点，尚无登录、授权和 CSRF 防护，不作为安全完备的公开应用部署。只在原页面中保留安全文本输出，不要求回到第 2 课再开发一套新四态页面。

### 6.3 只交一个作业包

1. M1 工程：HTML 三页、三 JSON 端点和探针；包含自己完成的两个模板及失败回填函数。
2. 表单异常证据：三字段 422、冲突 409；成功 303／GET／刷新与独立连接回读。相同观察可支撑多个验收项，不按截图数量评分。
3. 教师六组并发记录及自己的机制解释；一个实际端点的执行方式判据。允许复用课堂数据，不要求课后重写压测器。
4. 自己与 AI 的失败回填函数 diff、采纳理由及回归结果。契约补充记录 HTML 路径／状态／表单编码即可，不再交多份独立报告。

不按路由行数、目录数量或模板结构完全一致评分；基础验收可课后补齐，不能当选做。没有现成教师设施就先补设施，不删掉三字段任务来制造“已完成”。

### 6.4 第 6 课交接

M1 交付仍是 SQLite 和同一服务层事务边界。第 6 课教师在课前准备 SQLite → PostgreSQL 16 的迁移与核对清单，不让学生课堂临时调驱动。迁移必须明确：

- 保留已有 id/title/body/created_at，迁移后重置序列，核对记录数量、编码与带时区时间。
- tags_json 可能含重复、空字符串或带空白标签；转关联表时明确去重／保留／拒绝规则、冲突报告和回归预期，不能悄悄丢数据。
- 现有 M1 没有作者关联。引入用户表／关系时教师提供虚构用户及既有数据映射，不声称旧记录原本已有 author 字段；实际认证与归属接口迁移按后续课次契约执行。
- 如果后续查询排序、回复数或公开字段变化，应登记差异并更新 JSON／HTML／测试；不能以换库为由悄悄改本课 id 降序或输入契约。
- 第 6 课按 v4 安排 80 分钟教学 + 15 分钟小测 + 5 分钟缓冲；现有第 6 课旧稿尚需另行重写，本轮不把其旧要求提前压给 M1。

## 七、教师参考：HTML 错误适配与应用装配

本节用于随包提供和课后核对，不作为额外课堂单元。沿用第 4 课完整处理器；在应用开始服务前，用下面的分流适配替换相同异常类型的处理器，非 HTML 请求交回原处理器。不要同时保留优先级更高的旧 DuplicateTitle 专用处理器，也不同时装两份 trace 中间件。

### 7.1 安全错误页与四类适配

```python
from html import escape

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


def is_html_request(request):
    path = request.url.path
    return path == "/ui" or path.startswith("/ui/")


def html_error(request, status, message, headers=None):
    rid = getattr(request.state, "request_id", "-")
    response = HTMLResponse(
        "<!doctype html><html lang=\"zh-CN\"><meta charset=\"utf-8\">"
        f"<title>请求未完成</title><h1>{escape(message)}</h1>"
        f"<p>请求编号：{escape(rid)}</p>"
        '<a href="/ui/questions">返回问题列表</a></html>',
        status_code=status, headers=headers,
    )
    response.headers["X-Request-ID"] = rid
    return response


def register_html_handlers(application):
    json_business = application.exception_handlers[AppError]
    json_validation = application.exception_handlers[RequestValidationError]
    json_http = application.exception_handlers[StarletteHTTPException]
    json_unexpected = application.exception_handlers[Exception]

    @application.exception_handler(AppError)
    async def business(request: Request, exc: AppError):
        if not is_html_request(request):
            return await json_business(request, exc)
        mapping = BUSINESS_HTTP.get(type(exc))
        if mapping is None:
            return await unexpected(request, exc)
        status, code, message = mapping
        values = getattr(request.state, "form_values", None)
        if type(exc) is DuplicateTitle and request.method == "POST" and values is not None:
            return render_form(request, values, {"title": message}, 409)
        return html_error(request, status, message)

    @application.exception_handler(RequestValidationError)
    async def validation(request: Request, exc: RequestValidationError):
        if not is_html_request(request):
            return await json_validation(request, exc)
        return html_error(request, 422, "请求参数不合法")

    @application.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        if not is_html_request(request):
            return await json_http(request, exc)
        messages = {404: "路径不存在", 405: "该路径不支持此方法"}
        return html_error(request, exc.status_code,
                          messages.get(exc.status_code, "HTTP 请求失败"), headers=exc.headers)

    @application.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception):
        response = await json_unexpected(request, exc)
        if not is_html_request(request):
            return response
        return html_error(request, 500, "服务器内部错误")
```

html_error 用固定结构与 escape，不依赖可能正出错的模板文件。未知异常先调用原兜底以复用安全错误日志，再为 HTML 请求生成固定页面；不把 JSONResponse 的 Content-Type／Content-Length 拷给 HTML 响应。预期错误经原中间件补 request-id，外层未知错误由 html_error 显式补头。

普通回填仅针对已解析的三项文本；框架解析失败或未知错误不承诺完整回填。request.state 只在本次请求保存输入，不写日志、Cookie 或全局变量。调试固定 `debug=False`；响应已经开始或后台任务失败时，不能再承诺替换整份页面。

### 7.2 只组装一次

```python
def make_ssr_application():
    application = make_application()
    register_html_handlers(application)
    application.include_router(ui)
    return application
```

make_application 是第 4 课 E 阶段工厂。所有模型、函数、ui 路由及异常适配定义好后，教师入口取得 `app = make_ssr_application()` 并保留原静态页挂载，再启动服务。JSON OpenAPI 快照不变；本例明确用 include_in_schema=False 排除 HTML 路由，其契约由 §1.2 与行为验收记录，不假称 OpenAPI 自动描述了模板和 PRG。

## 八、选做：签名 Cookie 的 flash

这是 v4 的选做方向，不加进 95 分钟主线，也不作为 M1 达标条件。教师另提供 SessionMiddleware 与依赖安装配置，密钥来自外部且无可用默认值，生产使用 HTTPS 与安全 Cookie 配置。

最小顺序：**调用创建服务成功返回 → 端点写 flash → 返回 303 → GET 详情读出并移除 flash**。写成功消息晚于服务提交；不在依赖退出阶段写入事务或 flash。若服务确认提交后抛异常，没有成功返回，也不应展示“发布成功”。

Starlette 的这类会话内容在客户端签名 Cookie 中，签名防篡改、不加密；不放正文、凭据等敏感内容。flash 是“一次读出后移除”的消息约定，session 是保存会话状态的机制，两者不是同一概念。响应丢失、并发标签页与 Cookie 更新仍有边界，不能承诺消息绝对只显示一次；不借此声称已经实现登录或 CSRF 防护。

## 九、制作与验证状态

本稿只提供教学底稿与可核对参考，不表示已有第五课独立工程。教师需要把模板文件、同步 SQLite 工厂、R/E 后续起点与异常分流按锁定环境真正装配。

- **本轮机制验证已完成**：从本稿提取 Python 代码与四个模板，组合第 3／4 课模型、SQLite 数据函数、事务服务和错误处理器。SSR 共 557 项断言通过，其中 555 项行为／模板／契约检查，2 项课时检查；另通过 7 项并发检查，累计 564 项。课时逐项为 5/15/18/25/20/12，共 95 分钟，加 5 分钟缓冲；学生单元细分为 4/7/6/5/3，共 25 分钟。
- **覆盖范围**：三页与静态路由顺序、搜索分页与空态、五字段详情、三字段同时非法及原值回填、正文首个／连续换行与 CRLF、长度与标签边界、额外／重复表单键、文本转义及查询串编码、409 回填、提交先于 303、独立连接回读、再次 GET 不写入、JSON 契约和 OpenAPI 不变、request-id／资源释放、探针故障恢复、提交前／确认后故障、服务输出校验仍为 500、模板损坏时的安全兜底。
- **验证环境**：Python 3.12.12、FastAPI 0.141.1、Starlette 1.6.0、Pydantic 2.13.5、httpx 0.28.1；Jinja2 3.1.6、python-multipart 0.0.32、MarkupSafe 3.0.3 仅安装到工作区隔离验证目录，未修改已有工程依赖或锁文件。TestClient 的 httpx 适配仍有弃用提示，未为消除提示升级框架。
- **证据边界**：SQLite 为共享内存隔离库，以独立连接检查提交可见性，不证明文件落盘或重启恢复；模板使用真实 Jinja2Templates 环境与 DictLoader，HTMLParser 检查生成文本和回填，另以 Chromium DOMParser 隔离核对 textarea 首换行规则，不等于已验收站点真实 DOM、点击或 F5。并发使用同进程单事件循环与 ASGITransport，没有网络服务器；客户端也受该循环阻塞，单请求计时不能覆盖获得调度之前的等待，网络连接池与超时行为未验收。
- **跨课核对**：第 5 课继续第 4 课的 SQLite、五字段、四字段 JSON 错误、单 status 探针及服务层提交，HTML 仅增加表现适配。第 6 课迁移清单与小测课时按 v4 交接，其旧稿待另行重写。临时核验脚本不是已交付的学生自检器或教师并发工具。

本轮进程内六组数据如下，每组总数 10、完整成功 10；线程容量已核对至少为 10。数据只验证等待能否重叠，不作为课堂真实 HTTP 实测数据或固定性能阈值：

| 模式 | 并发 1 总时长 | 并发 10 总时长 |
|---|---|---|
| blocking | 10.159 秒 | 10.057 秒 |
| awaiting | 10.022 秒 | 1.012 秒 |
| threaded | 10.066 秒 | 1.014 秒 |

工作区临时复核命令（依赖上述隔离安装及第 3／4 课核验脚本，不是学生工程启动命令）：

```bash
uv run --offline --project snippets/ch01/m0-tracer --no-sync python .build-check/validate_lesson05.py --wait
```

- **试讲前必须补齐**：M1 独立起点／完成版、两个学生模板骨架、失败回填函数任务壳、Form 适配与 HTML 处理器、真实文件库、锁定依赖、压测脚本与六组记录、PRG 和失败回填备用录屏。
- **必须实测的行为**：真实浏览器表单提交／回填、自动转义后的 DOM、303 与 F5、单 worker 真实 HTTP 并发、连接故障与恢复、文件库重启及数据保留；模拟响应或进程内测试不能替代这些证据。
- **教学负荷验证**：记录学生在 25 分钟内完成两个模板、失败回填函数和三字段输入所需提示；记录把失败 POST 页刷新误认为 GET、把 async 理解为自动非阻塞的错因。不能仅凭代码运行就宣称课堂负荷已验证。
