const express = require("express");
const connectDB = require("./db");

const bronzeRoutes = require("./routes/bronzeRoutes.js");
const silverRoutes = require("./routes/silverRoutes");
const goldRoutes = require("./routes/goldRoutes");

const app = express();

app.use(express.json());

async function startServer() {

  try {
    const db = await connectDB();

    app.use("/api", bronzeRoutes(db));
    app.use("/api", silverRoutes(db));
    app.use("/api", goldRoutes(db));

    app.listen(3000, () => {
      console.log("Server running on port 3000");
    });
  } catch (err) {
    console.error("Failed to start server due to DB error:", err);
    process.exit(1);
  }

}

startServer();