import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Phone, Play, Square, SkipForward, LogOut, Loader, User, Calendar } from "lucide-react";
import { DoctorService } from "../services/api";
import ErrorMessage from "../components/ErrorMessage";

const DoctorPage = () => {
  const navigate = useNavigate();
  
  // Doctor info from localStorage
  const [doctorId, setDoctorId] = useState(null);
  const [doctorName, setDoctorName] = useState("");
  
  // State machine
  const [state, setState] = useState("initializing"); // initializing, callNext, ready, consulting
  
  // Current patient data
  const [currentPatient, setCurrentPatient] = useState(null);
  const [queueDate] = useState(new Date().toISOString().split('T')[0]); // Today's date in YYYY-MM-DD
  
  // Queue statistics
  const [queueStats, setQueueStats] = useState({
    waiting: 0,
    present: 0,
    skipped: 0,
    nextWaiting: []
  });
  
  // UI states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Initialize - check if doctor is logged in
  useEffect(() => {
    const storedDoctorId = localStorage.getItem("doctorId");
    const storedDoctorName = localStorage.getItem("doctorName");
    
    if (!storedDoctorId || !storedDoctorName) {
      // Not logged in, redirect to login
      navigate("/doctor-login");
      return;
    }
    
    setDoctorId(storedDoctorId);
    setDoctorName(storedDoctorName);
    
    // Ready to call next patient
    setState("callNext");
  }, [navigate]);

  // Fetch queue statistics
  const fetchQueueStats = async () => {
    if (!doctorId) return;
    
    try {
      const stats = await DoctorService.getQueueStatus({
        doctor_id: doctorId,
        queue_date: queueDate,
        role: "doctor"
      });
      
      setQueueStats({
        waiting: stats.counts?.waiting || 0,
        present: stats.counts?.present || 0,
        skipped: stats.counts?.skipped || 0,
        nextWaiting: stats.next_waiting || []
      });
    } catch (err) {
      console.error("Failed to fetch queue stats:", err);
      // Don't show error to user for stats fetch, just log it
    }
  };

  // Fetch queue stats when doctor is set and periodically
  useEffect(() => {
    if (doctorId) {
      fetchQueueStats();
      
      // Refresh stats every 30 seconds
      const interval = setInterval(fetchQueueStats, 30000);
      return () => clearInterval(interval);
    }
  }, [doctorId, queueDate]);

  const handleCallNext = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await DoctorService.callNext({
        doctor_id: doctorId,
        queue_date: queueDate,
      });
      
      // Set current patient data
      setCurrentPatient({
        visitId: response.visit_id,
        patientId: response.patient_id,
        tokenNumber: response.token_number,
        name: response.patient_name,
        age: response.patient_age,
        contact: response.patient_contact,
        symptoms: response.symptoms_summary,
      });
      
      setState("ready");
      
      // Refresh queue stats after calling next
      fetchQueueStats();
    } catch (err) {
      console.error("Call next error:", err);
      setError(err.message || "Failed to call next patient");
    } finally {
      setLoading(false);
    }
  };

  const handleStartConsultation = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await DoctorService.startConsultation({
        doctor_id: doctorId,
        visit_id: currentPatient.visitId,
        queue_date: queueDate,
      });
      
      setState("consulting");
    } catch (err) {
      console.error("Start consultation error:", err);
      setError(err.message || "Failed to start consultation");
    } finally {
      setLoading(false);
    }
  };

  const handleEndConsultation = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await DoctorService.endConsultation({
        doctor_id: doctorId,
        visit_id: currentPatient.visitId,
        queue_date: queueDate,
      });
      
      // Clear current patient and return to callNext state
      setCurrentPatient(null);
      setState("callNext");
      
      // Refresh queue stats after ending consultation
      fetchQueueStats();
    } catch (err) {
      console.error("End consultation error:", err);
      setError(err.message || "Failed to end consultation");
    } finally {
      setLoading(false);
    }
  };

  const handleSkipConsultation = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await DoctorService.skipPatient({
        doctor_id: doctorId,
        visit_id: currentPatient.visitId,
        queue_date: queueDate,
        reason: "Patient not present",
      });
      
      // Clear current patient and return to callNext state
      setCurrentPatient(null);
      setState("callNext");
      
      // Refresh queue stats after skipping
      fetchQueueStats();
    } catch (err) {
      console.error("Skip consultation error:", err);
      setError(err.message || "Failed to skip patient");
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem("doctorId");
    localStorage.removeItem("doctorName");
    localStorage.removeItem("doctorSpecialization");
    localStorage.removeItem("doctorDepartment");
    navigate("/doctor-login");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-12 max-w-2xl w-full">
        {/* Doctor Header */}
        <div className="text-center mb-6 pb-4 border-b border-gray-200">
          <div className="flex items-center justify-center gap-2 mb-2">
            <User size={24} className="text-indigo-600" />
            <h2 className="text-xl font-semibold text-gray-700">
              {doctorName}
            </h2>
          </div>
          <div className="flex items-center justify-center gap-2 text-gray-500 text-sm">
            <Calendar size={16} />
            <span>{new Date().toLocaleDateString()}</span>
          </div>
        </div>

        {/* Queue Statistics Dashboard */}
        {doctorId && state !== "initializing" && (
          <div className="mb-6 grid grid-cols-3 gap-3">
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">
                {queueStats.waiting}
              </div>
              <div className="text-xs text-gray-600 uppercase tracking-wide mt-1">
                Waiting
              </div>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">
                {queueStats.present}
              </div>
              <div className="text-xs text-gray-600 uppercase tracking-wide mt-1">
                Present
              </div>
            </div>
            <div className="bg-orange-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">
                {queueStats.skipped}
              </div>
              <div className="text-xs text-gray-600 uppercase tracking-wide mt-1">
                Skipped
              </div>
            </div>
          </div>
        )}

        {/* Next Waiting Tokens */}
        {doctorId && state !== "initializing" && queueStats.nextWaiting.length > 0 && (
          <div className="mb-6 bg-indigo-50 rounded-lg p-4">
            <div className="text-xs uppercase tracking-wide text-gray-600 mb-2">
              Next in Queue
            </div>
            <div className="flex gap-2">
              {queueStats.nextWaiting.map((token, idx) => (
                <div
                  key={idx}
                  className={`flex-1 text-center py-2 rounded-md font-semibold text-sm ${
                    token.status === 'present'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  #{token.token_number}
                  <div className="text-xs mt-1 capitalize opacity-75">
                    {token.status}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mb-6">
            <ErrorMessage message={error} />
          </div>
        )}

        {/* Initializing State */}
        {state === "initializing" && (
          <div className="text-center py-12">
            <Loader size={48} className="mx-auto mb-4 text-indigo-600 animate-spin" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Loading...
            </h2>
            <p className="text-gray-500">
              Setting up your session
            </p>
          </div>
        )}

        {/* Call Next State - Only show Call Next button */}
        {state === "callNext" && (
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-800 mb-12">
              Ready to Start
            </h2>
            <button
              onClick={handleCallNext}
              disabled={loading}
              className="w-full bg-indigo-500 hover:bg-indigo-600 text-white font-semibold py-4 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader size={20} className="animate-spin" />
                  Calling...
                </>
              ) : (
                <>
                  <Phone size={20} className="group-hover:scale-110 transition" />
                  Call Next Patient
                </>
              )}
            </button>
          </div>
        )}

        {/* Ready/Consulting State - Patient Details */}
        {state !== "initializing" && state !== "callNext" && currentPatient && (
          <>
            {/* Patient Information Card */}
            <div className="mb-8 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl p-6">
              <div className="text-center mb-4">
                <h1 className="text-4xl font-bold text-gray-800 mb-2">
                  {currentPatient.name}
                </h1>
                <div className="flex items-center justify-center gap-6 text-sm text-gray-600">
                  <span>Token: <span className="font-semibold text-indigo-600">#{currentPatient.tokenNumber}</span></span>
                  {currentPatient.age && <span>Age: {currentPatient.age}</span>}
                  <span>📞 {currentPatient.contact}</span>
                </div>
              </div>
              
              {currentPatient.symptoms && (
                <div className="mt-4 p-4 bg-white rounded-lg">
                  <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">Symptoms</p>
                  <p className="text-gray-700">{currentPatient.symptoms}</p>
                </div>
              )}
              
              {state === "consulting" && (
                <div className="mt-4 text-center">
                  <div className="inline-block bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium">
                    ● Consultation Active
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              {/* Ready State - Show Start, Skip */}
              {state === "ready" && (
                <>
                  <button
                    onClick={handleStartConsultation}
                    disabled={loading}
                    className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-4 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2 group disabled:opacity-50"
                  >
                    {loading ? (
                      <Loader size={20} className="animate-spin" />
                    ) : (
                      <>
                        <Play size={20} className="group-hover:scale-110 transition" />
                        Start Consultation
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleSkipConsultation}
                    disabled={loading}
                    className="w-full bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-4 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2 group disabled:opacity-50"
                  >
                    {loading ? (
                      <Loader size={20} className="animate-spin" />
                    ) : (
                      <>
                        <SkipForward size={20} className="group-hover:scale-110 transition" />
                        Skip (Patient Not Present)
                      </>
                    )}
                  </button>
                </>
              )}

              {/* Consulting State - Show Only End Consultation */}
              {state === "consulting" && (
                <button
                  onClick={handleEndConsultation}
                  disabled={loading}
                  className="w-full bg-red-500 hover:bg-red-600 text-white font-semibold py-4 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2 group disabled:opacity-50"
                >
                  {loading ? (
                    <Loader size={20} className="animate-spin" />
                  ) : (
                    <>
                      <Square size={20} className="group-hover:scale-110 transition" />
                      End Consultation
                    </>
                  )}
                </button>
              )}

              {/* Sign Out Button */}
              <button 
                onClick={handleSignOut}
                className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-3 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2 group mt-6"
              >
                <LogOut size={18} className="group-hover:scale-110 transition" />
                Sign Out
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default DoctorPage;
