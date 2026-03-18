const jwt = require('jsonwebtoken');
require('dotenv').config();

const JWT_SECRET = process.env.JWT_SECRET;


module.exports = (db) => {
  const revoked = db.collection('revoked_tokens');
  
  revoked.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 }).catch(() => {});

  return async function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) return res.status(401).json({ message: 'Token missing' });

    try {
      const user = jwt.verify(token, JWT_SECRET);
      const found = await revoked.findOne({ token });
      if (found) return res.status(403).json({ message: 'Token revoked' });
      req.user = user;
      next();
    } catch (err) {
      return res.status(403).json({ message: 'Invalid token' });
    }
  };
};
