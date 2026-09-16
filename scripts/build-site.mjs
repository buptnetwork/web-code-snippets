// 整站构建脚本（pnpm build）：
// 1. 扫描根目录 ch*.md，逐章执行 slidev build（--base 带部署前缀）到 dist/<前缀>/chXX
// 2. 生成站点根文件：index.html（自动跳转第一章）与 _redirects（Netlify 每章路由兜底）
// 3. 生成 dist/index.html（整站发布时访问站点根也能进入课程）
// 部署前缀 DEPLOY_PREFIX：部署在网站根时改为 ''；当前部署在 https://study.imedix.cn/web-2026b/
import { execSync } from 'node:child_process'
import { readdirSync, rmSync, writeFileSync } from 'node:fs'

const DEPLOY_PREFIX = '/web-2026b'

const prefix = DEPLOY_PREFIX.replace(/\/+$/, '') // 规范化：''（根部署）或 '/web-2026b'
const chapters = readdirSync('.').filter(f => /^ch\d+\.md$/.test(f)).sort()
if (!chapters.length) throw new Error('未发现章节入口（ch*.md）')
const slugs = chapters.map(f => f.replace(/\.md$/, ''))
const outRoot = `dist${prefix}`
rmSync(outRoot, { recursive: true, force: true }) // 干净重建，避免旧章节残留
const first = slugs[0]

for (const slug of slugs) {
  console.log(`\n[build-site] 构建 ${slug}（base=${prefix}/${slug}/）`)
  execSync(`pnpm exec slidev build ${slug}.md --base=${prefix}/${slug}/ -o ${outRoot}/${slug}`, { stdio: 'inherit' })
}

const page = url => `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="0; url=${url}">
<title>现代Web开发技术课程课件</title>
<style>
  body { font-family: system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
         display: flex; min-height: 100vh; margin: 0; align-items: center; justify-content: center; }
  a { color: #0d9488; }
</style>
</head>
<body>
<p>正在进入课程……若未自动跳转，请<a href="${url}">点此进入</a>。</p>
</body>
</html>
`

const redirects = '# 由 scripts/build-site.mjs 自动生成（每章 SPA 路由兜底）\n'
  + slugs.map(s => `${prefix}/${s}/*  ${prefix}/${s}/index.html  200`).join('\n') + '\n'

writeFileSync(`${outRoot}/index.html`, page(`${prefix}/${first}/`))
writeFileSync(`${outRoot}/_redirects`, redirects)
writeFileSync('dist/index.html', page(`${prefix}/`))
console.log(`\n[build-site] 完成：dist${prefix}/（章节：${slugs.join(', ')}）；站点根文件已生成`)
