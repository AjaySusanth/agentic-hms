import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import RegistrationPage from './pages/RegistrationPage'
import SuccessPage from './pages/SuccessPage'
import Layout from './components/Layout'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<RegistrationPage />} />
          <Route path="/success" element={<SuccessPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
