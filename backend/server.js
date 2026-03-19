require('dotenv').config();
const express = require("express");
const connectDB = require("./db");

const bronzeRoutes = require("./routes/bronzeRoutes.js");
const silverRoutes = require("./routes/silverRoutes");
const goldRoutes = require("./routes/goldRoutes");
const userRoutes = require("./routes/userRoutes");
const { authenticateToken } = require('./middleware/auth');

const app = express();
const cors = require("cors");

app.use(cors());
app.use(express.json());

async function startServer() {

  try {

    const db = await connectDB();

    app.use("/api", bronzeRoutes(db));
    app.use("/api", silverRoutes(db));
    app.use("/api", goldRoutes(db));

    const authenticateToken = require('./middleware/auth')(db);


    app.use('/api/users', userRoutes(db));

    const port = process.env.PORT || 3000;
    app.listen(port, () => {
      console.log(`Server running on port ${port}`);
    });
  } catch (err) {
    console.error("Failed to start server due to DB error:", err);
    process.exit(1);
  }

}

startServer();