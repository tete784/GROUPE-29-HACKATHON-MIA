import re
from datetime import datetime

# Je definis les patterns pour chaque champ, du plus precis au plus generique
# Integre les patterns de Theo (ocr_analyzer.py) avec les miens en fusion

# SIRET : label explicite en priorite, fallback sur 14 chiffres bruts
SIRET_PATTERNS = [
    r"SIRET\s*[:\s]\s*([\d\s]{14,17})",
    r'\b(\d{14})\b',
]

# TVA taux (%) pour la validation mathematique
TVA_RATE_RE = re.compile(r'TVA\s*[:\s]*(\d+(?:[.,]\d+)?)\s*%', re.IGNORECASE)

# TVA numero (FR + 11 chiffres) pour identification fournisseur
TVA_NUM_RE = re.compile(r'TVA\s*[:\s]*\s*(FR[\d\s]{11,13})', re.IGNORECASE)

# Montants HT : 3 patterns de Theo plus exhaustifs que le mien initial
MONTANT_HT_PATTERNS = [
    r"(?:Montant|Prix)?\s*(?:HT|hors\s*taxes?)\s*[:]?\s*([\d\s\.,]+)",
    r"([\d\s\.,]+)\s*(?:€|EUR|euros?)\s*(?:HT|hors\s*taxes?)",
    r"([\d\s\.,]+)\s*(?:HT|hors\s*taxes?)",
]

# Montants TTC : meme logique
MONTANT_TTC_PATTERNS = [
    r"(?:Montant|Prix)?\s*(?:TTC|toutes\s*taxes?\s*comprises?)\s*[:]?\s*([\d\s\.,]+)",
    r"([\d\s\.,]+)\s*(?:€|EUR|euros?)\s*(?:TTC|toutes\s*taxes?\s*comprises?)",
    r"([\d\s\.,]+)\s*(?:TTC|toutes\s*taxes?\s*comprises?)",
]

# Date emission : patterns labels de Theo
DATE_EMISSION_PATTERNS = [
    r"Date\s+d['\u2019]émission\s*[:\s]\s*(\d{2}/\d{2}/\d{4})",
    r"Date\s+émission\s*[:\s]\s*(\d{2}/\d{2}/\d{4})",
    r"Date\s*[:\s]\s*(\d{2}/\d{2}/\d{4})",
    r'\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})\b',
]

# Date expiration : fusion des deux approches
DATE_EXPIRY_PATTERNS = [
    r"Date\s+(?:d['\u2019])?expiration\s*[:\s]\s*(\d{2}/\d{2}/\d{4})",
    r"Validit[eé][^\d]*(\d{2}/\d{2}/\d{4})",
    r"(?:valable?\s+jusqu'?au|expire?\s+le)\s*[:\s]*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})",
]

# IBAN : pattern de Theo
IBAN_RE = re.compile(r'IBAN\s*[:\s]\s*([A-Z0-9 ]{15,40})', re.IGNORECASE)
IBAN_FORMAT = re.compile(r'FR\d{2}[A-Z0-9]{23}')


def _first_match(text: str, patterns: list[str]) -> re.Match | None:
    # J'essaie chaque pattern dans l'ordre et retourne le premier match
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m
    return None


def _to_float(s: str) -> float | None:
    try:
        return float(s.replace(' ', '').replace(',', '.'))
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


def _parse_date_str(s: str) -> datetime | None:
    parts = re.split(r'[/\-.]', s.strip())
    if len(parts) == 3:
        return _parse_date(*parts)
    return None


def extract_fields(ocr_text: str) -> dict:
    # J'extrais tous les champs metier en combinant mes patterns et ceux de Theo
    fields: dict = {}

    # SIRET
    m = _first_match(ocr_text, SIRET_PATTERNS)
    if m:
        siret = m.group(1).replace(' ', '')
        if len(siret) == 14:
            fields['siret'] = siret

    # TVA taux (pour validation HT*TVA=TTC)
    m = TVA_RATE_RE.search(ocr_text)
    if m:
        fields['tva'] = _to_float(m.group(1))

    # TVA numero fournisseur
    m = TVA_NUM_RE.search(ocr_text)
    if m:
        fields['tva_numero'] = m.group(1).replace(' ', '')

    # Montant HT
    m = _first_match(ocr_text, MONTANT_HT_PATTERNS)
    if m:
        val = _to_float(m.group(1))
        if val is not None:
            fields['montant_ht'] = val

    # Montant TTC
    m = _first_match(ocr_text, MONTANT_TTC_PATTERNS)
    if m:
        val = _to_float(m.group(1))
        if val is not None:
            fields['montant_ttc'] = val

    # Date document (emission)
    m = _first_match(ocr_text, DATE_EMISSION_PATTERNS)
    if m:
        groups = m.groups()
        if len(groups) == 1:
            fields['date_document'] = _parse_date_str(groups[0])
        elif len(groups) == 3:
            fields['date_document'] = _parse_date(*groups)

    # Date expiration
    m = _first_match(ocr_text, DATE_EXPIRY_PATTERNS)
    if m:
        fields['date_expiration'] = _parse_date_str(m.group(1))

    # IBAN
    m = IBAN_RE.search(ocr_text)
    if m:
        iban = m.group(1).replace(' ', '')
        if IBAN_FORMAT.fullmatch(iban):
            fields['iban'] = iban

    return fields
