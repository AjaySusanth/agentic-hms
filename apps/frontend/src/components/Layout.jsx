import { Building2, LogOut } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const Layout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const hospitalName = localStorage.getItem('hospital_name') || 'Hospital';
  const hospitalLocation = localStorage.getItem('hospital_location') || '';

  const handleSwitchHospital = () => {
    localStorage.removeItem('hospital_id');
    localStorage.removeItem('hospital_name');
    localStorage.removeItem('hospital_code');
    localStorage.removeItem('hospital_location');
    // Also clear doctor session
    localStorage.removeItem('doctorId');
    localStorage.removeItem('doctorName');
    localStorage.removeItem('doctorSpecialization');
    localStorage.removeItem('doctorDepartment');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-primary-600 p-2 rounded-lg">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  {hospitalName}
                </h1>
                <p className="text-sm text-gray-600">
                  {hospitalLocation ? `${hospitalLocation} • ` : ''}Hospital Management System
                </p>
              </div>
            </div>
            <button
              onClick={handleSwitchHospital}
              className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 transition-colors px-3 py-2 rounded-lg hover:bg-gray-100"
            >
              <LogOut size={16} />
              Switch Hospital
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="mt-auto py-6 text-center text-sm text-gray-600">
        <p>© 2024 Hospital Management System. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Layout;