# classroom-interaction 技术说明与接口契约

> 面向：互动后端、学生 Web、测试与部署开发人员。
> 版本：交接基线 v1，API 前缀 `/classroom-api/v1`，SSE `schemaVersion=1`。
> 状态：课件端已实现；本文没有附带已实现的后端、学生页或生产服务。开发安排与验收见[团队交接说明](classroom-interaction-handover.md)，架构背景见[系统设计](classroom-interaction-design.md)。

## 1. 如何使用本文

本文区分三类约定：

- **现有契约**：当前 Slidev 代码已经发送或读取的格式。新后端必须兼容，变更需同步课件端。
- **实现要求**：原设计确定的权限、业务、持久化和运行要求，尚需新项目实现与验证。
- **建议契约**：学生端专用字段和运维细节，现有课件代码没有消费者，由新团队在首轮 OpenAPI 中确认。

现有契约的核对依据是 [types/classroom.ts](../types/classroom.ts)、[HTTP/SSE 客户端](../services/classroom-client.ts)、[课堂 store](../composables/useClassroom.ts) 和 [教师面板](../components/classroom/TeacherPanel.vue)。类型文件不是服务器实现，也不保证服务器安全。

若文档与源码出现差异，先记录并双方确认；不得为了兼容前端而放宽权限。新增可选字段一般可兼容，但新增状态枚举、改字段名、删必填字段、改变事件格式或版本都需要联调后发布。

## 2. 系统边界与技术基线

| 项目 | 负责内容 | 当前状态 |
|---|---|---|
| `web-development-slidev` | 原生 Vue 全局入口、教师面板、二维码、题目/结果/评论投影、教师和展示端 HTTP/SSE | 已实现，默认关闭 |
| `classroom-interaction/backend/` | 认证授权、课堂、活动、提交、审核、角色快照、SSE、持久化、限流 | 待开发 |
| `classroom-interaction/web/` | 独立手机页、加入、答题、提交回执、恢复与结束态 | 待开发 |
| 部署设施 | HTTPS 同源代理、持久化卷、备份、监控 | 待联调 |

课件当前使用 Vue 3、Slidev 52、TypeScript，二维码本地生成。不是 iframe 集成，不需要新团队修改 Slidev 核心、重新建设教师网站或建设 Addon 平台。

新项目首期推荐 Python 3.12、FastAPI、Uvicorn、`sse-starlette`、SQLAlchemy 2 异步接口、aiosqlite、Alembic、Argon2id；学生端 Vue 3 + Vite + TypeScript。依赖版本由新项目锁定。

容量目标是 1～3 个并发课堂，每课约 100 人。采用 SQLite WAL、本地持久化卷、一个后端实例、一个 Uvicorn worker；广播表和轻量限流放内存。暂不引入 Redis、消息队列、微服务。换成 PostgreSQL 也不能直接允许多 worker：跨进程广播是独立问题。

### 2.1 同源路径

| 浏览器路径 | 服务 |
|---|---|
| `/web-2026b/ch00/`、`/web-2026b/ch01/` | 现有课件静态文件 |
| `/classroom/` | 学生 SPA |
| `/classroom-api/v1/...` | 后端 HTTP 与 SSE |

课件按网站 origin 解析互动地址，不拼接章节 base。当前客户端拒绝异域地址、URL 用户信息、查询参数和 fragment；首期不能直接把 API 配成另一个域名。代理保留完整路径，不剥掉 `/classroom-api`。

### 2.2 公开课件的零自动请求约束

1. 打开课件、翻页、有教师 Cookie、存在恢复记录：均不请求互动 API。
2. 点击“互动”：仅延迟加载面板，仍不请求身份或创建 SSE。
3. 点击“教师登录 / 选择课堂”：查询身份、列出本人当前章节课堂，仍无 SSE。
4. 明确创建、选择、恢复课堂，或兑换展示配对码后：GET state，校验通过才连接 SSE。
5. 一个课件应用实例只有一条 SSE；收起面板和普通翻页不增加连接。

不能把 GET 身份/列表/state/events 实现成隐式创建课堂。课件里的“退出互动”只清本地连接，不调用后端结束或注销接口。

## 3. 认证、授权与数据隔离

### 3.1 角色与凭证（实现要求）

| 角色 | 凭证 | 权限 |
|---|---|---|
| 教师 | `teacher_sid` | 管理本人课堂；读取教师视图 |
| 学生 | `student_sid` | 读取加入课堂的学生视图；仅提交/读取自己的回答 |
| 展示端 | `display_sid` | 读取指定课堂展示视图；无写权限 |

所有 Cookie：随机不透明值、`HttpOnly`、`SameSite=Lax`、`Path=/classroom-api/`、生产 `Secure`，不设置 Domain。服务端只存凭证哈希；不把 Cookie、长期令牌或配对码写入 URL/localStorage。清 Cookie 时使用相同 Path。

- 教师账号由运维命令创建/重置，无公开注册；密码采用 Argon2id，哈希验证在线程池执行并限制并发。
- 教师会话默认 12 小时；学生和展示会话最长 8 小时，不超过课堂过期时间。
- `view=teacher|student|display` 明确选择对应 Cookie，缺少该角色凭证即拒绝；不能拿教师 Cookie 自动降级/替代展示 Cookie，也不能让展示请求返回教师字段。
- 教师 A 不能访问教师 B 的资源；学生/展示凭证必须与路径课堂一致；活动和回答必须追溯其所属课堂。
- 元数据、`sourceSlide`、`sessionId`、Slidev 演讲者模式都不是授权证明。
- 已结束课堂允许仍有效的授权读取最终快照；禁止新加入、新提交和重新开放。授权到期后拒绝读取。
- 注销教师登录仅撤销该登录会话及其 SSE，不结束课堂，不撤销独立学生或展示会话。

写接口（含登录、加入、配对）校验浏览器 Origin 与 JSON Content-Type，拒绝缺失/不匹配的 Origin 和跨站表单；GET/SSE 允许合法同源请求不带 Origin，有 Origin 时校验，结合 Fetch Metadata 拒绝跨站。不启用通配 CORS，可信代理范围明确配置。

### 3.2 各角色快照白名单

| 字段或内容 | teacher | display | student |
|---|---|---|---|
| 课堂公开元数据、状态、当前已开题内容 | 允许 | 允许 | 允许 |
| 尚未开启的草稿内容 | 教师专用活动接口允许 | 禁止 | 禁止 |
| `session.joinCode` | active 课堂允许 | 仅 active 且 `displayMode=join` | 不返回 |
| `results` | 当前选择题实时统计 | 关闭且已公开才返回，否则 null | 同 display |
| `currentActivity.correctOptionIds` | 允许，投票为空数组 | 揭晓后才返回，此前省略字段 | 同 display |
| `comments` | 当前活动有限公开墙 | 仅 visible，最多 20 条 | 同 display |
| pending/hidden 评论历史 | 仅教师审核分页接口 | 禁止 | 仅自己的私有回答接口 |
| `participantCount`、`pendingCount` | 建议始终返回整数 | 不返回 | 不返回 |
| 他人身份、教师账号、凭证、配对码 | 不进入公共快照 | 禁止 | 禁止 |

`comments` 不是审核队列；即使 teacher SSE 也不发送完整私有历史。`pendingCount` 表示当前活动待审核条数，无当前文本活动时为 0；`participantCount` 是已加入参与者数，不是在线连接数。

响应必须由角色专用模型白名单构造，不能先序列化 ORM 全对象再靠前端隐藏。当前 TypeScript 公共类型含可选教师字段，不代表允许向所有角色发送。隐藏投影只改变画面，不撤销已经公开给学生的数据。

## 4. HTTP 通用约定（现有契约）

- 基础路径 `/classroom-api/v1`；下文路径均省略此公共前缀。
- JSON 字段 camelCase，返回裸对象，不包 `{data: ...}`，分页固定 `{items: [...], nextCursor: null|string}`。
- `Content-Type: application/json`；不要只返回 `application/problem+json`，当前客户端不按该类型解析错误体。
- 前端 fetch 使用 `credentials: 'same-origin'`、`cache: 'no-store'`、`redirect: 'error'`，10 秒超时。
- 所有非 GET 请求带 JSON Content-Type；无业务字段时发送 `{}`，不是表单。
- 创建课堂/活动携带 `Idempotency-Key`，其它教师命令当前不带该头。
- 时间为 UTC ISO 8601 字符串，推荐统一 `...Z`；展示名称内时间按 Asia/Shanghai 生成。ID 为不透明字符串，资源 UUID 由服务端生成。
- 前端选项 ID 是客户端生成的字符串，不要限定为带连字符 UUID，不要擅自改写选项 ID。
- 数量、revision 为非负整数；JSON 序列化 revision 不得超出 JavaScript 安全整数范围。
- 普通命令成功可以 204，但有返回对象消费者的接口必须返回指定 JSON。200 空 body、JSON null、HTML 成功页不兼容。
- 所有 API 响应禁止缓存；错误不能进入 SPA fallback。

**FastAPI 路由注意：** 当前调用路径无尾斜杠，如 `/sessions`。必须直接匹配，不能依赖 `/sessions/` 的 307/308 自动跳转；登录重定向到 HTML 页面也不兼容。

### 4.1 错误响应

```json
{
  "code": "ACTIVITY_NOT_OPEN",
  "message": "活动已停止收集，未保存本次修改。",
  "requestId": "req-example-001"
}
```

`code` 的具体枚举由后端 OpenAPI 固化；上例为建议名称。`message` 应可安全显示给教师/学生，不包含堆栈、内部路径、密码或正文。FastAPI 默认 `{"detail": ...}` 需转换为上述结构，包括请求校验错误。

| HTTP | 含义与客户端影响 |
|---|---|
| 401 / 403 | 身份失效或无权限；课件操作通常清理本地绑定。未登录 GET `/auth/me` 的 401 只进入登录状态 |
| 404 | 资源不存在/不可访问；state 恢复时终止重试 |
| 409 | 业务状态冲突、重复幂等键但 body 不同、配额冲突；显示错误，不当成登录失效 |
| 410 | 已结束/过期的新写操作；state 在凭证仍有效时应返回 200 最终快照，而不是直接 410 |
| 422 | 字段或选项校验不合法；保留输入 |
| 429 | 限流，带 `Retry-After` 秒数或 HTTP 日期 |
| 503 | 暂时不可用，如数据库锁等待耗尽；可重试，不能伪造成功 |

课件的普通教师命令失败后由用户重试，不自动重放写请求；SSE 的 state 恢复遇网络/5xx 会退避，遇 401/403/404/410 或协议错误终止。不要用 403 表示“已有开放题”这类业务冲突。

## 5. 数据结构（现有契约）

下方为可独立阅读的字段摘要；完整前端声明见 [types/classroom.ts](../types/classroom.ts)。`?` 表示字段可省略，不表示可以发送 null。

```ts
interface CourseMetadata {
  courseId: string
  courseName: string
  deckId: string
  chapterName: string
}
interface Teacher {
  teacherId: string
  displayName: string
}
interface ClassroomSession extends CourseMetadata {
  sessionId: string
  displayName: string
  classLabel?: string
  status: 'active' | 'ended'
  startedAt: string
  expiresAt: string
  joinCode?: string
}
interface ActivityDraft {
  type: 'choice' | 'text'
  title: string
  selectionMode?: 'single' | 'multiple'
  options?: { id: string; label: string }[]
  correctOptionIds?: string[]
  sourceSlide?: number
}
interface ClassroomActivity extends ActivityDraft {
  activityId: string
  sessionId: string
  status: 'draft' | 'open' | 'closed'
  resultsPublished: boolean
  answersRevealed: boolean
}
interface ChoiceStatistics {
  respondentCount: number
  counts: Record<string, number>
}
interface ClassroomComment {
  responseId: string
  activityId: string
  text: string
  visibility: 'pending' | 'visible' | 'hidden'
  pinned: boolean
  createdAt: string
}
interface ClassroomSnapshot {
  schemaVersion: 1
  revision: number
  sessionId: string
  session: ClassroomSession
  displayMode: 'hidden' | 'join' | 'activity' | 'results'
  currentActivity: ClassroomActivity | null
  results: ChoiceStatistics | null
  comments: ClassroomComment[]
  participantCount?: number
  pendingCount?: number
}
```

### 5.1 无活动的教师快照示例

以下所有 ID、时间和加入码仅为样例，不是真实授权。展示视图在 hidden 模式还必须去掉 `joinCode` 和两个计数字段。

```json
{
  "schemaVersion": 1,
  "revision": 1,
  "sessionId": "7f6d8a10-9b21-4c32-8d43-5e6f708192a3",
  "session": {
    "sessionId": "7f6d8a10-9b21-4c32-8d43-5e6f708192a3",
    "courseId": "web-development-2026b",
    "courseName": "现代Web开发技术",
    "deckId": "ch00",
    "chapterName": "课程导论",
    "classLabel": "周四 1 班",
    "displayName": "现代Web开发技术 · 课程导论 · 周四 1 班 · 2026-09-17 08:00",
    "status": "active",
    "startedAt": "2026-09-17T00:00:00Z",
    "expiresAt": "2026-09-17T08:00:00Z",
    "joinCode": "ABCD2345"
  },
  "displayMode": "hidden",
  "currentActivity": null,
  "results": null,
  "comments": [],
  "participantCount": 0,
  "pendingCount": 0
}
```

顶层 `currentActivity`、`results`、`comments` 必须出现，不能用 omit-none 序列化把 null 字段删掉。`sessionId` 在顶层、session 和当前活动中一致。可选的 `correctOptionIds` 在未揭晓公共视图中是省略，不是 null。

### 5.2 选择题与评论示例

教师 POST 活动或 PATCH 草稿发送：

```json
{
  "type": "choice",
  "title": "以下哪些属于 HTTP 方法？",
  "selectionMode": "multiple",
  "options": [
    { "id": "opt-a", "label": "GET" },
    { "id": "opt-b", "label": "POST" },
    { "id": "opt-c", "label": "HTML" }
  ],
  "correctOptionIds": ["opt-a", "opt-b"],
  "sourceSlide": 12
}
```

活动响应需增加 `activityId`、`sessionId`、`status` 和两个公开标志。新草稿的公开标志均为 false。text 请求仅需 `type`、`title` 和可选 `sourceSlide`；草稿从 choice 改成 text 时清理旧选项和答案。

统计样例（多选 2 人回答，各项比例可合计超过 100%）：

```json
{"respondentCount":2,"counts":{"opt-a":2,"opt-b":1,"opt-c":0}}
```

审核返回的评论对象示例：

```json
{
  "responseId": "response-example-001",
  "activityId": "activity-example-001",
  "text": "希望通过一次真实请求理解 HTTP。",
  "visibility": "visible",
  "pinned": true,
  "createdAt": "2026-09-17T00:10:00Z"
}
```

评论对象不包含作者凭证或个人身份。审核接口必须返回更新后的对象，不能用 `{ok:true}` 代替。

## 6. 课件端 HTTP 接口清单（现有契约）

`sid`、`aid`、`rid` 分别指课堂、活动、回答 ID。所有 owner 接口要求 teacher Cookie 且资源属于本人。

### 6.1 身份、课堂与展示

| 请求 | 请求体/查询 | 成功响应与后续动作 |
|---|---|---|
| `POST /auth/login` | `{username,password}` | 200 `Teacher` + Set-Cookie；前端随后查课堂列表 |
| `GET /auth/me` | 无 | 200 `Teacher`，未登录 401；不能返回 `teacher:null` |
| `POST /auth/logout` | `{}` | 204 或 JSON；撤销当前登录会话，前端清理本地 |
| `POST /sessions` | `CourseMetadata` + `classLabel`，必带幂等头 | 首次 201 `ClassroomSession`，重试返回原资源；前端用其 ID 读 state |
| `GET /sessions` | `courseId,deckId,status=active,cursor?` | 200 `{items:ClassroomSession[],nextCursor}`；只列本人匹配章节 |
| `GET /sessions/{sid}/state` | `view=teacher` 或 `display` | 200 完整角色快照，不能 204 |
| `GET /sessions/{sid}/events` | `view=teacher` 或 `display` | SSE，见第 8 节 |
| `POST /sessions/{sid}/end` | `{}` | 204 或 JSON；前端停止 SSE 并补取最终 state |
| `PATCH /sessions/{sid}/display` | `{displayMode}` | 204 或 JSON；前端补取 state |
| `POST /sessions/{sid}/pairings` | `{}` | 201/200 `{code,expiresAt}`；不能 204 |
| `POST /display/exchange` | `{code}`，前端 trim 后转大写 | 200 `{sessionId}` + 展示 Set-Cookie；随后读 display state |
| `POST /sessions/{sid}/display-revoke` | `{}` | 204 或 JSON；撤销该课堂全部展示会话及未兑换配对码 |

创建课堂请求总会带 `classLabel`，即使值是空字符串；空标签应视为未填写。前端不传 `displayName`、时间或 joinCode，由后端生成。名称变更不改变历史元数据快照，课堂唯一性不依赖显示名称。

展示配对码随机 10 位字母数字，有效 5 分钟，一次性原子消费；学生加入码随机 8 位非易混淆字母数字，二者不同用途。撤权主动通知匹配 SSE，最迟一个心跳周期检查到失效。兑换响应已到达但随后 state 失败时，课件保存非敏感绑定供显式恢复；若兑换响应本身丢失，不能保证原码可重试，应由教师重新生成。

### 6.2 活动与审核

| 请求 | 请求体/查询 | 成功响应与后续动作 |
|---|---|---|
| `GET /sessions/{sid}/activities` | `cursor?` | `{items:ClassroomActivity[],nextCursor}`，教师专用含答案；不得仅返回摘要字段 |
| `POST /sessions/{sid}/activities` | `ActivityDraft`，必带幂等头 | 推荐 201 活动对象；现前端也接受 204，随后刷新列表 |
| `PATCH /activities/{aid}` | `ActivityDraft`，无幂等头 | 推荐 200 活动对象；也接受 204，随后刷新列表 |
| `POST /activities/{aid}/open` | `{}` | 204 或 JSON；前端补取 state 与活动列表 |
| `POST /activities/{aid}/close` | `{}` | 204 或 JSON；同上 |
| `PATCH /activities/{aid}/publication` | `{resultsPublished:true}` 或 `{answersRevealed:true}` | 204 或 JSON；前端补取 state 与列表 |
| `GET /activities/{aid}/responses` | `visibility=pending\|visible\|hidden,cursor?` | `{items:ClassroomComment[],nextCursor}` |
| `PATCH /responses/{rid}/moderation` | `{visibility:'visible'\|'hidden',pinned:boolean}` | 200 更新后的 `ClassroomComment`，随后前端补取 state |

重要细节：

- publication 是部分更新；第二次只传 `answersRevealed:true`，不能将省略的 `resultsPublished` 重置为 false。两个标志仅 false → true。
- 公开历史活动结果不代表切换当前活动；当前 UI 没有任意选择历史题投影的接口。
- 草稿保存不自动开启；关闭活动保留 currentActivity，开始下一题才替换它。
- 审核列表显式分页刷新；SSE 只更新数量和有限公开墙，不自动加载完整审核队列。
- pinned=true 只能用于 visible；hidden 必须取消 pinned。对 text 不调用 publication，评论由审核状态决定公开。
- 默认分页 50 条，上限 100 条。当前课件只发送 cursor，不发送 page/pageSize。
- 游标采用稳定排序（建议 createdAt + ID），末页明确 null；客户端追加列表不主动去重。可变审核结果允许刷新后复位，不承诺分页期间的一致性快照。

`GET /activities/{aid}/results` 是原设计中的历史教师统计接口，当前课件没有调用，也没有对应历史查看 UI；可后置，不应作为首个联调阻塞项。

## 7. 业务状态与一致性（实现要求）

### 7.1 状态流转

- 课堂 `active → ended`，不重开；活动 `draft → open → closed`，不重开。复制活动由前端重新 POST 草稿，不需要 clone 接口。
- 一课堂最多一个 open 活动。开启新题时如旧题仍 open，返回 409，不能自动关闭旧题。
- 开题原子更新活动状态、currentActivity、`displayMode=activity`；新活动公开标志为 false。
- 草稿可编辑；开始后题干、类型、选项、正确答案不可改。重复 open/close/end 幂等，但关闭后 open 不允许“复活”。
- 结束课堂原子关闭当前 open 活动、设置 ended 和 hidden、使加入码失效；结束不是立即删掉状态记录。
- 课堂默认最长 8 小时，后台每分钟关闭到期课堂，启动时补处理；各 API 也校验期限。

展示模式校验：hidden/join 不改变收集状态；activity 需要已开启过的当前活动；choice 的 results 模式需要 closed 且 resultsPublished；text 的 results 模式可在 open/closed 展示获准评论，空墙合法。教师前端仍可能发出不满足条件的请求，由后端返回业务冲突。

### 7.2 题目与投稿约束

| 对象 | 约束 |
|---|---|
| 题干 | trim 后 1～500 字符，纯文本 |
| choice | single/multiple，2～8 选项，每标签 trim 后 1～100 字符，ID 不重复 |
| 正确答案 | 可空表示投票；必须是选项 ID 子集，无重复；single 最多 1 个 |
| 学生选择 | single 恰好 1 个；multiple 至少 1 个，ID 有效且不重复 |
| choice 保存 | 每活动每参与者一份，开放期可修改；统计分母为有效回答人数 |
| text 保存 | trim 后 1～500 字符，每人每活动最多 5 条，不支持修改 |
| 审核与墙 | 新评论 pending；visible 才上墙；最多 3 条 pinned，墙最多 20 条 |

后端按 Unicode 字符校验，不按 UTF-8 字节长度；前端 HTML maxlength 不是服务器校验替代品。缺省计数为 0，统计含各有效选项人数，不含未公开答案标记。

### 7.3 幂等与事务

- 创建课堂/活动：幂等作用域包含教师、操作及目标课堂（创建活动时）；相同 key+body 返回原资源，同 key 不同 body 返回 409。记录至少保留 24 小时，写入结果与幂等记录应原子提交。
- 课件创建课堂重试键保存在内存和可用的 sessionStorage；活动重试键只保留内存，不能承诺刷新页面后自动识别未知结果。超时后先查列表再决定新建。
- text 使用 `(activity_id, participant_id, client_submission_id)` 唯一键；相同 ID+正文返回原记录，即使活动已经关闭；不同正文返回 409。
- choice 使用 `(activity_id, participant_id)` 条件唯一索引，PUT 保存最终选择不增票。关题后相同选择重试可返回原已存回答，新增或改票拒绝。
- 先鉴权，再查幂等结果，再判断新写是否允许；幂等不是越权通道。
- 活动 `status=open` 对 session_id 建条件唯一索引；回答/活动/参与者必须属同课堂。
- 开关题、提交、加入上限、文字条数、置顶数和 revision 的检查/更新在短写事务内，必要时用 `BEGIN IMMEDIATE`。
- SQLite：WAL、foreign_keys=ON、busy_timeout=5000，本地磁盘。事务中不等待网络、不广播、不做密码哈希；提交成功后才回复成功并通知广播。

所有影响快照的实际变更在同事务递增课堂 revision；读取、心跳、没有改变结果的幂等重试不需要递增。状态与统计从一致性读事务取值，不能将新 revision 配旧结果。

## 8. SSE 协议与广播（现有契约 + 实现要求）

### 8.1 连接与事件格式

原生 EventSource 自动带同源 Cookie，没有自定义 Authorization 头。响应：`Content-Type: text/event-stream`、`Cache-Control: no-store`、`X-Accel-Buffering: no`。

只消费以下命名事件，普通无 event 名的 `message` 不能替代：

| event | data | 处理 |
|---|---|---|
| `snapshot` | 完整角色 `ClassroomSnapshot` JSON | 覆盖本地快照 |
| `session.ended` | 完整角色快照，`session.status=ended` | 保存终态并关闭连接 |
| `auth.expired` | 建议 `{}` | 清理授权数据与连接，停止重试 |
| 注释心跳 | `: ping`，每 15 秒 | 不触发业务事件，不更新 revision |

合法初帧示例（完整最小 display 快照；不是增量 patch）：

```text
event: snapshot
data: {"schemaVersion":1,"revision":0,"sessionId":"s-example","session":{"sessionId":"s-example","courseId":"web-development-2026b","courseName":"现代Web开发技术","deckId":"ch00","chapterName":"课程导论","displayName":"示例课堂","status":"active","startedAt":"2026-09-17T00:00:00Z","expiresAt":"2026-09-17T08:00:00Z"},"displayMode":"hidden","currentActivity":null,"results":null,"comments":[]}

```

实际流中每个事件以空行结束，data 行内必须是合法 JSON。`session.ended` 不能只发送 `{sessionId}` 或 `{reason}`；额外结束原因可以扩展，但当前课件不读取。首次订阅必须立即尽力发送快照，客户端首帧最多等 15 秒，仅心跳不算建立业务连接。

### 8.2 生命周期与故障恢复

- 连接前鉴权；先注册订阅，再读取一致性初始快照，按 revision 防止订阅/读库竞争漏掉更新。
- 服务端每个心跳周期校验授权期限/撤销，撤销时主动发 `auth.expired` 并关闭。
- 正常结束优先发送完整终态并关闭；已经 ended 的 events 请求返回 204。state 在有效授权范围内仍返回最终快照，让客户端收敛停止重连。
- 不实现历史回放；可忽略 Last-Event-ID，重新发送最新完整快照。公开视图 revision 跳跃正常，不要求连续。
- 客户端 error 时主动 close 旧 EventSource，再退避 GET state，成功后建新源；最大退避 15 秒，state 429 尊重 Retry-After。
- EventSource 无法读取 HTTP 错误详情或 Retry-After。若只对 events 返回 429 而 state 永远 200，课件无法知道服务端等待值；连接配额限流应与恢复查询的可重试错误策略协调，不能把 429 当作未授权。
- 服务重启丢失内存订阅是可接受的；课堂、幂等、回答、revision 必须持久化，重连不能重新创建课堂。

### 8.3 单进程广播约束

按 sessionId + role 管理连接；同课堂角色快照复用序列化，学生快照不含个人答案。不为每个学生单独查公共数据。

- 投稿数量/统计最多每 500ms 合并一次；开题、关题、公开、审核撤下、展示变化和结束立即通知。
- 每连接仅一个待发送最新快照槽位；新快照覆盖旧快照，不能排无限队列。
- 终态与撤权是优先控制消息，不能被普通快照覆盖；慢消费者发送超时后关闭，不拖住其它连接。
- 快照公开内容未变化可不广播对应角色；不要仅因 revision 递增而对所有学生广播未公开投稿。
- SSE 生命周期不得持有数据库连接、事务或写锁。断连后及时清订阅和配额计数。

## 9. 学生端接入（建议契约，需新团队固化）

本节不是已经实现的 TypeScript 学生接口；当前课件的 `ClassroomRole` 只有 teacher/display。可在新项目复用公共快照形状，但不要把课件教师 store 原样用于学生页。

### 9.1 页面与行为

| 页面 | 行为 |
|---|---|
| `/classroom/` | 手动输入加入码 |
| `/classroom/join/{joinCode}` | 加入确认、可选昵称；GET 不创建参与者 |
| `/classroom/session/{sessionId}` | 用 Cookie 恢复，等待/答题/回执/结果/终态 |

确认加入才 POST `/join`。同课堂有效 Cookie 返回原参与者，不重复计数。首期一浏览器同时加入一课堂；换课堂必须明确确认。匿名身份仅浏览器级，不承诺防作弊或一人一票。

### 9.2 建议请求/响应

| 请求 | 建议请求体 | 建议成功响应 |
|---|---|---|
| `POST /join` | `{joinCode,nickname?,replaceCurrent?:boolean}` | `{sessionId,participantId,nickname,expiresAt}` + student Cookie |
| `GET /sessions/{sid}/state?view=student` | 无 | 第 5 节完整公共快照 |
| `GET /sessions/{sid}/events?view=student` | 无 | 第 8 节命名 SSE |
| `PUT /activities/{aid}/answer` | `{optionIds:string[]}` | 下方 ChoiceAnswer |
| `POST /activities/{aid}/responses` | `{text,clientSubmissionId}` | 下方 TextSubmission |
| `GET /activities/{aid}/my-responses` | 无 | `{activityId,answer:ChoiceAnswer\|null,responses:TextSubmission[]}` |

建议 `ChoiceAnswer={responseId,activityId,optionIds,updatedAt}`；`TextSubmission={responseId,activityId,clientSubmissionId,text,visibility,pinned,createdAt}`。未作答返回 answer=null，text 最多 5 条无需分页；choice 的 responses=[]，text 的 answer=null。仅作者可读取这些私有信息。

`replaceCurrent` 是建议新增字段：默认 false，已有另一课堂身份时返回 409；用户确认换课堂后 true，再原子更换浏览器学生授权。错误响应不要泄露不属于该用户的课堂信息。昵称建议缺省为空字符串，trim 后最多 20 字，不收集学号、电话。

### 9.3 提交与恢复要求

- HTTP 成功回执才显示“已保存”；SSE 不代替回执，也不发送个人私有回答。
- 同一道 choice 一次只允许一个保存请求在途，结果未知时先恢复/重试，不并发发送不同选择造成覆盖乱序。
- text 一次编辑对应稳定 clientSubmissionId，超时重试复用；相同 ID 不得换正文。成功后新投稿才换 ID。
- 首次进入、切题、断线恢复补取自己的回答，按 sessionId/activityId/请求代次隔离迟到响应。
- 暂存草稿按课堂和活动隔离；切题不自动提交旧题，不将本地队列跨题重放。失败保留输入及重试 ID。
- `displayMode=hidden/join` 不妨碍已加入学生看到正在收集的题目；答题依据活动状态，不能把投影遮罩当投稿权限。
- 手机返回前台时校验 state 并重连；课堂 ended 或授权无效进入终态/重新加入，不无限重试。
- 纯文本渲染，不支持 HTML/Markdown/图片；只显示已公开统计和答案。学生页不加载 Slidev 资源或第三方统计。

## 10. 最小部署与运维要求

建议工程结构、表设计详见[系统设计第 7 节](classroom-interaction-design.md#7-新建后端的最小工程设计)。至少包含教师、授权会话、课堂、参与者、活动、回答、配对与命令幂等记录；不额外建设课程/班级管理表。

### 10.1 初始限额

| 项目 | 默认基线 |
|---|---|
| active 课堂 | 3，可配置 |
| 每课堂参与者 | 150，按身份不按连接 |
| 全局 SSE | 600；每授权会话最多 2 条 |
| 学生写操作 | 每参与者每 10 秒最多 5 次 |
| 文本 | 每人每活动 5 条，每课堂每活动最多 750 条 |
| pinned / 评论墙 | 每活动 3 条 / 20 条 |
| 请求体 | 最大 16 KB |
| 登录失败 | 账号/来源分别限速，账号每分钟 5 次失败后短暂冷却作为起点 |
| 加入/配对 | 按来源及码限速；加入来源阈值考虑共享 NAT（每分钟 600 次作为起点），配对失败更严格 |

数据库业务限额必须事务内执行；内存限流重启重置可接受。不能每 IP 只准两条 SSE，校园共享 NAT 会覆盖整个班级。

### 10.2 代理与持久化

- 生产全站 HTTPS；API 不重定向、不缓存、不落入学生或章节 fallback。
- SSE 上游 HTTP/1.1，关闭缓冲/缓存/该路径压缩，读取超时至少 75 秒，确保 15 秒心跳穿透。
- `/classroom/` SPA fallback 不拦截 `/classroom-api/`。后端可托管学生构建，不与课件 pnpm build 合并。
- SQLite 放本地持久化卷，单 worker；建议以 2 vCPU/2 GB 开始测试，文件描述符预留至少 4096，不视作容量保证。
- health/live 仅存活，health/ready 做轻量 DB 探测，最终外部路径由部署约定；不泄露内部配置。
- 日志记录 requestId、耗时、状态、连接数、锁等待，不记录密码、Cookie、配对码、完整加入 URL、评论/答案正文。
- 学生页 `Referrer-Policy: no-referrer`；加入 URL 访问日志脱敏或关闭，静态页错误报告也避免上报完整加入路径。
- SQLite 使用在线备份接口，每天备份、保留 7 天并演练恢复；不能仅复制活跃主文件忽略 WAL。
- 已结束课堂及关联数据默认保留 90 天；备份另有最长 7 天残留窗口。迁移先备份，发布安排在课间，不承诺无停机。

本说明不是已应用的生产配置。启动命令、nginx 模板、运行手册、测试和上线门槛统一见[团队交接说明](classroom-interaction-handover.md)。
