import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ocrApi } from '../api'

function UploadPage() {
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setImage(file)
      setPreview(URL.createObjectURL(file))
      setError(null)
    }
  }

  const handleSubmit = async () => {
    if (!image) {
      alert("Choisis une photo d'abord !")
      return
    }

    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', image)

      // On récupère la session de l'utilisateur, ou on en crée/sauvegarde une nouvelle
      let currentSessionId = localStorage.getItem('session_id')
      if (!currentSessionId) {
        currentSessionId = crypto.randomUUID()
        localStorage.setItem('session_id', currentSessionId)
      }
      formData.append('session_id', currentSessionId)

      const { data } = await ocrApi.post('/extract-and-ingest', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })


      navigate('/result', {
        state: {
          preview,
          ocrResult: data.ocr_result,
          ingestResult: data.ingest_result,
        },
      })
    } catch (err) {
      console.error('Erreur upload:', err)
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Upload un document</h1>

      <input
        type="file"
        accept="image/*,.pdf"
        onChange={handleImageChange}
        style={{ margin: '20px 0' }}
      />


      {preview && (
        <div>
          {image?.type === 'application/pdf' ? (
            <p>📄 {image.name}</p>
          ) : (
            <img
              src={preview}
              alt="Aperçu"
              style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '10px' }}
            />
          )}
        </div>
      )}

      {error && (
        <p style={{ color: 'red', marginTop: '10px' }}>❌ {error}</p>
      )}

      <br />
      <button
        onClick={handleSubmit}
        disabled={loading}
        style={{
          marginTop: '20px',
          padding: '12px 30px',
          fontSize: '16px',
          backgroundColor: loading ? '#999' : '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '10px',
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? '⏳ Analyse en cours...' : 'Analyser'}
      </button>
    </div>
  )
}

export default UploadPage