import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import RegistrationPage from './pages/RegistrationPage'
import SuccessPage from './pages/SuccessPage'
import QueuePage from "./pages/QueuePage";
import DoctorPage from "./pages/DoctorPage";
import DoctorLoginPage from "./pages/DoctorLoginPage";
import Layout from "./components/Layout";

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<RegistrationPage />} />
          <Route path="/queue" element={<QueuePage />} />
          <Route path="/success" element={<SuccessPage />} />
          <Route path="/doctor-login" element={<DoctorLoginPage />} />
          <Route path="/doctor" element={<DoctorPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App
