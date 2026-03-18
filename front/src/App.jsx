import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import UploadPage from './pages/UploadPage'
import ResultPage from './pages/ResultPage'
import DashboardPage from './pages/DashboardPage'
import CRM from './pages/CRM'
import Navbar from './components/Navbar'

function Layout({ children }) {
  const location = useLocation()
  const hideNavbar = ['/', '/login', '/register'].includes(location.pathname)

  return (
    <>
      {!hideNavbar && <Navbar />}
      {children}
    </>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="/crm" element={<CRM />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App