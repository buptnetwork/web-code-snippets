# 第 14 次课教学底稿
## 认证与授权：你是谁，以及你能做什么

---

## 〇、给 PPT 制作团队的全局说明

本次课 100 分钟，留 5 分钟缓冲。**本次课是安全两课的第一课，正面修复第 13 次课当众暴露的那个洞。**

**本次课的核心思想，请让它贯穿始终**：

> **认证回答"你是谁"，授权回答"你能做什么"。**
>
> **AI 写的认证代码，几乎总是把第一个问题做完就收工了。**
>
> **而绝大多数真实的安全事故，出在第二个问题上。**

**本次课有三个高光，按重要性排序**：

1. **IDOR 越权改帖（单元 7，16 分钟）**。这是现场必做，也是第 13 次课那个 curl 穿透的真正修复。戏剧性在于：代码里**明明有 `Depends(get_current_user)`**——认证做了，登录检查也有，token 也验了，**然后用户 B 一个 PATCH 就改掉了用户 A 的帖子**。这一刻"认证 ≠ 授权"从一句口号变成了一个事故。
2. **现场解开 JWT（单元 4，10 分钟）**。把 localStorage 里那串 token 复制到终端，`base64 -d`，**`{"sub":"42","role":"user","email":"..."}` 明文跳出来**。全场至少一半人以为 JWT 是加密的。这个认知纠正必须当场做，它是单元 8 决策矩阵的前提。
3. **把授权做成依赖，让 handler 拿不到未授权的对象（单元 7.4，8 分钟）**。这是本次课最重要的结构性设计，也是全课程"让正确的路成为唯一的路"这条线最漂亮的一次兑现——它和 `response_model`、`lazy="raise"` 是**同一个形式**。这张表要做成封面级。

**第四处值得重点制作的**：单元 5.2 **现场跑一次哈希速度对比**。Python 里 `sha256` 每秒几百万次，`bcrypt(cost=12)` 每秒个位数。**差了五六个数量级**，这个数字比任何解释都有说服力。

**一个必须守住的边界**：本次课**不讲 XSS、CSRF、注入**。单元 6 会讲 `HttpOnly` 和 `SameSite` 的**作用**，但**不讲它们防的那个攻击怎么打**——那是第 15 次课的现场必做。看到"那 XSS 怎么偷 cookie"的提问，一句"下节课现场打给你看"带过。

**合规声明必须在开场后第一时间打出**，见单元 1.4。

**若时间不够的压缩顺序**：先压单元 10 的 C 档卡（整体移课后）→ 再压单元 9 的前端接入（只留 401 拦截那段代码和 `credentials` 一句）→ 再压单元 6.5 的"记住我"。**单元 3、4、5、6.1–6.4、7、8 不能压缩。**

---

## 一、开场：回到那张三格拼图

**约 5 分钟。**

### 1.1 把上节课的犯罪现场打回来

**原样重放第 13 次课演示四的三格拼图**：

```
┌─────────────────┬─────────────────────┬──────────────────┐
│ 界面上           │ 终端                 │ 刷新后            │
│ 删除按钮不见了    │ curl -X DELETE ...  │ 那条问题没了       │
│                 │ HTTP/1.1 204        │                  │
└─────────────────┴─────────────────────┴──────────────────┘
```

讲：

> 上节课我们发现：**前端的 `&&` 不是权限控制。**
>
> 当时我说了两件事要留到后面：
>
> | 问题 | 当时说 |
> |---|---|
> | 前端怎么知道当前用户是谁 | **第 14 次课** |
> | 后端应该在哪一层做这个检查 | 第 15 次课 |
>
> **今天还第一笔账，而且会顺手把第二笔也还掉一大半。**

### 1.2 先把那个作弊道具删掉

> 上节课为了演示，我们加了一个临时的调试头：
>
> ```python
> # ⚠️ 仅教学用
> def current_user(x_debug_user: str = Header(None)) -> User:
>     return db.get(User, int(x_debug_user))
> ```
>
> **现在删掉它。**

**然后立刻做一件事（醒目页）**：

```python
# tests/test_conventions.py
def test_no_debug_auth_backdoor():
    src = Path("app").rglob("*.py")
    for f in src:
        text = f.read_text()
        assert "X-Debug-User" not in text, f"{f} 里还有调试后门"
        assert "x_debug_user" not in text, f"{f} 里还有调试后门"
```

> **这一步不能省，而且它本身就是本次课的第一个教学点。**
>
> 那个调试头是一个"只在开发期用的便利"。它非常好用，而且**没有任何东西阻止它上生产**。
>
> **回收第 12 次课那条判据：任何"只在开发期有效"的便利，都是在推迟问题。**
>
> **今天给它补上后半句：任何"只在开发期有效"的便利，都必须有一道护栏保证它留在开发期。**
>
> 靠"我记得删"是不行的——**你已经记了整整一周，如果我今天不提，它就上线了。**

### 1.3 本次课要回答的问题

- 服务器怎么知道请求是谁发的？
- 密码该怎么存？为什么不能用 SHA256？
- token 放哪？localStorage 还是 Cookie？
- Cookie 那五个属性分别防什么？
- 为什么登出之后 token 还能用？
- **为什么 `Depends(get_current_user)` 不等于安全？**
- 401、403、404 该怎么选？
- Session 还是 JWT？

### 1.4 合规声明（**必须打出并口头宣读**）

**醒目页，红底**：

> **本次课包含攻击演示（越权访问、token 解析）。**
>
> | 条 | 内容 |
> |---|---|
> | 1 | 所有演示**仅限本课程提供的本地环境和你自己的项目** |
> | 2 | **严禁**对任何真实系统、他人系统、公司生产环境实施本课所学技术 |
> | 3 | 未经书面授权的访问测试，在我国《刑法》第 285、286 条下可能构成犯罪 |
> | 4 | 学习攻击的目的是**建立防御**。下节课的合规确认书今天就要签 |
>
> **判据：你能打，不代表你可以打。区别在于授权。**
>
> **这正是今天这节课的主题——而它不只适用于代码。**

---

## 二、解剖台：AI 写的登录系统

**约 12 分钟。五个演示都要做。**

### 情境设定

> 你对 AI 说："给这个项目加上用户注册和登录，登录后才能发帖，只有作者能改自己的帖子。"
>
> 它给了你一套完整的代码，README 里写着"**已实现 JWT 认证和权限控制**"。
>
> **它能跑。注册能注册，登录能登录，未登录访问会跳转登录页，非作者看不到编辑按钮。**
>
> **产品验收会通过。测试会通过。**

### 代码（tag: `v14-broken`）

```python
# app/routers/auth.py —— AI 原样产出
import hashlib, jwt

SECRET = "my-secret-key"                                    # ① 硬编码密钥

@router.post("/register")
def register(form: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=form.email).first():
        raise HTTPException(400, "该邮箱已注册")             # ② 账号枚举
    user = User(
        email=form.email,
        password_hash=hashlib.sha256(form.password.encode()).hexdigest(),   # ③ 通用哈希
    )
    db.add(user); db.commit()
    return {"id": user.id}


@router.post("/login")
def login(form: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=form.email).first()
    if not user:
        raise HTTPException(404, "用户不存在")               # ② 账号枚举
    if user.password_hash != hashlib.sha256(form.password.encode()).hexdigest():
        raise HTTPException(401, "密码错误")                 # ② 账号枚举
    token = jwt.encode({"sub": user.id, "email": user.email,
                        "role": user.role}, SECRET, algorithm="HS256")   # ④ 无过期时间
    return {"token": token}
```

```python
# app/deps.py
def get_current_user(authorization: str = Header(None), db=Depends(get_db)) -> User:
    token = authorization.split(" ")[1]
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    return db.get(User, payload["sub"])
```

```python
# app/routers/questions.py
@router.patch("/questions/{qid}", response_model=QuestionOut)
def update_question(qid: int, payload: QuestionUpdate,
                    user: User = Depends(get_current_user),     # ⑤ 认证了
                    db: Session = Depends(get_db)):
    q = db.get(Question, qid)                                   # ⑤ 但没授权
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(q, k, v)
    db.commit()
    return q
```

```tsx
// web/src/auth.ts
export async function login(email: string, password: string) {
  const res = await fetch("/api/login", { method: "POST", body: ... });
  const { token } = await res.json();
  localStorage.setItem("token", token);              // ⑥ localStorage
}

export function logout() {
  localStorage.removeItem("token");                  // ⑦ 服务端什么都没做
  setUser(null);
}
```

先让学生看 90 秒，问：**你能找出几个问题？**

**典型反应：多数人能指出 ① 硬编码密钥。少数人知道 ③ 不该用 SHA256。几乎没有人指出 ⑤——因为那行 `Depends(get_current_user)` 看起来太像"已经处理了"。**

### 演示一：token 里写着什么，所有人都能看

打开 DevTools → Application → Local Storage：

```
token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjQyLCJlbWFpbCI6ImFsaWNlQGV4YW1wbGUuY29tIiwicm9sZSI6InVzZXIifQ.xR7...
```

复制中间那一段，粘进终端：

```bash
echo 'eyJzdWIiOjQyLCJlbWFpbCI6ImFsaWNlQGV4YW1wbGUuY29tIiwicm9sZSI6InVzZXIifQ' | base64 -d
```

```json
{"sub":42,"email":"alice@example.com","role":"user"}
```

**停 10 秒。**

> **邮箱、用户 id、角色，全部明文。**
>
> **单元 4 会完整展开。现在只记一件事：JWT 不是加密的。**

### 演示二：登出之后，token 还能用（**震撼点**）

**四步，每步都停**：

1. 登录，从 localStorage 里复制 token 存到变量
2. 点"退出登录"，页面跳回登录页，**看起来已经登出了**
3. 终端：

```bash
curl -H "Authorization: Bearer $TOKEN" localhost:8000/me
```

4. 结果：

```json
{"id":42,"email":"alice@example.com","role":"user"}
```

**停 15 秒。**

> **登出了，token 还能用。**
>
> 因为 `logout()` 只做了一件事：`localStorage.removeItem`。
>
> **服务端什么都不知道。** 它从头到尾没有存过任何东西——这正是"无状态"的意思。
>
> 所以：
>
> | 场景 | 后果 |
> |---|---|
> | 用户在网吧登录，退出后走了 | **如果 token 被复制过，它还能用** |
> | 发现账号被盗，改了密码 | **旧 token 到期前一直有效** |
> | 管理员把某人降权 | **要等他的 token 过期** |
>
> 而 AI 写的这个 token **根本没有过期时间**（问题 ④）——**它永远有效。**
>
> **单元 8 会把这件事做成一张决策矩阵。**

### 演示三：不用密码也能枚举出谁注册了

```bash
curl -X POST localhost:8000/login -d '{"email":"alice@example.com","password":"x"}'
# → 401 {"detail":"密码错误"}          ← 这个邮箱存在

curl -X POST localhost:8000/login -d '{"email":"nobody@example.com","password":"x"}'
# → 404 {"detail":"用户不存在"}        ← 这个邮箱不存在
```

> **两个不同的响应，等于一个免费的"查这个邮箱有没有在这注册"的接口。**
>
> 有什么用？
>
> | 攻击者拿它干什么 |
> |---|
> | 确认目标是否是你的用户，再做针对性钓鱼 |
> | 拿一份泄漏的邮箱库，筛出在你这注册过的 |
> | **对交友、医疗、借贷类站点，"是不是用户"本身就是隐私** |
>
> **回收第 4 次课：错误信息不应该泄漏内部细节。**
>
> 当时我们说的是"不要泄漏堆栈和 SQL"。**今天扩展一条：不要泄漏"这个账号存在"。**

**然后加一层（很多人想不到的）**：

```bash
time curl -X POST localhost:8000/login -d '{"email":"alice@example.com","password":"x"}'
# real 0m0.31s     ← 存在：做了一次哈希

time curl -X POST localhost:8000/login -d '{"email":"nobody@example.com","password":"x"}'
# real 0m0.02s     ← 不存在：直接返回，没做哈希
```

> **就算你把两个响应改成一模一样，时间差还在。**
>
> 用户存在 → 要算一次哈希 → 慢。用户不存在 → 直接返回 → 快。
>
> **这叫时序侧信道。** 单元 5.3 会讲怎么堵。

### 演示四：预演 IDOR（**完整版在单元 7**）

用 Bob 的账号登录，改 Alice 的帖子：

```bash
curl -X PATCH localhost:8000/questions/42 \
     -H "Authorization: Bearer $BOB_TOKEN" \
     -d '{"title":"Bob 到此一游"}'
```

```
HTTP/1.1 200 OK
{"id":42,"title":"Bob 到此一游","author_id":7}
```

**指着那行 `Depends(get_current_user)`**：

> **这行代码在。它工作得很好。它确实验证了 Bob 是 Bob。**
>
> **然后 Bob 改掉了 Alice 的帖子。**
>
> **单元 7 完整展开。**

### 演示五：一行 XSS 就能拿走 token（**埋点第 15 次课**）

在 DevTools Console 里：

```js
localStorage.getItem("token")
// → "eyJhbGci..."
```

> **任何能在你的页面上执行 JS 的人，都能读到它。**
>
> 而"让别人的 JS 在你的页面上执行"，有一个专门的名字：**XSS**。
>
> 今天不讲怎么打 XSS——**下节课现场打给你看。**
>
> 今天只需要知道：**localStorage 对 JS 是完全开放的，没有任何保护。**
>
> **而 Cookie 有一个属性可以让 JS 读不到它。单元 6 讲。**

### 五个演示的归类（**封面级素材**）

| # | 问题 | 属于 | 谁能利用 |
|---|---|---|---|
| ① | token 内容明文可读 | 认知错误 | 任何拿到 token 的人 |
| ② | **登出无效 / token 不过期** | **会话管理** | 任何复制过 token 的人 |
| ③ | 账号枚举 + 时序泄漏 | 信息泄漏 | 任何人，不需要账号 |
| ④ | **越权改他人数据** | **授权缺失** | **任何一个合法用户** |
| ⑤ | token 可被 JS 读走 | 存储位置 | 任何能注入 JS 的人 |

**核心句**：

> **注意第 ④ 行：利用它不需要任何攻击技术，只需要一个正常注册的账号。**
>
> **这就是为什么 IDOR 常年排在 OWASP Top 10 第一位——它的门槛是零。**

### 欠账清单

| 问题 | 本次课处理 | 何时还 |
|---|---|---|
| 认证与授权的区别 | **单元 3** | — |
| 401 / 403 / 404 | **单元 3.3** | — |
| JWT 到底是什么 | **单元 4** | — |
| 密码存储、账号枚举、时序 | **单元 5** | — |
| Cookie 五属性、会话固定、登出 | **单元 6** | — |
| **IDOR 与对象级授权** | **单元 7** | — |
| Session vs JWT | **单元 8** | — |
| 前端 401 拦截、CORS credentials | **单元 9** | — |
| XSS 怎么打 | 埋点 | **第 15 次课** |
| CSRF 与 SameSite 的因果链 | 单元 6.2 埋点 | **第 15 次课** |
| 密钥怎么管、生产配置 | 单元 5.1 记账 | **第 16 次课** |
| 限流、验证码、MFA | 单元 10 结论卡 | 课后自读 |

---

## 三、认证 ≠ 授权

**约 8 分钟。本次课的方法论核心。**

### 3.1 两个不同的问题

**封面级素材**：

| | **认证（Authentication）** | **授权（Authorization）** |
|---|---|---|
| 回答的问题 | **你是谁？** | **你能做什么？** |
| 什么时候做 | 每个请求一次 | **每个操作、每个对象各一次** |
| 出错的后果 | 冒名顶替 | **越权** |
| 典型实现 | 验 token / 查 session | 查所有权、查角色、查状态 |
| 能不能做成"全局中间件" | **能** | **不能** |

**最后一行是关键**：

> **认证可以一次性解决——写一个依赖，所有路由都挂上，完事。**
>
> **授权不行。** 因为"能不能改这篇帖子"这个问题，**答案取决于具体是哪一篇帖子**。
>
> 你没法写一个中间件说"检查用户有没有权限"——**没有对象，就没有权限可言。**
>
> **这就是为什么 AI 总是只做一半：认证那一半是可以模板化的，授权那一半必须一个一个想。**

### 3.2 授权的三个层次

**醒目页**：

| 层次 | 问题 | 例子 | 漏掉的后果 |
|---|---|---|---|
| **① 功能级** | 这类操作你能做吗 | 只有管理员能封禁用户 | 普通用户调管理接口 |
| **② 对象级** | **这一个对象你能动吗** | **只有作者能改自己的帖** | **IDOR** |
| **③ 字段级** | 这个字段你能改吗 | 用户不能自己改 `role` | **提权** |

> 三层的难度递增，**AI 的覆盖率递减**：
>
> | 层次 | AI 通常 |
> |---|---|
> | ① 功能级 | **经常做**（`require_admin` 这种很模板化） |
> | ② 对象级 | **经常漏**（要理解业务才知道"谁拥有它"） |
> | ③ 字段级 | **几乎总是漏** |

**第 ③ 层现场看一眼**：

```python
@router.patch("/users/{uid}")
def update_user(uid: int, payload: dict, user=Depends(get_current_user)):
    u = db.get(User, uid)
    for k, v in payload.items():       # ← 前端传什么就改什么
        setattr(u, k, v)
```

```bash
curl -X PATCH localhost:8000/users/42 -d '{"role":"admin"}'
```

> **自己给自己升管理员。**
>
> **回收第 3 次课：`response_model` 管的是"输出哪些字段"，请求模型管的是"接受哪些字段"。**
>
> 当时我们说过一句话：**"不要用 `dict` 接收请求体。"** 今天你看到了它的完整代价。

### 3.3 401 / 403 / 404 怎么选（**回收第 2 次课埋点**）

**封面级素材**：

| 状态码 | 含义 | 什么时候用 |
|---|---|---|
| **401 Unauthorized** | **我不知道你是谁** | 没带凭证 / 凭证无效或过期 |
| **403 Forbidden** | **我知道你是谁，但你不能做这个** | 已认证，权限不够 |
| **404 Not Found** | 没有这个东西 | 资源不存在，**或者不该让你知道它存在** |

> 第 2 次课我们说过"401 的名字起错了，它其实是未认证"。今天补完判据。

**关键的一条：什么时候该用 404 代替 403**

```python
q = db.get(Question, qid)
if q is None:
    raise NotFound()
if q.author_id != user.id:
    raise NotFound()          # ← 不是 403
```

> **为什么？因为 403 泄漏了"这个资源存在"。**
>
> ```bash
> PATCH /questions/1    → 404     这个帖子不存在
> PATCH /questions/42   → 403     这个帖子存在，只是不归我
> ```
>
> 攻击者用这个差异可以**枚举出所有存在的 id**——**这是演示三那个账号枚举的同一个毛病，换了个地方。**

**但要给出判据，不要一刀切（醒目页）**：

| 场景 | 用 |
|---|---|
| 资源**存在性本身是敏感的**（私有文档、他人订单、私信） | **404** |
| 资源存在性是公开的，只是操作受限（公开帖子，但你不是作者） | **403**，信息更有用 |
| 完全不确定 | **404 更保守** |

> **判据：选 403 还是 404，取决于"这个资源存在"这件事本身算不算信息泄漏。**
>
> **安全上的默认选择是更少泄漏的那个。**

### 3.4 本单元的一句话

**封面级素材**：

> **认证是一道门。授权是每一个房间的锁。**
>
> **装了门不等于装了锁。**
>
> **而 AI 很擅长装门。**

### 材料

- **封面级素材**：3.1 的认证/授权五行对照表（**最后一行"能不能做成中间件"高亮**）。
- **封面级素材**：3.3 的 401/403/404 三行表 + "选 403 还是 404"判据。
- **封面级素材**：3.4 的"门与锁"。
- 高光图：3.2 的授权三层次表 + AI 覆盖率表。
- 截图：`PATCH /users/42 -d '{"role":"admin"}'` 自我提权成功。

---

## 四、现场必做一：解开 JWT

**约 10 分钟。**

### 4.1 三段，各是什么

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 . eyJzdWIiOjQyLCJyb2xlIjoidXNlciJ9 . xR7mK9...
└──────────── header ──────────────┘  └─────────── payload ──────────┘  └ signature ┘
```

**逐段现场解**：

```bash
# header
echo 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' | base64 -d
{"alg":"HS256","typ":"JWT"}

# payload
echo 'eyJzdWIiOjQyLCJyb2xlIjoidXNlciJ9' | base64 -d
{"sub":42,"role":"user"}
```

**封面级素材**：

> **`base64` 不是加密，是编码。**
>
> | | 编码 | 加密 |
> |---|---|---|
> | 目的 | 让数据能安全传输（比如放进 URL） | 让没有密钥的人读不懂 |
> | 需要密钥吗 | **不需要** | 需要 |
> | 能还原吗 | **任何人都能** | 只有有密钥的人 |
> | 例子 | Base64、URL 编码、Hex | AES、RSA |
>
> **JWT 的 payload 是 Base64 编码的，不是加密的。**
>
> **任何拿到 token 的人，都能读到里面的全部内容。**

### 4.2 那签名是干什么的

**现场改一个字试试**：

```python
# 把 payload 里的 role 改成 admin，重新 base64 编码，拼回去
forged = header + "." + b64({"sub": 42, "role": "admin"}) + "." + old_signature
```

```bash
curl -H "Authorization: Bearer $FORGED" localhost:8000/admin/users
```

```
401 {"detail":"Invalid token"}
```

> **改不动。** 因为签名对不上。
>
> **所以 JWT 的保证是：**
>
> | JWT 保证 | JWT 不保证 |
> |---|---|
> | **完整性**——你改了我能发现 | **机密性**——内容是明文的 |
> | **来源可信**——只有持密钥的人能签 | **不可复制**——谁拿到都能用 |
>
> **判据（封面级）：**
>
> **签名保证"不可篡改"，不保证"不可读"，更不保证"不可复用"。**
>
> **推论一：不要把敏感信息放进 JWT payload。** 手机号、身份证、内部 id 规则，全部不行。
>
> **推论二：JWT 就是一张"谁捡到谁能用"的凭证。** 它必须像现金一样保管。

### 4.3 两个真实的坑

**坑一：`algorithms` 不能省**

```python
# ❌ 致命
jwt.decode(token, SECRET)                          # 不指定算法

# ❌ 更致命
jwt.decode(token, SECRET, algorithms=["HS256", "none"])
```

> 历史上有一类经典漏洞：攻击者把 header 的 `alg` 改成 `"none"`，**签名段留空**，某些库就直接放行了。
>
> 还有一类：把 `RS256`（非对称）改成 `HS256`（对称），**用公钥当密钥去签**——而公钥是公开的。
>
> **判据：解 token 时必须显式锁定算法白名单。**
>
> ```python
> jwt.decode(token, SECRET, algorithms=["HS256"])   # ✅
> ```
>
> **这是"白名单而不是黑名单"的第三次出现**：
>
> | 场景 | 白名单 | 哪次课 |
> |---|---|---|
> | 排序字段 | `Literal["latest","views"]` | 第 7 次课 |
> | URL 参数 | `parseListParams` | 第 13 次课 |
> | **JWT 算法** | **`algorithms=["HS256"]`** | **今天** |

**坑二：过期时间**

```python
# AI 写的
jwt.encode({"sub": user.id}, SECRET, algorithm="HS256")        # 永不过期

# 应该是
now = datetime.now(timezone.utc)
jwt.encode({
    "sub": str(user.id),
    "iat": now,
    "exp": now + timedelta(minutes=15),        # ← 短
    "jti": secrets.token_urlsafe(16),          # ← 唯一标识，吊销时要用
}, SECRET, algorithm="HS256")
```

> **为什么必须短？** 因为**你没有别的办法让它失效**（演示二）。
>
> 过期时间是 JWT 唯一的"止损机制"。
>
> **所以它的取值是一个权衡：**
>
> | 设置 | 后果 |
> |---|---|
> | 15 分钟 | 泄漏损失小；**但用户每 15 分钟要重登**（除非做刷新 token） |
> | 7 天 | 用户舒服；**泄漏后 7 天内一直有效** |
>
> 于是就有了刷新 token 那一套。**而一旦你开始做刷新 token，你就需要在服务端存它、能吊销它——**
>
> **那你就已经有状态了。单元 8 会把这个循环讲完。**

### 4.4 一个练习

**让学生现场做（2 分钟）**：

> 打开 https://jwt.io，把你自己项目里的 token 粘进去。
>
> **看看你的 payload 里都有什么。**
>
> 然后问自己：**这些东西，你愿意让一个陌生人看到吗？**

### 材料

- **封面级素材**：4.1 的"编码 vs 加密"四行表。
- **封面级素材**：4.2 的"签名保证什么、不保证什么" + 两条推论。
- 高光图：4.1 的三段结构图（**payload 段高亮**）。
- 高光图：4.3 的"白名单第三次出现"表。
- 高光图：4.3 的过期时间权衡表。
- **录屏（关键）**：从 DevTools 复制 token → 终端 `base64 -d` → 明文 JSON 跳出来。**一镜到底，不要剪辑。**
- 截图：jwt.io 上解开的 payload。
- 截图：伪造 role=admin 后返回 401（**说明签名有用**）。

---

## 五、密码与注册

**约 12 分钟。**

### 5.1 现场测一次哈希速度（**震撼点**）

```python
# bench.py
import hashlib, time, bcrypt

def bench(fn, n):
    t = time.perf_counter()
    for _ in range(n): fn()
    return n / (time.perf_counter() - t)

print("sha256 :", bench(lambda: hashlib.sha256(b"password123").hexdigest(), 200_000))
print("bcrypt :", bench(lambda: bcrypt.hashpw(b"password123", bcrypt.gensalt(12)), 5))
```

**现场跑，把结果打在屏幕上**：

```
sha256 : 2,140,000 次/秒
bcrypt : 3.7 次/秒
```

**停 10 秒。**

**封面级素材**：

> **同一台机器，同一个密码：**
>
> **SHA-256：每秒 200 万次。**
> **bcrypt(cost=12)：每秒 3.7 次。**
>
> **差了 57 万倍。**
>
> 而这还只是 Python、单核 CPU。**换成 GPU 集群，SHA-256 能到每秒几百亿次。**

**这意味着什么（醒目页）**：

假设一个 8 位的常见密码，攻击者拿到了你的数据库：

| 哈希算法 | 破解一个密码大约需要 |
|---|---|
| SHA-256（单张现代显卡） | **几分钟到几小时** |
| bcrypt cost=12 | **几十年** |

> **判据：通用哈希（MD5 / SHA-1 / SHA-256）是为"快"设计的。**
>
> **而密码哈希必须为"慢"设计。**
>
> 这是一个**故意的、可调的慢**——`cost` 参数就是在调它。

**正确的做法**：

```python
from passlib.context import CryptContext

pwd = CryptContext(schemes=["argon2"], deprecated="auto")

# 注册
user.password_hash = pwd.hash(form.password)

# 登录
if not pwd.verify(form.password, user.password_hash):
    ...
```

**三条要点**：

| 要点 | 说明 |
|---|---|
| **加盐是自动的** | bcrypt / Argon2 的输出里已经包含盐，你不需要自己存 |
| **参数要跟上时代** | Argon2id 推荐参数、bcrypt cost ≥ 12，**每隔几年要上调** |
| **`deprecated="auto"` 支持平滑升级** | 用户下次登录时自动用新参数重新哈希 |

**看一眼输出格式**：

```
$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$RdescudvJCsgt3ub+b+dWRWJTmaaJObG
 └ 算法 ┘ └版本┘ └─── 参数 ───┘ └─ 盐 ─┘ └────── 哈希 ──────┘
```

> **算法、参数、盐全部编码在字符串里。** 这就是为什么升级参数不会让老用户登不上——**验证时用的是它自己记录的那套参数。**

**记一笔账**：

> `SECRET = "my-secret-key"` 这行硬编码密钥还在。
>
> **回收第 10 次课：前端密钥必然泄漏。** 今天这个在后端，但它**进了 git 仓库**——同样是泄漏。
>
> **→ 第 16 次课正式处理密钥管理。** 今天先做最低限度：

```python
SECRET = settings.jwt_secret           # 从环境变量读
assert len(SECRET) >= 32, "密钥太短"
```

```python
# tests/test_conventions.py
def test_no_hardcoded_secret():
    for f in Path("app").rglob("*.py"):
        assert 'SECRET = "' not in f.read_text(), f"{f} 里有硬编码密钥"
```

### 5.2 注册：两道闸门

```python
class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

    @field_validator("password")
    @classmethod
    def not_too_common(cls, v: str) -> str:
        if v.lower() in COMMON_PASSWORDS:      # 一份常见弱口令表
            raise ValueError("密码过于常见")
        return v
```

**两条判据**：

> **一、长度比复杂度重要。**
>
> 强制"大小写+数字+符号"的结果，通常是 `Passw0rd!`——**它在任何字典里都排前列。**
>
> 现在的共识（NIST SP 800-63B）是：**要长度下限、查常见口令表、不要强制组成规则、不要强制定期改。**
>
> **二、唯一约束必须在数据库上。**

```python
# ❌ AI 写的
if db.query(User).filter_by(email=form.email).first():
    raise HTTPException(400, "已注册")
```

> **回收第 6 次课：这是一个 check-then-act，在并发下会失效。**
>
> 两个请求同时检查、同时发现"没有"、同时插入——**两条一样的邮箱。**
>
> 唯一的保证在数据库：
>
> ```python
> __table_args__ = (UniqueConstraint("email", name="uq_user_email"),)
> ```
>
> 然后捕获冲突：
>
> ```python
> try:
>     db.add(user); db.commit()
> except IntegrityError:
>     db.rollback()
>     ...  # 见 5.3
> ```
>
> **这是第 6 次课那条判据的第三次出现：应用层的检查是体验，数据库约束才是保证。**
>
> | 次课 | 说法 |
> |---|---|
> | 第 6 次课 | 唯一约束防重复 |
> | 第 11 次课 | `disabled` 是体验，唯一约束是保证 |
> | **今天** | **注册查重是体验，唯一约束是保证** |

### 5.3 不泄漏账号是否存在

**三个地方要统一**：

**① 登录失败**

```python
@router.post("/login")
def login(form: LoginIn, db=Depends(get_db)):
    user = db.query(User).filter_by(email=form.email).first()

    # 关键：无论用户是否存在，都做一次哈希验证
    ok = pwd.verify(form.password, user.password_hash if user else DUMMY_HASH)

    if not user or not ok:
        raise HTTPException(401, "邮箱或密码错误")    # ← 同一个消息、同一个状态码
    ...
```

> 两点都必要：
>
> | 做法 | 防的是 |
> |---|---|
> | **统一错误消息和状态码** | 直接从响应读出账号是否存在 |
> | **用户不存在时也跑一次哈希**（对一个预置的假哈希） | **时序侧信道**（演示三第二段） |

**现场验证**：

```bash
time curl ... alice@example.com    # real 0m0.31s
time curl ... nobody@example.com   # real 0m0.30s     ← 现在一样了
```

**② 注册时邮箱已存在**

> 这个更麻烦——**你必须告诉用户点什么**。
>
> 三种做法：
>
> | 做法 | 泄漏 | 体验 |
> |---|---|---|
> | 直接说"该邮箱已注册" | **泄漏** | 好 |
> | **总是返回"验证邮件已发送"，邮件内容按情况区分** | **不泄漏** | 好 |
> | 返回通用错误 | 不泄漏 | **差，用户不知道怎么办** |
>
> **推荐第二种：把区分转移到邮箱里。** 只有邮箱主人能看到。
>
> **判据：当"不泄漏"和"好体验"冲突时，找一条只有本人能看到的通道。**

**③ 找回密码**

> 同理：无论邮箱存不存在，都返回"如果该邮箱已注册，我们已发送重置链接"。

### 5.4 登录接口要限流（**记账**）

> 演示三那个枚举，**一秒能试几百次**。
>
> 加上密码爆破，登录接口是全站最需要限流的地方。
>
> 今天给出判据，实现留到第 16 次课：
>
> | 维度 | 策略 |
> |---|---|
> | 按 IP | 防大规模扫描 |
> | **按账号** | **防针对某个人的爆破**（换 IP 也没用） |
> | 失败多次后 | 加验证码，或临时锁定 |
>
> **注意"按账号"这条：只按 IP 限流，攻击者换代理就绕过了。**

### 材料

- **封面级素材**：5.1 的速度对比（**"200 万 vs 3.7，差 57 万倍"用超大字**）。
- **封面级素材**：5.1 的"通用哈希为快设计，密码哈希必须为慢设计"。
- 高光图：5.1 的破解时间对比表。
- 高光图：5.1 的 Argon2 输出格式解剖图。
- 高光图：5.2 的"长度比复杂度重要" + "唯一约束第三次出现"表。
- **封面级素材**：5.3 的"找一条只有本人能看到的通道"。
- 高光图：5.3 的注册三做法对照表。
- **录屏（关键）**：现场跑 `bench.py`，两个数字打出来。
- 截图：修复前后的 `time curl` 对比（**时间差消失**）。
- 截图：硬编码密钥检查在 CI 里变红。

---

## 六、会话：Cookie 的五个属性

**约 13 分钟。**

### 6.1 先换掉 localStorage

```python
@router.post("/login")
def login(form: LoginIn, response: Response, db=Depends(get_db)):
    user = authenticate(form, db)
    sid = create_session(user.id)                      # 服务端存一条
    response.set_cookie(
        key="sid",
        value=sid,
        httponly=True,                                  # ①
        secure=True,                                    # ②
        samesite="lax",                                 # ③
        max_age=None,                                   # ④ 会话 cookie
        path="/",                                       # ⑤
    )
    return {"ok": True}                                 # ← 响应体里没有 token
```

**注意最后一行**：

> **响应体里不返回 token。** 前端拿不到、也不需要拿到它——**浏览器会自动带。**
>
> **回收第 2 次课：Cookie 是浏览器自动携带的。**
>
> 当时这是一个中性的机制说明。今天它有两面：
>
> | 好处 | 坏处 |
> |---|---|
> | 前端不用管凭证 | **自动携带 = 别人的页面发起的请求也会带上** |
> | JS 碰不到它 | ← **这就是 CSRF，第 15 次课** |

### 6.2 五个属性逐项（**封面级素材**）

| 属性 | 作用 | **不设的后果** | 谁来防 |
|---|---|---|---|
| **`HttpOnly`** | **JS 读不到 `document.cookie`** | **XSS 能直接偷走会话** | 第 15 次课的 XSS |
| **`Secure`** | 只在 HTTPS 下发送 | 明文 WiFi 下被截获 | 网络窃听 |
| **`SameSite`** | 跨站请求不自动携带 | **CSRF** | 第 15 次课的 CSRF |
| **`Max-Age` / `Expires`** | 有效期 | 永久会话；共用电脑风险 | 会话滞留 |
| **`Path` / `Domain`** | 作用范围 | 范围过宽 → 子域泄漏 | 最小权限 |

**现场在 Application 面板逐项验证**：

```
DevTools → Application → Cookies → http://localhost:5173

Name    Value       HttpOnly  Secure  SameSite  Expires
sid     a3f9...     ✓         ✓       Lax       Session
```

**然后现场试一次**：

```js
// Console
document.cookie
// → ""          ← 读不到！
```

> **这就是 `HttpOnly` 的全部作用，而它值一整个类别的攻击。**
>
> 对比演示五：`localStorage.getItem("token")` 一行就拿到了。

**`SameSite` 三个值（醒目页）**：

| 值 | 行为 | 代价 |
|---|---|---|
| `Strict` | 任何跨站请求都不带 | **从外站点链接进来会显示未登录** |
| **`Lax`**（现代浏览器默认） | 跨站的 **GET 顶级导航**会带，其余不带 | **推荐默认** |
| `None` | 总是带 | **必须同时设 `Secure`**；仅在真正需要跨站时用 |

> **`Lax` 挡住了绝大多数 CSRF**——因为 CSRF 的经典形式是跨站发 POST。
>
> **但它不是全部。第 15 次课会讲为什么还需要 token。**

**Secure 在本地开发的坑**：

> `secure=True` 意味着**只在 HTTPS 下发送**。而你本地是 `http://localhost`。
>
> 好消息：**浏览器对 `localhost` 有豁免**，`Secure` cookie 在 localhost 上可用。
>
> 但如果你用 `http://192.168.1.5` 之类的地址调试，**cookie 会静默消失**——
>
> **回收第 5 次课：静默失败比响亮失败更危险。** 你看到的现象是"登录了但一直显示未登录"，而没有任何报错。

### 6.3 会话固定攻击：为什么登录后必须换 id

**画一个攻击时间线（封面级素材）**：

```
① 攻击者访问你的站点，拿到一个 session id：  sid = ABC123
② 攻击者诱导受害者用这个 id：
      发一个链接 https://yoursite.com/?sid=ABC123
      或在共用电脑上预先访问一次
③ 受害者用 ABC123 这个会话登录
④ 如果服务端沿用 ABC123 —— 攻击者手上的 ABC123 现在是已登录状态
⑤ 攻击者直接用它访问 → 冒充受害者
```

**修复只有一行**：

```python
def login(...):
    user = authenticate(form, db)
    old_sid = request.cookies.get("sid")
    if old_sid:
        destroy_session(old_sid)          # 销毁旧会话
    sid = create_session(user.id)         # ← 签发全新的 id
    response.set_cookie("sid", sid, ...)
```

**封面级素材**：

> **判据：任何权限级别发生变化的时刻，都要重新签发会话标识。**
>
> | 时刻 | 要重签吗 |
> |---|---|
> | 登录 | ✅ |
> | 登出 | ✅ |
> | **提权**（普通用户 → 管理模式） | ✅ |
> | 改密码 | ✅ **并且要踢掉其他所有会话** |
> | 普通请求 | ❌ |

### 6.4 session id 是 key 的第六次出现（**本单元的高光**）

**封面级素材**：

| 层 | 要回答 | 叫什么 | 要求 | 哪次课 |
|---|---|---|---|---|
| 数据库 | 是不是同一行 | 主键 | 唯一 | 第 6 次课 |
| UI 树 | 是不是同一个组件实例 | `key` | 唯一、稳定 | 第 11 次课 |
| 缓存 | 是不是同一份数据 | `queryKey` | 唯一、完整 | 第 12 次课 |
| 路由 | 要不要重建 | 路由 `key` | 随业务身份变化 | 第 13 次课 |
| **会话** | **是不是同一个人** | **session id** | **唯一 + 不可预测** | **今天** |

**关键句**：

> **前四次，key 的要求只有"唯一"。**
>
> **这一次多了一个：不可预测。**
>
> 因为 **key 被猜到，就是安全事故**。
>
> ```python
> # ❌ 自增
> sid = str(next_id())              # 猜下一个就行
>
> # ❌ 时间戳
> sid = str(time.time())            # 可枚举
>
> # ❌ 用户 id 的 md5
> sid = md5(str(user.id))           # 算得出来
>
> # ✅
> sid = secrets.token_urlsafe(32)   # 密码学随机，256 位
> ```
>
> **判据：凡是"猜中了就有后果"的标识，必须用 `secrets`，不能用 `random`。**
>
> `random` 是**可预测的伪随机**——观察到足够多的输出，就能推算出后续的值。它是为模拟和游戏设计的，不是为安全设计的。

### 6.5 登出与"记住我"

**登出必须服务端生效**：

```python
@router.post("/logout")
def logout(request: Request, response: Response):
    sid = request.cookies.get("sid")
    if sid:
        destroy_session(sid)                # ← 关键：服务端删掉
    response.delete_cookie("sid", path="/")
    return {"ok": True}
```

**现场重做演示二**：

```bash
# 登出前
curl -b "sid=$SID" localhost:8000/me       # → 200

# 登出
curl -X POST -b "sid=$SID" localhost:8000/logout

# 登出后
curl -b "sid=$SID" localhost:8000/me       # → 401 ✅
```

> **对比 JWT 版本：同样的操作，那边还是 200。**
>
> **这就是"有状态"换来的东西。单元 8 会把这笔账算清楚。**

**"记住我"**：

| 不勾 | 勾 |
|---|---|
| `max_age=None` → 会话 cookie，关浏览器就没了 | `max_age=30*86400` |
| | **但敏感操作（改密码、改邮箱、付款）要重新验证密码** |

> **判据：长期会话和敏感操作要分开。**
>
> "记住我"的意思是"记住我是谁"，**不是"记住我可以做任何事"**。

### 材料

- **封面级素材**：6.2 的 Cookie 五属性表（**`HttpOnly` 和 `SameSite` 两行用不同颜色，并标注"第 15 次课"**）。
- **封面级素材**：6.3 的会话固定攻击时间线 + "权限变化就重签"判据表。
- **封面级素材**：6.4 的"key 的六次出现"表（**最后一行"不可预测"高亮**）。
- 高光图：6.2 的 `SameSite` 三值表。
- 高光图：6.5 的登出前后 curl 对比。
- **截图（关键）**：Application 面板里 cookie 的五个属性列 + Console 里 `document.cookie` 返回空串，**同屏**。
- 截图：localStorage 方案里一行就读到 token（**与上一张并排，形成对照**）。
- 截图：JWT 版登出后仍 200 vs Session 版登出后 401。

---

## 七、现场必做二：IDOR 与对象级授权

**约 16 分钟。本次课最高光。**

### 7.1 完整复现

**准备**：两个账号 Alice（id=7）、Bob（id=9）。Alice 有一篇帖子 id=42。

**第 1 步**：Bob 登录，打开帖子 42。

```
界面上：没有"编辑"按钮，没有"删除"按钮。
```

> **前端做对了它该做的事。**

**第 2 步**：Bob 打开 DevTools，看一眼 Alice 编辑自己帖子时发的请求长什么样（或者直接看 `/docs`）。

**第 3 步**：

```bash
curl -X PATCH http://localhost:8000/questions/42 \
     -b "sid=$BOB_SID" \
     -H "Content-Type: application/json" \
     -d '{"title":"Bob 到此一游","body":"这是我的帖子了"}'
```

```
HTTP/1.1 200 OK
{"id":42,"title":"Bob 到此一游","author_id":7,...}
```

**第 4 步**：刷新页面。

```
标题：Bob 到此一游
作者：Alice                    ← 作者还是 Alice
```

**停 20 秒。**

> **注意最后这个细节：作者显示的还是 Alice。**
>
> 也就是说，**Bob 用 Alice 的名义发布了内容**。
>
> 这已经不只是数据被改了——**这是身份被冒用。**

**第 5 步：把范围扩大**

```bash
for i in $(seq 1 100); do
  curl -s -X PATCH localhost:8000/questions/$i -b "sid=$BOB_SID" \
       -d '{"title":"已被接管"}' -o /dev/null -w "$i:%{http_code} "
done
```

```
1:200 2:200 3:200 4:200 5:200 ... 100:200
```

> **全站的帖子，一个循环改完。**
>
> **门槛：一个正常注册的账号 + 会用 curl。**

### 7.2 这个漏洞叫什么

**封面级素材**：

> **IDOR — Insecure Direct Object Reference（不安全的直接对象引用）**
>
> 定义：**接口用一个可猜测的标识直接定位对象，而没有检查调用者是否有权访问这个对象。**
>
> | 它排第几 | OWASP Top 10 2021 **第 1 位**（Broken Access Control） |
> |---|---|
> | 需要什么技术 | **不需要任何技术** |
> | 需要什么条件 | **一个合法账号 + 改一个数字** |
> | 自动化扫描能发现吗 | **通常不能**——因为请求本身完全合法 |
> | 代码评审能发现吗 | **要一行一行看，而且要懂业务** |

**关键的一点**：

> **这个请求在任何日志、任何监控、任何 WAF 眼里，都是一个完全正常的请求。**
>
> - 它有合法的会话
> - 它的参数类型正确
> - 它没有任何注入特征
> - 它返回 200
>
> **回收第 12 次课、第 13 次课那条线：**
>
> | 类型 | 什么时候可见 |
> |---|---|
> | 类型错误 | 编译期 |
> | 竞态 | 只在特定时序 |
> | 假权限 | **看起来生效了** |
> | **IDOR** | **请求本身完全正常，只有业务语义是错的** |
>
> **工具看不见"语义"。这就是为什么授权必须靠设计，不能靠扫描。**

### 7.3 为什么 AI 会漏掉

**打出那段代码**：

```python
@router.patch("/questions/{qid}")
def update_question(qid: int, payload: QuestionUpdate,
                    user: User = Depends(get_current_user),     # ← 这里
                    db: Session = Depends(get_db)):
    q = db.get(Question, qid)
    ...
```

> **`user` 这个参数就是罪魁祸首。**
>
> 它让代码**看起来**处理了权限：
>
> - 有一个 `user`
> - 它来自 `Depends(get_current_user)`
> - 名字里有 `current_user`
>
> **然后这个 `user` 变量，在函数体里一次都没有被用到。**
>
> **判据（封面级）：如果一个 handler 声明了 `current_user` 却没有在逻辑里用到它，那它大概率漏了授权。**
>
> **这条判据可以变成一条自动检查。单元 7.5 会做。**

**再回收第 13 次课的 AI 错误四类表**：

> IDOR 属于**第四类：看得见的假实现**。
>
> | | 表现 |
> |---|---|
> | 界面上 | 按钮正确隐藏了 |
> | 代码里 | 有 `Depends(get_current_user)` |
> | README 里 | 写着"已实现权限控制" |
> | 测试里 | 通过（因为测试用的是作者本人） |
> | **真实情况** | **完全没有授权** |
>
> **四重假象，每一重都在阻止你去检查。**

### 7.4 修复：把授权做成依赖（**本次课最重要的设计**）

**先看"能跑但不好"的修法**：

```python
@router.patch("/questions/{qid}")
def update_question(qid: int, ..., user=Depends(get_current_user)):
    q = db.get(Question, qid)
    if q is None or q.author_id != user.id:      # ← 加一个 if
        raise NotFound()
    ...
```

> **这样能修好这一个接口。**
>
> **问题是：你有多少个接口？**
>
> ```
> PATCH  /questions/{qid}
> DELETE /questions/{qid}
> POST   /questions/{qid}/publish
> PATCH  /answers/{aid}
> DELETE /answers/{aid}
> POST   /answers/{aid}/accept
> ...
> ```
>
> **每一个都要记得写这个 if。漏一个就是一个洞。**
>
> **而三个月后新加的接口，是另一个人写的。**

**正确的做法**：

```python
# app/deps.py
async def get_owned_question(
    qid: int = Path(gt=0),                          # ← 入口闸门，第 3/9 次课
    user: User = Depends(require_login),
    db: AsyncSession = Depends(get_db),
) -> Question:
    q = await db.get(Question, qid)
    if q is None:
        raise NotFoundError("question", qid)
    if q.author_id != user.id:
        raise NotFoundError("question", qid)        # ← 404 不是 403，见 3.3
    return q
```

```python
@router.patch("/questions/{qid}", response_model=QuestionOut)
async def update_question(
    payload: QuestionUpdate,
    q: Question = Depends(get_owned_question),      # ← 只能拿到"已授权的对象"
    db: AsyncSession = Depends(get_db),
):
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(q, k, v)
    await db.commit()
    return q
```

**指着 handler 的签名，讲最关键的一句（封面级素材）**：

> **注意 handler 里已经没有 `qid` 这个参数了。**
>
> **它拿不到 id，只能拿到对象。**
>
> **而要拿到对象，就必须经过那个依赖。**
>
> **你不可能"忘记检查"——因为不检查，你手上什么都没有。**

### 7.5 这是"让正确的路成为唯一的路"（**封面级素材**）

| 护栏 | 机制 | **忘了会怎样** | 哪次课 |
|---|---|---|---|
| `response_model` | 不声明的字段不输出 | 字段消失，**立刻看见** | 第 3 次课 |
| `lazy="raise"` | 不显式加载就抛异常 | **当场报错** | 第 7 次课 |
| 生成的类型 | 字段名写错编译不过 | **编译期红** | 第 8 次课 |
| `readonly` | 原地改 state 编译不过 | **编译期红** | 第 11 次课 |
| **`get_owned_question`** | **不经授权拿不到对象** | **handler 里没有对象可用，写不下去** | **今天** |

**核心句**：

> **五道护栏，同一个形式：**
>
> **不是"检查你有没有做对"，而是"不做对就走不通"。**
>
> **判据：最好的护栏，让错误的写法根本写不出来。**
>
> 差一级的护栏是"写出来会报错"（类型检查、测试）。
> 再差一级是"写出来会有警告"（lint）。
> 最差的是"写文档提醒你"。

**然后加一道兜底检查（第 9 次课的固定动作）**：

```python
# tests/test_authz.py
PUBLIC_ROUTES = {
    ("GET", "/healthz"), ("POST", "/login"), ("POST", "/register"),
    ("GET", "/questions"), ("GET", "/questions/{qid}"),
    ("GET", "/docs"), ("GET", "/openapi.json"),
}

def test_every_mutating_route_requires_authz():
    """所有写操作路由，必须要么在白名单，要么依赖链里有认证。"""
    for route in app.routes:
        for method in route.methods & {"POST", "PATCH", "PUT", "DELETE"}:
            if (method, route.path) in PUBLIC_ROUTES:
                continue
            names = _all_dependency_names(route.dependant)
            assert names & {"require_login", "get_owned_question", "require_role"}, \
                f"{method} {route.path} 没有任何认证/授权依赖"


def test_no_unused_current_user():
    """声明了 current_user 却没用到的 handler，大概率漏了对象级授权。"""
    for fn in _all_route_handlers(app):
        sig = inspect.signature(fn)
        if "user" not in sig.parameters:
            continue
        src = inspect.getsource(fn)
        body = src.split(":", 1)[1]
        assert "user" in body, f"{fn.__name__} 声明了 user 但没用到，检查是否漏了授权"
```

> **第二个检查直接把 7.3 那条判据变成了机制。**
>
> **回收第 9 次课：新增一条纪律，当场补一条检查。这是第 N 次兑现。**

**然后加一条纪律：默认拒绝**

```python
# app/main.py
app.include_router(
    questions_router,
    dependencies=[Depends(require_login)],        # ← 整个路由组默认要登录
)

# 公开的路由显式豁免
@router.get("/questions", dependencies=[Depends(allow_anonymous)])
async def list_questions(...): ...
```

**封面级素材**：

> **判据：安全配置的默认值必须是"拒绝"，例外要显式写出来。**
>
> | 默认允许 + 列出要保护的 | **默认拒绝 + 列出公开的** |
> |---|---|
> | 忘记 = **洞** | 忘记 = **404/401，立刻被发现** |
> | 新人加接口默认不安全 | 新人加接口默认安全 |
>
> **这条判据不只用在这里：**
>
> | 场景 | 默认拒绝的形式 | 哪次课 |
> |---|---|---|
> | 输出字段 | `response_model` 白名单 | 第 3 次课 |
> | 排序字段 | `Literal` 白名单 | 第 7 次课 |
> | URL 参数 | `parseListParams` | 第 13 次课 |
> | JWT 算法 | `algorithms=["HS256"]` | 今天单元 4 |
> | **路由访问** | **默认需要登录** | **今天** |
>
> **第五次。这已经不是技巧，是一条通用原则。**

### 7.6 角色控制与审计日志

**角色（功能级授权）**：

```python
def require_role(*roles: str):
    async def dep(user: User = Depends(require_login)) -> User:
        if user.role not in roles:
            raise ForbiddenError()          # 这里用 403：资源存在性不敏感
        return user
    return dep

@router.post("/users/{uid}/ban", dependencies=[Depends(require_role("admin"))])
async def ban_user(...): ...
```

**审计日志（回收第 4 次课）**：

```python
logger.info(
    "question.updated",
    extra={
        "actor_id": user.id,
        "target_type": "question",
        "target_id": q.id,
        "request_id": get_request_id(),          # ← 第 4 次课
    },
)
```

**三条纪律（醒目页）**：

| 纪律 | 理由 |
|---|---|
| **记"谁对谁做了什么"** | 事后才能追溯 |
| **带上 `request_id`** | 能和访问日志、错误日志串起来 |
| **绝不记录密码、token、session id** | **回收第 4 次课的日志脱敏** |

> 最后一条要强调：**审计日志通常保留期最长、访问人最多**。
>
> **一条写错的审计日志，比一条写错的调试日志危险得多。**

### 材料

- **封面级素材**：7.2 的 IDOR 定义卡（**"OWASP 第 1 位 + 不需要任何技术"用大字**）。
- **封面级素材**：7.2 的"工具看不见语义"四行表。
- **封面级素材**：7.3 的"声明了 current_user 却没用到 = 大概率漏授权"。
- **封面级素材**：7.3 的"四重假象"表。
- **封面级素材**：7.4 的 handler 签名对比（**"没有 qid，只有 q"高亮**）。
- **封面级素材**：7.5 的"五道护栏同一形式"表 + "让错误的写法根本写不出来"。
- **封面级素材**：7.5 的"默认拒绝第五次出现"表。
- 高光图：7.6 的审计日志三条纪律。
- **录屏（本次课最关键）**：IDOR 五步，一镜到底。**第 4 步刷新后"标题被改、作者仍是 Alice"要停住；第 5 步的批量循环要让 `200` 刷满屏幕。**
- **截图（杀手级）**：三格——**界面无编辑按钮 / curl 返回 200 / 刷新后标题变了但作者还是 Alice**。
- 截图：批量修改 100 条全部 200。
- 截图：修复后同样的 curl 返回 404。
- 截图：`test_no_unused_current_user` 在修复前变红、修复后变绿。
- 截图：新加一个路由忘记加依赖 → `test_every_mutating_route_requires_authz` 变红。
- tag `v14-idor-fixed`。

---

## 八、Session vs JWT

**约 8 分钟。**

### 8.1 决策矩阵（**封面级素材**）

| 维度 | **Session（服务端存储）** | **JWT（无状态）** |
|---|---|---|
| **吊销** | **删一行，即时生效** | **做不到** |
| 改了权限何时生效 | **立即** | **等 token 过期** |
| 改密码踢掉其他设备 | **可以** | 做不到 |
| 水平扩展 | 需要共享存储（Redis） | 不需要 |
| 每个请求的体积 | 一个 id，约 40 字节 | **几百字节到几 KB** |
| 泄漏后的损失 | 可立即止损 | **到期前一直有效** |
| 适合跨服务/跨域 | 受 Cookie 同站限制 | 灵活 |
| **实现复杂度** | **低**（就是存一张表） | **看起来低，实际高** |

**最后一行要展开**：

> JWT 看起来简单：签一个、验一个，不用存。
>
> **然后你会依次遇到这些需求：**
>
> ```
> "登出要立即失效"        → 需要黑名单 → 你有状态了
> "改密码要踢掉其他设备"   → 需要版本号或黑名单 → 你有状态了
> "token 有效期太短，用户老掉线" → 需要刷新 token
> "刷新 token 也要能吊销"  → 需要存刷新 token → 你有状态了
> ```
>
> **每一步都把你推回有状态。** 而到最后你发现：**你实现了一个更复杂的 session，只是名字叫 JWT。**

### 8.2 一句话判据

**封面级素材**：

> **"无状态"不是免费的。它是用"不能吊销"换来的。**
>
> **而绝大多数 Web 应用都需要吊销。**

**给具体的选择建议（醒目页）**：

| 场景 | 选 |
|---|---|
| **单体 Web 应用**（我们的项目） | **Session + HttpOnly Cookie** |
| 前后端分离但同站部署 | **Session + Cookie**（第 12 次课的同源部署） |
| 移动 App / 多端 | JWT 或不透明 token（服务端存） |
| 多个互不信任的微服务需要验身份 | **JWT 的主场** |
| 第三方接入、OAuth | JWT / OIDC |

> **判据：JWT 的正确用途是"跨信任边界传递已验证的身份"。**
>
> 而**一个单体应用内部，没有信任边界可跨。**

### 8.3 一个常见的误解

> 很多人选 JWT 的理由是"**性能更好，不用查数据库**"。
>
> **两个问题：**
>
> | 问题 | 说明 |
> |---|---|
> | 你真的不查吗 | **你还是要查用户**（拿角色、拿状态、检查是否被封禁）。除非你把这些全塞进 token——那就回到"改了不生效"的问题 |
> | 查一次 session 有多贵 | **Redis 的一次 GET 是 0.1ms 量级**。跟你那次数据库查询、那次模板渲染比，可以忽略 |
>
> **回收第 13 次课那条判据：引入一个东西之前，先说清"不用它我要写什么"。**
>
> **今天加一条对称的：也要说清"用了它我要额外写什么"。**

### 8.4 ADR：写下来

> 作业要求写一份 ADR（架构决策记录）。格式：

```markdown
# ADR-003：会话方案选择

## 背景
本项目是单体 Web 应用，前端 SPA 与后端同站部署（第 12 次课拓扑 C）。
需要支持登录、登出、改密码后踢出其他设备。

## 考虑过的方案
1. JWT + localStorage
2. JWT + HttpOnly Cookie
3. Session + HttpOnly Cookie   ← 选定

## 决定
选 3。

## 理由
- 需要"改密码踢掉其他设备"，JWT 做不到（见 8.1 表）
- 同站部署，Cookie 无跨域障碍
- localStorage 方案无法抵御 XSS（第 15 次课）
- 会话查询走 Redis，实测 0.15ms，不构成瓶颈

## 代价
- 需要运维一个 Redis
- 水平扩展时必须用共享存储，不能用本地内存

## 什么情况下会重新考虑
- 如果要做原生 App，Cookie 方案不适用
- 如果拆成多个服务，需要跨服务传递身份
```

> **注意最后一节："什么情况下会重新考虑"。**
>
> **判据：一份没有写明"失效条件"的决策记录，半年后就会变成教条。**

### 材料

- **封面级素材**：8.1 的决策矩阵（**"吊销"那行用醒目色**）。
- **封面级素材**：8.1 的"每一步都把你推回有状态"四行推演。
- **封面级素材**：8.2 的"无状态是用不能吊销换来的"。
- 高光图：8.2 的场景选择表。
- 高光图：8.4 的 ADR 模板（**"失效条件"那节高亮**）。

---

## 九、前端接入

**约 7 分钟。**

### 9.1 `credentials` 与 CORS（**回收第 12 次课**）

```ts
// web/src/client.ts
export const client = createClient<paths>({
  baseUrl: import.meta.env.VITE_API_BASE,
  credentials: "include",            // ← 关键：让浏览器带上 cookie
});
```

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,       # 明确白名单，不能是 *
    allow_credentials=True,                    # ← 第 12 次课那个开关
    ...
)
```

> **第 12 次课我们说过：`allow_credentials=True` 和 `allow_origins=["*"]` 不能共存。**
>
> **今天你知道为什么了**：`*` 的意思是"任何站点都能读我的响应"，credentials 的意思是"带上用户的登录态"。**两者同时成立 = 任何站点都能用用户的身份读你的数据。**
>
> **而如果你按第 12 次课的结论选了同源部署，这一整段都不需要。** 这就是同源的好处。

### 9.2 401 拦截

```ts
const authMiddleware: Middleware = {
  async onResponse({ response }) {
    if (response.status === 401) {
      queryClient.clear();                              // ← 清掉所有缓存
      const next = encodeURIComponent(
        location.pathname + location.search
      );
      router.navigate(`/login?next=${next}`);
    }
    return response;
  },
};
```

**两条要点**：

> **一、必须 `queryClient.clear()`。**
>
> **回收第 13 次课：`currentUser` 是"query 层 + Context"的双重归属。**
>
> 如果不清缓存，登出后再登录另一个账号，**你会看到上一个人的数据**——因为 React Query 的缓存条目还在。
>
> 登录成功后同理：
>
> ```ts
> await login(form);
> queryClient.clear();                     // 或至少 invalidateQueries(["me"])
> ```
>
> **判据：任何改变"我是谁"的操作，都必须让所有跟身份相关的缓存失效。**

> **二、`next` 参数必须校验。**

```ts
// ❌ 开放重定向
navigate(searchParams.get("next")!);

// ✅ 只允许站内相对路径
const raw = searchParams.get("next") ?? "/";
const safe = raw.startsWith("/") && !raw.startsWith("//") ? raw : "/";
navigate(safe);
```

> 不校验会怎样？
>
> ```
> https://yoursite.com/login?next=https://evil.com/fake-login
> ```
>
> 用户看到的是**你的域名**、你的登录页，登录成功后**被送到钓鱼站**。
>
> **这叫开放重定向。** 它本身不直接窃取数据，**但它借用了你的可信度。**
>
> **回收第 13 次课的入口闸门：`next` 是 URL 参数，就是用户输入，就要校验。**
>
> **判据：任何把用户输入当成跳转目标的地方，都必须白名单。第六次。**

### 9.3 不要在前端"判断是否登录"

```ts
// ❌ AI 常写的
const isLoggedIn = !!localStorage.getItem("token");

// ✅
const { data: me, isPending } = useQuery({
  queryKey: ["me"],
  queryFn: () => client.GET("/me"),
  retry: false,
});
```

> **用 Cookie 方案后，前端根本看不到凭证**（`HttpOnly`）。
>
> **这是好事**——它迫使你用唯一正确的方式判断登录状态：**问服务器。**
>
> | 前端自己判断 | 问服务器 |
> |---|---|
> | token 过期了前端不知道 | 准确 |
> | token 被吊销了前端不知道 | 准确 |
> | 用户被封禁了前端不知道 | 准确 |
>
> **判据（第 13 次课那条的第四次）：前端的登录状态是缓存，服务器的判断才是真相。**

### 材料

- 高光图：9.1 的 credentials + CORS 配对。
- **封面级素材**：9.2 的"任何改变'我是谁'的操作都要让身份缓存失效"。
- 高光图：9.2 的开放重定向示例（**假域名那一行标红**）。
- 高光图：9.3 的"前端判断 vs 问服务器"三行表。
- 截图：登出后不清缓存 → 换账号登录看到上一个人的数据（**很有说服力**）。
- tag `v14-final`。

---

## 十、C 档结论卡

**约 3 分钟。时间不够整体跳过。**

| 问题 | 结论 |
|---|---|
| OAuth2 / OIDC / "用 GitHub 登录" | **不要自己实现 OAuth 流程**，用成熟库。它解决的是"让第三方验证身份" |
| 多因素认证（MFA/2FA） | TOTP 是最容易落地的一种。**备用恢复码必须提供**，否则用户会被锁死 |
| 密码重置 | token 要**一次性、短时效、与用户绑定、用后立即失效**。不要用可预测的值 |
| 邮箱验证 | 同上。**注意：未验证邮箱的账号应该受限，而不是完全可用** |
| 限流 | 登录、注册、密码重置三个接口必须限流。**按 IP + 按账号双维度** |
| 验证码 | 不要作为第一道防线。它是"失败若干次之后"的升级手段 |
| 会话存哪 | Redis 最常见。数据库也行，**注意加 TTL 清理** |
| 并发会话数限制 | "同一账号最多 3 个设备"这类需求，**Session 方案一行代码，JWT 方案做不到** |
| 权限模型（RBAC / ABAC） | 小项目角色枚举就够。**当你开始写 `if role == 'admin' or (role == 'editor' and ...)`，考虑升级** |
| 前端路由守卫还要不要 | **要**，它是体验。但要记住它不提供任何安全保证（第 13 次课） |
| 密码强度提示 | 用 zxcvbn 这类基于真实泄漏库的估算，**比"必须含大写字母"有意义得多** |
| 泄漏密码检测 | Have I Been Pwned 有一个 k-匿名 API，**可以在不发送密码的前提下检查** |

---

## 十一、作业与欠账

**约 5 分钟。**

### 11.1 作业一：认证授权闭环（必交）

| # | 要求 | 验收方式 |
|---|---|---|
| 1 | 注册：Argon2/bcrypt 推荐参数、长度下限 ≥ 12、常见口令拦截 | 代码 + 测试 |
| 2 | **数据库唯一约束**防重复注册（不是应用层 if） | 迁移文件 + 并发测试 |
| 3 | **不泄漏账号是否存在**：三处（登录/注册/找回）响应统一 | 三组 curl 截图 |
| 4 | **时序统一**：存在与不存在的登录请求耗时差 < 20% | `time curl` 前后对比截图 |
| 5 | 登录成功后**重签会话标识**，旧的立即失效 | 测试 |
| 6 | Cookie 五属性全部正确设置 | **Application 面板截图** |
| 7 | **登出服务端生效**：登出后用旧凭证请求返回 401 | curl 前后对比 |
| 8 | **所有写操作路由**通过 `require_login` / `get_owned_*` / `require_role` 之一 | `test_every_mutating_route_requires_authz` 通过 |
| 9 | **对象级授权做成依赖**，handler 拿不到裸 id | 代码 + 截图 |
| 10 | 至少一处角色控制 + 审计日志（含 `request_id`，无敏感信息） | 日志截图 |
| 11 | 前端 401 拦截 + 身份变化时清缓存 + `next` 参数白名单 | 代码 + 录屏 |
| 12 | 硬编码密钥检查、调试后门检查进 CI | CI 截图 |

### 11.2 作业二：IDOR 修复证据（必交，评分重点）

**必须是红-绿两步（第 9 次课的方法论）**：

| 步骤 | 交什么 |
|---|---|
| ① **复现** | 录屏：用账号 B 修改/删除账号 A 的资源，**至少两个不同的接口** |
| ② **批量证明** | 截图：循环遍历 id，统计有多少条能被越权操作 |
| ③ **写测试（红）** | 测试代码 + **失败截图** |
| ④ **修复** | diff：改成依赖注入的形式 |
| ⑤ **测试（绿）** | 通过截图 |
| ⑥ **兜底检查** | `test_every_mutating_route_requires_authz` + `test_no_unused_current_user` 两条都要有 |
| ⑦ **回归验证** | **新加一个写操作路由，故意不加依赖，证明 CI 会红** |

**第 ⑦ 步是关键**：

> **前六步证明你修好了这一次。第七步证明下一次也不会出问题。**
>
> **回收第 9 次课：修一个 bug 的完整形式，是让同类 bug 不能再次发生。**

### 11.3 作业三：会话方案 ADR（必交）

按 8.4 的格式写，必须包含：

- 你考虑过的**至少三个**方案
- 你的选择和**具体到本项目的**理由（不要抄通用结论）
- **代价**：这个选择让你多付出了什么
- **失效条件**：什么情况下你会重新考虑

### 11.4 作业四：AI 认证代码审查（**课程主题作业**）

**第一部分：拿样本**

> 向 AI 提需求：**"给我的 FastAPI + React 项目加上用户认证，支持注册、登录、登出，只有作者能编辑自己的文章。"**
>
> 原样保存输出，**不要给任何额外约束**。

**第二部分：对照检查表逐项打分**

| # | 检查项 | 它做了吗 | 后果 |
|---|---|---|---|
| 1 | 密码用了慢哈希（bcrypt/Argon2）吗 | | |
| 2 | 密钥从环境变量读吗 | | |
| 3 | JWT 有过期时间吗 | | |
| 4 | `jwt.decode` 锁定算法白名单了吗 | | |
| 5 | token 存哪？localStorage 还是 HttpOnly Cookie | | |
| 6 | Cookie 的五个属性设了几个 | | |
| 7 | 登录成功后重签会话标识了吗 | | |
| 8 | 登出在服务端生效吗 | | |
| 9 | 登录失败的错误信息区分"用户不存在"和"密码错"吗 | | |
| 10 | **有对象级授权吗**（改文章时检查作者） | | |
| 11 | **有字段级授权吗**（能不能自己改 role） | | |
| 12 | 有限流吗 | | |

**统计：12 项，做对 ___ 项。**

**第三部分：实际攻击验证**

| 步骤 | 做什么 | 结果 |
|---|---|---|
| ① | 解开它签发的 token，看 payload 里有什么 | |
| ② | 用账号 B 尝试修改账号 A 的资源 | 成功/失败 |
| ③ | 尝试 `PATCH /users/me -d '{"role":"admin"}'` | 成功/失败 |
| ④ | 登出后用旧凭证请求 | 成功/失败 |
| ⑤ | 用不存在的邮箱和存在的邮箱各登录一次，对比响应和耗时 | |

**第四部分：必答六问（评分重点）**

| # | 问题 |
|---|---|
| 1 | 12 项里它做对了几项？**做对的那些有什么共同点？做错的那些有什么共同点？** |
| 2 | 第 10、11 项（对象级/字段级授权）它做了吗？**如果没做，它的代码里有没有任何"看起来像做了"的东西？** |
| 3 | **查一查：它用的 token 存储方案，在哪一年是主流推荐？现在还是吗？** |
| 4 | 基于第 3 问，第 13 次课那张"AI 错误四类表"够用吗？**如果不够，你要加第五类吗？它和前四类的区别是什么？对策有什么不同？** |
| 5 | 假设你没上过这节课，你会怎么验收这段代码？**你的验收方式能发现第三部分里的哪几个问题？** |
| 6 | 给出一条"验收 AI 生成的认证代码"的操作规则。**要具体到可执行**，不能是"要仔细检查" |

> **第 3、4 问是本次作业的核心。**
>
> 提示：AI 写 `localStorage.setItem("token", ...)` **不是因为它不知道 HttpOnly Cookie**。
>
> 这个写法在 2015–2019 年的教程里是**绝对主流**，当时"前后端分离就该用 token，Cookie 是老古董"是普遍共识。
>
> **AI 没有写错，它写的是那个年代的正确答案。**

**封面级素材（讲作业时打出）**：

| 类别 | AI 的行为 | 为什么会这样 | 对策 |
|---|---|---|---|
| ① 缺信息 | 猜字段名 | 它不知道你的项目 | **补信息** |
| ② 模仿多数 | `key={index}` | 训练数据里多数这么写 | **加约束**（lint/类型） |
| ③ 编写期不可见 | 没有竞态保护 | 这类错误在代码里看不出来 | **改结构** |
| ④ 看得见的假实现 | 前端隐藏按钮当权限 | 有可见效果，且效果是假的 | **绕过界面验证** |
| **⑤ 过时的正确答案** | **token 存 localStorage** | **它在某个年代确实是主流** | **核对时效** |

> **第五类最隐蔽的地方：你去搜索验证，也会搜到一堆支持它的文章。**
>
> 因为那些文章和 AI 的训练数据是**同一批材料**。
>
> | | 第②类 | **第⑤类** |
> |---|---|---|
> | 当年是对的吗 | **不是** | **是** |
> | 搜索能纠正吗 | 能（多数现在写对了） | **不能——搜到的是同一批老文章** |
> | 有工具能拦吗 | 有（lint 规则） | **几乎没有** |
> | 怎么办 | 加规则 | **查官方文档的更新日期；查 OWASP 当前版本；看"这个建议是哪年提出的"** |
>
> **判据：对安全相关的建议，永远要问"这是哪一年的共识"。**
>
> **安全领域的知识有保质期，而 AI 不标注生产日期。**

### 11.5 欠账登记

| 欠账 | 何时还 |
|---|---|
| **XSS 怎么打、怎么偷 Cookie** | **第 15 次课（现场必做）** |
| **CSRF 与 SameSite 的完整因果链** | **第 15 次课** |
| SQL 注入、参数化查询 | **第 15 次课** |
| 安全响应头、CSP | **第 15 次课** |
| 依赖漏洞扫描 | **第 15 次课** |
| 密钥管理、环境隔离 | **第 16 次课** |
| 限流的实现 | **第 16 次课** |
| HTTPS / 证书 | **第 16 次课** |
| MFA、OAuth、密码重置、会话存储选型 | 课后自读 |

---

## 十二、素材清单与制作说明

### 必需素材

| 素材 | 说明 |
|---|---|
| tag `v14-broken` | 起始版：AI 原样的认证系统。**必须能正常登录使用**，否则学生不会相信"它看起来是对的" |
| tag `v14-jwt-fixed` | 单元 4 结束 |
| tag `v14-pwd-fixed` | 单元 5 结束 |
| tag `v14-session` | 单元 6 结束 |
| tag `v14-idor-fixed` | 单元 7 结束 |
| tag `v14-final` | 作业参考交付 |
| `bench.py` | 单元 5.1 的哈希速度对比，**课堂现场跑** |
| `tests/test_authz.py` | 两条兜底检查 |
| `tests/test_conventions.py` 扩展 | 调试后门、硬编码密钥 |
| 两个测试账号 Alice / Bob + 种子数据 100 条帖子 | 单元 7 必需 |
| **合规确认书** | 单元 1.4，**本次课签署，第 15 次课生效** |
| **封面级 A** | 单元 1.1 的三格拼图（**第 13 次课原图重放**） |
| **封面级 B** | 单元 2 的五个演示归类表 |
| **封面级 C** | 单元 3.1 的认证/授权对照表 |
| **封面级 D** | 单元 3.3 的 401/403/404 + 选择判据 |
| **封面级 E** | 单元 3.4 的"门与锁" |
| **封面级 F** | 单元 4.1 的"编码 vs 加密" |
| **封面级 G** | 单元 4.2 的"签名保证什么、不保证什么" |
| **封面级 H** | 单元 5.1 的速度对比（**超大字**） |
| **封面级 I** | 单元 5.1 的"通用哈希为快设计，密码哈希必须为慢" |
| **封面级 J** | 单元 5.3 的"找一条只有本人能看到的通道" |
| **封面级 K** | 单元 6.2 的 Cookie 五属性表 |
| **封面级 L** | 单元 6.3 的会话固定时间线 |
| **封面级 M** | 单元 6.4 的"key 的六次出现"（**"不可预测"高亮**） |
| **封面级 N** | 单元 7.2 的 IDOR 定义卡 |
| **封面级 O** | 单元 7.2 的"工具看不见语义" |
| **封面级 P** | 单元 7.3 的"声明了 current_user 却没用到" |
| **封面级 Q** | 单元 7.3 的"四重假象" |
| **封面级 R** | 单元 7.4 的 handler 签名对比 |
| **封面级 S** | **单元 7.5 的"五道护栏同一形式"表**（本次课最重要的方法论页） |
| **封面级 T** | 单元 7.5 的"默认拒绝第五次出现" |
| **封面级 U** | 单元 8.1 的决策矩阵 |
| **封面级 V** | 单元 8.1 的"每一步都把你推回有状态" |
| **封面级 W** | 单元 8.2 的"无状态是用不能吊销换来的" |
| **封面级 X** | 单元 9.2 的"身份变化时清缓存" |
| **封面级 Y** | **单元 11.4 的 AI 错误五类表 + 第②/⑤类对照**（第五类新增） |
| 高光图 Z | 单元 3.2 的授权三层次 + AI 覆盖率 |
| 高光图 AA | 单元 4.3 的"白名单第三次出现" |
| 高光图 AB | 单元 5.1 的 Argon2 输出格式解剖 |
| 高光图 AC | 单元 6.2 的 SameSite 三值 |
| 高光图 AD | 单元 8.4 的 ADR 模板 |
| **录屏 1（最关键）** | **IDOR 五步一镜到底**。第 4 步刷新后停 5 秒；第 5 步 200 刷满屏 |
| **录屏 2（关键）** | 从 DevTools 复制 token → `base64 -d` → 明文 JSON |
| **录屏 3** | 现场跑 `bench.py`，两个数字出来 |
| **截图（杀手级 1）** | IDOR 三格：**无编辑按钮 / curl 200 / 标题变了但作者还是 Alice** |
| **截图（杀手级 2）** | **Application 面板五属性 + Console `document.cookie` 为空**，同屏 |
| **截图（杀手级 3）** | 与上一张并排：**localStorage 方案里一行读到 token** |
| 截图 | 登出后 JWT 仍 200 vs Session 401 |
| 截图 | 账号枚举：404 vs 401 两个响应 |
| 截图 | 时序泄漏：修复前后 `time curl` 对比 |
| 截图 | `PATCH /users/42 -d '{"role":"admin"}'` 自我提权 |
| 截图 | 伪造 role=admin 的 token 返回 401 |
| 截图 | 批量越权 100 条全 200 |
| 截图 | 修复后同样 curl 返回 404 |
| 截图 | 两条兜底测试的红/绿 |
| 截图 | 新加路由忘加依赖 → CI 红 |
| 截图 | 调试后门检查 / 硬编码密钥检查 CI 红 |
| 截图 | 登出后不清缓存 → 换账号看到上一个人的数据 |
| 截图 | jwt.io 上解开的 payload |

### 可后补

- C 档结论卡（纯文字）。
- 单元 6.5 的"记住我"相关截图（若压缩则不需要）。

### 备用材料

| 风险 | 备用方案 |
|---|---|
| **`bench.py` 在教室机器上跑太慢**（bcrypt cost=12 每次约 0.3s） | 把 bcrypt 的 n 降到 3 次；**备好预跑结果截图** |
| `base64 -d` 在 Windows 上不可用 | 提供 Python 一行版 `python -c "import base64,sys;print(base64.urlsafe_b64decode(sys.argv[1]+'=='))"`；或用 jwt.io |
| JWT payload 的 base64 缺 padding 导致解码失败 | **课件里的示例 token 预先构造成 padding 正好**；并提供补 `==` 的说明 |
| `secure=True` 导致本地 cookie 不生效 | 强调 localhost 豁免；若用 IP 访问则提供 `settings.cookie_secure` 按环境切换 |
| 学生问"那我现在项目里的 JWT 要全改吗" | 准备一页迁移路径：**可以先保留 JWT，但必须加过期时间 + 移出 localStorage** |
| IDOR 演示时忘记切账号导致"修复了也能改" | **两个终端各自固定一个账号的 cookie**，终端标题写明 Alice/Bob |
| 有学生想在外网试手 | **合规声明必须当场签，并口头强调第 3 条法律条款** |
| passlib 与新版 bcrypt 的兼容告警 | 锁版本；底稿标注版本号 |
| AI 现场调用失败 | 预录样本。**必须真实包含 localStorage + 缺对象级授权**，不要人工编造 |
| 时间超支 | 按单元〇压缩顺序；单元 6、8 有自读材料 `docs/session.md`、`docs/session-vs-jwt.md` |

### 环境与运行条件

后端新增：`passlib[argon2]`、`pyjwt`、Redis（会话存储，可用内存字典替代但要说明）。

**演示开始时的初始状态**：后端在 tag `v14-broken` 已启动；前端已启动；已有 Alice/Bob 两个账号和 100 条种子帖子；**两个终端分别预置好 `$ALICE_SID` 和 `$BOB_SID`，终端标题标明身份**；浏览器 DevTools 的 Application 面板已打开。

**复位方式**：`git checkout v14-broken -- app web/src && python scripts/seed.py --reset`。

---

## 十三、与前后课的衔接

**本次课回收的前序埋点**：

| 来源 | 埋点 | 回收位置 |
|---|---|---|
| 第 2 次课 | Cookie 是浏览器自动携带的 | **单元 6.1**（今天给出它的两面性） |
| 第 2 次课 | 401 的名字起错了，它是未认证 | **单元 3.3**（补完 403/404 判据） |
| 第 3 次课 | 入口闸门：外层收窄类型 | 单元 7.4（`qid: int = Path(gt=0)`） |
| 第 3 次课 | 不要用 `dict` 接收请求体 | **单元 3.2**（字段级越权的完整代价） |
| 第 3 次课 | `response_model` 白名单 | **单元 7.5**（五道护栏之一） |
| 第 4 次课 | 错误信息不泄漏内部细节 | **单元 2 演示三、5.3**（扩展到"不泄漏账号存在"） |
| 第 4 次课 | 结构化日志 + `X-Request-Id` | 单元 7.6（审计日志） |
| 第 4 次课 | 日志脱敏 | 单元 7.6（审计日志绝不记 token） |
| 第 5 次课 | 静默失败比响亮失败更危险 | 单元 6.2（`Secure` 在非 localhost 的静默失效） |
| 第 6 次课 | 唯一约束防重复（check-then-act 会失效） | **单元 5.2**（第三次出现） |
| 第 6 次课 | 主键标识一行 | 单元 6.4（key 六次之一） |
| 第 7 次课 | `lazy="raise"` | **单元 7.5**（五道护栏之一） |
| 第 7 次课 | 排序字段 `Literal` 白名单 | 单元 4.3、7.5（默认拒绝第二次） |
| 第 9 次课 | 红-绿两步 | 作业二 |
| 第 9 次课 | 新增纪律当场补检查 | 单元 1.2、5.1、7.5 三次兑现 |
| 第 9 次课 | `Path(gt=0)` 入口闸门 | 单元 7.4 |
| 第 10 次课 | 密钥必然泄漏 → 不能进产物 | 单元 5.1（今天是后端版：不能进仓库） |
| 第 10 次课 | 生成的类型是最便宜的护栏 | 单元 7.5 |
| 第 11 次课 | 前端校验是体验，后端是安全 | **单元 9.3**（第四次） |
| 第 11 次课 | `readonly` 护栏 | 单元 7.5（五道护栏之一） |
| 第 12 次课 | `allow_credentials` + 不能用 `*` | **单元 9.1**（今天给出理由） |
| 第 12 次课 | "只在开发期有效"的便利是在推迟问题 | **单元 1.2**（补上后半句：必须有护栏保证它留在开发期） |
| 第 12 次课 | 同源部署最省事 | 单元 9.1 |
| 第 12 次课 | AI 错误三类 | **单元 11.4 扩到五类** |
| 第 13 次课 | **curl 穿透三格拼图** | **单元 1.1 开场重放，单元 7 正式修复** |
| 第 13 次课 | 前端隐藏是体验，后端授权才是安全 | 单元 3、7 全程 |
| 第 13 次课 | 路由守卫是导航体验，不是访问控制 | 单元 10 结论卡 |
| 第 13 次课 | `currentUser` 双重归属 | **单元 9.2**（`queryClient.clear()`） |
| 第 13 次课 | URL 会进日志、历史、Referer | 单元 6.1（所以 token 不放 URL） |
| 第 13 次课 | URL 参数白名单闸门 | **单元 9.2**（`next` 参数，第六次） |
| 第 13 次课 | **`X-Debug-User` 必须删掉** | **单元 1.2**（如约兑现，并补 CI 检查） |
| 第 13 次课 | AI 错误第四类"看得见的假实现" | **单元 7.3**（IDOR 是最佳标本） |

**本次课埋下、下次课必须回引的五处**（请在课件中明显标记）：

- **单元 2 演示五**（`localStorage.getItem("token")` 一行读走）→ **第 15 次课的 XSS 现场必做，就是把这一行变成攻击者的代码**；
- **单元 6.2 的 `HttpOnly`** → 第 15 次课 XSS 复测时，**同样的攻击载荷在 HttpOnly 下偷不到东西**，这是 before/after 的核心证据；
- **单元 6.2 的 `SameSite`** → 第 15 次课 CSRF 的因果链起点；
- **单元 7.5 的"默认拒绝"** → 第 15 次课的 CSP 是同一条原则在浏览器层的应用（默认拒绝所有脚本源，白名单放行）；
- **单元 11.4 的第⑤类"过时的正确答案"** → 第 15 次课会遇到大量同类：MD5 加盐、`mysql_real_escape_string`、`X-XSS-Protection` 头，**全部是"当年的正确答案"**。

**本次课不承担、请勿提前引入**：XSS/CSRF/注入的攻击手法（第 15 次课）、CSP 与安全响应头（第 15 次课）、依赖漏洞扫描（第 15 次课）、密钥管理与生产配置（第 16 次课）、限流实现（第 16 次课）。

**给第 15 次课的提示**：

今天建立了会话机制，**也就等于给第 15 次课准备好了攻击目标**。

建议第 15 次课这样开场：

> **把今天单元 6 那张"Application 面板 + `document.cookie` 为空"的截图打回来。**
>
> 然后说：**"上节课我说 `HttpOnly` 能挡住 XSS。今天先证明 XSS 有多容易，再证明它真的挡得住。"**

同时提醒第 15 次课注意三个今天埋下的具体钩子：

| 今天埋的 | 第 15 次课怎么接 |
|---|---|
| 两套并存的凭证方案（localStorage / HttpOnly Cookie） | **XSS 攻击对两者的效果完全不同**，这是最有说服力的 before/after |
| 单元 7.5 的"默认拒绝"五次出现 | CSP 是第六次，而且是在浏览器层 |
| 单元 7.2 的"工具看不见语义" | 与第 15 次课形成对照：**注入和 XSS 恰恰是工具看得见的**，所以它们有扫描器、有自动防护；而 IDOR 没有。**这个对比能帮学生理解"为什么有些漏洞有工具，有些只能靠设计"** |

最后，**第 15 次课交付 M5，是安全两课的合并验收**。今天的作业二（IDOR 红-绿证据）和第 15 次课的攻防三连，应该合并成一份完整的安全加固报告。建议在今天布置作业时就说明这一点，让学生用同一套格式记录。