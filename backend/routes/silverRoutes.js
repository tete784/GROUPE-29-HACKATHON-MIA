const express = require("express");
const router = express.Router();

module.exports = (db) => {

  const silver = db.collection("layer_silver");
  const authenticateToken = require('../middleware/auth')(db);

  function normalizeSessionId(session_id) {
    if (!session_id) return null;
    if (typeof session_id === 'number' && isFinite(session_id) && session_id > 0) return Number(session_id);
    if (typeof session_id === 'string' && /^\d+$/.test(session_id)) return Number(session_id);
    const parsed = Date.parse(session_id);
    if (!isNaN(parsed)) return parsed;
    return null;
  }

  
  router.post("/silver", authenticateToken, async (req, res) => {

    const document = req.body || {};

    const sessionTs = normalizeSessionId(document.session_id);
    if (!sessionTs) return res.status(400).json({ message: 'Missing or invalid session_id' });

    if (!req.user || !req.user.user_id) return res.status(401).json({ message: 'Unauthorized' });
    const sessions = db.collection('sessions');
    const session = await sessions.findOne({ session_id: sessionTs, user_id: req.user.user_id });
    if (!session) return res.status(403).json({ message: 'Session not found or does not belong to user' });

    // Validate expected schema for silver layer
    const { document_id, type, siret, montant_ht, tva, montant_ttc, date_document } = document;
    if (!document_id || typeof document_id !== 'string') return res.status(400).json({ message: 'Invalid or missing document_id' });
    const allowedTypes = ['facture', 'devis', 'attestation'];
    if (!type || typeof type !== 'string' || !allowedTypes.includes(type)) return res.status(400).json({ message: 'Invalid or missing type' });
    if (!siret || typeof siret !== 'string') return res.status(400).json({ message: 'Invalid or missing siret' });

    const numMontantHt = typeof montant_ht === 'number' ? montant_ht : (typeof montant_ht === 'string' && !isNaN(Number(montant_ht)) ? Number(montant_ht) : null);
    const numTva = typeof tva === 'number' ? tva : (typeof tva === 'string' && !isNaN(Number(tva)) ? Number(tva) : null);
    const numMontantTtc = typeof montant_ttc === 'number' ? montant_ttc : (typeof montant_ttc === 'string' && !isNaN(Number(montant_ttc)) ? Number(montant_ttc) : null);
    if (numMontantHt === null || numTva === null || numMontantTtc === null) return res.status(400).json({ message: 'montant_ht, tva and montant_ttc must be numbers' });

    
    let normalizedDateDocument = null;
    if (date_document) {
      const parsed = Date.parse(date_document);
      if (isNaN(parsed)) return res.status(400).json({ message: 'Invalid date_document' });
      normalizedDateDocument = new Date(parsed).toISOString();
    }

    
    document.user_id = req.user.user_id;
    document.session_id = sessionTs;
    document.montant_ht = numMontantHt;
    document.tva = numTva;
    document.montant_ttc = numMontantTtc;
    if (normalizedDateDocument) document.date_document = normalizedDateDocument;
    document.parsed_at = new Date().toISOString();

    await silver.insertOne(document);

    res.json({ message: "Document ajouté dans layer_silver" });

  });

  
  router.get("/silver", async (req, res) => {

    const documents = await silver.find().toArray();

    res.json(documents);

  });

  return router;

};