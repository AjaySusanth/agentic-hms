import { useState, useEffect } from "react";
import { Phone, Play, Square, SkipForward, LogOut, Loader } from "lucide-react";

const DoctorPage = () => {
  const patients = ["John Doe", "Jane Smith", "Michael Johnson"];
  const [state, setState] = useState("initializing"); // initializing, callNext, ready, consulting
  const [patientName, setPatientName] = useState("");
  const [currentPatientIndex, setCurrentPatientIndex] = useState(0);

  // Simulate analyzing state
  useEffect(() => {
    const analyzeState = async () => {
      // Simulate API call to analyze queue state
      await new Promise((resolve) => setTimeout(resolve, 2000));
      setState("callNext");
    };

    analyzeState();
  }, []);

  const handleStartConsultation = () => {
    setState("consulting");
  };

  const handleEndConsultation = () => {
    setState("callNext");
  };

  const handleSkipConsultation = () => {
    setState("callNext");
    // In real app, mark as skipped in queue
  };

  const handleCallNext = () => {
    // Fetch next patient from queue
    const nextIndex = (currentPatientIndex + 1) % patients.length;
    setPatientName(patients[nextIndex]);
    setCurrentPatientIndex(nextIndex);
    setState("ready");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-12 max-w-md w-full">
        {/* Initializing State */}
        {state === "initializing" && (
          <div className="text-center py-12">
            <Loader size={48} className="mx-auto mb-4 text-indigo-600 animate-spin" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Analyzing State
            </h2>
            <p className="text-gray-500">
              Loading queue information...
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
              className="w-full bg-indigo-500 hover:bg-indigo-600 text-white font-semibold py-4 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2 group"
            >
              <Phone size={20} className="group-hover:scale-110 transition" />
              Call Next
            </button>
          </div>
        )}

        {/* Ready/Consulting State */}
        {state !== "initializing" && state !== "callNext" && (
          <>
            {/* Patient Name - Main Content */}
            <div className="text-center mb-12">
              <h1 className="text-5xl font-bold text-gray-800 mb-2">
                {patientName}
              </h1>
              <p className="text-gray-500 text-sm uppercase tracking-wide">
                Current Patient
              </p>
              {state === "consulting" && (
                <div className="mt-4 inline-block bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium">
                  Consultation Active
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              {/* Ready State - Show Start Consultation, Skip, Call Next */}
              {state === "ready" && (
                <>
                  <button
                    onClick={handleStartConsultation}
                    className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-4 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2 group"
                  >
                    <Play size={20} className="group-hover:scale-110 transition" />
                    Start Consultation
                  </button>

                  <button
                    onClick={handleSkipConsultation}
                    className="w-full bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-4 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2 group"
                  >
                    <SkipForward size={20} className="group-hover:scale-110 transition" />
                    Skip Consultation
                  </button>

                  <button
                    onClick={handleCallNext}
                    className="w-full bg-indigo-500 hover:bg-indigo-600 text-white font-semibold py-4 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2 group"
                  >
                    <Phone size={20} className="group-hover:scale-110 transition" />
                    Call Next
                  </button>
                </>
              )}

              {/* Consulting State - Show Only End Consultation */}
              {state === "consulting" && (
                <button
                  onClick={handleEndConsultation}
                  className="w-full bg-red-500 hover:bg-red-600 text-white font-semibold py-4 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2 group"
                >
                  <Square size={20} className="group-hover:scale-110 transition" />
                  End Consultation
                </button>
              )}

              {/* Sign Out Button */}
              {state !== "initializing" && state !== "callNext" && (
                <button className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-3 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2 group mt-6">
                  <LogOut size={18} className="group-hover:scale-110 transition" />
                  Sign Out
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default DoctorPage;
