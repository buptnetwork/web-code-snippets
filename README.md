# web-code-snippets

《现代Web开发技术》课程共享代码。本仓库由课件仓库
[`buptnetwork/web-development-slidev`](https://github.com/buptnetwork/web-development-slidev)
的 `snippets/` 目录通过 [git subtree](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging#_subtree_merge)
拆分而来,单独发布给学生;课件仍按原路径 `<<< @/snippets/...` 引用这些示例。

## 目录

| 路径 | 内容 |
|---|---|
| `lesson00/` | 课前课 Python 素材:注解/装饰器演示、调用栈与 traceback、`mini/` 迷你分层示例、`demo_server.py` |
| `ch01/m0-tracer/` | 第一次课「请求全链路」的可运行 FastAPI 演示与取证脚本(见下) |
| `external.ts` | Slidev 代码外置导入(`<<<`)的 TypeScript region 示例 |

## m0-tracer 运行

在 `ch01/m0-tracer/` 目录下执行,要求 Python 3.12 与 [uv](https://docs.astral.sh/uv/):

```bash
uv sync --frozen
uv run python seed.py                                   # 初始化演示用 SQLite
uv run uvicorn v1_ai_raw:app --host 127.0.0.1 --port 8000
```

- `v1_ai_raw:app`:能运行的反例(拼接 SQL、详情不存在仍返回 200)。
- `v2_traceable:app`:课堂目标,支持 `TRACE_MODE=plain|trace`、`SQL_ECHO=1` 等开关。
- `v3_m0:app`:课后参考实现。
- `verify_m0.py` / `bench.py` / `capture_evidence.py`:验收、并发与取证脚本;`make verify` 为默认检查。

复制 `.env.example` 为 `.env` 后,用 `uv run --env-file .env ...` 显式加载。默认数据库为
`sqlite:///./demo.db`,结构与固定虚构数据见 `seed.sql` / `seed.py`;复位执行
`uv run python seed.py --reset`。

## 说明

- `.venv`、`__pycache__`、`.capture/`、`*.db`、`.env` 等运行产物与本地凭据已由 `.gitignore` 排除,不入库。
- 全部数据与示例均为教学虚构,不连接任何生产数据。
- 本仓库通常由课件仓库通过 subtree 单向发布;如需回改,请在课件仓库修改 `snippets/` 后 `git subtree push`,避免两端并发编辑。
