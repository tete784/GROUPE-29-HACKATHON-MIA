import { useNavigate, useLocation } from 'react-router-dom'

function ResultPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const preview = location.state?.preview

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Résultat</h1>

      {preview && (
        <img
          src={preview}
          alt="Photo analysée"
          style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '10px', marginBottom: '20px' }}
        />
      )}

      <div style={{
        backgroundColor: '#f5f5f5',
        borderRadius: '10px',
        padding: '20px',
        textAlign: 'left',
        marginBottom: '20px'
      }}>
        <h3>Résultat analyse</h3>
        <p style={{ color: '#888' }}>L'analyse apparaîtra ici plus tard...</p>
      </div>

      <button
        onClick={() => navigate('/upload')}
        style={{
          padding: '12px 30px',
          fontSize: '16px',
          backgroundColor: '#2196F3',
          color: 'white',
          border: 'none',
          borderRadius: '10px',
          cursor: 'pointer'
        }}
      >
        Nouveaux documents
      </button>
    </div>
  )
}

export default ResultPage