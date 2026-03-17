const express = require("express");
const router = express.Router();

module.exports = (db) => {

  const bronze = db.collection("layer_bronze");

  // Ajouter document brut
  router.post("/bronze", async (req, res) => {

    const document = req.body;

    await bronze.insertOne(document);

    res.json({ message: "Document ajouté dans layer_bronze" });

  });

  // Récupérer tous les documents
  router.get("/bronze", async (req, res) => {

    const documents = await bronze.find().toArray();

    res.json(documents);

  });

  return router;

};