import os
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

# Je charge les variables d'environnement depuis .env avant toute utilisation
load_dotenv()

_client: MongoClient | None = None


def get_client() -> MongoClient:
    # Je maintiens un client MongoDB singleton pour eviter les reconnexions inutiles
    global _client
    if _client is None:
        uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        _client = MongoClient(uri)
    return _client


def get_db() -> Database:
    return get_client()['document_processing']


# --- Lecture Bronze ---

def fetch_bronze_unprocessed(session_id: str | None = None) -> list[dict]:
    # Je recupere les documents dont l'OCR est fait mais l'analyse anomalie pas encore effectuee
    query: dict = {'ocr_processed': True, 'anomaly_checked': {'$ne': True}}
    if session_id:
        query['session_id'] = session_id
    return list(get_db()['layer_bronze'].find(query, {'_id': 0}))


# --- Ecriture Silver ---

def save_silver(doc: dict) -> None:
    get_db()['layer_silver'].update_one(
        {'document_id': doc['document_id']},
        {'$set': doc},
        upsert=True,
    )


# --- Ecriture Gold ---

def save_gold(result: dict) -> None:
    get_db()['layer_gold'].update_one(
        {'document_id': result['document_id']},
        {'$set': result},
        upsert=True,
    )


# --- Marquage Bronze traite ---

def mark_bronze_checked(document_id: str) -> None:
    get_db()['layer_bronze'].update_one(
        {'document_id': document_id},
        {'$set': {'anomaly_checked': True, 'checked_at': datetime.utcnow()}},
    )


# --- Lecture Gold (pour l'API de resultats) ---

def fetch_gold_by_session(session_id: str) -> list[dict]:
    # Je cherche d'abord par session_id, puis directement en gold si introuvable en bronze
    bronze_docs = list(get_db()['layer_bronze'].find(
        {'session_id': session_id},
        {'document_id': 1, 'id': 1, '_id': 0},
    ))
    if not bronze_docs:
        return list(get_db()['layer_gold'].find({'session_id': session_id}, {'_id': 0}))
    doc_ids = [d.get('document_id') or d.get('id') for d in bronze_docs]
    return list(get_db()['layer_gold'].find({'document_id': {'$in': doc_ids}}, {'_id': 0}))


def fetch_all_gold() -> list[dict]:
    return list(get_db()['layer_gold'].find({}, {'_id': 0}))
