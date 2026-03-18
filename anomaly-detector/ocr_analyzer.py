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
    
<<<<<<< HEAD
    # 1. Cohérence des montants (Calcul de la TVA à 20%)
    ht = donnees.get("montant_ht")
    ttc = donnees.get("montant_ttc")
=======
    # 1. Cohérence des montants (Validation multi-TVA et équation stricte)
    ht = donnees.get("montant_ht")
    ttc = donnees.get("montant_ttc")
    tva = donnees.get("tva")
>>>>>>> origin/main
    
    if ht not in ["manquant", "donnee_incorrecte"] and ttc not in ["manquant", "donnee_incorrecte"]:
        try:
            val_ht = float(ht)
            val_ttc = float(ttc)
<<<<<<< HEAD
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
=======
            
            # Vérification absolue HT + TVA = TTC si TVA extraite
            if tva not in ["manquant", "donnee_incorrecte"]:
                val_tva = float(tva)
                if abs((val_ht + val_tva) - val_ttc) > 0.05:
                    anomalies.append(f"Incohérence entre montant HT, TVA et TTC : HT ({val_ht}) + TVA ({val_tva}) != TTC ({val_ttc})")
            
            # Les taux de TVA existants : 0, 1.05%, 1.75%, 2.1%, 5.5%, 8.5%, 10%, 20%
            taux_tva_possibles = [0, 1.05, 1.75, 2.1, 5.5, 8.5, 10, 20]
            valide = False
            
            for taux in taux_tva_possibles:
                ttc_attendu = val_ht * (1 + taux / 100)
                if abs(val_ttc - ttc_attendu) <= 0.05:
                    valide = True
                    break
                    
            if not valide:
                if val_ttc < val_ht * 0.99 or val_ttc > val_ht * 1.20 + 0.05:
                    anomalies.append(f"Incohérence montants : le TTC ({val_ttc}) ne correspond à aucun taux connu et sort de l'encadrement valide vis-à-vis du HT ({val_ht})")
        except ValueError:
            pass

    # 2. Cohérence des dates (Émission et Expiration)
    emission = donnees.get("date_emission")
    expiration = donnees.get("expiration")
    
    if emission not in ["manquant", "donnee_incorrecte"]:
        try:
            date_debut = datetime.strptime(emission, "%d/%m/%Y")
            
            # Une facture ne peut pas être émise dans le futur
            if date_debut > datetime.now():
                anomalies.append("Date d’émission dans le futur")
                
            if expiration not in ["manquant", "donnee_incorrecte"]:
                date_fin = datetime.strptime(expiration, "%d/%m/%Y")
                if date_fin < date_debut:
                    anomalies.append(f"Incohérence dates : Expiration ({expiration}) est avant l'émission ({emission})")
>>>>>>> origin/main
        except ValueError:
            pass

    return anomalies

def analyser_texte_ocr(id_document, texte_ocr, document_type=None):
    """
    Analyse le texte brut issu d'un OCR pour en extraire les infos clés.
    """
    
    # Définition des motifs de recherche (Regex)
    
    # SIRET : 14 chiffres (on autorise des espaces lors de la capture brute)
<<<<<<< HEAD
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
=======
    motifs_siret = [r"SIRET[^0-9]*([0-9\s]+)"]
    format_siret = r"\d{14}"
    
    # TVA : Montant de la TVA (et non pas le SIRET de TVA intra)
    motifs_tva = [
        r"(?:Montant|Total|Totat|Tota)?[ \t]*TVA(?:[^0-9\n]*\d+[\.,]?\d*\s*%)?[^0-9\n]*([0-9]+[0-9 \t\.,]*)(?:€|EUR|euros?)?",
        r"([0-9]+[0-9 \t\.,]*)[^0-9\n]*(?:Montant|Total|Totat|Tota)?[ \t]*TVA"
    ]
    
    # Montant HT : "HT" ou "hors taxe" sur la même ligne ou suivante (grâce au stop newline)
    motifs_ht = [
        r"(?:Montant|Prix|Total|Totat|Tota)?\s*(?:HT|hors\s*taxes?)[^0-9\n]*([0-9]+[0-9 \t\.,t]*)(?:€|EUR|euros?)?",
        r"([0-9]+[0-9 \t\.,t]*)[^0-9\n]*(?:HT|hors\s*taxes?)"
>>>>>>> origin/main
    ]
    
    # Montant TTC : "TTC" ou "toutes taxes comprises"
    motifs_ttc = [
<<<<<<< HEAD
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
=======
        r"(?:Montant|Prix|Total|Totat|Tota)?\s*(?:TTC|toutes\s*taxes?\s*comprises?)[^0-9\n]*([0-9]+[0-9 \t\.,t]*)(?:€|EUR|euros?)?",
        r"([0-9]+[0-9 \t\.,t]*)[^0-9\n]*(?:TTC|toutes\s*taxes?\s*comprises?)"
    ]
    
    # Date Émission : différents formats de label avant la date JJ/MM/AAAA ou JJ mois AAAA
    motifs_emission = [
        r"Date d'émission\s*[:]?\s*(\d{1,2}[\s/\-\.][a-zA-Z0-9]+[\s/\-\.]\d{2,4})",
        r"Date émission\s*[:]?\s*(\d{1,2}[\s/\-\.][a-zA-Z0-9]+[\s/\-\.]\d{2,4})",
        r"Date\s*[:]?\s*(\d{1,2}[\s/\-\.][a-zA-Z0-9]+[\s/\-\.]\d{2,4})"
    ]
    
    # Expiration : "Date expiration" ou "Validité" ou "Échéance"
    motifs_expiration = [
        r"Date d'expiration[^0-9]*(\d{1,2}[\s/\-\.][a-zA-Z0-9]+[\s/\-\.]\d{2,4})",
        r"Date expiration[^0-9]*(\d{1,2}[\s/\-\.][a-zA-Z0-9]+[\s/\-\.]\d{2,4})",
        r"Validité[^\d]*(\d{1,2}[\s/\-\.][a-zA-Z0-9]+[\s/\-\.]\d{2,4})",
        r"[EÉeé]ch[eé]ance[^\d]*(\d{1,2}[\s/\-\.][a-zA-Z0-9]+[\s/\-\.]\d{2,4})"
>>>>>>> origin/main
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
<<<<<<< HEAD
            # On nettoie le format numérique (virgule -> point, suppression espaces)
            valeur = valeur.replace(",", ".").replace(" ", "")
            try:
                chiffre = float(valeur)
                # On formate sans décimales si c'est un nombre rond
=======
            # On nettoie le format numérique (OCR t -> 1, , -> .)
            valeur = valeur.replace("t", "1").replace("T", "1")
            valeur = valeur.replace("€", "").replace("EUR", "").replace("euros", "").replace("euro", "")
            valeur = valeur.replace(",", ".").replace(" ", "")
            try:
                chiffre = float(valeur)
>>>>>>> origin/main
                if chiffre == int(chiffre):
                    return str(int(chiffre))
                else:
                    return str(chiffre)
            except ValueError:
                return "donnee_incorrecte"
        return valeur

<<<<<<< HEAD
=======
    def parse_date_string(valeur):
        valeur = valeur.lower().strip()
        # Séparateurs uniformisés en un seul espace
        valeur = re.sub(r'[\s/\-\.]+', ' ', valeur)
        parts = valeur.split(' ')
        if len(parts) == 3:
            jour, mois, annee = parts
            jour = jour.zfill(2)
            mois_map = {
                "janvier": "01", "février": "02", "fevrier": "02", "mars": "03",
                "avril": "04", "mai": "05", "juin": "06", "juillet": "07",
                "août": "08", "aout": "08", "septembre": "09", "octobre": "10",
                "novembre": "11", "décembre": "12", "decembre": "12"
            }
            if mois in mois_map:
                mois = mois_map[mois]
            elif mois.isdigit():
                mois = mois.zfill(2)
            else:
                return "donnee_incorrecte"
            
            if len(annee) == 2:
                annee = "20" + annee
            elif len(annee) != 4 or not annee.isdigit():
                return "donnee_incorrecte"
                
            return f"{jour}/{mois}/{annee}"
        return "donnee_incorrecte"

    def extraire_date(motifs):
        valeur = extraire_champ(texte_ocr, motifs)
        if valeur not in ["manquant", "donnee_incorrecte"]:
            return parse_date_string(valeur)
        return valeur

>>>>>>> origin/main
    # Étape 1 : Extraction brute des données

    brutes = {
        "siret": extraire_et_nettoyer(motifs_siret, format_siret, True),
<<<<<<< HEAD
        "tva": extraire_et_nettoyer(motifs_tva, format_tva, True),
        "montant_ht": extraire_montant(motifs_ht),
        "montant_ttc": extraire_montant(motifs_ttc),
        "date_emission": extraire_champ(texte_ocr, motifs_emission),
        "expiration": extraire_champ(texte_ocr, motifs_expiration),
        "iban": extraire_et_nettoyer(motifs_iban, format_iban, True)
    }
    
=======
        "tva": extraire_montant(motifs_tva),
        "montant_ht": extraire_montant(motifs_ht),
        "montant_ttc": extraire_montant(motifs_ttc),
        "date_emission": extraire_date(motifs_emission),
        "expiration": extraire_date(motifs_expiration),
        "iban": extraire_et_nettoyer(motifs_iban, format_iban, True)
    }
    
    # SECTION HEURISTIQUES DE SECOURS (au secours)
    
    # 1. Fallback pour la date d'émission
    if brutes["date_emission"] in ["manquant", "donnee_incorrecte"]:
        en_tete = texte_ocr[:500]
        match = re.search(r"(\d{1,2}[\s/\-\.][a-zA-Z0-9]+[\s/\-\.]\d{2,4})", en_tete)
        if match:
            parsed = parse_date_string(match.group(1))
            if parsed != "donnee_incorrecte":
                brutes["date_emission"] = parsed

    # 2. Fallback pour les montants (Les derniers montants en € du document)
    if brutes["montant_ht"] in ["manquant", "donnee_incorrecte"] or brutes["montant_ttc"] in ["manquant", "donnee_incorrecte"]:
        prices_matches = re.findall(r"([0-9]+[0-9 \t\.,]*)\s*(?:€|EUR|euros)", texte_ocr, re.IGNORECASE)
        valeurs_propres = []
        for p in prices_matches:
            clean = p.replace(",", ".").replace(" ", "")
            try:
                val = float(clean)
                valeurs_propres.append(val)
            except ValueError:
                pass
                
        # Sur une facture (même cassée par l'OCR), les totaux sont généralement à la toute fin
        if len(valeurs_propres) >= 3:
            brutes["montant_ht"] = str(valeurs_propres[-3])
            brutes["tva"] = str(valeurs_propres[-2])
            brutes["montant_ttc"] = str(valeurs_propres[-1])
        elif len(valeurs_propres) >= 2:
            brutes["montant_ht"] = str(min(valeurs_propres[-1], valeurs_propres[-2]))
            brutes["montant_ttc"] = str(max(valeurs_propres[-1], valeurs_propres[-2]))
            
    # 3. Correction logique des montants aberrants et déduction
    ht_val = brutes["montant_ht"]
    tva_val = brutes["tva"]
    
    # Rejet de la TVA si elle est supérieure au HT (grossière erreur d'OCR)
    if ht_val not in ["manquant", "donnee_incorrecte"] and tva_val not in ["manquant", "donnee_incorrecte"]:
        try:
            if float(tva_val) > float(ht_val):
                brutes["tva"] = "donnee_incorrecte"
        except ValueError:
            pass

    # Déduction logique de la TVA si manquante/rejetée mais que HT et TTC sont bons
    if brutes["montant_ht"] not in ["manquant", "donnee_incorrecte"] and brutes["montant_ttc"] not in ["manquant", "donnee_incorrecte"]:
        if brutes["tva"] in ["manquant", "donnee_incorrecte"]:
            try:
                v_ht = float(brutes["montant_ht"])
                v_ttc = float(brutes["montant_ttc"])
                if v_ttc >= v_ht:
                    brutes["tva"] = str(round(v_ttc - v_ht, 2))
            except ValueError:
                pass

>>>>>>> origin/main
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
