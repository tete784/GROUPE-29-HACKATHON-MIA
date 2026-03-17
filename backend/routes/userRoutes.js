const express = require('express');
const router = express.Router();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
require('dotenv').config();

const JWT_SECRET = process.env.JWT_SECRET ;

module.exports = (db) => {
  const users = db.collection('user');
  const revoked = db.collection('revoked_tokens');
  revoked.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 }).catch(() => {});
  const sessions = db.collection('sessions');
  sessions.createIndex({ session_id: 1 }, { unique: true }).catch(() => {});

  router.post('/register', async (req, res) => {
    try {
      const { user_id, name, email, password, admin } = req.body;

      if (!user_id || !email || !password || !name) {
        return res.status(400).json({ message: 'Missing required fields' });
      }

      const existing = await users.findOne({ $or: [{ user_id }, { email }] });
      if (existing) return res.status(409).json({ message: 'User with given id or email already exists' });

      const hashed = await bcrypt.hash(password, 10);

      const doc = {
        user_id,
        name,
        email,
        password: hashed,
        admin: !!admin,
        created_at: new Date().toISOString(),
      };

      await users.insertOne(doc);

      const token = jwt.sign({ user_id: doc.user_id, admin: doc.admin }, JWT_SECRET, { expiresIn: '7d' });

      res.status(201).json({ message: 'User created', token });
    } catch (err) {
      console.error(err);
      res.status(500).json({ message: 'Server error' });
    }
  });

  router.post('/login', async (req, res) => {
    try {
      const { user_id, email, password } = req.body;
      if ((!user_id && !email) || !password) return res.status(400).json({ message: 'Missing credentials' });

      const query = user_id ? { user_id } : { email };
      const user = await users.findOne(query);
      if (!user) return res.status(401).json({ message: 'Invalid credentials' });

      const match = await bcrypt.compare(password, user.password);
      if (!match) return res.status(401).json({ message: 'Invalid credentials' });

      const token = jwt.sign({ user_id: user.user_id, admin: user.admin }, JWT_SECRET, { expiresIn: '7d' });

      // create a session for this login and return session_id
      const sessionId = Date.now();
      const sessionDoc = {
        session_id: sessionId,
        user_id: user.user_id,
        created_at: new Date().toISOString(),
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
      };
      await sessions.insertOne(sessionDoc).catch(() => {});

      res.json({ message: 'Authenticated', token, session_id: sessionId });
    } catch (err) {
      console.error(err);
      res.status(500).json({ message: 'Server error' });
    }
  });

  // Logout
  router.post('/logout', async (req, res) => {
    try {
      // Accept token 
      const authHeader = req.headers['authorization'];
      let token = authHeader && authHeader.split(' ')[1];
      if (!token && req.body && req.body.token) token = req.body.token;
      if (!token) return res.status(400).json({ message: 'Token missing' });

      // Verify token and determine expiry from token payload when possible
      let decoded;
      try {
        decoded = jwt.verify(token, JWT_SECRET);
      } catch (err) {
        const payload = jwt.decode(token);
        if (!payload) {
          return res.status(400).json({ message: 'Invalid token' });
        }

        // Use exp from payload when available, otherwise default to 7 days
        const expiresAt = payload.exp ? new Date(payload.exp * 1000) : new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
        await revoked.insertOne({ token, expiresAt, revokedWithoutVerify: true });

        return res.json({ message: 'Logged out (token revoked without verification)' });
      }

      // If token verified, determine expiresAt from payload when possible
      let expiresAt;
      try {
        const payload = jwt.decode(token);
        if (payload && payload.exp) {
          expiresAt = new Date(payload.exp * 1000);
        }
      } catch (e) {
        
      }
      if (!expiresAt) {
        expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
      }

      await revoked.insertOne({ token, expiresAt });

      res.json({ message: 'Logged out' });
    } catch (err) {
      console.error(err);
      res.status(500).json({ message: 'Server error' });
    }
  });

  // get my own profile
  router.get('/me', async (req, res) => {
    
    if (!req.user) return res.status(401).json({ message: 'Unauthorized' });
    const user = await users.findOne({ user_id: req.user.user_id }, { projection: { password: 0 } });
    res.json(user);
  });

  return router;
};
