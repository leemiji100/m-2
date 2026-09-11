# 그림 공부 비서

내 그림 연습 기록(날짜 · 그린 개수 · 메모)을 분석해서, 그 데이터를 아는 AI와 대화할 수 있는 개인 비서 웹 서비스입니다.

## 무엇을 해결하나요
일반적인 챗봇은 "이번 주 얼마나 그렸어?"라고 물어도 알지 못합니다. 이 서비스는 내가 기록한 그림 연습 데이터를 요약해 AI에게 컨텍스트로 넘겨주기 때문에, 내 상황에 맞는 답변을 받을 수 있습니다.

## 기술 스택
- 백엔드: FastAPI, Firebase Admin SDK (Firestore), OpenAI API
- 프론트엔드: HTML / CSS / JavaScript (프레임워크 없음)
- 배포: 백엔드 Render, 프론트엔드 Vercel

## 폴더 구조
```
drawing_assistant/
  backend/
    main.py                 # FastAPI 앱 진입점
    firebase_config.py      # Firestore 클라이언트
    models.py                # Pydantic 모델
    routers/
      data.py                # 데이터 CRUD + 요약
      conversations.py       # 대화 저장/조회/삭제
      chat.py                 # 컨텍스트 주입 방식 AI 채팅
    requirements.txt
    .env.example
  frontend/
    index.html                # 단일 파일 프론트엔드 (채팅 / 기록 / 대화기록 / 설정 탭)
```

## 로컬 실행 방법

### 백엔드
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows는 venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # 값 채워넣기
uvicorn main:app --reload
```
- Swagger UI: [[([https://m-2-mlrsbwmkr-zheltpdl.vercel.app]](https://m-2-lovat.vercel.app/)

### 프론트엔드
`frontend/index.html`을 브라우저로 열거나, VSCode의 Live Server 등으로 실행합니다.
화면 우측 상단 탭에서 **⚙ 설정** 탭을 눌러 백엔드 API 주소(예: `http://127.0.0.1:8000`)를 입력하면 연결됩니다.

## 환경 변수 (backend/.env)
| 변수명 | 설명 |
|---|---|
| `OPENAI_API_KEY` | OpenAI API 키 ([발급 링크](https://platform.openai.com/api-keys)) |
| `OPENAI_MODEL` | 사용할 모델 (기본값 `gpt-4o-mini`) |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Firebase 서비스 계정 키 JSON 전체를 한 줄 문자열로 |
| `ALLOWED_ORIGINS` | 프론트엔드 배포 도메인 (쉼표로 여러 개 구분) |

> 참고: OpenAI Chat Completions API를 사용합니다.

## API 엔드포인트
| Method | Path | 설명 |
|---|---|---|
| POST | `/api/data` | 그림 기록 추가 |
| GET | `/api/data` | 기록 목록 조회 |
| PUT | `/api/data/{id}` | 기록 수정 |
| DELETE | `/api/data/{id}` | 기록 삭제 |
| GET | `/api/data/summary` | 요약 정보 (기간/개수/통계/추세) |
| POST | `/api/conversations` | 대화 수동 저장 |
| GET | `/api/conversations` | 대화 목록 조회 |
| GET | `/api/conversations/{id}` | 특정 대화 전체 메시지 조회 |
| DELETE | `/api/conversations/{id}` | 대화 삭제 |
| POST | `/api/chat` | AI 채팅 (데이터 요약을 시스템 프롬프트에 주입, 대화 자동 저장) |

## 배포
1. **백엔드 (Render)**: `backend` 폴더를 GitHub에 푸시 → Render에서 Web Service 생성 → 시작 명령어 `uvicorn main:app --host 0.0.0.0 --port $PORT` → 위 환경 변수 등록.
2. **프론트엔드 (Vercel)**: `frontend` 폴더를 그대로 배포 (정적 사이트). 배포 후 설정 탭에서 Render URL을 입력.

## 제출 스크린샷 체크리스트
- [ ] 데이터 요약이 보이는 채팅 화면 (질문 + 답변 포함)
- [ ] <img width="1272" height="847" alt="image" src="https://github.com/user-attachments/assets/d6469d2e-4314-4462-9658-4671d333ecf8" />

- [ ] 데이터 관리 화면 (기록 추가/수정/삭제 중 1개 동작)
- [ ] <img width="1290" height="897" alt="image" src="https://github.com/user-attachments/assets/4c0b6538-50c1-4241-b547-4b79b8372355" />
<img width="1875" height="897" alt="image" src="https://github.com/user-attachments/assets/7e2961e7-3e3d-4dab-a481-83468b824b64" />

- [ ] 대화 기록 화면 (불러오기 동작)
- [ ] <img width="1430" height="875" alt="image" src="https://github.com/user-attachments/assets/08a1c6b6-e86e-4088-8355-dc4d5ae117b7" />
<img width="1915" height="960" alt="image" src="https://github.com/user-attachments/assets/d685d1f3-852a-4d0c-b263-a138e88b0d6d" />


https://m-2-aja3.onrender.com/docs
https://vercel.com/zheltpdl/m-2


