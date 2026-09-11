import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from routers import chat, conversations, data  # noqa: E402

app = FastAPI(
    title="그림 공부 비서 API",
    description="개인 그림 연습 기록을 분석하고, 이를 바탕으로 대화하는 AI 비서 API",
    version="1.0.0",
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


@app.get("/")
def root():
    return {"status": "ok", "service": "그림 공부 비서 API"}
