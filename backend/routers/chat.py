import os
from datetime import datetime, timezone

import requests
from fastapi import APIRouter, HTTPException

from firebase_config import get_db
from models import ChatRequest, ChatResponse
from routers.data import get_summary

router = APIRouter()
CONVO_COLLECTION = "conversations"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def _build_system_prompt(summary) -> str:
    return f"""당신은 사용자의 그림 공부 현황을 잘 아는 개인 그림 공부 비서입니다.

[사용자 데이터 요약]
- 데이터 기간: {summary.period}
- 총 기록: {summary.count}개
- 주요 지표: 합계 {summary.metrics.total}장 / 평균 {summary.metrics.average}장 / 최대 {summary.metrics.max}장 / 최소 {summary.metrics.min}장
- 최근 추세: {summary.trend}

위 데이터를 참고해서 사용자의 그림 연습 현황에 맞춰 친근하고 구체적으로 답변하세요."""


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY가 설정되지 않았습니다.")

    db = get_db()
    summary = get_summary()
    system_prompt = _build_system_prompt(summary)

    conversation_id = req.conversation_id
    messages = []
    if conversation_id:
        doc = db.collection(CONVO_COLLECTION).document(conversation_id).get()
        if doc.exists:
            messages = doc.to_dict().get("messages", [])

    messages.append({"role": "user", "content": req.message})

    openai_messages = [{"role": "system", "content": system_prompt}]
    for m in messages:
        openai_messages.append({"role": m["role"], "content": m["content"]})

    try:
        resp = requests.post(
            OPENAI_URL,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": openai_messages,
                "max_tokens": 800,
            },
            timeout=30,
        )
        if resp.status_code == 429:
            raise HTTPException(
                status_code=502,
                detail="OpenAI API 크레딧이 부족합니다. 결제 설정이나 사용량 한도를 확인하세요.",
            )
        resp.raise_for_status()
        data = resp.json()
        reply_text = data["choices"][0]["message"]["content"]
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"OpenAI request failed: {exc}")
        raise HTTPException(
            status_code=502, detail="AI 응답 생성 중 오류가 발생했습니다. OpenAI API 키와 모델 설정을 확인하세요."
        ) from exc

    messages.append({"role": "assistant", "content": reply_text})

    if conversation_id:
        db.collection(CONVO_COLLECTION).document(conversation_id).update(
            {"messages": messages}
        )
    else:
        doc_ref = db.collection(CONVO_COLLECTION).document()
        doc_ref.set(
            {
                "title": req.message[:20],
                "messages": messages,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        conversation_id = doc_ref.id

    return ChatResponse(reply=reply_text, conversation_id=conversation_id)
