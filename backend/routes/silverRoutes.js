const express = require("express");
const router = express.Router();

module.exports = (db) => {

  const silver = db.collection("layer_silver");

  // Ajouter données OCR
  router.post("/silver", async (req, res) => {

    const document = req.body;

    await silver.insertOne(document);

    res.json({ message: "Document ajouté dans layer_silver" });

  });

  // Récupérer documents structurés
  router.get("/silver", async (req, res) => {

    const documents = await silver.find().toArray();

    res.json(documents);

  });

  return router;

};