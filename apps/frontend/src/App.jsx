import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import RegistrationPage from './pages/RegistrationPage'
import SuccessPage from './pages/SuccessPage'
import QueuePage from "./pages/QueuePage";
import DoctorPage from "./pages/DoctorPage";
import DoctorLoginPage from "./pages/DoctorLoginPage";
import ChatbotPage from './pages/ChatbotPage';
import HospitalLoginPage from './pages/HospitalLoginPage';
import Layout from "./components/Layout";
import HospitalGuard from "./components/HospitalGuard";

function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes (no hospital login required) */}
        <Route path="/login" element={<HospitalLoginPage />} />
        <Route path="/chat" element={<ChatbotPage />} />

        {/* Protected routes (behind hospital login + Layout) */}
        <Route path="/" element={
          <HospitalGuard>
            <Layout><RegistrationPage /></Layout>
          </HospitalGuard>
        } />
        <Route path="/queue" element={
          <HospitalGuard>
            <Layout><QueuePage /></Layout>
          </HospitalGuard>
        } />
        <Route path="/success" element={
          <HospitalGuard>
            <Layout><SuccessPage /></Layout>
          </HospitalGuard>
        } />
        <Route path="/doctor-login" element={
          <HospitalGuard>
            <Layout><DoctorLoginPage /></Layout>
          </HospitalGuard>
        } />
        <Route path="/doctor" element={
          <HospitalGuard>
            <Layout><DoctorPage /></Layout>
          </HospitalGuard>
        } />
      </Routes>
    </Router>
  );
}

export default App
