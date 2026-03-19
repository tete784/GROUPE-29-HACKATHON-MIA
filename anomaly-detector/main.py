import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel

from flows import analyze_session_flow
from collections import Counter

from mongo_client import fetch_all_gold, fetch_gold_by_session, get_db, save_bronze


from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # J'initialise la connexion MongoDB une seule fois au demarrage du service
    get_db()
    yield


app = FastAPI(title="Anomaly Detector", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Schemas ---

class OcrDocument(BaseModel):
    id: str
    document_type: str
    ocr_text: str


class IngestRequest(BaseModel):
    session_id: str
    documents: list[OcrDocument]


class AnalyzeRequest(BaseModel):
    session_id: str | None = None


# --- Endpoints ---

@app.post("/ingest", status_code=202)
def ingest_and_analyze(body: IngestRequest, background_tasks: BackgroundTasks):
    for doc in body.documents:
        save_bronze({
            'document_id': doc.id,
            'document_type': doc.document_type,
            'ocr_text': doc.ocr_text,
            'session_id': body.session_id,
            'ocr_processed': True,
            'uploaded_at': datetime.utcnow(),
        })

    background_tasks.add_task(analyze_session_flow, body.session_id)

    return {
        "status": "accepted",
        "session_id": body.session_id,
        "message": "Documents ingérés, analyse lancée en arrière-plan"
    }

@app.post("/analyze", status_code=202)
async def trigger_analysis(body: AnalyzeRequest, background_tasks: BackgroundTasks):
    # Je declenche l'analyse en arriere-plan (utile si bronze est deja peuple)
    background_tasks.add_task(analyze_session_flow, body.session_id)
    return {"status": "started", "session_id": body.session_id}


@app.get("/results")
def get_all_results():
    return fetch_all_gold()


@app.get("/results/{session_id}")
def get_session_results(session_id: str):
    results = fetch_gold_by_session(session_id)
    if not results:
        raise HTTPException(status_code=404, detail="Session introuvable ou non encore traitee")
    return results


@app.get("/stats")
def get_stats():
    all_results = fetch_all_gold()
    if not all_results:
        return {"total": 0, "fraud_count": 0, "fraud_rate": 0, "avg_risk_score": 0, "top_anomaly": None}

    total = len(all_results)
    fraud_count = sum(1 for r in all_results if r.get('fraud_detected'))
    fraud_rate = round(fraud_count / total * 100, 1)
    scores = [r.get('risk_score', 0) for r in all_results]
    avg_risk_score = round(sum(scores) / len(scores), 1)

    all_issues = [issue for r in all_results for issue in r.get('issues', [])]
    top_anomaly = None
    if all_issues:
        prefixes = [i.split(':')[0].strip() for i in all_issues]
        top_anomaly = Counter(prefixes).most_common(1)[0][0]

    return {
        "total": total,
        "fraud_count": fraud_count,
        "fraud_rate": fraud_rate,
        "avg_risk_score": avg_risk_score,
        "top_anomaly": top_anomaly,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8001)), reload=True)
