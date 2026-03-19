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
    # J'extrais tous les champs metier en utilisant le parseur robuste de Theo (ocr_analyzer.py)
    from ocr_analyzer import analyser_texte_ocr
    from datetime import datetime

    # Appel au script robuste avec heuristiques
    res = analyser_texte_ocr("dummy", ocr_text)
    theo_data = res.get("validated_data", {})
    
    fields: dict = {}

    if "siret" in theo_data:
        fields['siret'] = theo_data["siret"]

    # Traitement des montants
    ht_str = theo_data.get("montant_ht")
    ttc_str = theo_data.get("montant_ttc")
    
    if ht_str:
        try:
            ht = float(ht_str)
            fields['montant_ht'] = ht
        except:
            pass
            
    if ttc_str:
        try:
            ttc = float(ttc_str)
            fields['montant_ttc'] = ttc
        except:
            pass
            
    # Le validateur d'Amine s'attend a recevoir le TAUX de TVA dans le champ 'tva'
    if "montant_ht" in fields and "montant_ttc" in fields:
        ht = fields["montant_ht"]
        ttc = fields["montant_ttc"]
        if ht > 0:
            rate = round(((ttc - ht) / ht) * 100, 2)
            fields['tva'] = rate
            
            # On stocke egalement le montant de la TVA au cas ou
            fields['montant_tva'] = round(ttc - ht, 2)

    # Date document (emission)
    if "date_emission" in theo_data:
        try:
            fields['date_document'] = datetime.strptime(theo_data["date_emission"], "%d/%m/%Y")
            # Pour la base de donnees et le front, on garde la string formattee
            fields['date_emission'] = theo_data["date_emission"]
        except:
            pass

    # Date expiration
    if "expiration" in theo_data:
        try:
            fields['date_expiration'] = datetime.strptime(theo_data["expiration"], "%d/%m/%Y")
            fields['expiration'] = theo_data["expiration"]
        except:
            pass

    # IBAN
    if "iban" in theo_data:
        fields['iban'] = theo_data["iban"]

    return fields
