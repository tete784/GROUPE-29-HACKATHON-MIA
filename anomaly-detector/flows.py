from datetime import datetime

from prefect import flow, task, get_run_logger

from extractor import extract_fields
from validator import analyze_session
from mongo_client import (
    fetch_bronze_unprocessed,
    save_silver,
    save_gold,
    mark_bronze_checked,
)


@task(name="extract-and-save-silver", retries=2, retry_delay_seconds=5)
def extract_and_save_silver(bronze_doc: dict) -> dict:
    # J'extrais les champs structures depuis le texte OCR et je les persiste en couche Silver
    logger = get_run_logger()

    fields = extract_fields(bronze_doc.get('ocr_text', ''))
    # Je gere les deux conventions de nommage : 'id' (OCR engine) et 'document_id' (schema Amine)
    doc_id = bronze_doc.get('document_id') or bronze_doc.get('id', 'unknown')
    silver_doc = {
        'document_id': doc_id,
        'type': bronze_doc.get('document_type', 'inconnu'),
        'session_id': bronze_doc.get('session_id'),
        'parsed_at': datetime.utcnow(),
        **fields,
    }

    save_silver(silver_doc)
    logger.info(f"Silver: {doc_id} - {len(fields)} champ(s) extraits")
    return silver_doc


@task(name="validate-and-save-gold")
def validate_and_save_gold(silver_docs: list[dict]) -> list[dict]:
    # J'analyse les anomalies sur l'ensemble du lot et je persiste les resultats en couche Gold
    logger = get_run_logger()

    results = analyze_session(silver_docs)
    for result in results:
        save_gold(result)
        mark_bronze_checked(result['document_id'])
        logger.info(
            f"Gold: {result['document_id']} -> {result['status']} "
            f"({len(result['issues'])} anomalie(s))"
        )

    return results


@flow(name="analyze-documents-session", log_prints=True)
def analyze_session_flow(session_id: str | None = None) -> list[dict]:
    # Je coordonne le pipeline complet Bronze -> Silver -> Gold pour une session donnee
    bronze_docs = fetch_bronze_unprocessed(session_id)

    if not bronze_docs:
        print(f"Aucun document a analyser (session={session_id})")
        return []

    print(f"{len(bronze_docs)} document(s) a analyser pour la session '{session_id}'")

    silver_docs = [extract_and_save_silver(doc) for doc in bronze_docs]
    return validate_and_save_gold(silver_docs)
