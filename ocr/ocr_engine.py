import fitz
import pytesseract
from PIL import Image
import io
import os
import docx 

def extraire_texte_pdf(chemin_pdf):
    """
    Extrait le texte d'un PDF uniquement via OCR (Tesseract).
    On transforme chaque page en image pour simuler la vision humaine.
    """
    document = fitz.open(chemin_pdf)
    texte_complet = ""

    for page in document:
        # On utilise un zoom (matrice) pour avoir une meilleure précision OCR
        matrice = fitz.Matrix(2, 2)
        image_page = page.get_pixmap(matrix=matrice)
        
        # Conversion du pixmap en format image PIL
        donnees_image = image_page.tobytes("png")
        img = Image.open(io.BytesIO(donnees_image))
        
        # Passage par Tesseract
        texte_page = pytesseract.image_to_string(img, lang='fra+eng')
        texte_complet += texte_page + "\n"

    document.close()
    return texte_complet.strip()

def extraire_texte_docx(chemin_docx):
    """
    Extrait le texte d'un fichier Word (.docx) nativement.
    """
    doc = docx.Document(chemin_docx)
    texte = [paragraphe.text for paragraphe in doc.paragraphs]
    return "\n".join(texte).strip()

def extraire_texte_image(chemin_image):
    """
    Extrait le texte d'une image via OCR.
    """
    img = Image.open(chemin_image)
    return pytesseract.image_to_string(img, lang='fra+eng').strip()

def detecter_type_document(texte):
    """
    Détecte le type de document en fonction des mots-clés présents dans le texte.
    """
    texte = texte.lower()

    types = {
        "facture": ["facture", "ht", "ttc", "tva", "montant", "paiement"],
        "devis": ["devis", "estimation", "validité"],
        "attestation": ["attestation", "certifie", "organisme"],
        "presentation": ["hackathon", "présentation", "groupe"],
        "contrat": ["contrat", "engagement", "signature"],
        "courrier": ["madame", "monsieur", "objet"]
    }

    scores = {}

    for type_doc, mots in types.items():
        score = 0
        for mot in mots:
            if mot in texte:
                score += 1
        scores[type_doc] = score

    # Le type avec le meilleur score
    meilleur = max(scores, key=scores.get)

    if scores[meilleur] == 0:
        return "inconnu"

    return meilleur

def extraire_texte(chemin_fichier):
    """
    Fonction principale qui choisit la méthode d'extraction selon l'extension.
    """
    if not os.path.exists(chemin_fichier):
        raise FileNotFoundError(f"Fichier introuvable : {chemin_fichier}")

    extension = os.path.splitext(chemin_fichier)[1].lower()
    texte_extrait = ""

    if extension == ".pdf":
        texte_extrait = extraire_texte_pdf(chemin_fichier)
    elif extension in [".docx", ".doc"]:
        texte_extrait = extraire_texte_docx(chemin_fichier)
    elif extension in [".png", ".jpg", ".jpeg", ".tiff"]:
        texte_extrait = extraire_texte_image(chemin_fichier)
    else:
        # Fallback : on essaie quand même une lecture brute si c'est du texte
        try:
            with open(chemin_fichier, "r", encoding="utf-8") as f:
                texte_extrait = f.read()
        except:
            raise ValueError(f"Format de fichier non supporté : {extension}")

    # Récupération de l'ID (nom du fichier)
    id_doc = os.path.splitext(os.path.basename(chemin_fichier))[0]

    # Détection automatique du type de document
    type_doc = detecter_type_document(texte_extrait)

    return {
        "id": id_doc,
        "document_type": type_doc,
        "ocr_text": texte_extrait
    }

if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        chemin = sys.argv[1]
        try:
            print(json.dumps(extraire_texte(chemin), indent=4, ensure_ascii=False))
        except Exception as e:
            print(f"Erreur : {e}")
    else:
        print("Usage : python ocr_engine.py <nom_du_fichier>")
