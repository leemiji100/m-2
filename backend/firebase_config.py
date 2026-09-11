"""Firebase Admin SDK 초기화 및 Firestore 클라이언트 제공."""
import os
import json
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

_db = None


def _init_app():
    if firebase_admin._apps:
        return

    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
    service_account_file = os.getenv("FIREBASE_SERVICE_ACCOUNT_FILE", "").strip()

    if service_account_file:
        credential_path = Path(service_account_file)
        if not credential_path.is_absolute():
            credential_path = Path(__file__).resolve().parent.parent / credential_path
        try:
            cred_dict = json.loads(credential_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"Firebase 서비스 계정 파일을 읽을 수 없습니다: {credential_path}"
            ) from exc
    elif service_account_json:
        try:
            cred_dict = json.loads(service_account_json)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "FIREBASE_SERVICE_ACCOUNT_JSON은 유효한 JSON이어야 합니다."
            ) from exc
    else:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT_FILE 또는 FIREBASE_SERVICE_ACCOUNT_JSON 환경 변수가 설정되지 않았습니다. "
            ".env 파일을 확인하세요."
        )

    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)


def get_db():
    """Firestore 클라이언트를 반환합니다 (최초 호출 시 1회 초기화)."""
    global _db
    if _db is None:
        _init_app()
        _db = firestore.client()
    return _db
