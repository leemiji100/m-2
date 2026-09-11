from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from firebase_config import get_db
from models import ConversationCreate, ConversationDetailOut, ConversationOut

router = APIRouter()
COLLECTION = "conversations"


@router.post("", response_model=ConversationDetailOut)
def create_conversation(payload: ConversationCreate):
    db = get_db()
    doc_ref = db.collection(COLLECTION).document()
    data = {
        "title": payload.title,
        "messages": [m.model_dump() for m in payload.messages],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    doc_ref.set(data)
    return {"id": doc_ref.id, **data}


@router.get("", response_model=list[ConversationOut])
def list_conversations():
    db = get_db()
    docs = db.collection(COLLECTION).order_by(
        "created_at", direction="DESCENDING"
    ).stream()
    result = []
    for d in docs:
        item = d.to_dict()
        result.append(
            {
                "id": d.id,
                "created_at": item.get("created_at", ""),
                "title": item.get("title", "제목 없음"),
            }
        )
    return result


@router.get("/{conversation_id}", response_model=ConversationDetailOut)
def get_conversation(conversation_id: str):
    db = get_db()
    doc = db.collection(COLLECTION).document(conversation_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    item = doc.to_dict()
    return {
        "id": doc.id,
        "created_at": item.get("created_at", ""),
        "title": item.get("title", "제목 없음"),
        "messages": item.get("messages", []),
    }


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str):
    db = get_db()
    doc_ref = db.collection(COLLECTION).document(conversation_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    doc_ref.delete()
    return {"deleted": True, "id": conversation_id}
