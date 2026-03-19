import { useState, useEffect } from 'react'
import api from '../api'

export default function CRM() {
  const [fournisseurs, setFournisseurs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.get('/api/silver')
        setFournisseurs(res.data)
      } catch (err) {
        console.error('Erreur lors du chargement des données silver :', err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const formatDate = (value) => {
    if (!value) return '—'
    const d = new Date(value)
    if (isNaN(d)) return value
    return d.toLocaleDateString('fr-FR')
  }

  const formatMontant = (value) => {
    if (value === null || value === undefined) return '—'
    return Number(value).toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €'
  }

  return (
    <div style={{ padding: '30px', color: 'white' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 'bold' }}>CRM Fournisseurs</h1>
        </div>
      </div>

      <div style={{ backgroundColor: '#bdcadb', border: '1px solid #b7c8e3', borderRadius: '12px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ backgroundColor: '#85a7f0', color: '#000000', fontSize: '13px' }}>
              <th style={{ padding: '12px 20px' }}>SIRET</th>
              <th style={{ padding: '12px 20px' }}>TVA</th>
              <th style={{ padding: '12px 20px' }}>Montant HT</th>
              <th style={{ padding: '12px 20px' }}>Montant TTC</th>
              <th style={{ padding: '12px 20px' }}>Date d'émission</th>
              <th style={{ padding: '12px 20px' }}>Expiration</th>
              <th style={{ padding: '12px 20px' }}>IBAN</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="7" style={{ padding: '60px 20px', textAlign: 'center' }}>
                  <p style={{ color: '#6b7280', fontSize: '16px' }}>Chargement...</p>
                </td>
              </tr>
            ) : fournisseurs.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ padding: '60px 20px', textAlign: 'center' }}>
                  <p style={{ color: '#9ca3af', fontSize: '16px', fontWeight: '500' }}>Aucun fournisseur pour le moment</p>
                  <p style={{ color: '#6b7280', fontSize: '13px', marginTop: '6px' }}>Les fiches seront créées automatiquement après l'analyse IA</p>
                </td>
              </tr>
            ) : (
              fournisseurs.map((f) => (
                <tr key={f._id || f.document_id} style={{ borderTop: '1px solid #374151' }}>
                  <td style={{ padding: '14px 20px', color: '#1f2937', fontWeight: '500' }}>{f.siret || '—'}</td>
                  <td style={{ padding: '14px 20px', color: '#374151' }}>{f.tva ?? f.montant_tva ?? '—'}</td>
                  <td style={{ padding: '14px 20px', color: '#374151' }}>{formatMontant(f.montant_ht)}</td>
                  <td style={{ padding: '14px 20px', color: '#374151' }}>{formatMontant(f.montant_ttc)}</td>
                  <td style={{ padding: '14px 20px', color: '#374151' }}>{formatDate(f.date_emission || f.date_document)}</td>
                  <td style={{ padding: '14px 20px', color: '#374151' }}>{formatDate(f.expiration)}</td>
                  <td style={{ padding: '14px 20px', color: '#374151' }}>{f.iban || '—'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}