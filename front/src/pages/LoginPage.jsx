import { useState } from 'react'
import api from '../api'
import { useNavigate, Link } from 'react-router-dom'


function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const res = await api.post('/api/users/login', { email, password })

      localStorage.setItem('token', res.data.token)
      localStorage.setItem('session_id', res.data.session_id)

      navigate('/dashboard')
    } catch (err) {
      if (err.response) {
        setError(err.response.data.message || 'Erreur de connexion')
      } else {
        setError('Impossible de joindre le serveur')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <form onSubmit={handleLogin} style={{ width: '300px' }}>
        <h1>Connexion</h1>
        <br />

        {error && (
          <div style={{
            backgroundColor: '#ffdddd',
            color: '#d00',
            padding: '10px',
            borderRadius: '8px',
            marginBottom: '10px',
            textAlign: 'center'
          }}>
            {error}
          </div>
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={{ width: '100%', padding: '10px', marginBottom: '10px', borderRadius: '8px', border: '1px solid #555' }}
        />
        <input
          type="password"
          placeholder="Mot de passe"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ width: '100%', padding: '10px', marginBottom: '20px', borderRadius: '8px', border: '1px solid #555' }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%', padding: '12px', fontSize: '16px',
            backgroundColor: loading ? '#999' : '#4CAF50',
            color: 'white', border: 'none', borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Connexion...' : 'Se connecter'}
        </button>
        <p style={{ textAlign: 'center', marginTop: '16px', fontSize: '14px' }}>
            Pas encore de compte ?{' '}
            <Link to="/register" style={{ color: '#4CAF50', textDecoration: 'none' }}>
                S'inscrire
            </Link>
        </p>
      </form>
    </div>
  )
}

export default LoginPage