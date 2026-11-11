"""应用入口：注册路由，并把业务异常翻译成 JSON 错误响应。

运行：uv run --env-file .env uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routes import router
from app.schemas import BUSINESS_HTTP, AppError

app = FastAPI(title="question-api（第 7 课 ORM 版）")
app.include_router(router)


@app.exception_handler(AppError)
async def business_error(request: Request, exc: AppError):
    status, code, message = BUSINESS_HTTP[type(exc)]
    return JSONResponse(status_code=status, content={"code": code, "message": message})
