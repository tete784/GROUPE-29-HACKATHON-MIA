# GROUPE-29-HACKATHON-MIA

## Lancement du backend Anomaly Detector (OCR)

L'API locale développée en Flask s'exécute sur le port `5003` et permet d'extraire des données de documents (factures, etc.).

### 1. Installation des dépendances
Depuis la racine du projet, installez les paquets Python requis listés dans le fichier `requirements.txt` :

```bash
pip install -r requirements.txt
```

### 2. Démarrage du serveur
Lancez le script principal de l'API :

```bash
python anomaly-detector/app.py
```

Le serveur sera alors accessible en local à l'adresse suivante : `http://127.0.0.1:5003/analyze`.

### 3. Utilisation de l'API

Pour utiliser l'API, vous devez envoyer une requête HTTP **POST** sur l'endpoint :
`http://127.0.0.1:5003/analyze`

Le corps de la requête (Body) doit être au format **JSON** et contenir les champs suivants :

```json
{
    "id": "id_001",
    "document_type": "document_type",
    "ocr_text": "text"
}
```