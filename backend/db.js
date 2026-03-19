const { MongoClient } = require("mongodb");
require('dotenv').config();

const uri = process.env.MONGODB_URI || "mongodb+srv://mino:Minososo1234+@cluster.fkflmzu.mongodb.net/";

const client = new MongoClient(uri);

async function connectDB() {
  try {
    await client.connect();
    console.log("Connected to MongoDB");

    const db = client.db("document_processing");

    return db;

  } catch (error) {
    console.error("Database connection error:", error);
    throw error;
  }
}

module.exports = connectDB;