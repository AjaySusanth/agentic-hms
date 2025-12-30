import { useLocation, useNavigate } from 'react-router-dom';
import { CheckCircle, Printer, Home, Calendar, User, Building2, Phone } from 'lucide-react';
import { useEffect } from 'react';

const SuccessPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const registrationData = location.state;

  // Redirect to home if no registration data
  useEffect(() => {
    if (!registrationData || !registrationData.tokenNumber) {
      navigate('/');
    }
  }, [registrationData, navigate]);

  if (!registrationData) {
    return null;
  }

  const handlePrint = () => {
    window.print();
  };

  const handleNewRegistration = () => {
    navigate('/');
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Success Header */}
      <div className="card text-center mb-6">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-4">
          <CheckCircle className="w-12 h-12 text-green-600" />
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Registration Successful!
        </h1>
        <p className="text-gray-600">
          Your appointment has been confirmed
        </p>
      </div>

      {/* Token Number - Highlighted */}
      <div className="card bg-gradient-to-br from-primary-50 to-primary-100 border-2 border-primary-300 mb-6">
        <div className="text-center">
          <p className="text-sm font-medium text-primary-700 mb-2">
            Your Token Number
          </p>
          <div className="text-6xl font-bold text-primary-600 mb-2">
            {registrationData.tokenNumber}
          </div>
          <p className="text-sm text-primary-700">
            Please remember this number for your visit
          </p>
        </div>
      </div>

      {/* Registration Details */}
      <div className="card mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Appointment Details
        </h2>
        
        <div className="space-y-4">
          {/* Patient Name */}
          <div className="flex items-center gap-3 pb-3 border-b border-gray-200">
            <div className="bg-gray-100 p-2 rounded-lg">
              <User className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Patient Name</p>
              <p className="font-medium text-gray-900">
                {registrationData.patientName}
              </p>
            </div>
          </div>

          {/* Department */}
          <div className="flex items-center gap-3 pb-3 border-b border-gray-200">
            <div className="bg-gray-100 p-2 rounded-lg">
              <Building2 className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Department</p>
              <p className="font-medium text-gray-900">
                {registrationData.department}
              </p>
            </div>
          </div>

          {/* Phone Number */}
          <div className="flex items-center gap-3 pb-3 border-b border-gray-200">
            <div className="bg-gray-100 p-2 rounded-lg">
              <Phone className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Contact Number</p>
              <p className="font-medium text-gray-900">
                {registrationData.phoneNumber}
              </p>
            </div>
          </div>

          {/* Date */}
          <div className="flex items-center gap-3">
            <div className="bg-gray-100 p-2 rounded-lg">
              <Calendar className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Appointment Date</p>
              <p className="font-medium text-gray-900">
                {new Date().toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Important Instructions */}
      <div className="card bg-blue-50 border-blue-200 mb-6">
        <h3 className="font-semibold text-gray-900 mb-3">
          Important Instructions
        </h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-start gap-2">
            <span className="text-primary-600 font-bold">•</span>
            <span>Please arrive 15 minutes before your scheduled time</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary-600 font-bold">•</span>
            <span>Bring your token number and a valid ID proof</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary-600 font-bold">•</span>
            <span>Report to the reception desk upon arrival</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary-600 font-bold">•</span>
            <span>Your token will be called in the waiting area</span>
          </li>
        </ul>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 print:hidden">
        <button
          onClick={handlePrint}
          className="btn-secondary flex-1 flex items-center justify-center gap-2"
        >
          <Printer className="w-4 h-4" />
          Print Details
        </button>
        <button
          onClick={handleNewRegistration}
          className="btn-primary flex-1 flex items-center justify-center gap-2"
        >
          <Home className="w-4 h-4" />
          New Registration
        </button>
      </div>

      {/* Print Styles */}
      <style>{`
        @media print {
          body {
            background: white;
          }
          .print\\:hidden {
            display: none !important;
          }
          header, footer {
            display: none !important;
          }
        }
      `}</style>
    </div>
  );
};

export default SuccessPage;
