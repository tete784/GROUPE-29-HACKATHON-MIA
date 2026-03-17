import json
import re
import os
from datetime import datetime

def extraire_champ(texte, motifs, format_attendu=None):
    """
    Extrait un champ du texte en utilisant une liste de motifs (regex).
    Si plusieurs motifs sont fournis, on les teste dans l'ordre.
    Si format_attendu est fourni, on valide la valeur trouvée.
    """
    for motif in motifs:
        match = re.search(motif, texte, re.IGNORECASE)
        if match:
            # On récupère le premier groupe de capture
            valeur = match.group(1).strip()
            
            # Validation sommaire du format si besoin
            if format_attendu:
                if not re.fullmatch(format_attendu, valeur):
                    return "donnee_incorrecte"
            return valeur
    return "manquant"

def verifier_coherence(donnees):
    """
    Vérifie la cohérence entre les différents champs extraits.
    Retourne une liste de messages d'anomalies.
    """
    anomalies = []
    
    # 1. Cohérence des montants (Calcul de la TVA à 20%)
    ht = donnees.get("montant_ht")
    ttc = donnees.get("montant_ttc")
    
    if ht not in ["manquant", "donnee_incorrecte"] and ttc not in ["manquant", "donnee_incorrecte"]:
        try:
            val_ht = float(ht)
            val_ttc = float(ttc)
            # On vérifie si TTC est environ égal à HT * 1.2
            ttc_attendu = val_ht * 1.2
            if abs(val_ttc - ttc_attendu) > 0.05:
                # Écart détecté
                anomalies.append(f"Incohérence montants : HT ({val_ht}) * 1.2 != TTC ({val_ttc})")
        except ValueError:
            pass

    # 2. Cohérence des dates (Expiration >= Émission)
    emission = donnees.get("date_emission")
    expiration = donnees.get("expiration")
    
    if emission not in ["manquant", "donnee_incorrecte"] and expiration not in ["manquant", "donnee_incorrecte"]:
        try:
            date_debut = datetime.strptime(emission, "%d/%m/%Y")
            date_fin = datetime.strptime(expiration, "%d/%m/%Y")
            if date_fin < date_debut:
                anomalies.append(f"Incohérence dates : Expiration ({expiration}) est avant l'émission ({emission})")
        except ValueError:
            pass

    return anomalies

def analyser_texte_ocr(id_document, texte_ocr, document_type=None):
    """
    Analyse le texte brut issu d'un OCR pour en extraire les infos clés.
    """
    
    # Définition des motifs de recherche (Regex)
    
    # SIRET : 14 chiffres (on autorise des espaces lors de la capture brute)
    motifs_siret = [r"SIRET\s*:\s*([\d\s]+)"]
    format_siret = r"\d{14}"
    
    # TVA : FR suivi de 11 chiffres
    motifs_tva = [r"TVA\s*:\s*(FR[\d\s]+)"]
    format_tva = r"FR\d{11}"
    
    # Montant HT : "HT" ou "hors taxe" avant ou après le nombre
    motifs_ht = [
        r"(?:Montant|Prix)?\s*(?:HT|hors\s*taxes?)\s*[:]?\s*([\d\s\.,]+)",
        r"([\d\s\.,]+)\s*(?:€|EUR|euros?)\s*(?:HT|hors\s*taxes?)",
        r"([\d\s\.,]+)\s*(?:HT|hors\s*taxes?)"
    ]
    
    # Montant TTC : "TTC" ou "toutes taxes comprises"
    motifs_ttc = [
        r"(?:Montant|Prix)?\s*(?:TTC|toutes\s*taxes?\s*comprises?)\s*[:]?\s*([\d\s\.,]+)",
        r"([\d\s\.,]+)\s*(?:€|EUR|euros?)\s*(?:TTC|toutes\s*taxes?\s*comprises?)",
        r"([\d\s\.,]+)\s*(?:TTC|toutes\s*taxes?\s*comprises?)"
    ]
    
    # Date Émission : différents formats de label avant la date JJ/MM/AAAA
    motifs_emission = [
        r"Date d'émission\s*:\s*(\d{2}/\d{2}/\d{4})",
        r"Date émission\s*:\s*(\d{2}/\d{2}/\d{4})",
        r"Date\s*:\s*(\d{2}/\d{2}/\d{4})"
    ]
    
    # Expiration : "Date expiration" ou "Validité"
    motifs_expiration = [
        r"Date expiration\s*:\s*(\d{2}/\d{2}/\d{4})",
        r"Date d'expiration\s*:\s*(\d{2}/\d{2}/\d{4})",
        r"Validité[^\d]*(\d{2}/\d{2}/\d{4})",
    ]
    
    # IBAN : préfixe FR + 25 caractères (on limite la capture pour éviter le BIC)
    motifs_iban = [r"IBAN\s*:\s*([A-Z0-9 ]{15,40})"]
    format_iban = r"FR\d{2}[A-Z0-9]{23}"

    # Fonctions utilitaires internes pour le nettoyage

    def extraire_et_nettoyer(motifs, regex_format=None, remove_spaces=False):
        valeur = extraire_champ(texte_ocr, motifs)
        if valeur not in ["manquant", "donnee_incorrecte"]:
            if remove_spaces:
                valeur = valeur.replace(" ", "")
            if regex_format and not re.fullmatch(regex_format, valeur):
                return "donnee_incorrecte"
        return valeur

    def extraire_montant(motifs):
        valeur = extraire_champ(texte_ocr, motifs)
        if valeur not in ["manquant", "donnee_incorrecte"]:
            # On nettoie le format numérique (virgule -> point, suppression espaces)
            valeur = valeur.replace(",", ".").replace(" ", "")
            try:
                chiffre = float(valeur)
                # On formate sans décimales si c'est un nombre rond
                if chiffre == int(chiffre):
                    return str(int(chiffre))
                else:
                    return str(chiffre)
            except ValueError:
                return "donnee_incorrecte"
        return valeur

    # Étape 1 : Extraction brute des données

    brutes = {
        "siret": extraire_et_nettoyer(motifs_siret, format_siret, True),
        "tva": extraire_et_nettoyer(motifs_tva, format_tva, True),
        "montant_ht": extraire_montant(motifs_ht),
        "montant_ttc": extraire_montant(motifs_ttc),
        "date_emission": extraire_champ(texte_ocr, motifs_emission),
        "expiration": extraire_champ(texte_ocr, motifs_expiration),
        "iban": extraire_et_nettoyer(motifs_iban, format_iban, True)
    }
    
    # Étape 2 : Vérification de la cohérence

    liste_anomalies = verifier_coherence(brutes)
    
    # Étape 3 : Filtrage des données validées

    validees = {}
    for cle, val in brutes.items():
        # On ignore ce qui est déjà marqué comme manquant ou incorrect
        if val in ["manquant", "donnee_incorrecte"]:
            continue
            
        # Si une anomalie touche les montants, on les écarte de la partie validée
        if cle in ["montant_ht", "montant_ttc"] and any("montants" in a.lower() for a in liste_anomalies):
            continue
        # Pareil pour les dates
        if cle in ["date_emission", "expiration"] and any("dates" in a.lower() for a in liste_anomalies):
            continue
            
        validees[cle] = val

    result = {
        "document_id": id_document,
        "extracted_data": brutes,
        "validated_data": validees,
        "anomalies": liste_anomalies
    }
    
    if document_type is not None:
        result["document_type"] = document_type
        
    return result

def main():
    # Chemins des fichiers relatifs au script
    dossier_actuel = os.path.dirname(os.path.abspath(__file__))
    fichier_entree = os.path.join(dossier_actuel, "dataset_ocr.json")
    fichier_sortie = os.path.join(dossier_actuel, "parsed_results.json")
    
    if not os.path.exists(fichier_entree):
        print(f"Erreur : le fichier {fichier_entree} est introuvable.")
        return

    # Chargement du JSON source
    with open(fichier_entree, "r", encoding="utf-8") as f:
        donnees_source = json.load(f)
        
    documents = donnees_source.get("documents", [])
    resultats_finaux = []
    
    # Traitement de chaque document
    for doc in documents:
        infos_extraites = analyser_texte_ocr(doc["id"], doc["ocr_text"])
        resultats_finaux.append(infos_extraites)
        
    # Sauvegarde des résultats
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        json.dump(resultats_finaux, f, indent=2, ensure_ascii=False)
        
    print(f"Analyse terminée. Les résultats sont dans {fichier_sortie}")

if __name__ == "__main__":
    main()
