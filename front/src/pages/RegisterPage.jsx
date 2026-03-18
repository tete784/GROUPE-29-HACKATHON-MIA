import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import api from '../api'

function RegisterPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleRegister = async (e) => {
    e.preventDefault()
    setError('')

    // Vérification mots de passe identiques
    if (password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas')
      return
    }

    // Vérification longueur mot de passe
    if (password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères')
      return
    }

    setLoading(true)

    try {
      const res = await api.post('/api/users/register', {
        name,
        email,
        password,
        admin: false
      })

      // Le backend renvoie un token à l'inscription
      localStorage.setItem('token', res.data.token)

      navigate('/dashboard')
    } catch (err) {
      if (err.response) {
        setError(err.response.data.message || "Erreur lors de l'inscription")
      } else {
        setError('Impossible de joindre le serveur')
      }
    } finally {
      setLoading(false)
    }
  }

  // Style réutilisable pour les inputs
  const inputStyle = {
    width: '100%',
    padding: '10px',
    marginBottom: '12px',
    borderRadius: '8px',
    border: '1px solid #555',
    fontSize: '14px',
    boxSizing: 'border-box'
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh'
    }}>
      <form onSubmit={handleRegister} style={{ width: '320px' }}>
        <h1>Inscription</h1>
        <br />

        {error && (
          <div style={{
            backgroundColor: '#ffdddd',
            color: '#d00',
            padding: '10px',
            borderRadius: '8px',
            marginBottom: '12px',
            textAlign: 'center',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}

        <input
          type="text"
          placeholder="Nom complet"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          style={inputStyle}
        />

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={inputStyle}
        />

        <input
          type="password"
          placeholder="Mot de passe"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={inputStyle}
        />

        <input
          type="password"
          placeholder="Confirmer le mot de passe"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          style={{ ...inputStyle, marginBottom: '20px' }}
        />

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px',
            fontSize: '16px',
            backgroundColor: loading ? '#999' : '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Inscription...' : "S'inscrire"}
        </button>

        <p style={{ textAlign: 'center', marginTop: '16px', fontSize: '14px' }}>
          Déjà un compte ?{' '}
          <Link to="/login" style={{ color: '#4CAF50', textDecoration: 'none' }}>
            Se connecter
          </Link>
        </p>
      </form>
    </div>
  )
}

export default RegisterPage