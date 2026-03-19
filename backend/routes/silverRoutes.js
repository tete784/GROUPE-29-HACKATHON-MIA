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

    const payload = req.body || {};

    const sessionTs = normalizeSessionId(payload.session_id);
    if (!sessionTs) return res.status(400).json({ message: 'Missing or invalid session_id' });

    if (!req.user || !req.user.user_id) return res.status(401).json({ message: 'Unauthorized' });
    const sessions = db.collection('sessions');
    const session = await sessions.findOne({ session_id: sessionTs, user_id: req.user.user_id });
    if (!session) return res.status(403).json({ message: 'Session not found or does not belong to user' });

    const { document_id, type } = payload;
    if (!document_id || typeof document_id !== 'string') return res.status(400).json({ message: 'Invalid or missing document_id' });
    const allowedTypes = ['facture', 'devis', 'attestation'];
    if (!type || typeof type !== 'string' || !allowedTypes.includes(type)) return res.status(400).json({ message: 'Invalid or missing type' });

   
    const siret = payload.siret ? String(payload.siret) : 'manquant';
    const tva = payload.tva ? String(payload.tva) : 'manquant';
    const montant_ht = (payload.montant_ht !== undefined && payload.montant_ht !== null) ? String(payload.montant_ht) : 'manquant';
    const montant_ttc = (payload.montant_ttc !== undefined && payload.montant_ttc !== null) ? String(payload.montant_ttc) : 'manquant';
    const date_raw = payload.date_emission || payload.date_document || null;
    let date_emission = 'manquant';
    if (date_raw) {
      const parsed = Date.parse(date_raw);
      if (!isNaN(parsed)) {
        const d = new Date(parsed);
        const dd = String(d.getDate()).padStart(2, '0');
        const mm = String(d.getMonth() + 1).padStart(2, '0');
        const yyyy = d.getFullYear();
        date_emission = `${dd}/${mm}/${yyyy}`;
      } else {
        date_emission = String(date_raw);
      }
    }
    const expiration = payload.expiration ? String(payload.expiration) : 'manquant';
    const iban = payload.iban ? String(payload.iban) : 'manquant';

    const docToStore = {
      document_id,
      type,
      session_id: sessionTs,
      user_id: req.user.user_id,
      siret,
      tva,
      montant_ht,
      montant_ttc,
      date_emission,
      expiration,
      iban,
      parsed_at: new Date().toISOString()
    };

    await silver.insertOne(docToStore);

    res.json({ message: "Document ajouté dans layer_silver", document: docToStore });

  });

  
  router.get("/silver", async (req, res) => {

    const documents = await silver.find().toArray();

    res.json(documents);

  });

  // Récupérer un document par document_id (propriétaire ou admin uniquement)
  router.get('/silver/:document_id', authenticateToken, async (req, res) => {
    try {
      const { document_id } = req.params;
      if (!document_id) return res.status(400).json({ message: 'Missing document_id' });

      const doc = await silver.findOne({ document_id });
      if (!doc) return res.status(404).json({ message: 'Document not found' });

      if (req.user && (req.user.user_id === doc.user_id || req.user.admin)) {
        return res.json(doc);
      }

      return res.status(403).json({ message: 'Forbidden' });
    } catch (err) {
      console.error(err);
      res.status(500).json({ message: 'Server error' });
    }
  });

  return router;

};
