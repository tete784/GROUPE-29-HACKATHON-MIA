from flask import Flask, request, jsonify
from flask_cors import CORS
from ocr_analyzer import analyser_texte_ocr

app = Flask(__name__)
CORS(app)  # Autoriser les requêtes cross-origin (utile si le frontend est sur un autre port)

@app.route('/analyze', methods=['POST'])
def analyze_document():
    data = request.json
    
    # Vérification de la présence des champs requis
    if not data or 'id' not in data or 'ocr_text' not in data or 'document_type' not in data:
        return jsonify({"error": "Les champs 'id', 'document_type' et 'ocr_text' sont requis."}), 400
        
    doc_id = data['id']
    doc_type = data['document_type']
    ocr_text = data['ocr_text']
    
    try:
        # Appel à la fonction d'analyse existante depuis ocr_analyzer.py
        result = analyser_texte_ocr(doc_id, ocr_text, doc_type)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": f"Une erreur est survenue lors de l'analyse : {str(e)}"}), 500

if __name__ == '__main__':
    # Lancement du serveur sur le port 5003 (uniquement local)
    app.run(debug=True, host='127.0.0.1', port=5003)
