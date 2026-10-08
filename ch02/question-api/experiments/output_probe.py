"""第 3 课隔离只读实验（教师演示 · 黑盒）：固定 QuestionOut，只改变返回数据。

沿用本课 models.QuestionOut，不删除共享数据库字段，也不对创建接口注入故障来混淆提交结果。
四种模式对照（底稿 5.2）：normal 200 五字段；missing 缺 created_at → 输出校验失败 500；
extra 多 internal_note → 被 extra="ignore" 过滤；direct 直接 JSONResponse → 绕过输出模型。

运行（包根，已激活本包环境；用 PROBE_MODE 选模式）：
    PROBE_MODE=missing python -m uvicorn experiments.output_probe:app --port 8001
用 TestClient 观察 500 时需 raise_server_exceptions=False，不改业务代码吞异常。
"""

import os

from models import QuestionOut


# region probe
from fastapi import FastAPI
from fastapi.responses import JSONResponse


def make_output_probe(mode):
    lab = FastAPI(debug=False)

    @lab.get("/probe", response_model=QuestionOut)
    def probe():
        result = {
            "id": 3, "title": "React 的 props 是什么？",
            "body": "想知道组件怎样接收数据。", "tags": [],
            "created_at": "2026-09-01T08:00:00+00:00",
        }
        if mode == "missing":
            result.pop("created_at")
        if mode in ("extra", "direct"):
            result["internal_note"] = "仅供教师隔离对照"
        if mode == "direct":
            return JSONResponse(content=result)
        return result

    return lab
# endregion probe


# 启动即按 PROBE_MODE 固定一种模式；课堂演示时改环境变量后重启。
app = make_output_probe(os.environ.get("PROBE_MODE", "normal"))
