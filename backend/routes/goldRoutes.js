const express = require("express");
const router = express.Router();

module.exports = (db) => {

  const gold = db.collection("layer_gold");

  
  router.post("/gold", async (req, res) => {

    const document = req.body;

    await gold.insertOne(document);

    res.json({ message: "Document ajouté dans layer_gold" });

  });

 
  router.get("/gold", async (req, res) => {

    const documents = await gold.find().toArray();

    res.json(documents);

  });

  return router;

};