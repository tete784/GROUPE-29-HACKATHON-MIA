const express = require("express");
const router = express.Router();

module.exports = (db) => {

  const gold = db.collection("layer_gold");
  const authenticateToken = require('../middleware/auth')(db);

  function normalizeSessionId(session_id) {
    if (!session_id) return null;
    if (typeof session_id === 'number' && isFinite(session_id) && session_id > 0) return Number(session_id);
    if (typeof session_id === 'string' && /^\d+$/.test(session_id)) return Number(session_id);
    const parsed = Date.parse(session_id);
    if (!isNaN(parsed)) return parsed;
    return null;
  }

  router.post("/gold", authenticateToken, async (req, res) => {

    const document = req.body || {};

    const sessionTs = normalizeSessionId(document.session_id);
    if (!sessionTs) return res.status(400).json({ message: 'Missing or invalid session_id' });

    if (!req.user || !req.user.user_id) return res.status(401).json({ message: 'Unauthorized' });
    const sessions = db.collection('sessions');
    const session = await sessions.findOne({ session_id: sessionTs, user_id: req.user.user_id });
    if (!session) return res.status(403).json({ message: 'Session not found or does not belong to user' });

    // Validate gold schema
    const { document_id, status, fraud_detected, issues, validated_at } = document;
    if (!document_id || typeof document_id !== 'string') return res.status(400).json({ message: 'Invalid or missing document_id' });
    const allowedStatus = ['validated', 'fraud_suspected'];
    if (!status || typeof status !== 'string' || !allowedStatus.includes(status)) return res.status(400).json({ message: 'Invalid or missing status' });

    const boolFraud = typeof fraud_detected === 'boolean' ? fraud_detected : (typeof fraud_detected === 'string' ? (fraud_detected === 'true') : false);
    if (typeof boolFraud !== 'boolean') return res.status(400).json({ message: 'fraud_detected must be boolean' });

    const arrIssues = Array.isArray(issues) ? issues : [];

    // normalize validated_at: if status is validated set to now, else if provided validate
    let normalizedValidatedAt = null;
    if (status === 'validated') {
      normalizedValidatedAt = new Date().toISOString();
    } else if (validated_at) {
      const pd = Date.parse(validated_at);
      if (isNaN(pd)) return res.status(400).json({ message: 'Invalid validated_at' });
      normalizedValidatedAt = new Date(pd).toISOString();
    }

    // enforce uploader user_id and session_id
    document.user_id = req.user.user_id;
    document.session_id = sessionTs;
    document.fraud_detected = boolFraud;
    document.issues = arrIssues;
    if (normalizedValidatedAt) document.validated_at = normalizedValidatedAt;

    await gold.insertOne(document);

    res.json({ message: "Document ajouté dans layer_gold" });

  });


  router.get("/gold", async (req, res) => {

    const documents = await gold.find().toArray();

    res.json(documents);

  });

  return router;

};
