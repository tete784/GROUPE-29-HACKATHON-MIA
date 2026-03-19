import os
import tempfile
from typing import Optional

import requests
import uvicorn
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ocr_engine import extraire_texte

ANOMALY_DETECTOR_URL = os.getenv("ANOMALY_DETECTOR_URL", "http://localhost:8001/ingest")

app = FastAPI(title="OCR Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract-and-ingest")
async def extract_and_ingest(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    x_session_id: Optional[str] = Header(None),
):
    """
    Reçoit un fichier, lance l'OCR, puis appelle automatiquement /ingest.
    Le session_id peut venir :
    - du champ form-data `session_id`
    - ou du header `x-session-id`
    """

    final_session_id = session_id or x_session_id
    if not final_session_id:
        raise HTTPException(
            status_code=400,
            detail="session_id manquant : passe-le en form-data ou dans le header x-session-id"
        )

    if not file.filename:
        raise HTTPException(status_code=400, detail="Aucun fichier envoyé")

    suffix = os.path.splitext(file.filename)[1]

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contenu = await file.read()
            tmp.write(contenu)
            tmp_path = tmp.name

        # OCR
        ocr_result = extraire_texte(tmp_path)

        # Remplacer l'id temporaire par le vrai nom du fichier
        ocr_result["id"] = file.filename

        payload = {
            "session_id": final_session_id,
            "documents": [
                {
                    "id": ocr_result["id"],
                    "document_type": ocr_result["document_type"],
                    "ocr_text": ocr_result["ocr_text"],
                }
            ]
        }

        response = requests.post(ANOMALY_DETECTOR_URL, json=payload, timeout=30)

        if response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail=f"Erreur lors de l'appel à /ingest : {response.text}"
            )

        return {
            "message": "OCR effectué et document transmis à anomaly-detector",
            "ocr_result": ocr_result,
            "ingest_result": response.json()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur OCR/ingest : {str(e)}")
    finally:
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)