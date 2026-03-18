import { useNavigate, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'

const MOCK_RESULTS = [
  {
    document_id: "facture_dupont",
    status: "fraud_suspected",
    fraud_detected: true,
    issues: ["SIRET incohérents dans le lot", "Attestation expirée le 01/01/2025"],
    validated_at: "2026-03-17T10:30:00"
  },
  {
    document_id: "devis_martin",
    status: "validated",
    fraud_detected: false,
    issues: [],
    validated_at: "2026-03-17T10:30:01"
  }
]

function ResultPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const preview = location.state?.preview

  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
      setResults(MOCK_RESULTS)
      setLoading(false)
  }, [])


  const getStatusStyle = (status) => {
    if (status === 'fraud_suspected') {
      return { backgroundColor: '#FFEBEE', borderLeft: '4px solid #F44336' }
    }
    return { backgroundColor: '#E8F5E9', borderLeft: '4px solid #4CAF50' }
  }

  const getStatusLabel = (status) => {
    if (status === 'fraud_suspected') return 'Fraude suspectée'
    if (status === 'validated') return 'Validé'
    return status
  }

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div style={{ padding: '20px', maxWidth: '700px', margin: '0 auto' }}>
      <h1 style={{ textAlign: 'center' }}>Résultats</h1>

      {preview && (
        <div style={{ textAlign: 'center' }}>
          <img
            src={preview}
            alt="Photo analysée"
            style={{
              maxWidth: '100%',
              maxHeight: '200px',
              borderRadius: '10px',
              marginBottom: '20px'
            }}
          />
        </div>
      )}

      {loading && (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          backgroundColor: '#f5f5f5',
          borderRadius: '10px'
        }}>
          <p style={{ color: '#666' }}>Analyse en cours...</p>
        </div>
      )}

      {!loading && results.map((doc) => (
        <div
          key={doc.document_id}
          style={{
            ...getStatusStyle(doc.status),
            borderRadius: '10px',
            padding: '16px 20px',
            marginBottom: '16px',
            textAlign: 'left'
          }}
        >
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '8px'
          }}>
            <h3 style={{ margin: 0 }}>{doc.document_id}</h3>
            <span style={{
              fontSize: '14px',
              fontWeight: 'bold',
              color: doc.fraud_detected ? '#D32F2F' : '#388E3C'
            }}>
              {getStatusLabel(doc.status)}
            </span>
          </div>

          <p style={{ margin: '4px 0', fontSize: '13px', color: '#888' }}>
            Analysé le {formatDate(doc.validated_at)}
          </p>

          {doc.issues.length > 0 && (
            <div style={{ marginTop: '10px' }}>
              <p style={{ margin: '0 0 6px 0', fontWeight: 'bold', fontSize: '14px' }}>
                Problèmes détectés :
              </p>
              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                {doc.issues.map((issue, i) => (
                  <li key={i} style={{ fontSize: '14px', color: '#D32F2F', marginBottom: '4px' }}>
                    {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}


          {doc.issues.length === 0 && (
            <p style={{ margin: '10px 0 0 0', fontSize: '14px', color: '#388E3C' }}>
              Aucun problème détecté ✓
            </p>
          )}
        </div>
      ))}


      {!loading && results.length > 0 && (
        <div style={{
          textAlign: 'center',
          padding: '12px',
          backgroundColor: '#f5f5f5',
          borderRadius: '10px',
          marginBottom: '20px',
          fontSize: '14px',
          color: '#666'
        }}>
          {results.filter(r => r.fraud_detected).length} fraude(s) suspectée(s)
          sur {results.length} document(s) analysé(s)
        </div>
      )}

      <div style={{ textAlign: 'center' }}>
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
    </div>
  )
}

export default ResultPage