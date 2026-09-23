# 第 2 次课教学底稿（完整整改版）
## HTTP 判据与请求—界面闭环

## 〇、备课定位与交接起点

第一课教“在哪里看”，本课教“根据实际请求与响应更新界面”。学生不需要会 React，使用原生 HTML/JS 与给定样式。主线是：**页面为什么没工作 → 查看请求 → 区分失败阶段 → 更新四态 → 安全显示文本。**

起点必须是合格 M0：
- 搜索 `GET /questions?keyword=...&page=1`，200 为 `{"success":true,"data":[...]}`，列表项已有 `title/body`。
- 详情 `GET /questions/{qid}`；`GET /healthz` 保留 200/503 原契约。
- 正常及框架已处理错误路径保留 request-id 与配对日志；`/boom` 的已知边界未在本课修复。
- 页面与 API 同源。第二课不更改后端路径、搜索容器或探针，不再要求保留 `/getQuestions`。

第三课才把集合迁移为 `items/total/page` 并同步前端。这里任何正常请求都读 `payload.data`，不能提前换成 `items`。教学故障夹具与合格 M0 分开，不能削弱 `verify_m0.py` 断言来使错误页面通过。

### 95 分钟教学 + 5 分钟缓冲

| 单元 | 分钟 | 课堂处理 |
|---|---:|---|
| 一、从结果到过程 | 4 | 主讲 |
| 二、分阶段页面反例 | 10 | 教师定位 null；其余故障逐步解锁 |
| 三、方法与状态码 | 12 | 讲主线判据，完整表课后读 |
| 四、参数位置与编码 | 8 | 教师对照 query / JSON / form |
| 五、加载时机与语义结构 | 10 | 教师修 defer 与表单 |
| 六、fetch 的失败边界 | 14 | 教师分阶段验证 |
| 七、搜索页四态闭环 | 22 | 唯一学生现场必做 |
| 八、缓存与状态载体 | 10 | 6 分钟缓存短演示，4 分钟条件导读 |
| 九、作业与收尾 | 5 | 基础 / 拓展分开 |
| 合计 | 95 | 另留 5 分钟缓冲 |

A 档课后基础阅读：完整状态码表、请求编码、错误分类与页面参考实现。缓存完整实验、Lighthouse、HTTP 版本比较是 B 档；Cookie/Storage 先掌握条件，认证与攻防留第十四、十五课。超时压缩缓存和状态载体口头展开，不占用唯一现场任务的核对时间。

## 一、开场：Network 成功不等于页面成功

**课堂 4 分钟。**

打开实际页面，只选一条搜索请求，沿着“提交事件→URL→HTTP→解析→字段→DOM”读。资源请求条数按现场实际记录，不预设一定十几条。

问题：列表没出现，是没有请求、返回 HTTP 错误、数据结构不对，还是页面操作失败？本课要让每种情况都有可解释的界面和证据。

讲：控制台错误通常指出出错位置，但不自动说明上游原因。没有报错也不代表可访问性、安全性和交互正确；同样，AI 也可能一开始就写对，评价依据是检查结果。

## 二、反例分阶段：不要让 null 阻断 XSS

**课堂 10 分钟。** 以下是待制作的隔离教学页面，不是声称仓库已有 `v2-ai-page` tag，也不是 M0 必须存在这些错误。

### 2.1 初始反例只验证加载时机

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>隔离页面反例</title>
  <script src="/static/lab-page.js"></script>
</head>
<body>
  <input id="kw" placeholder="搜索问题">
  <div onclick="doSearch()">搜索</div>
  <div id="list"></div>
</body>
</html>
```

```js
const listEl = document.getElementById('list');

async function doSearch() {
  const query = new URLSearchParams({
    keyword: document.getElementById('kw').value, page: '1',
  });
  const res = await fetch(`/questions?${query}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const payload = await res.json();
  listEl.innerHTML = '';
  for (const q of payload.data) {
    listEl.innerHTML += `<div>${q.title}</div>`;
  }
}
```

前提是同源服务、脚本确实加载、M0 请求成功。`listEl` 在解析到 body 前取得 null；点击后先在 `innerHTML` 赋值处失败。不要称这个版本“点搜索正常且控制台无错误”。

### 2.2 明确的阶段矩阵

| 阶段 | 只改变什么 | 预期现象 |
|---|---|---|
| A | head 同步脚本，保留其他条件 | listEl 为 null，渲染提前中断 |
| B | 仅给脚本加 defer | 普通列表出现，仍使用不安全 HTML 插入 |
| C | B 上用本地无害标题夹具 | 浏览器把标题解释为 HTML；在允许内联事件的隔离环境中可出现提示 |
| D | 改用 textContent，再加完整四态 | 同一标题按文字显示，错误有明确分类 |

XSS 的本地夹具为 `<img src=x onerror="alert('xss')">`，仅无害提示，不读 Cookie、不访问外部目标。不修改共享数据库；教师可在隔离副本 seed 或响应夹具中提供。若 CSP 已阻止事件执行，记录其作用，不为了“必弹窗”撤掉学生项目的正确安全措施。

回车不提交另由没有 form 和真实 button 解释。三个现象按条件分别验证，不把它们声称为同一初始版同时成功复现。

## 三、HTTP 方法与状态码：结论要带条件

**课堂 12 分钟，完整表 A 档课后阅读。**

### 3.1 三种性质

- 安全：客户端不请求业务状态变更；不禁止日志等附带动作。GET 删除内容违反这一语义，预取和爬虫可能触发真实副作用。
- 幂等：多次相同请求的预期服务器效果与一次相同，不要求每次响应相同。DELETE 首次 204、再次 404 仍可幂等。
- 可缓存：是否允许存储并复用，取决于方法、状态、缓存指令、认证等，不是只看方法的一格勾号。

| 方法 | 安全 | 幂等语义 | 缓存与用途 |
|---|:--:|:--:|---|
| GET / HEAD | 是 | 是 | 常用于读取；按响应缓存策略处理 |
| POST | 否 | 不保证 | 创建或操作；满足特定条件可缓存，通用缓存支持有限 |
| PUT | 否 | 是 | 按契约整体替换目标状态 |
| PATCH | 否 | 不保证 | 局部修改；某些具体操作可以幂等 |
| DELETE | 否 | 是 | 删除目标资源 |

本课不实现 PUT/PATCH。缺字段怎样处理由契约决定，不能说“PUT 漏 body 必然清空”；PATCH 的缺失/null 在第八课系统处理。

### 3.2 主线状态码

| 状态 | 选择与观察 |
|---|---|
| 200 | 成功且有响应内容；仍核对业务数据 |
| 201 | 已创建资源；课程创建接口用 Location 指向新资源 |
| 204 | 成功且没有正文；不能无条件调用 res.json() |
| 400 / 422 | 区分一般客户端错误与无法处理的内容；框架具体映射必须实测 |
| 404 | 资源或路径不存在；也可能按策略隐藏资源存在性 |
| 409 | 与当前资源状态冲突，例如本课程标题重复 |
| 429 | 超出速率限制，按 Retry-After 和策略处理 |
| 500 | 服务端未能完成请求；不把内部堆栈回显给用户 |
| 502 / 504 | 网关收到无效上游响应 / 等上游超时；结合网关与应用日志 |
| 503 | 暂时不可用；M0 探针数据库故障用此状态 |
| 303 | 本课只认识重定向；第五课 POST 后引导 GET |

**FastAPI 默认把 JSON 语法错误也列为 422。** 不先讲“必定 400”，第三课再说框架不符合。课程第三、四课保持这一状态，仅第四课明确迁移错误正文；媒体类型错误也不能一概归为 400，API 可以声明 415。

401 表示缺少有效认证凭据，需注意 `WWW-Authenticate`；403 表示服务器拒绝执行，不必然证明“已认证”。完整认证选择留后续。

重试不只看 4xx/5xx：具体原因、请求副作用、结果是否未知、幂等性和退避都重要。搜索 GET 可以提供用户触发的重试，但不要求自动无限重试。错误 200 会误导只读状态码的工具，不意味着所有缓存、代理都必定做出同一种动作。

## 四、数据在哪里：query、表单与 JSON

**课堂 8 分钟；教师演示，学生课后查表。**

| 发法 | 典型代码或头 | 参数去哪里 |
|---|---|---|
| GET 搜索 | `new URLSearchParams({keyword, page:'1'})` | URL 查询串 |
| 原生 POST form | 默认 `application/x-www-form-urlencoded` | 正文中的键值对 |
| 文件 form / FormData | `multipart/form-data; boundary=...` | 正文分段 |
| fetch JSON | `Content-Type: application/json` + JSON.stringify | JSON 正文 |

```js
await fetch('/lab/echo', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ title: '学习 HTTP', body: '这是课程虚构的表单正文。' }),
});
```

`/lab/echo` 是待制作的教师教学端点，不是 M0 已有端点。若使用 FormData，让浏览器设置包含 boundary 的 Content-Type，不手工只填 `multipart/form-data`。文件上传的常用原生表单编码是 multipart，不宣称二进制绝对不可能通过其他编码发送。

中文、`&`、`#` 等必须正确编码；URL 长度限制由浏览器、代理、服务器决定，不是协议统一 2KB。查询串可能进入历史、日志或按 Referrer-Policy 传播，敏感数据不放这里。换成 POST 本身不提供加密。

Content-Type 声明正文格式，服务端还要按接口期望解析。FastAPI 的 JSON 模型与 Form 是不同输入适配路径，第五课才实现 Form，且需要 `python-multipart`。

## 五、加载时机与语义结构

**课堂 10 分钟。** 先修阶段 B，观察普通标题，再按第二单元条件做无害 XSS 对照，最后进入完整页面。

| script 形态 | 执行时机 | 注意 |
|---|---|---|
| 外部经典脚本，无属性 | 遇到时等待并执行，阻塞解析 | 可能在目标 DOM 之前运行 |
| 外部经典脚本 defer | 文档解析完，DOMContentLoaded 前 | 按文档顺序执行 |
| async | 下载就绪后尽早执行 | 可能打断解析，不保证相互顺序 |
| module | 默认延后执行，处理模块依赖图 | async、依赖与顶层 await 等会影响时序；不把复杂模块图简单等同经典 defer |

完整页面骨架：

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>问题搜索</title>
  <script src="/static/app.js" defer></script>
</head>
<body>
  <header><h1>问答社区</h1></header>
  <main>
    <form id="search-form">
      <label for="kw">搜索问题</label>
      <input id="kw" name="keyword" type="search">
      <button type="submit">搜索</button>
    </form>
    <p id="status" role="status" aria-live="polite"></p>
    <ul id="list" aria-busy="false"></ul>
    <p id="asset-version"></p>
  </main>
</body>
</html>
```

form 提供提交语义，button 提供焦点与键盘行为，label 提供名称。JS 监听 submit 并 preventDefault 才把原生导航改成局部更新；不是“加 form 什么代码都不用写就得到 AJAX”。页面没有导航需求就不用硬凑 nav 标签。

## 六、fetch：用阶段解释，而不是一个 catch 都叫网络失败

**课堂 14 分钟。**

先看一个没有渲染副作用的最小预测函数，避免 `render` 错误干扰结论：

```js
async function observe(fetchImpl = fetch) {
  try {
    const res = await fetchImpl('/questions?keyword=react');
    const payload = await res.json();
    console.log(res.status, payload);
    return 'parsed';
  } catch (error) {
    return error.name;
  }
}
```

| 输入场景 | fetch 阶段 | 后续阶段 | 上例是否 catch |
|---|---|---|---|
| 500 + 合法 JSON | fulfilled，res.ok=false | JSON 解析成功 | 仅这段代码通常不会 |
| 500 + HTML | fulfilled，res.ok=false | res.json 解析失败 | 会，常见 SyntaxError |
| 无法获得可用响应 | rejected | 未开始解析 | 会；也可能是取消等，不只 DNS |
| 200 + 错误结构 JSON | fulfilled | JSON 可解析但不满足业务字段 | 上例不校验结构；渲染代码另可能抛错 |

fetch 不因 HTTP 4xx/5xx 自行 reject；它也可能因无效请求、取消、浏览器安全限制等失败。**reject 不证明服务器没执行。** 读取响应正文期间也可能中断。默认 axios 对非成功状态拒绝，但 `validateStatus` 可以改变策略，不能混用两个库的默认行为解释。

生产页面按下面阶段分类：

```text
获得可用响应？否 → request-error
  是 → HTTP 成功？否 → http-error（不按成功列表解析）
    是 → 正文可读？否 → body-error
      是 → JSON 可解析？否 → parse-error
        是 → 契约正确？否 → contract-error
          是 → 渲染成功？否 → render-error
            是 → success / empty
```

这是四态中的 error 子类别，不是要求学生记九种 UI 状态。第一课“观察位置”在这里落实为失败阶段。

## 七、唯一现场必做：实现并验证搜索四态

**课堂 22 分钟。** 给完整骨架，学生补齐关键分支、核对界面与报文；中途先验证普通结果和空结果，再检查错误与按钮恢复。其余边界课后完成。

### 7.1 请求与数据边界（完整参考）

```js
class PageError extends Error {
  constructor(kind, message, status = null, rid = '') {
    super(message);
    this.kind = kind;
    this.status = status;
    this.rid = rid;
  }
}

async function readSearch(keyword, fetchImpl = fetch) {
  const query = new URLSearchParams({ keyword, page: '1' });
  let res;
  try {
    res = await fetchImpl(`/questions?${query}`);
  } catch {
    throw new PageError('request-error', '未获得可用响应，请检查连接或稍后重试');
  }
  const rid = res.headers.get('X-Request-ID') || '';
  if (!res.ok) {
    throw new PageError('http-error', `服务返回 HTTP ${res.status}`, res.status, rid);
  }
  let text;
  try {
    text = await res.text();
  } catch {
    throw new PageError('body-error', '响应正文未能完整读取', res.status, rid);
  }
  let payload;
  try {
    payload = JSON.parse(text);
  } catch {
    throw new PageError('parse-error', '响应不是有效 JSON', res.status, rid);
  }
  if (!payload || payload.success !== true || !Array.isArray(payload.data)
      || !payload.data.every(q => q && typeof q.title === 'string'
        && typeof q.body === 'string')) {
    throw new PageError('contract-error', '响应结构与当前接口契约不一致', res.status, rid);
  }
  return { items: payload.data, rid };
}
```

这里 `items` 只是前端适配器的内部名称，**线上容器仍是 payload.data**。第三课迁移时只集中修改适配器及受影响字段，不能全局混用两个版本。校验仅覆盖此页需要的字段，不冒称完整 JSON Schema 校验。

500 HTML 在正式实现中直接归 HTTP 错误；只有 2xx 的非法 JSON 才走 parse-error。这与上单元“先不检查 res.ok 的预测片段”是两个明确版本。

### 7.2 DOM 与四态（与上段组成 app.js）

```js
const formEl = document.getElementById('search-form');
const kwEl = document.getElementById('kw');
const listEl = document.getElementById('list');
const statusEl = document.getElementById('status');
const btnEl = formEl.querySelector('button');
let busy = false;

function setState(state, message = '') {
  statusEl.dataset.state = state;
  statusEl.textContent = message;
  listEl.setAttribute('aria-busy', String(state === 'loading'));
}

function render(items) {
  const fragment = document.createDocumentFragment();
  for (const q of items) {
    const li = document.createElement('li');
    const title = document.createElement('h3');
    const body = document.createElement('p');
    title.textContent = q.title;
    body.textContent = q.body;
    li.append(title, body);
    fragment.append(li);
  }
  listEl.replaceChildren(fragment);
}

async function load(keyword) {
  if (busy) return;
  busy = true;
  btnEl.disabled = true;
  listEl.replaceChildren();
  setState('loading', '正在加载……');
  try {
    const { items } = await readSearch(keyword);
    try {
      render(items);
    } catch {
      throw new PageError('render-error', '页面渲染失败，请联系维护者');
    }
    setState(items.length ? 'success' : 'empty',
      items.length ? `找到 ${items.length} 条结果` : '没有找到相关问题');
  } catch (error) {
    const message = error instanceof PageError ? error.message : '页面发生未知错误';
    const suffix = error instanceof PageError && error.rid ? `；请求编号 ${error.rid}` : '';
    setState('error', message + suffix);
    console.error('搜索失败类别：', error instanceof PageError ? error.kind : 'unexpected');
  } finally {
    busy = false;
    btnEl.disabled = false;
    listEl.setAttribute('aria-busy', 'false');
  }
}

formEl.addEventListener('submit', event => {
  event.preventDefault();
  void load(kwEl.value);
});
```

条件：上述 DOM 元素存在，脚本通过 defer 执行；页面初始化失败仍需看 Console，不能声称捕获所有浏览器错误。busy 同时处理按钮和 Enter 导致的重复提交；本课暂串行搜索，第十二课再处理“并发搜索旧结果覆盖新结果”。禁用按钮不等于服务端幂等。

`textContent` 只把文本放进文本节点，不是 HTML 清洗器；不能因此认为把用户值放 URL、CSS、事件属性也安全。React 以后可按状态声明 UI，不是自动修复一切不安全 DOM 使用。

### 7.3 教师夹具与验收条件

核心页面只访问 `/questions`。教师在隔离实验应用中提供 `/lab/http/questions`，可配置 slow、500 JSON、500 HTML、200 非法 JSON、200 错结构、empty 等场景；**该端点和静态页当前待制作，不声称 M0 支持 `?fail=500`**。实验副本临时切换请求地址，交付前回到 `/questions`。

在不运行服务的阶段，可向 `readSearch` 传入返回 `Response` 或抛异常的 fetchImpl 验证分支。这是模拟结果，没有真实 Network 请求，不能提交为浏览器报文证据。

| 基础证据 | 观察与判定 |
|---|---|
| 正常 / empty | 200 合格容器，空列表不是失败 |
| loading | 受控延迟中显示加载，结束恢复按钮 |
| HTTP 500 | 即使正文 HTML，也按 HTTP 错误处理 |
| 无可用响应 | Offline 或本地受控失败；恢复网络后可再次搜索 |
| 数据异常 | 200 非法 JSON 和错误结构与网络失败分开 |
| 无害恶意标题 | 安全版本按文字显示；不执行 HTML |

浏览器 Offline 是可控演示条件，不推广为所有 reject 都是断网。不要用访问陌生域名替代“等价网络失败”，它可能引入 CORS、代理与 DNS 等不同变量。

## 八、缓存与状态载体：课堂导读，保留完整自学材料

**课堂 10 分钟；完整缓存实验 B 档选做。**

### 8.1 缓存实验先固定条件

独立页面、无 Service Worker、同一浏览器会话，记录浏览器版本。检查并取消 Disable cache，不假设其默认值。缓存只针对实验 JS，入口 HTML 为 `Cache-Control: no-cache`，API 不混进静态实验。

JS 中真实存在版本标记：

```js
document.getElementById('asset-version').textContent = '资源版本：A';
```

教师提供实验静态服务：响应 ETag 与内容对应；协商阶段设 no-cache，强缓存阶段设 `public, max-age=3600`。可以用以下受控处理器表达实验原理，完整静态部署留第十六课：

```python
import hashlib
from fastapi import Request, Response

ASSET_VERSION = "A"
ASSET_POLICY = "no-cache"

@app.get("/lab/cache/app.js", include_in_schema=False)
def cache_asset(request: Request):
    source = f"document.getElementById('asset-version').textContent='资源版本：{ASSET_VERSION}';"
    etag = '"' + hashlib.sha256(source.encode()).hexdigest() + '"'
    headers = {"Cache-Control": ASSET_POLICY, "ETag": etag}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return Response(source, media_type="text/javascript", headers=headers)
```

这是只处理本实验单个精确 ETag 的示例，不是完整 If-None-Match 弱比较、列表或通配符实现。版本与策略为教师控制常量，不接受用户输入。可用浏览器条件请求或 curl 显式 If-None-Match 作对照。

| 阶段 | 控制动作 | 观察，不强求某个界面颜色 |
|---|---|---|
| 首次获取 | 新实验 URL 或清理仅实验资源，policy=no-cache | 200、实际正文、ETag |
| 协商 | 相同内容与 URL，确认带 If-None-Match | 匹配时服务端返回 304，无新正文；浏览器复用旧正文 |
| 强缓存入场 | 切 max-age 后先确保真实 200 获取新头 | 确认响应包含新策略，不能只改服务器就假设缓存已更新 |
| 观察复用 | 同一 URL 普通链接导航 / 新开同源文档，版本仍 A | 看缓存来源、请求头与服务器访问记录 |
| 版本变更 | 服务器 JS 改 B，旧 URL 仍有新鲜缓存 | 可能继续 A；若浏览器选择验证，记录真实原因 |
| 指纹更新 | 发布实际存在的新内容文件，HTML 引用新名字 | 核对取到 B 与新资源名 |

F5、硬刷新、普通导航、扩展及缓存驱逐行为并不完全相同。不能承诺“F5 必 304”或“连按刷新必强缓存”。同一 URL 重新获取的结果也与已有响应缓存头有关。

| 指令 / 策略 | 含义 |
|---|---|
| no-cache | 允许存储，但复用前需要验证；不是不缓存 |
| no-store | 不存储此响应；不是清除所有过去缓存 |
| max-age | 在新鲜期内可复用；不是永久保存保证 |
| 指纹资源长缓存 | 内容变则 URL 变，入口 HTML 及时验证；旧文件需保留合理发布窗口 |

文件名指纹是常见静态构建策略，不是唯一解法。HTML 可以存储，使用 no-cache 便于发现新的资源引用。个性化 API 的缓存涉及 private、认证与权限，不能一律公开缓存。

### 8.2 状态载体条件表

| 载体 | 自动发送 | JS / 服务器可见性 | 边界 |
|---|---|---|---|
| 查询串 | 请求目标的一部分 | 双方通常可见 | 长度和日志风险因环境而异 |
| Cookie | 满足作用域与策略时由浏览器附带 | HttpOnly 阻止 JS 直接读取；服务器可读收到的 Cookie | Domain、Path、Secure、SameSite、fetch credentials、浏览器隐私策略共同作用 |
| localStorage | 不自动附带 | 同源脚本可读；须主动发送服务端才可见 | 容量因浏览器而异，XSS 可威胁其中凭据 |
| sessionStorage | 不自动附带 | 同源页面脚本可读 | 还受顶层浏览上下文生命周期影响 |
| JS 内存 | 不自动附带 | 运行中的页面代码可见 | 刷新通常重置 |

HTTP 无状态不等于服务端“不能保存任何状态”。服务器可存会话；请求如何关联会话要有协议。Cookie 自动携带是 CSRF 的条件之一，不是“只要目标同域一定带上”。HttpOnly 也不消灭 XSS 发起同源操作的风险。

## 九、作业与后续引用

**课堂 5 分钟。**

A 档基础必交：
1. 在合格 M0 上交付搜索页，保持 GET 路径与 `success/data`；现有后端验收不能因页面改写退化。
2. 四态与错误类别记录：普通、空结果、加载、HTTP 500、无可用响应；200 解析/结构异常可用注明“模拟”的分支检查，浏览器报文证据必须来自真实请求。
3. 安全渲染与键盘提交证据；有 request-id 时显示或记录，前端显示 id 可复用第一课 B 档，不把截图硬性要求扩大成设计完整报障系统。
4. 对 M0 搜索、详情、探针填写“实际方法/状态→判断→依据”。若已正确就保留并说明，不要求改三处、不改弱验收。

B 档：按受控条件完成缓存实验；HTTP 版本与性能阅读；可选择 Lighthouse 报告解读。INP 是交互指标，普通 Lighthouse 导航报告不能保证给出真实 INP；区分实验室 TBT 等代理指标和需要交互 / 现场数据的指标，不要求三个指标都凭一张报告测得。

HTTP/1.1 的连接与并发限制依实现；h2 多路复用降低某些请求成本，不等于请求数量永远不重要。文件合并、域名分片、内联、雪碧图均要结合握手、包体、缓存粒度和测量判断，不能列成“全部失效”。完整构建取舍第十课再用。

下一课承接：修好的页面与 M0 后端；第三课会明确更改响应结构、增加创建和出口模型，必须同步本课 `readSearch` 与 `render`。本课不实现 PATCH、认证、ORM 或 CORS 配置。

## 十、素材和验证状态

已有 M0 工程可提供真实 GET 搜索与探针，但当前仓库没有本底稿的独立静态页、完整故障夹具、缓存服务与录屏。上文是可实施参考，不使用“已验证稳定复现”标签覆盖缺失素材。

制作前须补：阶段 A/B/C/D 的页面副本、同源静态挂载、故障响应夹具、版本标记与 ETag 条件、带环境说明的截图。允许以已标注的模拟数据讲原理，但不据此宣称真实浏览器缓存、XSS 或可访问性验收通过。

本轮直接提取本文 observe、readSearch 和DOM四态代码，在Node v22.14.0用模拟fetch/DOM完成39项断言：覆盖各失败分支、空结果、重复提交拦截、恢复与textContent赋值。缓存处理器在FastAPI 0.141.1 / Starlette 1.6.0中通过精确ETag的200→304和内容变更→200检查；这是临时机制验证，不是已发布的课堂回归包。

最终还要在浏览器核对 defer、Enter/Tab、loading、Offline 恢复、安全文本显示、真实缓存记录。模拟DOM不证明事件载荷在真实浏览器的执行结果；ETag处理器测试不证明浏览器强缓存行为。复位只作用于隔离页面和教学数据，不清空学生整个项目或浏览器其他站点。
