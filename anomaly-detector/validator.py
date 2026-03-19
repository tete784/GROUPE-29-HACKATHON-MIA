from datetime import datetime

# Taux de TVA legaux en France
FR_TVA_RATES = frozenset({0.0, 2.1, 5.5, 8.5, 10.0, 20.0})

# Tolerance de 5% pour absorber les erreurs d'arrondi OCR sur les montants
AMOUNT_TOLERANCE = 0.05


def _luhn(number: str) -> bool:
    # Je valide le checksum SIRET/SIREN via l'algorithme de Luhn
    digits = [int(d) for d in number]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0


def validate_siret(siret: str | None) -> str | None:
    if not siret:
        return "SIRET absent du document"
    if not siret.isdigit() or len(siret) != 14:
        return f"Format SIRET invalide: {siret} (14 chiffres attendus)"
    if not _luhn(siret):
        return f"Checksum SIRET invalide: {siret}"
    return None


def validate_tva_rate(tva: float | None) -> str | None:
    if tva is None:
        return None
    if not any(abs(tva - r) < 0.1 for r in FR_TVA_RATES):
        return f"Taux TVA non reconnu: {tva}% (taux FR: {sorted(FR_TVA_RATES)})"
    return None


def validate_amounts(ht: float | None, tva: float | None, ttc: float | None) -> str | None:
    if None in (ht, tva, ttc):
        return None
    expected = round(ht * (1 + tva / 100), 2)
    if abs(expected - ttc) / max(ttc, 0.01) > AMOUNT_TOLERANCE:
        return f"Incoherence montants: HT={ht} * (1+{tva}%) = {expected} != TTC={ttc}"
    return None


def validate_expiry(date_exp: datetime | None, doc_type: str) -> str | None:
    if date_exp is None or doc_type != 'attestation':
        return None
    if date_exp < datetime.now():
        return f"Attestation expiree le {date_exp.strftime('%d/%m/%Y')}"
    return None


def _cross_siret_issues(documents: list[dict]) -> list[str]:
    # Je compare les SIRET entre tous les documents du meme lot pour detecter les incoherences
    sirets = {doc['document_id']: doc.get('siret') for doc in documents if doc.get('siret')}
    unique = set(sirets.values())
    if len(unique) > 1:
        return [f"SIRET incoherents dans le lot: {unique}"]
    return []


ISSUE_WEIGHTS = {
    'siret': 40,
    'tva_rate': 25,
    'amounts': 25,
    'expiry': 10,
}


def _compute_risk_score(issues_by_type: dict) -> int:
    score = 0
    if issues_by_type.get('siret'):
        score += ISSUE_WEIGHTS['siret']
    if issues_by_type.get('tva_rate'):
        score += ISSUE_WEIGHTS['tva_rate']
    if issues_by_type.get('amounts'):
        score += ISSUE_WEIGHTS['amounts']
    if issues_by_type.get('expiry'):
        score += ISSUE_WEIGHTS['expiry']
    return min(score, 100)


def analyze_document(doc: dict) -> dict:
    issues_by_type = {
        'siret': validate_siret(doc.get('siret')),
        'tva_rate': validate_tva_rate(doc.get('tva')),
        'amounts': validate_amounts(doc.get('montant_ht'), doc.get('tva'), doc.get('montant_ttc')),
        'expiry': validate_expiry(doc.get('date_expiration'), doc.get('type', '')),
    }
    issues = [v for v in issues_by_type.values() if v]
    risk_score = _compute_risk_score(issues_by_type)

    return {
        'document_id': doc['document_id'],
        'status': 'fraud_suspected' if issues else 'validated',
        'fraud_detected': bool(issues),
        'risk_score': risk_score,
        'issues': issues,
        'validated_at': datetime.utcnow(),
    }


def analyze_session(documents: list[dict]) -> list[dict]:
    # J'analyse chaque document individuellement puis j'applique les verifications croisee
    results = [analyze_document(doc) for doc in documents]
    cross_issues = _cross_siret_issues(documents)

    if cross_issues:
        for result in results:
            result['issues'].extend(cross_issues)
            result['fraud_detected'] = True
            result['status'] = 'fraud_suspected'

    return results
