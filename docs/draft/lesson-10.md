# 第 10 次课教学底稿
## 前端工程化：模块、构建与类型护栏

---

## 〇、给 PPT 制作团队的全局说明

本次课 100 分钟，留 5 分钟缓冲。**本次课要回答一个学生从第 8 次课起就没真正搞懂、却每天都在用的问题：`npm install` 和 `npm run build` 到底干了什么。**

**本次课的核心思想，请让它贯穿始终**：

> **前端没有秘密。**
>
> **凡是进了 `dist/` 的东西，都已经发给了每一个用户。**
>
> **`.gitignore` 保护的是仓库，不是产物。**

这三句要做成一页封面级素材，在单元 5 现场 grep 出密钥的那一刻再打一次。

**本次课有三个高光，按重要性排序**：

1. **在 `dist/` 里 grep 出 API 密钥（单元 5，15 分钟）**。这是现场必做。戏剧性在于：`.env` 在 `.gitignore` 里，AI 还在注释里写了"放在环境变量里更安全"，学生会真心觉得没问题。然后一条 `grep` 把密钥原文打在屏幕上。**这个演示做完必须立刻讲"泄漏之后怎么办"——答案是轮换密钥，不是删代码。**
2. **构建产物解剖 + sourcemap 反查（单元 5.1、6.3）**。把 `dist/` 一个文件一个文件拆开看，说清每个文件为什么存在。sourcemap 反查要现场做：压缩后的 `a(b.c)` 报错，点一下跳回原始 `.tsx` 的第 37 行。
3. **类型检查是 AI 生成代码最便宜的护栏（单元 7，课程主题落点）**。核心不是"类型好"，是**"每单位成本能拦住多少错误"**。必须同时给出类型**抓不到**什么——否则学生会以为有了 TS 就不用测试了。

**第四处值得重点制作的**：单元 4.4"转译与类型检查是分开的"。这解释了一个学生普遍困惑的现象——**编辑器里一片红波浪线，页面却跑得好好的**。讲清它，学生才会理解为什么 `tsc --noEmit` 必须单独进 CI（第 9 次课已经做了，今天补上原理）。

**一个必须守住的边界**：本次课**引入 React 技术栈，但不讲 React**。单元 3.0 只做"读懂模板结构"，组件、状态、渲染机制全部留给第 11 次课。**看到 `useState` 请一句带过，不要展开。**

**若时间不够的压缩顺序**：先压单元 9 的 C 档卡（整体移课后）→ 再压单元 8 的拆包（只给判据，实操移作业）→ 再压单元 3.4 的幻觉依赖（移到作业三）。**单元 4、5、7 不能压缩。**

---

## 一、开场：能跑，和能交付

**约 4 分钟。**

### 1.1 盘点现状

讲：

> 第 8 次课我们做了一个前端，第 9 次课给它加了 `tsc --noEmit` 和契约一致性检查，两条都进了 CI。
>
> 它能跑，能测，CI 是绿的。
>
> **但有一串问题，我们从来没问过：**

**醒目页**：

| 你每天在用 | 你能回答吗 |
|---|---|
| `npm install` | 它到底装了什么？**装了多少个包？** |
| `package.json` 里的 `^1.2.3` | 这个 `^` 是什么意思？**明天再装一次，版本会一样吗？** |
| `npm run dev` | 浏览器为什么能直接跑 `.tsx`？ |
| `npm run build` | 它产出的那些 `index-a3f9c2.js` 是什么？**为什么文件名里有一串乱码？** |
| `.env` 里的配置 | **它去哪了？** |
| 编辑器里的红波浪线 | **为什么红着还能跑？** |

> 这些问题有一个共同点：**不知道答案也能开发**。所以大部分人一直没问。
>
> 直到某一天出事——密钥泄漏、线上报错看不懂、CI 和本地装出了不同的版本、首屏加载 3 秒。
>
> **今天把这个黑盒拆开。**

### 1.2 一句话定位

> 第 8 次课解决的是"前后端怎么对话"，第 9 次课解决的是"怎么保证它不坏"。
>
> **今天解决的是"这堆代码怎么变成用户真正下载到的那几个文件"。**
>
> 这个过程叫**构建**。它不是魔法，是一条你可以完整拆开的管道。

### 1.3 本次课要回答的问题

- 浏览器为什么不能直接跑我写的代码？**具体卡在哪一步？**
- `npm install` 两次，装出来的东西一样吗？**怎么保证一样？**
- Vite 在 dev 和 build 时做的是**同一件事吗**？
- 前端的 `.env` 能放密钥吗？**为什么不能？已经放了怎么办？**
- 类型错了为什么还能跑？**那 `tsc` 有什么用？**
- 为什么文件名里要带 hash？
- **AI 推荐的依赖，我该不该装？怎么判断？**

---

## 二、解剖台：AI 给的前端工程

**约 12 分钟。四个演示都要做。**

### 情境设定

> 你对 AI 说："帮我把前端改成 React，用 TypeScript，另外我要接一个第三方的地图服务和一个搜索框。"
>
> 它给了你一套完整的工程配置。`npm install`，`npm run dev`，能跑。
>
> **而且它还很贴心地告诉你：密钥已经放进 `.env` 了，`.env` 也加进 `.gitignore` 了，很安全。**

### 代码（tag: `v10-broken`）

```jsonc
// package.json —— AI 原样产出
{
  "name": "web",
  "scripts": {
    "dev": "vite",
    "build": "vite build",              // ← 注意这里
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "lodash": "^4.17.21",               // ← 只用了一个 debounce
    "moment": "^2.30.1",                // ← 只用来格式化一个日期
    "axios": "^1.7.2",                  // ← fetch 明明够用
    "react-map-widgets": "^2.1.0"       // ← 这个包存在吗？
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "vite": "^5.3.0",
    "@vitejs/plugin-react": "^4.3.0"
  }
}
```

```bash
# .gitignore
node_modules
dist
.env
package-lock.json          # ← AI 加的，"避免冲突"
```

```bash
# .env —— AI 的注释原样保留
# 把密钥放在环境变量里，不要硬编码在代码中，这样更安全
VITE_API_BASE=http://localhost:8000
VITE_MAP_API_KEY=sk-live-8f2a91c4e7b3d6a0
VITE_SEARCH_SECRET=srch_prod_11f9c0de4a
```

```tsx
// src/lib/format.ts
import _ from 'lodash';                    // ← 整包引入
import moment from 'moment';

export const debouncedSearch = _.debounce(doSearch, 300);
export const fmt = (d: string) => moment(d).format('YYYY-MM-DD');
```

先让学生看 40 秒，问：**你看得出几个问题？**

学生通常能指出 `lodash`，很少有人指出 `.env`——**因为 AI 那句注释太有说服力了**。

### 演示一：`.gitignore` 了，但没保护到

```bash
npm run build
grep -r "sk-live" dist/
```

```
dist/assets/index-a3f9c21b.js:  ...,MAP_KEY:"sk-live-8f2a91c4e7b3d6a0",...
```

**停下来，让它停留 10 秒。**

> **密钥在这里。这个文件会被发给每一个打开你网站的人。**
>
> AI 说的"放进 `.env` 更安全"——**这句话本身没错，但它只对后端成立。**
>
> 对前端，`.env` 只是一个**构建时的输入**。构建完，它的值就被写死进 JS 文件里了。
>
> **`.gitignore` 保护的是"代码仓库"。它管不了"构建产物"。**
>
> 这两件事之间隔着一整条构建管道，而 AI 把它们混为一谈了。

单元 5 会完整展开这件事，**现在只留一个问题**：

> 你的 `.env` 里，有几个值是真的秘密？

### 演示二：一个 `debounce` 换来多少字节

```bash
npx vite build
```

```
dist/assets/index-a3f9c21b.js   412.7 kB │ gzip: 131.2 kB
```

现在改两行：

```diff
- import _ from 'lodash';
- export const debouncedSearch = _.debounce(doSearch, 300);
+ import debounce from 'lodash-es/debounce';
+ export const debouncedSearch = debounce(doSearch, 300);

- import moment from 'moment';
- export const fmt = (d: string) => moment(d).format('YYYY-MM-DD');
+ export const fmt = (d: string) =>
+   new Intl.DateTimeFormat('sv-SE').format(new Date(d));   // 原生，0 字节
```

```
dist/assets/index-7c04e8d9.js   198.3 kB │ gzip:  64.8 kB
```

〔制作团队：以上数字为示例量级，**以课件实测截图为准**。关键是两次的对比，不是绝对值。〕

**醒目页**：

| | 改之前 | 改之后 |
|---|---|---|
| 产物（gzip） | 131 kB | **65 kB** |
| 实际用到的功能 | 一个 `debounce` + 一个日期格式化 | 一样 |
| 3G 网络首屏多等 | ~0.9 s | — |

> **两行 import，占了一半的包体。**
>
> 为什么？两个原因：
>
> 1. **`import _ from 'lodash'` 把整个 lodash 拉进来了。** lodash 的主包是 CommonJS 格式，打包器**没法安全地做 tree-shaking**（原因单元 3 会讲）——它不知道你只用了 `debounce`。
> 2. **`moment` 默认带全部 locale**，而且它整个库的设计是"一个大对象"，同样摇不掉。
>
> 判据：**装一个包之前，先问"标准库有没有"。** `Intl.DateTimeFormat` 是浏览器内置的，0 字节。
>
> 这条判据在 AI 时代特别重要——**AI 倾向于推荐它见过最多的库，而不是最合适的方案。** `moment` 在训练数据里出现了几百万次，尽管它官方已经宣布进入维护模式多年。

### 演示三：两个人装出了不同的东西

```bash
# 同学 A，今天装
npm install
node -e "console.log(require('react-dom/package.json').version)"
# 18.3.1

# 同学 B，两周后装
npm install
# 18.3.7
```

> `package.json` 里写的是 `^18.3.1`。这个 `^` 的意思是"**18.x.x 里任何比 18.3.1 新的版本都行**"。
>
> 所以两个人、两台机器、两个时间点，装出来的**不是同一套代码**。
>
> **而 AI 把 `package-lock.json` 加进了 `.gitignore`。**
>
> 那个文件的作用就是锁住"实际装的是哪个精确版本"。删掉它，等于宣布："我们不在乎每次装的是不是同一个东西。"

后果演示——**第 9 次课那句话的前端版本**：

```
本地：npm run build 成功
CI：  npm install && npm run build
      → TypeError: xxx is not a function
```

> **"在我机器上是好的"，这就是它最常见的来源之一。**
>
> 而且注意这个问题的性质：**它不是"某次装错了"，是"根本没有'装对'这个概念"。** 每次安装都是一次新的解析。

### 演示四：那个包存在吗

```bash
npm view react-map-widgets
```

```
npm ERR! 404 Not Found - GET https://registry.npmjs.org/react-map-widgets
npm ERR! 404 '"react-map-widgets@*" is not in this registry.'
```

> **AI 编了一个包名。**
>
> 这不是笔误，是**幻觉**：它见过 `react-map-gl`、`react-leaflet`、`@vis.gl/react-google-maps`，于是合成了一个听起来非常合理的名字。
>
> 这类错误的性质和第 6 次课那个"漏了业务约束"、第 8 次课那个"猜字段名"是同一类——**AI 在需要外部事实的地方会自信地编造**。
>
> 但今天这一类有一个**前两类没有的性质**：
>
> **它可以被攻击者利用。**
>
> 单元 3.4 会展开。现在只记一句：**AI 推荐的每一个包名，装之前都要验证它真的存在、并且是你以为的那个包。**

### 四个问题的性质对照（**做成一页**）

| # | 问题 | 什么时候暴露 | 谁付代价 |
|---|---|---|---|
| ① | 密钥进产物 | **可能永远不暴露**，直到被人用掉 | 你（账单 / 数据） |
| ② | 依赖膨胀 | 用户等首屏时 | 用户 |
| ③ | 没有 lockfile | CI 挂 / 线上莫名其妙 | 团队 |
| ④ | 幻觉依赖 | `npm install` 失败——**或者更糟：成功了** | 见单元 3.4 |

> 注意 ① 和 ④ 的共同点：**它们最好的结局是立刻失败。**
>
> ④ 报 404，你立刻知道有问题，这是好事。**真正危险的是它装成功了**——那说明有人抢注了这个名字。

### 欠账清单

| 问题 | 本次课处理 | 何时还 |
|---|---|---|
| 密钥进产物 | **单元 5** | — |
| 依赖膨胀 / tree-shaking 失效 | 单元 3.2、**单元 8** | — |
| 没有 lockfile | **单元 3.3** | — |
| 幻觉依赖与供应链 | **单元 3.4** | — |
| `build` 脚本没串 `tsc` | **单元 4.4** | — |
| 为什么必须构建 | **单元 4** | — |
| 产物文件名的 hash | **单元 6** | — |
| 生产环境的跨域（proxy 只在 dev 有） | 单元 4.3 指出 | **第 12 次课** |
| 静态产物怎么部署、缓存头怎么配 | 单元 6.2 给判据 | **第 16 次课** |
| React 本身 | **不讲** | **第 11 次课** |
| 依赖漏洞扫描进 CI | 单元 3.5 记一笔 | 作业二 |

---

## 三、模块与依赖：`npm install` 到底做了什么

**约 13 分钟。**

### 3.0 一个技术栈决定：换到 React 模板

**先花 90 秒交代清楚，避免学生困惑。**

> 第 8 次课我明确说过：**不用框架，因为那节课的主题是契约，框架会把契约问题藏起来。**
>
> 现在契约有了（`api.d.ts`），测试有了，CI 有了。**地基打好了，可以上框架了。**
>
> 今天把 `web/` 换成 Vite 的 **React + TS** 模板。但要说清楚**今天换的是什么、不换什么**：

| 层 | 今天 | 说明 |
|---|---|---|
| `src/api.d.ts` | **完全不动** | 生成的契约，与框架无关 |
| `src/client.ts` | **完全不动** | `openapi-fetch` 封装 |
| 页面逻辑 | 暂时照搬，用 React 当壳 | **组件化是第 11 次课的作业** |
| 工程配置 | **全部重做** | 这是今天的主题 |

> 这个安排本身就是一个判据：
>
> **换框架时，先确认"哪些东西不该跟着换"。** 契约层、数据获取层、类型定义，都应该独立于 UI 框架。
>
> 如果你换个框架要把 `api.d.ts` 重写一遍，**说明你的契约和框架耦合了。**

**模板结构，逐个说明（不要跳过，学生真的不知道每个文件干什么）**：

```
web/
├── index.html              ← 入口。注意：它在项目根目录，不在 public/
├── package.json            ← 依赖清单 + 脚本
├── package-lock.json       ← 锁定实际版本（必须提交！）
├── tsconfig.json           ← 类型检查配置
├── vite.config.ts          ← 构建配置
├── .env / .env.local ...   ← 环境变量（单元 5）
├── public/                 ← 原样拷贝到 dist/，不经过构建
├── src/
│   ├── main.tsx            ← JS 入口，被 index.html 引用
│   ├── App.tsx
│   ├── api.d.ts            ← 生成物（第 8 次课）
│   └── client.ts
└── dist/                   ← 构建产物（单元 5）
```

> 两处容易混淆的：
>
> - **`index.html` 在根目录，不在 `src/`**。这是 Vite 的设计：HTML 是构建的入口，不是一个"静态资源"。
> - **`public/` 里的东西不经过构建**，原样拷到 `dist/`。放 `favicon.ico`、`robots.txt` 这类东西。**不要往里放需要处理的资源。**

### 3.1 ESM：`import` 是什么

**先给最小集，够用即可**：

```ts
// 命名导出 / 导入
export function formatDate(d: string) { ... }
export const MAX = 100;
import { formatDate, MAX } from './lib/format';

// 默认导出 / 导入
export default function App() { ... }
import App from './App';

// 重导出（做"桶文件"）
export * from './format';
```

**要讲的两个性质（醒目页）**：

> **一、ESM 是静态的。**
>
> `import` 必须写在模块顶层，路径必须是字符串字面量，**不能是变量**。
>
> ```ts
> import x from './a';           // ✅
> if (cond) import x from './a'; // ❌ 语法错误
> import x from someVar;         // ❌ 语法错误
> ```
>
> 这个限制看起来很烦，但它带来一个关键能力：**打包器不运行你的代码，光靠读就能知道谁依赖谁、谁用了什么**。
>
> **Tree-shaking 就建立在这个性质上**——能静态分析出"这个导出没人用"，才能删掉它。
>
> 这解释了演示二：**lodash 的主包是 CommonJS**（`require` + `module.exports`），`require` 可以写在任何地方、路径可以是变量、导出可以运行时动态添加——**静态分析不了，所以摇不掉。**
>
> | | ESM | CommonJS |
> |---|---|---|
> | 语法 | `import` / `export` | `require` / `module.exports` |
> | 何时确定依赖 | **静态，读代码就知道** | 运行时 |
> | 能 tree-shake 吗 | **✅** | ❌ |
> | 浏览器原生支持 | ✅ | ❌ |
>
> 判据：**选包时优先选提供 ESM 版本的。** `lodash` vs `lodash-es`，差别就在这里。
>
> **二、动态 `import()` 是例外，而且是故意的。**
>
> ```ts
> const mod = await import('./heavy-chart');   // 返回 Promise
> ```
>
> 这是唯一允许运行时决定的导入方式，**它是代码拆分的基础**（单元 8）。

### 3.2 裸说明符：浏览器卡在哪

**现场演示。这是"为什么必须构建"最直观的证据。**

写一个最小的 HTML，不用任何构建工具，直接用浏览器打开：

```html
<script type="module">
  import React from 'react';
  console.log(React);
</script>
```

```
Uncaught TypeError: Failed to resolve module specifier "react".
Relative references must start with either "/", "./", or "../".
```

**醒目页**：

> **浏览器只认三种模块路径：**
>
> | 形式 | 例子 | 浏览器认吗 |
> |---|---|---|
> | 相对路径 | `./lib/format.js` | ✅ |
> | 绝对路径 | `/src/main.js` | ✅ |
> | 完整 URL | `https://esm.sh/react` | ✅ |
> | **裸说明符** | **`react`、`lodash`** | ❌ |
>
> `import React from 'react'` 里的 `react` 叫**裸说明符（bare specifier）**。
>
> **浏览器不知道去哪找它。** 它没有 `node_modules` 的概念——那是 Node.js 的模块解析规则，浏览器从来没实现过。
>
> 判据：**Node 的模块解析规则和浏览器的模块解析规则，从一开始就是两套东西。** 构建工具的第一个职责，就是把前者翻译成后者。

〔补一句：`<script type="importmap">` 可以让浏览器认识裸说明符。但它要你手工维护每个包的 URL、处理不了传递依赖、也解决不了后面两个问题。**知道它存在即可。**〕

### 3.3 semver 与 lockfile

**版本号的三段式**：

```
    18  .  3  .  1
    ↑      ↑     ↑
  major  minor  patch
 破坏性   加功能   修 bug
  变更   向后兼容  向后兼容
```

**范围写法（醒目页，学生天天看见但没人讲过）**：

| 写法 | 含义 | 会装到 |
|---|---|---|
| `18.3.1` | 精确 | 只有 18.3.1 |
| `~18.3.1` | 允许 patch | 18.3.1 ~ 18.3.x |
| **`^18.3.1`** | **允许 minor + patch**（默认） | **18.3.1 ~ 18.x.x** |
| `*` / `latest` | 任意 | **不要用** |

> 注意 `^` 是 `npm install` 的**默认行为**。所以你的 `package.json` 里几乎全是 `^`。
>
> 它的前提是：**包作者严格遵守 semver**。
>
> 而这个前提**经常不成立**——一个"修 bug"的 patch 版本改掉了某个边界行为，你的代码就坏了。这不是理论，是每个前端团队都遇到过的事。

**lockfile 解决什么（醒目页）**：

```jsonc
// package-lock.json 片段
"node_modules/react-dom": {
  "version": "18.3.1",                                  // ← 精确版本
  "resolved": "https://registry.npmjs.org/react-dom/-/react-dom-18.3.1.tgz",
  "integrity": "sha512-5m4nQKp+rZRb09LNH59GM4BxTh9251/ylbKIbpe7TpGxfJ+9kv6BLkLBXIjjspbgbnIBNqlI23tRnTWT0snUIw==",
                                                        // ↑ 内容哈希
  "dependencies": { "scheduler": "^0.23.2" }            // ← 传递依赖也锁
}
```

| `package.json` | `package-lock.json` |
|---|---|
| 我**想要**什么（范围） | 我**实际装了**什么（精确） |
| 人写的 | 工具生成的 |
| 几十行 | 几千行 |
| **必须提交** | **必须提交** |

> `integrity` 那个哈希还有第二个作用：**校验下载的包内容没被篡改**。如果 registry 上的某个版本被人替换了，安装会直接失败。
>
> **判据：lockfile 必须提交。任何"避免冲突"的理由都不成立。**
>
> lockfile 冲突确实烦人，但解法是"删掉重新生成一次"，不是"不提交"。

**`npm ci` vs `npm install`（第 9 次课 CI 里那一行，今天讲清楚）**：

| | `npm install` | `npm ci` |
|---|---|---|
| 依据 | `package.json`，**可能更新 lockfile** | **严格按 lockfile** |
| lockfile 与 package.json 不一致时 | 更新 lockfile | **直接报错退出** |
| 现有 `node_modules` | 增量更新 | **先删光再装** |
| 速度 | 较慢 | 快 |
| 用在哪 | 本地开发、加新依赖 | **CI、构建机、Docker** |

> 第 9 次课的 CI 里我写的是 `npm ci`，当时没解释。**现在解释了：它保证 CI 装的和你本地装的是同一套字节。**
>
> 而且它还顺手做了一条检查：**如果有人改了 `package.json` 却忘了更新 lockfile，`npm ci` 会直接失败。**
>
> 这是第 9 次课那条判据的又一个实例：**能让工具报错的地方，不要靠人对账。**

### 3.4 幻觉依赖与供应链（**本单元最需要认真讲的一段**）

回到演示四。

> `react-map-widgets` 报了 404。**你运气好。**
>
> 现在设想另一种情况：**它装成功了。**

**醒目页**：

> **攻击链：**
>
> ```
> 1. 攻击者反复向各种 LLM 提问，收集它们编造出来的包名
> 2. 挑那些高频出现的，在 npm / PyPI 上注册同名包
> 3. 包里放一段 postinstall 脚本：读 ~/.ssh、读 .env、读 CI 的环境变量，发走
> 4. 等着。等某个开发者照着 AI 的建议 npm install
> ```
>
> 这类攻击有个名字：**slopsquatting**——类比 typosquatting（抢注拼写错误的域名/包名），只不过这次抢注的不是"人会打错的名字"，是"**AI 会编出来的名字**"。

**为什么这比 typosquatting 更危险，三条**：

| | typosquatting | slopsquatting |
|---|---|---|
| 触发条件 | 人手滑打错 | **AI 稳定地推荐同一个错名** |
| 出现频率 | 随机、低 | **可预测、可批量收集** |
| 人的警觉度 | "我是不是打错了" | **"AI 说的，应该对吧"** |

> 第三行是关键：**这个名字是"被推荐"的，不是"打错"的。人对推荐的警惕性远低于对自己失误的警惕性。**

**关于比例（请谨慎表述）**：

> 已有公开研究统计过 LLM 生成代码中包名幻觉的比例。**不同模型、不同语言差异很大**——商业模型大致在个位数百分比，开源模型明显更高。
>
> **我不打算给你一个精确数字，因为它每个月都在变。**
>
> 你要记住的是**方法，不是数字**：

**依赖评估清单（醒目页，这是学生今天能直接带走的东西）**：

| # | 检查项 | 怎么查 | 红线 |
|---|---|---|---|
| 1 | **它存在吗** | `npm view <name>` | 404 → **停** |
| 2 | 是不是你以为的那个包 | 看 repository 字段、README | 对不上 → 停 |
| 3 | 周下载量 | `npm view <name> ` / npm 页面 | 极低且很新 → **高度警惕** |
| 4 | 最后发布时间 | `npm view <name> time.modified` | 三年没更新 → 评估 |
| 5 | 有没有 `postinstall` 脚本 | `npm view <name> scripts` | 有 → 看清楚它干什么 |
| 6 | 传递依赖有多少 | `npm ls <name>` | 一个工具函数带来 40 个包 → 重新考虑 |
| 7 | 体积 | bundlephobia / 构建前后对比 | 见单元 8 |
| 8 | **标准库 / 已有依赖能做吗** | 想一下 | 能 → **不装** |
| 9 | license | `npm view <name> license` | 不兼容 → 停 |

> 第 1 条和第 8 条是**每次都要做的**，其余按风险取舍。
>
> **判据：AI 推荐依赖时，它在做一件它不擅长的事——它在陈述外部事实。**
>
> 回到第 6 次课那条判断：**AI 在"需要它不掌握的信息"的地方会自信地编造。** 第 6 次课是业务约束，第 8 次课是你的字段名，**今天是 npm registry 的真实内容**。
>
> 三次的共同结构：**它给出的是"听起来最合理的东西"，不是"真实存在的东西"。**

### 3.5 一条新纪律，一条新检查

**兑现第 9 次课的固定动作。**

```python
# tests/test_conventions.py —— 后端仓库里也能查前端
def test_lockfile_committed():
    assert Path("web/package-lock.json").exists(), "lockfile 必须提交"

def test_gitignore_does_not_exclude_lockfile():
    ignore = Path("web/.gitignore").read_text()
    assert "package-lock.json" not in ignore
```

```yaml
# CI 里加两步
- run: cd web && npm ci            # 不是 npm install
- run: cd web && npm audit --audit-level=high
```

> `npm audit` 比对你的依赖树和已知漏洞库。**它有噪音**（很多漏洞在你的使用场景下不可达），所以设 `--audit-level=high`，不要一有 low 就红。
>
> **回收第 9 次课的判据：宁可少几条检查，也不要有一条会误报的检查。** audit 的默认级别误报太多，会训练人忽略它。

### 材料

- **高光图**：3.1 的 ESM vs CommonJS 四行对照表。
- **封面级素材**：3.2 的"浏览器只认三种路径"表 + 裸说明符报错截图。
- **封面级素材**：3.3 的 `package.json` vs `package-lock.json` 对照、`npm ci` vs `npm install` 五行表。
- **封面级素材**：3.4 的 slopsquatting 攻击链四步图。
- **高光图**：3.4 的依赖评估九条清单（**这是最可能被学生截图带走的一页**）。
- 截图：`npm view react-map-widgets` 的 404。
- 截图：两次 `npm install` 装出不同版本。
- tag `v10-deps`（本单元结束：lockfile 提交、多余依赖清掉）。

---

## 四、为什么必须构建；Vite 的两条链路

**约 13 分钟。**

### 4.1 三个理由，一个都绕不过

**醒目页**：

| # | 浏览器做不到的 | 具体表现 |
|---|---|---|
| 1 | **解析裸说明符** | `import React from 'react'` → 报错（单元 3.2 已演示） |
| 2 | **认识 TS / JSX** | `.tsx` 里的类型标注和 `<div>` 语法，浏览器一律语法错误 |
| 3 | **接受几百个请求** | 一个中等项目几百个模块，每个一次请求 |

**第 3 条现场演示（dev 模式）**：

```bash
npm run dev
```

打开 Network 面板，刷新：

```
请求数：217
```

> 每个 `.tsx`、每个 `.ts`、每个 CSS，**都是一次独立的 HTTP 请求**。
>
> 在本地这没问题——localhost 没有网络延迟。
>
> **但如果生产也这样**：217 个请求，每个 RTT 50ms，**即使完全并行，浏览器也有并发上限**。首屏会灾难性地慢。
>
> 这正是第 8 次课前端 N+1 那条判据的放大版：**"请求数"是前端最重要的性能指标。**

**再补两条次要但真实的理由**：

| # | 理由 |
|---|---|
| 4 | **语法降级**：你写的 `??`、`?.`、`class fields`，老浏览器不认 |
| 5 | **资源处理**：CSS 要提取、图片要压缩、小文件要内联 |

### 4.2 Vite 的两条链路（**本单元核心，醒目页**）

> **Vite 在 `dev` 和 `build` 时，做的是完全不同的两件事。**
>
> 这不是实现细节，**它会直接影响你的日常**——后面会看到三个具体后果。

| | `npm run dev` | `npm run build` |
|---|---|---|
| **业务代码** | **不打包**，浏览器原生 ESM 逐个加载 | **打包**（Rollup） |
| **第三方依赖** | 预构建一次（esbuild），转成 ESM 并合并 | 一起打包 |
| **转译** | 按需，浏览器请求哪个文件才转哪个 | 全量 |
| **请求数** | 几百个 | **几个** |
| **谁在服务** | Vite dev server | **没有服务器**，就是静态文件 |
| **proxy** | ✅ 有 | ❌ **没有** |
| **改一行代码** | HMR，**毫秒级** | 重新构建全部 |
| **速度来源** | 不打包 | 打包 |

**为什么这么设计（一句话）**：

> **开发时你在乎"改完多久能看到"，生产时你在乎"用户多久能看到"。这是两个不同的优化目标，所以用两套机制。**
>
> 这个取舍本身值得记住：**开发体验和生产性能经常是矛盾的。承认矛盾、分开优化，比强求一致好。**

### 4.3 双链路的三个实际后果

**这一节比原理更重要，请完整讲。**

**后果一：dev 好好的，build 挂了。**

> 常见原因：
> - 文件名大小写（macOS 不区分，Linux 构建机区分）
> - 只在 dev 下被 Vite 容忍的写法（比如某些 CJS/ESM 互操作）
> - 环境变量在两个模式下取值不同
>
> 判据：**`npm run build` 必须在 CI 里跑，不能只在发布前跑一次。**
> 〔第 9 次课的 CI 里已经有 `npm run check`，**今天要加 `npm run build`。**〕

**后果二：proxy 在生产不存在。**

**回收第 8 次课的欠账**：

> 第 8 次课我们用 `vite.config.ts` 里的 proxy 绕过了 CORS，当时我说"这只在开发期有效"。
>
> **现在你知道为什么了：proxy 是 dev server 的功能。`build` 之后只有静态文件，没有任何东西在转发请求。**
>
> ```
> dev:    浏览器 → Vite dev server（转发）→ 后端
> build:  浏览器 → ??? → 后端
> ```
>
> 生产环境那个 `???` 必须由别的东西填上：nginx 反向代理、或者后端开 CORS。
>
> **→ 第 12 次课正面处理。** 今天只是把"为什么"补齐。

**后果三：`vite preview` 的作用。**

```bash
npm run build && npm run preview
```

> 它起一个**最简单的静态服务器**来伺服 `dist/`。
>
> **判据：提交前至少跑一次 `preview`，它跑的是真正要上线的产物。**
>
> 注意 `preview` 也有 proxy 配置，但**生产的 nginx 没有**——所以 preview 通过不代表生产没问题。它只解决后果一，不解决后果二。

### 4.4 转译与类型检查是分开的（**回答"为什么红着还能跑"**）

**现场演示**：

```ts
// src/main.tsx
const count: number = "hello";        // ← 编辑器立刻红
```

```bash
npm run dev
# ✅ 启动成功，页面正常渲染
```

```bash
npm run build          # AI 给的脚本："build": "vite build"
# ✅ 构建成功！
```

**停下来。**

> **类型错误，dev 能跑，build 也能过。那 TypeScript 有什么用？**

**醒目页**：

> **Vite 用 esbuild 处理 TS。esbuild 做的事情是：**
>
> ```
> 删掉类型标注，剩下的原样输出。
> ```
>
> **它不做类型检查。这是故意的。**
>
> | | 转译（esbuild / SWC） | 类型检查（tsc） |
> |---|---|---|
> | 做什么 | 删类型、转语法 | 推导类型、比对、报错 |
> | 需要看几个文件 | **一个**（逐文件独立） | **全部**（跨文件推导） |
> | 速度 | **毫秒级** | 秒级到分钟级 |
> | 能并行吗 | ✅ 完全并行 | 受限 |
>
> **esbuild 快 10-100 倍的秘密，就在"只看一个文件"。** 而类型检查的本质要求就是看全部文件。
>
> 所以这是一个**无法调和的取舍**，工具链的选择是：**分开做**。

**于是 `tsc --noEmit` 这个命令的含义就清楚了**：

```
tsc --noEmit
     ↑
  只检查，不产出文件（产出交给 esbuild）
```

> 第 9 次课我把它写进了 CI，当时只说"零错误"。**今天知道了：如果不单独跑它，类型错误会一路进生产。**

**修 `package.json`**：

```diff
-  "build": "vite build",
+  "build": "tsc -b && vite build",
+  "check": "tsc --noEmit",
```

再构建一次：

```
src/main.tsx:3:7 - error TS2322: Type 'string' is not assignable to type 'number'.
```

**加一条检查（第 9 次课固定动作）**：

```python
def test_build_script_runs_typecheck():
    pkg = json.loads(Path("web/package.json").read_text())
    build = pkg["scripts"]["build"]
    assert "tsc" in build, "build 脚本必须先做类型检查"
```

> **判据：凡是"能跳过的检查"，最终都会被跳过。** 把它串进 `build`，就跳不过了。

### 材料

- **封面级素材**：4.2 的双链路八行对照表。
- **封面级素材**：4.4 的"转译 vs 类型检查"四行表 + "esbuild 快的秘密"。
- **高光图**：4.1 的三个理由。
- **高光图**：4.3 的三个实际后果（proxy 那条要配 dev/build 两条链路的示意图）。
- 截图：dev 模式 Network 面板 217 个请求的瀑布图。
- 截图：类型错误下 `npm run dev` 正常启动、页面正常渲染（**两者同屏**）。
- 截图：改完 build 脚本后构建失败的输出。
- tag `v10-build`（本单元结束）。

---

## 五、现场必做：拆开 `dist/`，grep 出密钥

**约 15 分钟。本次课最高光。**

### 5.1 第一步：把 `dist/` 一个文件一个文件看清楚

```bash
npm run build
tree dist/
```

```
dist/
├── index.html                      1.2 kB
├── favicon.ico                     4.3 kB      ← 从 public/ 原样拷来
└── assets/
    ├── index-a3f9c21b.js         198.3 kB      ← 你的代码 + 依赖
    ├── index-a3f9c21b.js.map     742.1 kB      ← sourcemap
    ├── vendor-7e4d0b18.js        142.7 kB      ← 第三方库（若配了拆分）
    └── index-5c81f0a2.css         12.4 kB      ← 提取出来的样式
```

**逐个讲（学生第一次看见这个目录，不要跳过任何一个）**：

```bash
cat dist/index.html
```

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <script type="module" crossorigin src="/assets/index-a3f9c21b.js"></script>
    <link rel="stylesheet" crossorigin href="/assets/index-5c81f0a2.css">
  </head>
  <body><div id="root"></div></body>
</html>
```

| 文件 | 它是什么 | 注意 |
|---|---|---|
| `index.html` | **唯一的入口**。源码里的 `<script src="/src/main.tsx">` 被改写成了打包产物的路径 | 只有 1.2 kB，**里面没有内容**——内容由 JS 渲染（这就是 CSR） |
| `assets/index-*.js` | 你的代码 + 依赖，压缩、混淆、合并后的结果 | 文件名里的 `a3f9c21b` 见单元 6 |
| `assets/*.css` | 从 `.tsx` 里 `import './x.css'` 提取出来的 | 构建时提取，不是运行时插入 |
| `*.js.map` | sourcemap，见单元 6.3 | **体积经常比 JS 还大** |
| `favicon.ico` | `public/` 里原样拷贝 | 不经过构建 |

**打开 JS 看一眼**：

```bash
head -c 300 dist/assets/index-a3f9c21b.js
```

```javascript
function Rr(e,t){for(var n=0;n<t.length;n++){const r=t[n];...
```

> **变量名全没了，换行全没了。** 这是压缩（minify）。
>
> 它的目的只有一个：**减少字节数**。
>
> 请注意：**这不是加密，也不是保护。** 代码的逻辑完整地在这里，任何人都能读——只是读起来费劲。下一步你就会看到，费劲不等于安全。

### 5.2 第二步：grep（**关键时刻**）

**先建立预期，再打脸。**

问学生：

> `.env` 在 `.gitignore` 里。密钥没有进 Git。
>
> **那它在 `dist/` 里吗？举手投票。**

然后：

```bash
grep -o "sk-live-[a-z0-9]*" dist/assets/*.js
```

```
sk-live-8f2a91c4e7b3d6a0
```

```bash
grep -o "srch_prod_[a-z0-9]*" dist/assets/*.js
```

```
srch_prod_11f9c0de4a
```

**再打开浏览器实证一次**（这一步不能省——终端 grep 学生可能觉得"那是你本机的文件"）：

1. `npm run preview`
2. 打开页面 → DevTools → Sources → `assets/index-a3f9c21b.js`
3. `Ctrl+F` 搜 `sk-live`
4. **在浏览器里，密钥原文出现在屏幕上**

**封面级素材，这一刻打出来**：

> **前端没有秘密。**
>
> **凡是进了 `dist/` 的东西，都已经发给了每一个用户。**
>
> **`.gitignore` 保护的是仓库，不是产物。**

### 5.3 为什么会这样：构建时注入

**看构建前后的同一行代码**：

```ts
// 源码
const key = import.meta.env.VITE_MAP_API_KEY;
```

```javascript
// dist 里
const key = "sk-live-8f2a91c4e7b3d6a0";
```

**醒目页**：

> **`import.meta.env.VITE_X` 不是一次"读取"，是一次"替换"。**
>
> 构建时，Vite 在你的源码里做**文本替换**，把 `import.meta.env.VITE_MAP_API_KEY` 整个换成那个字符串字面量。
>
> 换完之后，**代码里根本不存在"环境变量"这个概念了**——只剩一个写死的字符串。
>
> 这和后端完全不同：
>
> | | 后端 `os.environ["KEY"]` | 前端 `import.meta.env.VITE_KEY` |
> |---|---|---|
> | 什么时候取值 | **运行时**，在你的服务器上 | **构建时**，在构建机上 |
> | 值存在哪 | 服务器的进程环境里 | **产物文件里** |
> | 谁能看到 | 能登上服务器的人 | **所有访问者** |
> | 换个环境要不要重新构建 | ❌ 不用 | ✅ **必须重新构建** |
>
> 最后一行有个很实际的后果：**"一次构建，到处部署"这个发布原则，在前端 env 上不成立。**
> **→ 第 16 次课回到这个问题。**

**另外说清 Vite 的 `VITE_` 前缀规则**：

```bash
VITE_API_BASE=http://localhost:8000      # ✅ 会被注入
DATABASE_URL=postgres://...              # ❌ 不会被注入
```

> Vite **只注入 `VITE_` 开头的变量**。这是一道防呆设计：防止你把整个 shell 环境（里面可能有真正的密钥）打包进去。
>
> **但它只防呆，不防错。** 你给密钥加个 `VITE_` 前缀，它照样进产物。
>
> 判据：**`VITE_` 这个前缀应该读作"我确认这个值是公开的"。** 每次给一个变量加这个前缀，就是在做这个声明。

### 5.4 那什么可以放，什么不可以

**醒目页，这是学生最需要的实操判据**：

> **一句话判据：把它打印在页面上，你能接受吗？**

| 可以放前端 env | 不可以 |
|---|---|
| API base URL | 任何 secret / private key |
| Sentry DSN（**设计上就是公开的**） | 数据库连接串 |
| Google Analytics ID | 第三方服务的 **server key** |
| 公钥 | JWT 签名密钥 |
| feature flag | 管理员密码、内部端点 |
| 应用版本号、构建时间 | 任何"如果泄漏要轮换"的东西 |

**但必须讲清一个反向的误区（否则学生会走极端）**：

> **有一类 key 是设计上就允许公开的，别把它们当成泄漏。**
>
> | 例子 | 为什么能公开 |
> |---|---|
> | Stripe **publishable** key (`pk_...`) | 它只能发起支付意图，不能查账、不能退款 |
> | Firebase `apiKey` | 它只是项目标识；安全靠 Security Rules 和域名白名单 |
> | Sentry DSN | 只能写入错误，不能读取 |
>
> 它们的共同点：**权限被设计得极小，并且有第二道机制（域名白名单 / 服务端规则）兜底。**
>
> 判据：**看 key 的名字**——`publishable` / `public` / `client` 通常可公开，`secret` / `private` / `server` 绝对不行。**拿不准就去读那个服务的文档，不要问 AI。**

### 5.5 那前端真的需要调第三方，怎么办

**三种正确做法（醒目页）**：

| 做法 | 怎么做 | 适合 |
|---|---|---|
| **① 后端代理**（首选） | 前端调 `/api/map/search`，后端带着密钥去调第三方 | 绝大多数情况 |
| **② 短期凭证** | 后端用密钥换一个**有限权限、会过期**的 token 给前端 | 大文件直传（S3 预签名）、实时推流 |
| **③ 用公开 key + 服务端规则** | 见 5.4 | 服务本身支持这种模式 |

**改造演示（tag `v10-secure`）**：

```diff
# .env
  VITE_API_BASE=http://localhost:8000
- VITE_MAP_API_KEY=sk-live-8f2a91c4e7b3d6a0
- VITE_SEARCH_SECRET=srch_prod_11f9c0de4a
```

```python
# app/routers/map.py —— 密钥只在后端
@router.get("/map/search", response_model=Page[PlaceOut])
def search_places(q: str = Query(min_length=1, max_length=100)):
    resp = httpx.get(MAP_ENDPOINT,
                     params={"q": q, "key": settings.map_api_key})
    ...
```

**顺手指出方案 ① 的两个额外好处**：

> 1. **你可以在自己的后端加限流**——否则别人拿你的密钥随便刷，账单是你的。
> 2. **你可以缓存**——同样的搜索词不用每次都打第三方。（**→ 第 11 次课**，如果课程安排里有缓存单元）
>
> 判据：**"密钥不能进前端"这条约束，逼出来的架构通常本身就更好。** 这是安全约束的一个常见副作用。

### 5.6 已经泄漏了怎么办（**必讲，不能省**）

**醒目页**：

> **第一反应通常是错的：**
>
> ❌ 从 `.env` 里删掉 → **没用**
> ❌ 重新构建一次 → **没用**
> ❌ `git filter-branch` 清历史 → **没用**（它根本没进 Git）
>
> **唯一有效的动作：去第三方服务的控制台，作废这个密钥，签发新的。**

**为什么删代码没用**：

| 旧产物在哪 | 你能删掉吗 |
|---|---|
| 用户浏览器的缓存里 | ❌ |
| CDN 的边缘节点上 | ❌（而且你给它配了一年的缓存，见单元 6） |
| 别人的抓包记录、爬虫库里 | ❌ |
| 公司内网的镜像、备份里 | ❌ |

> **判据：密钥一旦被构建进产物，就永久地公开了。唯一的补救是轮换。**
>
> 这条判据的推论：**泄漏的严重程度取决于"轮换有多难"。** 一个能一键轮换的密钥，泄漏是个小事故；一个写死在十个系统里、轮换要协调三个团队的密钥，泄漏是个大事故。
>
> **所以：新接一个第三方服务时，先确认"这个密钥怎么轮换"。** 这个问题应该在接入前问，不是在泄漏后问。

### 5.7 把这个 grep 变成检查（**本单元收口，第 9 次课固定动作**）

> 我们刚才用一条 `grep` 发现了密钥。
>
> **那就让 CI 每次都 grep 一遍。**

```python
# scripts/check_dist_secrets.py
import re, sys
from pathlib import Path

PATTERNS = [
    (r"sk-live-[A-Za-z0-9]{8,}",        "疑似 live 密钥"),
    (r"sk_live_[A-Za-z0-9]{8,}",        "疑似 Stripe secret key"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY",  "私钥"),
    (r"AKIA[0-9A-Z]{16}",               "AWS access key"),
    (r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.", "疑似 JWT"),
    (r"postgres(ql)?://[^\s\"']+:[^\s\"']+@", "数据库连接串"),
]

hits = []
for f in Path("web/dist").rglob("*"):
    if f.suffix not in {".js", ".css", ".html", ".map"}:
        continue
    text = f.read_text(errors="ignore")
    for pat, desc in PATTERNS:
        for m in re.finditer(pat, text):
            hits.append(f"{f}: {desc} → {m.group()[:24]}…")

if hits:
    print("构建产物中发现疑似机密：", *hits, sep="\n  ")
    sys.exit(1)
print("产物机密扫描通过")
```

```yaml
- run: cd web && npm ci && npm run build
- run: python scripts/check_dist_secrets.py       # ← 新增
```

**红-绿两步（第 9 次课的方法论，今天继续执行）**：

```
$ python scripts/check_dist_secrets.py
构建产物中发现疑似机密：
  web/dist/assets/index-a3f9c21b.js: 疑似 live 密钥 → sk-live-8f2a91c4e7…
```

修掉密钥，重新构建：

```
产物机密扫描通过
```

**要讲的两点**：

> **一、这条检查有假阳性和假阴性。**
>
> - 假阴性：你的密钥格式不在这个列表里 → **漏掉**
> - 假阳性：某个库里恰好有个字符串长得像 → **误报**
>
> 它**不是一道完备的防线**，是一道**便宜的网**。
>
> 判据（回收第 9 次课 5.6）：**检查的严谨程度要配得上问题的严重程度和检查的成本。** 这条检查 30 行、跑 1 秒，能拦住最常见的那类事故——性价比极高。
>
> 真正完备的方案是专门的 secret scanning 工具（gitleaks、trufflehog）。**知道它们存在，需要时再上。**
>
> **二、这是第八道结构性护栏。**

**封面级素材，累加表，第八行**：

| 次课 | 护栏 | 拦住什么 | 拦截时机 |
|---|---|---|---|
| 第 3 次课 | `response_model` | 字段泄漏 | 运行时 |
| 第 4 次课 | 全局异常处理器 | 内部信息泄漏 | 运行时 |
| 第 5 次课 | Jinja2 自动转义 | 输入变 HTML | 运行时 |
| 第 6 次课 | 数据库约束 | 脏数据写入 | 运行时 |
| 第 7 次课 | `lazy="raise"` | 静默 N+1 | 运行时 |
| 第 8 次课 | 生成的类型 | 字段名写错 | 编译期 |
| 第 9 次课 | CI 检查 | 违反任何约定 | 合并前 |
| **第 10 次课** | **lockfile + `npm ci`** | **"装了什么"不确定** | **安装时** |
| **第 10 次课** | **产物机密扫描** | **密钥随产物发出去** | **构建后** |

> 请注意第八、九道的位置：**它们不在"你写的代码"上，在"你的供应链"和"你的产物"上。**
>
> **判据：护栏要覆盖整条链路，不只是你亲手写的那部分。** 你的代码是对的，但装错了包、或者把密钥打包进去了，一样出事。

### 材料

- **封面级素材**：三句核心话（"前端没有秘密…"），在 grep 出结果那一刻打出。
- **封面级素材**：5.3 的"后端 env vs 前端 env"四行对照表。
- **封面级素材**：5.4 的"能放 / 不能放"两列表 + 公开 key 的反向说明。
- **封面级素材**：5.6 的"删代码没用"四行表 + "唯一有效动作是轮换"。
- **封面级素材**：护栏累加表（八、九两行新增，"安装时/构建后"用新颜色）。
- **录屏（最关键的素材）**：从 `cat .env`（含 AI 那句"更安全"的注释）→ `npm run build` → `grep` 命中 → 浏览器 DevTools 里搜到密钥原文。**一镜到底，不要切。**
- 截图：`tree dist/` 全貌，每个文件配一句注释。
- 截图：`head -c 300` 的压缩代码（说明"不是加密"）。
- 截图：源码 `import.meta.env.VITE_X` 与产物里字符串字面量的并排对比。
- 截图：`check_dist_secrets.py` 的红 / 绿两态。
- tag `v10-secure`。

---

## 六、hash 指纹与长缓存

**约 8 分钟。**

### 6.1 那串乱码是什么

```
dist/assets/index-a3f9c21b.js
                  ^^^^^^^^
```

> 这是**内容哈希**：把文件内容算一遍哈希，取前几位。
>
> **内容变一个字节，这串就变。内容不变，这串永远不变。**

**回收第 2 次课**：

> 第 2 次课讲 HTTP 缓存时，我们看过这组头：
>
> | 头 | 效果 |
> |---|---|
> | `Cache-Control: max-age=N` | N 秒内**不发请求**，直接用本地副本 |
> | `ETag` / `If-None-Match` | 发一个条件请求，没变就返回 304 |
>
> 当时有一个无解的矛盾：
>
> **缓存时间设长了，改了代码用户拿不到新的；设短了，每次都要问一遍服务器。**
>
> **hash 指纹把这个矛盾消掉了。**

### 6.2 缓存策略：两类文件，两种配法

**醒目页**：

| 文件 | `Cache-Control` | 理由 |
|---|---|---|
| `assets/*-[hash].js/css` | `public, max-age=31536000, immutable` | **文件名唯一对应内容。内容变了文件名就变了，不可能拿到旧的** |
| `index.html` | `no-cache`（或 `max-age=0, must-revalidate`） | **它是索引**。必须每次问一次，才能知道新的 hash 是什么 |

**讲清这个机制怎么运转**：

```
发版前：index.html → index-a3f9c21b.js   （用户缓存里有这个）
发版后：index.html → index-7c04e8d9.js   （新文件名）

用户刷新：
  1. 请求 index.html          → no-cache，一定会问服务器 → 拿到新的
  2. 请求 index-7c04e8d9.js   → 本地没有 → 下载
  3. 其他没变的 chunk          → 文件名没变 → 直接用缓存，0 请求
```

> **结果：只下载真正变了的部分，其余全部命中缓存。**
>
> 判据：**"缓存多久"这个问题问错了。正确的问题是"这个 URL 会不会指向不同的内容"。**
>
> 不会 → 缓存一年。
> 会 → 根本不该缓存。
>
> `immutable` 这个指令就是在说这件事：**"这个 URL 的内容永远不会变，连条件请求都别发。"**

**一个实际的坑**：

> 这也解释了单元 5.6 那句"CDN 上的旧产物你删不掉"——**你亲手给它配了一年的 `immutable`。**
>
> 安全事故和缓存策略在这里撞上了。**这就是为什么泄漏只能靠轮换。**

〔部署时这些头具体怎么配（nginx / CDN / 对象存储）→ **第 16 次课。**〕

### 6.3 sourcemap：现场反查一次

**先制造一个线上报错**：

```javascript
// 压缩后的产物里
Uncaught TypeError: Cannot read properties of undefined (reading 'name')
    at Rr (index-a3f9c21b.js:1:8421)
```

> `Rr`，第 1 行第 8421 列。**这个信息等于没有。**

**打开 sourcemap，再看一次**：

DevTools 自动加载 `.map` 文件后：

```
Uncaught TypeError: Cannot read properties of undefined (reading 'name')
    at QuestionCard (QuestionCard.tsx:37:22)
```

点一下，**直接跳到 `QuestionCard.tsx` 第 37 行，原始代码、原始变量名**。

> sourcemap 就是一张对照表：**产物的第几行第几列 ↔ 源码的哪个文件第几行第几列**，还包括变量名的还原。
>
> 浏览器通过产物末尾那行注释找到它：
>
> ```javascript
> //# sourceMappingURL=index-a3f9c21b.js.map
> ```

**要不要上生产（判据表，醒目页）**：

| 方案 | 配置 | 代价 | 适合 |
|---|---|---|---|
| 不生成 | `sourcemap: false` | **线上报错完全看不懂** | 几乎不推荐 |
| 生成并公开 | `sourcemap: true` | **等于公开源码** | 开源项目、内部工具 |
| **生成但不部署** | 构建后上传到错误监控平台，**不拷进 CDN** | 需要接监控平台 | **推荐** |
| hidden sourcemap | `sourcemap: 'hidden'`（生成 map 但**不写那行注释**） | 需要手工关联 | 折中 |

> **判据：sourcemap 要生成，但不一定要公开。**
>
> 它的价值全在"报错时能定位"，而这件事可以在服务端（Sentry 之类）完成，不需要放给用户。
>
> 顺便：**sourcemap 里包含完整的原始源码**。如果你的前端代码里有不该公开的业务逻辑，公开 sourcemap 等于把源码发出去。
>
> 〔注意：**这不影响单元 5 的结论。** 密钥就算没有 sourcemap 也能 grep 到——**混淆从来不是安全措施。**〕

### 材料

- **封面级素材**：6.2 的两类文件缓存策略表 + 发版流程三步图。
- **高光图**：6.3 的 sourcemap 四种方案判据表。
- 录屏：报错从 `at Rr (index-*.js:1:8421)` → 开启 sourcemap 后跳到 `QuestionCard.tsx:37`（**一镜到底**）。
- 截图：产物末尾的 `//# sourceMappingURL=` 注释。
- 截图：改一个组件后重新构建，**只有一个 chunk 的 hash 变了**（其余不变）。

---

## 七、类型护栏：TypeScript 最小集，与 AI 代码

**约 16 分钟。本次课的课程主题落点。**

### 7.1 TypeScript 最小集：四件事

**只讲够用的，不做语言教学。**

**① 标注在哪（不是到处标）**

```ts
// ✅ 该标：函数的入参和返回值——这是"契约"
function formatCount(n: number): string {
  return n > 999 ? `${Math.floor(n / 1000)}k` : String(n);
}

// ✅ 该标：组件的 props
interface QuestionCardProps {
  question: components["schemas"]["QuestionOut"];   // ← 第 8 次课的生成类型
  onSelect: (id: number) => void;
  highlighted?: boolean;                            // ? = 可选
}

// ❌ 不用标：局部变量，推断得很好
const total = items.length;          // 自动推断为 number
const names = users.map(u => u.name);  // 自动推断为 string[]
```

> 判据：**在"边界"上标注，内部让它推断。**
>
> 边界 = 函数签名、组件 props、模块导出、外部数据。
> 这和后端是同一条判据——第 3 次课的"入口闸门"。

**② `interface` 与联合类型**

```ts
interface UserBrief { id: number; display_name: string; }

// 联合类型：这个值只能是这几个之一
type Sort = "latest" | "oldest" | "views";      // ← 第 7 次课的 Literal 白名单

// 可辨识联合：第 8 次课的 State<T>
type State<T> =
  | { kind: "loading" }
  | { kind: "error"; message: string; requestId?: string }
  | { kind: "empty" }
  | { kind: "success"; data: T };
```

> 可辨识联合是 TS 最有价值的特性，因为：
>
> ```ts
> switch (state.kind) {
>   case "loading": ...
>   case "error":   console.log(state.message);   // ← 这里 TS 知道有 message
>   case "empty":   ...
>   // 漏了 "success" → 编译错误
> }
> ```
>
> **它把"记得处理所有情况"从纪律变成了编译检查。** 这是第 8 次课三态那个设计能成立的原因。

**③ `any` 的代价**

```ts
const data: any = await res.json();
data.itmes.map(...)        // 拼错了，TS 一声不吭
data.foo.bar.baz           // 全都不报错
```

**醒目页**：

> **`any` 会传染。**
>
> | | `any` | `unknown` |
> |---|---|---|
> | 能不能随便访问属性 | ✅ **不报错** | ❌ 必须先收窄 |
> | 能不能传给任何函数 | ✅ | ❌ |
> | 它的属性是什么类型 | **还是 `any`** | — |
>
> `data.foo` 是 `any`，`data.foo.bar` 也是 `any`……**一个 `any` 能让一整条调用链失去检查。**
>
> 判据：**要表达"我不知道这是什么"，用 `unknown`，不要用 `any`。** `unknown` 逼你在使用前检查，`any` 让你跳过检查。
>
> 补一句：**`as` 断言是 `any` 的近亲。** `data as QuestionOut` 是在对编译器说"相信我"，**它不做任何运行时检查**。

**④ 类型只存在于编译期（回收 4.4）**

```ts
const q: QuestionOut = await res.json();    // ← 这里没有任何校验
```

**这一条最重要，一定要讲透**：

> 单元 4.4 说过：**esbuild 把类型删掉就完事了。**
>
> 所以 `const q: QuestionOut = await res.json()` 这一行，运行时**没有任何检查**。后端返回什么，`q` 就是什么。你只是在对编译器许诺。
>
> **类型不校验运行时数据。这是本课程最容易被误解的一句话。**
>
> | 边界 | 谁来保证真的是那个形状 |
> |---|---|
> | 后端 → 前端 | **第 9 次课的契约测试**（schemathesis 验证响应符合 openapi） |
> | 用户输入 → 前端 | 前端即时校验（体验）+ **后端 Pydantic**（权威） |
> | 第三方 API → 你的代码 | **没人保证**——这里必须运行时校验（zod 之类） |
>
> 判据：**类型保证"你的代码内部一致"，不保证"外部数据符合预期"。** 后者只能靠运行时校验或契约测试。
>
> 这正是第 8、9、10 三次课连起来的地方：
>
> ```
> 第 8 次课：从后端契约生成类型      → 前端内部一致
> 第 9 次课：契约测试验证后端守约    → 外部数据可信
> 第 10 次课：tsc 进 build 和 CI     → 保证前两条真的被执行
> ```

### 7.2 为什么类型检查是 AI 生成代码最便宜的护栏（**本单元核心**）

**先现场做一个 A/B 实验（两份提示词、两份输出并排）。**

**A 组**：

> 写一个 React 组件，展示一个问题卡片，显示标题、作者、回答数，点击时回调。

**B 组**：

> 附件是 `api.d.ts`。写一个 React 组件 `QuestionCard`，props 类型为
> `{ question: components["schemas"]["QuestionOut"]; onSelect: (id: number) => void }`。
> 必须通过 `tsc --noEmit`，不许用 `any` 和 `as`。

**对比**：

| | A 组 | B 组 |
|---|---|---|
| props 类型 | `{ question: any }` 或自己编一个 interface | 用了生成的类型 ✅ |
| 字段名 | `question.authorName` / `question.answers` —— **猜的** | `question.author.display_name` ✅ |
| 回调签名 | `onClick: () => void`（丢了 id） | `onSelect: (id: number) => void` ✅ |
| 可空处理 | 没处理 | 处理了 |
| `tsc --noEmit` | ❌ | ✅ |
| 你要改几行 | 4–6 行 | 0–1 行 |

**然后给出本次课最重要的判断（封面级素材）**：

> **护栏的价值 = 它能拦住的错误 ÷ 它的成本。**
>
> 按这个公式排一下我们有的几种手段：

| 手段 | 一次性成本 | 每次使用成本 | 拦截速度 | 能拦住什么 |
|---|---|---|---|---|
| **类型检查** | **配一次**（半天） | **0** | **秒级** | 字段名、签名、可空、结构 |
| ESLint | 配一次 | 0 | 秒级 | 用法模式、常见陷阱 |
| 单元/集成测试 | **每个场景都要写** | 维护 | 分钟级 | 逻辑、边界、集成 |
| 代码评审 | 0 | **人的时间**（最贵） | 小时到天 | 意图、设计、业务 |
| 线上监控 | 中 | 0 | **出事之后** | 一切 |
|
> **类型检查的独特之处：一次性配置，之后边际成本为零，而且覆盖 AI 最常犯的那一类错误。**
>
> AI 生成代码的错误可以分三类：

**醒目页，这张表必须做**：

| 错误类型 | AI 犯的频率 | 类型能抓吗 | 谁来抓 |
|---|---|---|---|
| 语法错误 | 极低 | — | 编译器 |
| **字段名猜错** | **高** | ✅ | **tsc** |
| **函数签名对不上** | **高** | ✅ | **tsc** |
| **可空没处理** | **高** | ✅ | **tsc** |
| **结构假设错**（以为返回数组，实际是 `{items}`） | **高** | ✅ | **tsc** |
| 用了不存在的包 | 中 | ❌ | `npm view`（单元 3.4） |
| 业务规则漏了 | **中高** | ❌ | 测试 + 评审 |
| 边界差一（off-by-one） | 中 | ❌ | **测试**（第 9 次课） |
| 权限判断漏了 | 中 | ❌ | 测试 + 评审 |
| N+1 / 性能 | 中 | ❌ | **性能守卫**（第 9 次课） |

> **上半部分（类型能抓的）恰好是 AI 最常犯的。这是巧合吗？**
>
> **不是。** 因为这几类错误的共同本质是：**AI 缺少你的项目特定信息，只能猜。**
>
> 而类型定义**恰恰就是那份信息的机器可读形式**。
>
> 把 `api.d.ts` 给它 → 它不用猜了；它还是猜错了 → tsc 立刻抓住。**两道都不花钱。**

**但必须同时给出反面（否则学生会误以为有类型就够了）**：

> **下半部分（类型抓不到的）同样重要，而且更危险——因为它们不会变红。**
>
> 一个类型完全正确、`tsc` 全绿的函数，可以：
> - 把 `offset` 算成 `page * size`（第 9 次课作业三那个 bug）
> - 忘了检查"只有作者能删自己的问题"
> - 对每个列表项发一次请求
>
> **判据：类型检查拦住的是"形状对不对"，测试拦住的是"行为对不对"。两者不能互相替代。**
>
> 这就是为什么第 9 次课要花一整节讲测试，而今天这节课**不能取代它**。

### 7.3 ESLint 的分工

> 有了 TS，还要 ESLint 吗？**要，但它们管的是不同的东西。**

| | TypeScript | ESLint |
|---|---|---|
| 管什么 | **类型对不对** | **写法好不好** |
| 例子 | `q.auther` 不存在 | 声明了没用的变量；`useEffect` 缺依赖；Promise 没 await |
| 能自动修吗 | ❌ | ✅ 部分（`--fix`） |

**最少要开的几条**：

```js
// eslint.config.js
export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    rules: {
      "@typescript-eslint/no-explicit-any": "error",        // ← 堵住 any
      "@typescript-eslint/no-floating-promises": "error",   // ← 忘了 await
      "no-console": ["warn", { allow: ["warn", "error"] }],
    },
  },
];
```

> `no-floating-promises` 值得单独说：它抓的是 `submitForm()` 忘了写 `await` —— **这个错误不会报任何错，只是静默地不等待**。AI 生成异步代码时很常犯。
>
> 注意它需要 type-aware lint（要读 tsconfig），配置稍麻烦，**但值得**。

**进 CI（第 9 次课已有骨架，今天补齐）**：

```yaml
  frontend:
    steps:
      - run: cd web && npm ci
      - run: cd web && npm run check       # tsc --noEmit
      - run: cd web && npm run lint        # eslint
      - run: cd web && npm run build       # ← 新增（单元 4.3 后果一）
      - run: python scripts/check_dist_secrets.py   # ← 新增（单元 5.7）
      - run: bash scripts/check_contract.sh
```

### 材料

- **封面级素材**：7.2 的"护栏成本/收益"五行表。
- **封面级素材**：7.2 的"AI 错误类型 vs 谁能抓"十行表（上半绿、下半红）。
- **封面级素材**：7.1 ④ 的"第 8/9/10 次课三条线"图。
- **高光图**：`any` vs `unknown` 三行表。
- **高光图**：TS vs ESLint 分工表。
- A/B 实验的两份输出并排，A 组猜错的地方逐个标红（**备预录产物**）。
- 截图：`any` 让一整条链失去检查的编辑器演示。

---

## 八、体积与拆包

**约 7 分钟。B 档，时间紧可只讲判据。**

### 8.1 先量

```bash
npm i -D rollup-plugin-visualizer
npm run build            # 配置后自动产出 stats.html
```

打开 `stats.html`，**现场指认三块**：

| 看到什么 | 说明 |
|---|---|
| 最大的那块 | 通常是 React + ReactDOM（不可避免） |
| **第二大但你没怎么用的** | **这是你要处理的**（演示二的 lodash） |
| 一堆小碎块 | 正常 |

> 判据：**先看"占比最大的"和"占比与价值最不匹配的"。** 不要试图优化所有东西。

### 8.2 一次动态 `import()`

**场景**：详情页有个 Markdown 渲染器，170 kB，但**只有详情页用**。

```diff
- import { renderMarkdown } from "./markdown";
-
- export function Detail({ q }) {
-   return <div dangerouslySetInnerHTML={{ __html: renderMarkdown(q.content) }} />;
- }

+ export function Detail({ q }) {
+   const [html, setHtml] = useState("");
+   useEffect(() => {
+     import("./markdown").then(m => setHtml(m.renderMarkdown(q.content)));
+   }, [q.content]);
+   return <div dangerouslySetInnerHTML={{ __html: html }} />;
+ }
```

〔`useState` / `useEffect` 一句带过，**第 11 次课讲**。这里只看构建产物的变化。〕

```
构建前：index-*.js  198 kB
构建后：index-*.js   31 kB
        markdown-*.js 167 kB     ← 独立 chunk，进详情页才下载
```

> **列表页的用户永远不会下载那 167 kB。**
>
> 判据：**该拆的三种情况：**
>
> | 情况 | 例子 |
> |---|---|
> | 只在某条路由用 | 详情页的渲染器、后台管理页 |
> | 只在某个交互后用 | 图表、富文本编辑器、二维码扫描 |
> | 体积大且非首屏必需 | 地图、视频播放器 |
>
> **不该拆的**：每个页面都用的东西（拆了反而多一次请求）、很小的模块（HTTP 开销大于收益）。

### 8.3 `dangerouslySetInnerHTML`

**顺手指出，一句话**：

> 看到 8.2 那个 `dangerouslySetInnerHTML` 了吗？
>
> **React 把这个 API 的名字起得这么长这么吓人，是故意的。** 回收第 8 次课那张表：
>
> | | 默认行为 | 危险的那个 |
> |---|---|---|
> | Jinja2 | 转义 | `\| safe` |
> | `innerHTML` | **不转义** | 默认就是它 |
> | React `{}` | 转义 | `dangerouslySetInnerHTML` |
>
> **→ 第 15 次课处理 Markdown 渲染的正确做法（消毒）。** 今天记账。

### 材料

- 截图：visualizer 的 treemap，lodash 那块圈红。
- 截图：拆包前后的 `dist/` 文件列表对比。
- 高光图：8.2 的"该拆/不该拆"判据表。

---

## 九、C 档结论卡

**约 3 分钟。时间不够整体跳过。**

### 9.1 打包器对照

| 工具 | 定位 | 什么时候选 |
|---|---|---|
| **Vite** | dev 用原生 ESM，build 用 Rollup | **默认选它** |
| webpack | 老牌、生态最全、配置最复杂 | 老项目；需要极冷门的 loader |
| esbuild | 极快的转译+打包，**不做类型检查** | 库的构建；作为其他工具的底层 |
| Rollup | 打包库的标准 | **你在写一个库而不是应用** |
| Turbopack / Rspack | webpack 的高性能替代 | 大型 webpack 项目要提速 |

> 判据：**应用用 Vite，库用 Rollup（或 tsup）。** 两者的目标不同：应用要产出"能直接跑的一坨"，库要产出"别人能再打包的干净 ESM"。

### 9.2 一句话结论卡

| 问题 | 结论 |
|---|---|
| pnpm / yarn 值得换吗 | pnpm 用硬链接省磁盘、装得快、**依赖隔离更严格**（不允许访问未声明的依赖）。新项目可以直接用 |
| monorepo | 多包共享代码时才需要。**两三个包不值得** |
| `devDependencies` vs `dependencies` | 前端应用其实**都会被打包**，区别只在"要不要装到生产机器"。库作者必须分清 |
| `peerDependencies` | 写库时用，声明"宿主必须提供 React"，避免装出两份 React |
| Vite 插件 | 大多数需求官方插件 + 社区插件够用。**写插件前先确认没有现成的** |
| 多环境构建 | 每个环境构建一次（单元 5.3）。若想"一次构建多处部署"→ 配置必须运行时拉（**第 16 次课**） |
| CSS 方案 | 本课程用原生 CSS + CSS Modules。Tailwind / CSS-in-JS 是取舍问题，不是对错问题 |
| 打包出的代码能被反编译吗 | **不需要"反编译"，它就是 JS**。混淆不是保护 |
| polyfill / browserslist | 决定语法降级到什么程度。**先问清楚你要支持哪些浏览器**，再配 |
| 构建缓存 | CI 里缓存 `~/.npm` 和 Vite 的 `node_modules/.vite`，能省大半时间 |

---

## 十、作业与欠账

**约 5 分钟。**

### 10.1 作业一：前端工程初始化（主线，必交）

在 `v10-broken` 基础上，交付一套**能上生产**的前端工程。

| # | 要求 | 自检 |
|---|---|---|
| 1 | `package-lock.json` 已提交，**且不在 `.gitignore` 里** | `git ls-files web/package-lock.json` |
| 2 | 所有依赖都通过单元 3.4 的评估清单，**删掉至少两个不必要的依赖** | 见作业三 |
| 3 | `build` 脚本串了 `tsc -b` | `npm run build` 在有类型错误时失败 |
| 4 | `npm run check`（`tsc --noEmit`）零错误，**零 `any`、零 `as`**（有则必须写注释说明理由） | grep |
| 5 | ESLint 配置就绪，`no-explicit-any` 和 `no-floating-promises` 为 error | `npm run lint` |
| 6 | **`.env` 里不含任何机密**；第三方密钥改为后端代理 | 见 7 |
| 7 | `scripts/check_dist_secrets.py` 接入 CI，**并提交一次"故意放密钥→CI 红"的截图** | 红/绿两张图 |
| 8 | env 分层正确：`.env` 提交、`.env.local` 不提交 | 看 `.gitignore` |
| 9 | CI 里前端 job 包含：`npm ci` → `check` → `lint` → `build` → 机密扫描 → 契约一致性 | CI 全绿截图 |
| 10 | `docs/decisions.md` 新增三条（见下） | — |

**`decisions.md` 必须包含**：
- 为什么从 vanilla TS 换到 React，以及**哪些层没有跟着换**（单元 3.0）
- sourcemap 的处置决定（四选一，说明理由）
- 第三方密钥的处置方案，以及**这个密钥怎么轮换**

### 10.2 作业二：产物体积报告与一次拆包（B 档，必交）

| # | 要求 |
|---|---|
| 1 | 接入 visualizer，交**优化前**的 treemap 截图 |
| 2 | 做至少两处优化（去依赖 / 换轻量方案 / 按需引入），交优化后截图 |
| 3 | 做**一次动态 `import()` 拆包**，交拆包前后 `dist/` 文件列表对比 |
| 4 | 填下表 |

| 优化项 | 改了什么 | gzip 前 | gzip 后 | 省了多少 |
|---|---|---|---|---|

**必答三问**：

1. 你拆出来的那个 chunk，**什么情况下用户会下载它？什么情况下不会？**
2. 单元 8.2 说"很小的模块不该拆"。**你怎么判断"多小算小"？** 给一个你能自圆其说的阈值和理由。
3. 如果 CI 里要加一条"产物体积不许超过 N kB"的检查，**N 你会设多少？依据是什么？**（提示：回收第 9 次课"断言性质优于断言数值"——**有没有比绝对值更好的断言方式？**）

> 第 3 问是重点。一个好答案会指出：**绝对阈值会随功能增长不断被调高，最后变成走形式；更好的断言是"单次 PR 的体积增量不超过 X"或"首屏 chunk 不许引入新的大依赖"。**

### 10.3 作业三：依赖审查与一次否决（**课程主题作业**）

**第一部分：向 AI 要一个功能，审查它给的依赖。**

选一个你的项目真实需要的功能（例：日期选择器、表格排序、Markdown 渲染、图表、防抖搜索、虚拟滚动），向 AI 提问：

> 我的项目是 Vite + React + TS，要实现 XXX。推荐方案和需要的依赖。

**原样保存输出**，然后对它推荐的**每一个**依赖填这张表：

| 包名 | 存在吗<br>(`npm view`) | 周下载量 | 最后更新 | 传递依赖数<br>(`npm ls`) | gzip 体积 | 有 postinstall 吗 | 原生/已有依赖能做吗 | **结论** |
|---|---|---|---|---|---|---|---|---|

**第二部分：至少否决一条（必做）**

从上表里选**至少一个**你决定**不装**的包，写一段 100 字以上的理由，必须包含：
- 你否决它的**具体依据**（表里的哪一列）
- 你的**替代方案**是什么
- 替代方案的**代价**是什么（不能说"没有代价"）

**第三部分：必答四问（评分重点）**

| # | 问题 |
|---|---|
| 1 | AI 推荐的包里，有没有**不存在**的？有没有**多年未更新**的？你是怎么发现的？ |
| 2 | 单元 3.4 说"AI 在陈述外部事实时会编造"。**对照第 6 次课（漏业务约束）和第 8 次课（猜字段名），这三类错误的共同结构是什么？** |
| 3 | 单元 7.2 的表把 AI 错误分成了"类型能抓"和"类型抓不到"两类。**"推荐了不存在的包"属于哪一类？为什么？你要用什么机制抓它？** |
| 4 | 给出一条你们团队可以直接执行的规则，管住"AI 推荐依赖"这件事。**这条规则必须能被机械检查，或者必须说明为什么它只能靠人。** |

> **第 2 问是本次作业的核心。**
>
> 提示一个答案方向：三次的共同结构是 **AI 用"训练数据里最常见的模式"填补了"它不掌握的具体事实"**——
>
> | | 它不掌握的事实 | 它填进去的东西 |
> |---|---|---|
> | 第 6 次课 | 你的业务规则 | 通用的 CRUD 逻辑 |
> | 第 8 次课 | 你的字段名 | 最常见的命名习惯 |
> | 第 10 次课 | npm registry 的真实内容 | 听起来最合理的包名 |
>
> **而且三次它都没有表达任何不确定。**
>
> 推论：**你的任务不是"让 AI 别犯错"，是"识别出哪些地方它必然在猜，并在那些地方加检查"。**

### 10.4 本次课新增的欠账登记

| 欠账 | 何时还 |
|---|---|
| React 本身（组件、状态、渲染） | **第 11 次课** |
| `dangerouslySetInnerHTML` 与 Markdown 消毒 | **第 15 次课** |
| 生产环境跨域（proxy 没了怎么办） | **第 12 次课** |
| 静态产物部署、缓存头怎么配、CDN | **第 16 次课** |
| "一次构建，多处部署"与运行时配置 | **第 16 次课** |
| 密钥轮换的运维流程 | **第 16 次课** |
| 专业的 secret scanning 工具（gitleaks） | 课后自读 |
| pnpm / monorepo | 课后自读 |
| polyfill 与 browserslist | 课后自读 |
| CI 构建缓存 | 课后自读 |

---

## 十一、素材清单与制作说明

### 必需素材

| 素材 | 说明 |
|---|---|
| tag `v10-broken` | 起始版：React 模板 + 四个问题齐备。**`.env` 里的 AI 注释必须原样保留**，它是戏剧性的来源 |
| tag `v10-deps` | 单元 3 结束：lockfile 提交、多余依赖清掉 |
| tag `v10-build` | 单元 4 结束：build 串上 tsc |
| tag `v10-secure` | 单元 5 结束：密钥移到后端、机密扫描接入 |
| tag `v10-typed` | 单元 7 结束：ESLint + 类型配置完整 |
| tag `v10-final` | 作业参考交付 |
| `scripts/check_dist_secrets.py` | 完整可用，含红/绿两态演示数据 |
| `eslint.config.js`、`tsconfig.json`、`vite.config.ts` | 完整可用 |
| **封面级 A** | 三句核心话（"前端没有秘密 / 都已经发给了每个用户 / `.gitignore` 保护的是仓库不是产物"） |
| **封面级 B** | 单元 1.1 的"你每天在用，你能回答吗"六行表 |
| **封面级 C** | 单元 3.2 的"浏览器只认三种路径" |
| **封面级 D** | 单元 3.3 的 `npm ci` vs `npm install` |
| **封面级 E** | 单元 3.4 的 slopsquatting 攻击链四步图 |
| **封面级 F** | 单元 3.4 的依赖评估九条清单 |
| **封面级 G** | 单元 4.2 的 Vite 双链路八行对照表 |
| **封面级 H** | 单元 4.4 的"转译 vs 类型检查" |
| **封面级 I** | 单元 5.3 的"后端 env vs 前端 env"四行表 |
| **封面级 J** | 单元 5.4 的"能放 / 不能放" |
| **封面级 K** | 单元 5.6 的"删代码没用 / 唯一有效是轮换" |
| **封面级 L** | 护栏累加表（新增第八、九行） |
| **封面级 M** | 单元 6.2 的两类文件缓存策略 + 发版三步图 |
| **封面级 N** | 单元 7.2 的"护栏成本/收益"五行表 |
| **封面级 O** | 单元 7.2 的"AI 错误类型 vs 谁能抓"十行表（**上半绿、下半红**） |
| **封面级 P** | 单元 7.1 ④ 的"第 8/9/10 次课三条线"图 |
| 高光图 Q | 单元 2 的四个问题性质对照 |
| 高光图 R | ESM vs CommonJS |
| 高光图 S | semver 四种写法 |
| 高光图 T | 单元 4.3 的三个实际后果（含 dev/build 两条链路的 proxy 示意） |
| 高光图 U | 单元 6.3 的 sourcemap 四方案 |
| 高光图 V | `any` vs `unknown` |
| 高光图 W | TS vs ESLint 分工 |
| 高光图 X | 单元 8.2 的"该拆 / 不该拆" |
| **录屏 1（最关键）** | `cat .env` → `npm run build` → `grep` 命中 → 浏览器 DevTools 搜到密钥原文。**一镜到底** |
| **录屏 2** | sourcemap 反查：`at Rr (index-*.js:1:8421)` → 点击 → `QuestionCard.tsx:37` |
| 截图 | 裸说明符报错原文 |
| 截图 | `npm view react-map-widgets` 的 404 |
| 截图 | 两次 `npm install` 版本不同 |
| 截图 | dev 模式 217 个请求的瀑布图 |
| 截图 | 类型错误下 dev 正常启动 + 页面正常渲染（同屏） |
| 截图 | `tree dist/` 全貌 |
| 截图 | 压缩后代码的前 300 字节 |
| 截图 | 源码 `import.meta.env.VITE_X` ↔ 产物字符串字面量 并排 |
| 截图 | `check_dist_secrets.py` 红 / 绿两态 |
| 截图 | 改一个组件后只有一个 chunk 的 hash 变了 |
| 截图 | visualizer treemap（lodash 圈红）+ 优化后对比 |
| 截图 | 拆包前后 `dist/` 文件列表 |

### 可后补

- 打包器对照表、一句话结论卡（纯文字）。
- 单元 8 的全部截图（若压缩则只需作业参考图）。

### 备用材料

| 风险 | 备用方案 |
|---|---|
| **`npm ci` 在教室网络下太慢**（最高风险） | 课前发放含 `node_modules` 的包；或用预装容器镜像；**演示 `npm install` 版本差异时用预录** |
| `react-map-widgets` 某天真的被人注册了 | **课前当天重新验证一次**；备用几个确认不存在的名字；或直接用预录截图并说明"这个演示的名字每学期要换" |
| 依赖版本变化导致体积数字对不上 | 所有体积数字标注"实测于 YYYY-MM，以现场为准"；**关键是对比，不是绝对值** |
| Vite 大版本升级改变产物结构 | 锁定 `package.json` 里的 Vite 版本；底稿中 `dist/` 结构图标注生成版本 |
| DevTools 界面改版，sourcemap 演示路径变 | 备录屏；同时准备命令行版本（`npx source-map-cli`） |
| AI 现场调用失败（7.2 A/B、作业三） | 预录两份输出。**A 组那份必须真实体现"猜字段名"和"用 any"**，不要人工编造 |
| 学生 Node 版本不一致 | `.nvmrc` + `package.json` 的 `engines`；课前统一 |
| 时间超支 | 按单元〇压缩顺序；单元 8 有自读材料 `docs/bundle.md` |

### 环境与运行条件

延用前序环境。**新增**：Node.js 20+、`rollup-plugin-visualizer`、ESLint + typescript-eslint。

**演示开始时的初始状态**：`web/` 在 tag `v10-broken`，**已完成 `npm install`**（不要现场装）；后端已启动；三个终端（一个 `npm run dev`、一个跑构建与 grep、一个后端）；浏览器两个标签（dev 页面、DevTools 已打开 Network 面板）。

**复位方式**：`git checkout v10-broken -- web/ && rm -rf web/dist`。

---

## 十二、与前后课的衔接

**本次课回收的前序埋点**：

| 来源 | 埋点 | 回收位置 |
|---|---|---|
| 第 2 次课 | HTTP 缓存：`Cache-Control` / `ETag`，"缓存多久"的两难 | **单元 6.1、6.2**（hash 指纹消掉了这个两难） |
| 第 3 次课 | 入口闸门：约束越靠前越好 | 单元 7.1 ①（在边界上标注类型） |
| 第 5 次课 | Jinja2 自动转义 / `\| safe` | 单元 8.3（React 的对应物） |
| 第 6 次课 | AI 在"需要它不掌握的信息"处会自信地编造 | **单元 3.4**（第三次出现：这次编造的是 npm 上的包） |
| 第 7 次课 | `Literal` 排序白名单 | 单元 7.1 ②（成为 TS 联合类型） |
| 第 8 次课 | Vite proxy 绕过 CORS，"只在开发期有效" | **单元 4.3 后果二**（讲清为什么：proxy 是 dev server 的功能） |
| 第 8 次课 | 生成的 `api.d.ts` 是第六道护栏 | **单元 7.1、7.2**（今天讲清它为什么便宜） |
| 第 8 次课 | 可辨识联合 `State<T>` | 单元 7.1 ② |
| 第 8 次课 | 前端 N+1：请求数是最重要的指标 | 单元 4.1（dev 的 217 个请求） |
| 第 8 次课 | `innerHTML` 默认不转义 | 单元 8.3（加上 React 一列） |
| 第 9 次课 | `tsc --noEmit` 进 CI（未解释原理） | **单元 4.4 补齐原理** |
| 第 9 次课 | CI 里用 `npm ci` 不是 `npm install`（未解释） | **单元 3.3 补齐原理** |
| 第 9 次课 | CI 是一个"容器"，任何能写成断言的规则都能装进去 | **单元 5.7**（装进去第一条产物级检查） |
| 第 9 次课 | "红-绿两步"方法论 | 单元 5.7（机密扫描的红/绿演示） |
| 第 9 次课 | 检查的严谨程度要配得上问题的严重程度 | 单元 3.5（audit level）、单元 5.7（正则不完备但便宜） |
| 第 9 次课 | 宁可少几条检查，也不要有一条会误报 | 单元 3.5（`--audit-level=high`） |
| 第 9 次课 | **固定动作：新增纪律当场补进 `test_conventions.py`** | **单元 3.5、4.4、5.7 各兑现一次** |
| 第 9 次课 | 断言性质优于断言数值 | 作业二第 3 问 |

**本次课埋下、后面必须回引的五处**（请在课件中明显标记）：

- **单元 4.3 后果二（proxy 是 dev server 的功能）** → 第 12 次课关掉 proxy，用 nginx 反代或后端 CORS 解决；
- **单元 5.3（前端 env 是构建时注入，换环境要重新构建）** → 第 16 次课的"一次构建、多处部署"必须回到这一页；
- **单元 6.2（`immutable` 一年缓存）** → 第 16 次课配部署的缓存头时直接用这张表；同时它是"泄漏只能轮换"的技术原因；
- **单元 7.2（类型抓不到的那半张表）** → 第 15 次课的权限/安全问题全部落在下半部分，要回引说明"为什么 tsc 全绿也不安全"；
- **单元 8.3（`dangerouslySetInnerHTML`）** → 第 15 次课讲 XSS 与富文本消毒。

**本次课不承担、请勿提前引入**：React 的组件/状态/渲染机制（第 11 次课）、CORS 的生产解法（第 12 次课）、认证与 token 存储（第 14 次课）、XSS/CSRF（第 15 次课）、部署与 CDN（第 16 次课）、CSS 方案之争（C 档卡）、monorepo/pnpm（C 档卡）。

**给第 11 次课的提示**：

本次课为第 11 次课准备好了三样东西，**请在开场直接使用，不要重新搭建**：

| 资产 | 第 11 次课怎么用 |
|---|---|
| 可用的 React + TS 工程 | 直接开始写组件，零配置时间 |
| `api.d.ts` + `QuestionCardProps` 这类类型 | **组件 props 直接用生成的类型**，现场演示"改后端字段 → 组件编译报错" |
| `tsc` / ESLint 已进 CI | `react-hooks/exhaustive-deps` 这条规则直接开着，**`useEffect` 漏依赖会当场变红** |

**另外，本次课留下了一个第 11 次课必须兑现的伏笔**：

单元 7.2 的表里，"类型抓不到"的下半部分列了"业务规则漏了""边界差一""性能问题"。**第 11 次课的现场必做（`key={index}` 导致输入错位）正好是第四类——类型完全正确、ESLint 不报、测试也可能通过，但界面就是错的。**

建议第 11 次课在复现那个 bug 之后，**把本次课这张表再打一次，在下半部分加上一行："框架的运行时约定（key、不可变更新、hooks 规则）"**——并指出其中只有一部分能被 ESLint 的 hooks 插件抓住，其余只能靠理解机制。

这会让"护栏不是万能的，理解机制仍然必要"这个判断，在学生心里落得更实。