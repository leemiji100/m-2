from statistics import mean

from fastapi import APIRouter, HTTPException

from firebase_config import get_db
from models import (
    DrawingRecordIn,
    DrawingRecordOut,
    DrawingRecordUpdate,
    SummaryMetrics,
    SummaryOut,
)

router = APIRouter()
COLLECTION = "data"


@router.post("", response_model=DrawingRecordOut)
def create_record(record: DrawingRecordIn):
    db = get_db()
    doc_ref = db.collection(COLLECTION).document()
    payload = {
        "date": record.date.isoformat(),
        "value": record.value,
        "memo": record.memo or "",
    }
    doc_ref.set(payload)
    return {"id": doc_ref.id, **payload}


@router.get("", response_model=list[DrawingRecordOut])
def list_records():
    db = get_db()
    docs = db.collection(COLLECTION).order_by("date").stream()
    result = []
    for d in docs:
        item = d.to_dict()
        result.append(
            {
                "id": d.id,
                "date": item.get("date", ""),
                "value": item.get("value", 0),
                "memo": item.get("memo", ""),
            }
        )
    return result


@router.put("/{record_id}", response_model=DrawingRecordOut)
def update_record(record_id: str, record: DrawingRecordUpdate):
    db = get_db()
    doc_ref = db.collection(COLLECTION).document(record_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="해당 기록을 찾을 수 없습니다.")

    update_data = {}
    if record.date is not None:
        update_data["date"] = record.date.isoformat()
    if record.value is not None:
        update_data["value"] = record.value
    if record.memo is not None:
        update_data["memo"] = record.memo

    if update_data:
        doc_ref.update(update_data)

    updated = doc_ref.get().to_dict()
    return {
        "id": record_id,
        "date": updated.get("date", ""),
        "value": updated.get("value", 0),
        "memo": updated.get("memo", ""),
    }


@router.delete("/{record_id}")
def delete_record(record_id: str):
    db = get_db()
    doc_ref = db.collection(COLLECTION).document(record_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="해당 기록을 찾을 수 없습니다.")
    doc_ref.delete()
    return {"deleted": True, "id": record_id}


@router.get("/summary", response_model=SummaryOut)
def get_summary():
    db = get_db()
    docs = list(db.collection(COLLECTION).order_by("date").stream())

    if not docs:
        return SummaryOut(
            period="데이터 없음",
            count=0,
            metrics=SummaryMetrics(total=0, average=0, max=0, min=0),
            trend="데이터 없음",
        )

    values = []
    dates = []
    for d in docs:
        item = d.to_dict()
        values.append(item.get("value", 0))
        dates.append(item.get("date", ""))

    total = sum(values)
    average = round(total / len(values), 2)
    highest = max(values)
    lowest = min(values)

    half = len(values) // 2
    trend = "유지"
    if half > 0:
        first_avg = mean(values[:half])
        second_avg = mean(values[half:])
        if second_avg > first_avg * 1.05:
            trend = "상승"
        elif second_avg < first_avg * 0.95:
            trend = "하락"

    period = f"{dates[0]} ~ {dates[-1]}"

    return SummaryOut(
        period=period,
        count=len(values),
        metrics=SummaryMetrics(total=total, average=average, max=highest, min=lowest),
        trend=trend,
    )
