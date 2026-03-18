import re
from datetime import datetime

# Je definis les patterns regex pour extraire les champs metier depuis le texte OCR brut

SIRET_RE = re.compile(r'\b(\d{14})\b')
TVA_RATE_RE = re.compile(r'TVA\s*[:\s]*(\d+(?:[.,]\d+)?)\s*%', re.IGNORECASE)
MONTANT_HT_RE = re.compile(r'(?:montant\s+HT|HT)\s*[:\s]*(\d+(?:[.,]\d{1,2})?)', re.IGNORECASE)
MONTANT_TTC_RE = re.compile(r'(?:montant\s+TTC|TTC)\s*[:\s]*(\d+(?:[.,]\d{1,2})?)', re.IGNORECASE)
DATE_RE = re.compile(r'\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})\b')
DATE_EXPIRY_RE = re.compile(
    r"(?:valable?\s+jusqu'?au|expire?\s+le|date\s+(?:de\s+)?(?:fin|expiration))\s*[:\s]*"
    r"(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})",
    re.IGNORECASE,
)


def _to_float(s: str) -> float | None:
    try:
        return float(s.replace(',', '.'))
    except (ValueError, AttributeError):
        return None


def _parse_date(d: str, m: str, y: str) -> datetime | None:
    year = int(y)
    if year < 100:
        year += 2000
    try:
        return datetime(year, int(m), int(d))
    except ValueError:
        return None


def extract_fields(ocr_text: str) -> dict:
    # J'extrais les champs structures du texte OCR en appliquant chaque pattern dans l'ordre
    fields: dict = {}

    match = SIRET_RE.search(ocr_text)
    if match:
        fields['siret'] = match.group(1)

    match = TVA_RATE_RE.search(ocr_text)
    if match:
        fields['tva'] = _to_float(match.group(1))

    match = MONTANT_HT_RE.search(ocr_text)
    if match:
        fields['montant_ht'] = _to_float(match.group(1))

    match = MONTANT_TTC_RE.search(ocr_text)
    if match:
        fields['montant_ttc'] = _to_float(match.group(1))

    match = DATE_RE.search(ocr_text)
    if match:
        fields['date_document'] = _parse_date(*match.groups())

    match = DATE_EXPIRY_RE.search(ocr_text)
    if match:
        parts = re.split(r'[/\-.]', match.group(1))
        if len(parts) == 3:
            fields['date_expiration'] = _parse_date(*parts)

    return fields
