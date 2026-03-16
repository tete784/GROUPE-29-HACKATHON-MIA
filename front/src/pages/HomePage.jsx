import { useNavigate } from 'react-router-dom'

function HomePage() {
  const navigate = useNavigate()

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Analyse IA</h1>
      <p>Analyse document administratif</p>
      <button
        onClick={() => navigate('/upload')}
        style={{
          marginTop: '30px',
          padding: '15px 40px',
          fontSize: '18px',
          backgroundColor: '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '10px',
          cursor: 'pointer'
        }}
      >
        Analyser
      </button>
    </div>
  )
}

export default HomePage