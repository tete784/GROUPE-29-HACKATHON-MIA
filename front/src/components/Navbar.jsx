import { Link } from 'react-router-dom'

function Navbar() {
  return (
    <nav style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '12px 20px',
      backgroundColor: '#16213e'
    }}>
      <Link to="/dashboard" style={{ color: 'white', textDecoration: 'none', fontWeight: 'bold', fontSize: '18px' }}>
        Analyse IA
      </Link>
      <div style={{ display: 'flex', gap: '20px' }}>
        <Link to="/dashboard" style={{ color: 'white', textDecoration: 'none' }}>Dashboard</Link>
        <Link to="/upload" style={{ color: 'white', textDecoration: 'none' }}>Upload</Link>
        <Link to="/result" style={{ color: 'white', textDecoration: 'none' }}>Résultats</Link>
        <Link to="/crm" style={{ color: 'white', textDecoration: 'none' }}>CRM</Link>
        <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Déconnexion</Link>
      </div>
    </nav>
  )
}

export default Navbar