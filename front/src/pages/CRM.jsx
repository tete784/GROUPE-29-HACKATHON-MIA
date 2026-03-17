export default function CRM() {
  const fournisseurs = []

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
              <th style={{ padding: '12px 20px' }}>Entreprise</th>
              <th style={{ padding: '12px 20px' }}>SIRET</th>
              <th style={{ padding: '12px 20px' }}>N° TVA</th>
              <th style={{ padding: '12px 20px' }}>Email</th>
              <th style={{ padding: '12px 20px' }}>Téléphone</th>
              <th style={{ padding: '12px 20px' }}>Statut</th>
            </tr>
          </thead>
          <tbody>
            {fournisseurs.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ padding: '60px 20px', textAlign: 'center' }}>
                  <p style={{ color: '#9ca3af', fontSize: '16px', fontWeight: '500' }}>Aucun fournisseur pour le moment</p>
                  <p style={{ color: '#6b7280', fontSize: '13px', marginTop: '6px' }}>Les fiches seront créées automatiquement après l'analyse IA</p>
                </td>
              </tr>
            ) : (
              fournisseurs.map((f) => (
                <tr key={f.id} style={{ borderTop: '1px solid #374151' }}>
                  <td style={{ padding: '14px 20px', fontWeight: '500' }}>{f.nom}</td>
                  <td style={{ padding: '14px 20px', color: '#d1d5db' }}>{f.siret}</td>
                  <td style={{ padding: '14px 20px', color: '#d1d5db' }}>{f.tva}</td>
                  <td style={{ padding: '14px 20px', color: '#d1d5db' }}>{f.email}</td>
                  <td style={{ padding: '14px 20px', color: '#d1d5db' }}>{f.telephone}</td>
                  <td style={{ padding: '14px 20px' }}>
                    <span style={{
                      padding: '4px 10px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      fontWeight: '500',
                      backgroundColor: f.statut === 'Actif' ? 'rgba(34,197,94,0.2)' : 'rgba(239,68,68,0.2)',
                      color: f.statut === 'Actif' ? '#4ade80' : '#f87171'
                    }}>
                      {f.statut}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}