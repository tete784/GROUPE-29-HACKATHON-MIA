import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function UploadPage() {
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState(null)
  const navigate = useNavigate()

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setImage(file)
      setPreview(URL.createObjectURL(file))
    }
  }

  const handleSubmit = () => {
    if (!image) {
      alert("Choisis une photo d'abord !")
      return
    }
    navigate('/result', { state: { preview } })
  }

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Upload un document</h1>

      <input
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleImageChange}
        style={{ margin: '20px 0' }}
      />

      {preview && (
        <div>
          <img
            src={preview}
            alt="Aperçu"
            style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '10px' }}
          />
        </div>
      )}

      <br />
      <button
        onClick={handleSubmit}
        style={{
          marginTop: '20px',
          padding: '12px 30px',
          fontSize: '16px',
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

export default UploadPage