const express = require("express");
const router = express.Router();

module.exports = (db) => {

  const bronze = db.collection("layer_bronze");
  const authenticateToken = require('../middleware/auth')(db);

  function normalizeSessionId(session_id) {
    if (!session_id) return null;
    if (typeof session_id === 'number' && isFinite(session_id) && session_id > 0) return Number(session_id);
    if (typeof session_id === 'string' && /^\d+$/.test(session_id)) return Number(session_id);
    const parsed = Date.parse(session_id);
    if (!isNaN(parsed)) return parsed;
    return null;
  }

  // Ajouter document brut (requiert authentification)
  router.post("/bronze", authenticateToken, async (req, res) => {
    const document = req.body || {};

    // session_id required and must be a timestamp
    const sessionTs = normalizeSessionId(document.session_id);
    if (!sessionTs) return res.status(400).json({ message: 'Missing or invalid session_id' });

    // enforce uploader user_id from authenticated token
    if (!req.user || !req.user.user_id) return res.status(401).json({ message: 'Unauthorized' });
    const sessions = db.collection('sessions');
    const session = await sessions.findOne({ session_id: sessionTs, user_id: req.user.user_id });
    if (!session) return res.status(403).json({ message: 'Session not found or does not belong to user' });

    // Validate expected bronze schema
    const { document_id, filename, file_url, ocr_processed, status } = document;
    if (!document_id || typeof document_id !== 'string') return res.status(400).json({ message: 'Invalid or missing document_id' });
    if (!filename || typeof filename !== 'string') return res.status(400).json({ message: 'Invalid or missing filename' });
    if (!file_url || typeof file_url !== 'string') return res.status(400).json({ message: 'Invalid or missing file_url' });

    
    const allowed = ['uploaded'];
    if (!status) document.status = 'uploaded';
    else if (typeof status !== 'string' || !allowed.includes(status)) return res.status(400).json({ message: 'Invalid status for bronze' });

    // ocr_processed must be boolean 
    let boolOcr;
    if (typeof ocr_processed === 'boolean') boolOcr = ocr_processed;
    else if (typeof ocr_processed === 'string') boolOcr = ocr_processed.toLowerCase() === 'true';
    else boolOcr = false;
    document.ocr_processed = boolOcr;

    
    document.user_id = req.user.user_id;
    document.session_id = sessionTs;
    document.uploaded_at = new Date().toISOString();

    await bronze.insertOne(document);

    res.json({ message: "Document ajouté dans layer_bronze" });

  });

  
  router.get("/bronze", async (req, res) => {

    const documents = await bronze.find().toArray();

    res.json(documents);

  });

  return router;

};
