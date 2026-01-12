import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import StepIndicator from '../components/StepIndicator';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import PhoneStep from '../components/steps/PhoneStep';
import PatientDetailsStep from '../components/steps/PatientDetailsStep';
import SymptomsStep from '../components/steps/SymptomsStep';
import DepartmentStep from '../components/steps/DepartmentStep';
import DoctorStep from '../components/steps/DoctorStep';
import RegistrationService, { QueueService } from "../services/api";

const RegistrationPage = () => {
  const navigate = useNavigate();

  // Core state
  const [sessionId, setSessionId] = useState(null);
  const [currentStep, setCurrentStep] = useState("collect_phone");
  const [agentState, setAgentState] = useState({});
  const [responseData, setResponseData] = useState({});
  const [queueInfo, setQueueInfo] = useState(null);
  const [handoffAnimating, setHandoffAnimating] = useState(false);

  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  /**
   * Main function to communicate with backend
   * BACKEND CONNECTION: This sends requests to the registration agent
   */
  const handleStepSubmit = async (input) => {
    setIsLoading(true);
    setError("");

    try {
      let response;

      // First interaction - start new session
      if (!sessionId) {
        response = await RegistrationService.startRegistration(
          input.phone_number
        );
      }
      // Subsequent interactions - continue existing session
      else {
        response = await RegistrationService.continueRegistration(
          sessionId,
          input
        );
      }

      console.log("Agent Response:", response);

      // Update session tracking
      if (response.session_id) {
        setSessionId(response.session_id);
      }

      // Update agent state
      if (response.state) {
        setAgentState(response.state);
        setCurrentStep(response.state.step);
      }

      // Store response data for rendering
      if (response.response) {
        setResponseData(response.response);
        // Capture queue details for confirmation screen
        if (response.response.queue_status) {
          setQueueInfo(response.response.queue_status);
        }

        // Also map legacy token if returned flat
        if (response.response.token_number && !response.response.queue_status) {
          setQueueInfo({ token_number: response.response.token_number });
        }
      }

      // Handle error messages from backend
      if (
        response.response?.message &&
        response.response.message.includes("Invalid")
      ) {
        setError(response.response.message);
      }
    } catch (err) {
      console.error("Registration Error:", err);
      setError(err.message || "An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // Kick off a short animation window when handoff completes, then auto-navigate
  useEffect(() => {
    if (currentStep === "handoff_complete" && queueInfo?.token_number) {
      setHandoffAnimating(true);
      const animTimer = setTimeout(() => setHandoffAnimating(false), 1800);
      const navTimer = setTimeout(() => {
        navigate("/queue", {
          state: {
            tokenNumber: queueInfo.token_number,
            visitId: agentState.visit_id,
            doctorId: agentState.doctor_id,
            queueDate: new Date().toISOString().split("T")[0],
            patientName: agentState.full_name,
            department: agentState.department_final,
            phoneNumber: agentState.phone_number,
            doctorName: agentState.doctor_name,
          },
        });
      }, 2500); // Navigate after animation + brief pause

      return () => {
        clearTimeout(animTimer);
        clearTimeout(navTimer);
      };
    }
  }, [currentStep, queueInfo, agentState, navigate]);

  /**
   * Render appropriate step based on current agent state
   */
  const renderCurrentStep = () => {
    switch (currentStep) {
      case "collect_phone":
      case "patient_lookup":
        return <PhoneStep onSubmit={handleStepSubmit} isLoading={isLoading} />;

      case "collect_patient_details":
        return (
          <PatientDetailsStep
            onSubmit={handleStepSubmit}
            isLoading={isLoading}
          />
        );

      case "collect_symptoms":
        return (
          <SymptomsStep
            onSubmit={handleStepSubmit}
            isLoading={isLoading}
            patientName={agentState.full_name}
          />
        );

      case "resolve_department":
        return (
          <DepartmentStep
            onSubmit={handleStepSubmit}
            isLoading={isLoading}
            suggestedDepartment={responseData.suggested_department}
            confidence={responseData.confidence}
            reasoning={responseData.reasoning}
            departments={responseData.departments || []}
          />
        );

      case "select_doctor":
        return (
          <DoctorStep
            onSubmit={handleStepSubmit}
            isLoading={isLoading}
            doctors={responseData.doctors || []}
          />
        );

      case "create_visit":
        return (
          <div className="card">
            <LoadingSpinner message="Creating your appointment..." />
          </div>
        );

      case "handoff_complete": {
        const token = queueInfo?.token_number;
        return (
          <div className="card">
            <div className="mb-4 text-center">
              <p className="text-sm font-semibold text-primary-700 uppercase tracking-wide">
                Appointment booked
              </p>
              <h2 className="text-2xl font-bold text-gray-900 mt-1">
                I’m handing you to the queue agent
              </h2>
              <p className="text-sm text-gray-600 mt-2">
                I’ve confirmed your visit with {agentState.full_name || "you"}{" "}
                in {agentState.department_final || "the selected department"}.
              </p>
            </div>

            {/* Animated handoff state */}
            {handoffAnimating && (
              <div className="flex flex-col items-center gap-3 py-6">
                <div className="relative">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-r from-primary-500 to-indigo-500 animate-pulse" />
                  <div className="absolute inset-2 rounded-full border-4 border-primary-100 animate-spin" />
                </div>
                <p className="text-sm text-gray-700">
                  Handing over to queue agent… securing your token
                </p>
              </div>
            )}

            {/* Token reveal */}
            {!handoffAnimating && (
              <div className="bg-gradient-to-br from-primary-50 to-primary-100 border border-primary-200 rounded-lg p-4 text-center">
                <p className="text-xs font-semibold text-primary-700 mb-2">
                  You’re in the queue
                </p>
                <div className="text-5xl font-extrabold text-primary-700 mb-1">
                  {token || "—"}
                </div>
                <p className="text-sm text-primary-700">Token number</p>
              </div>
            )}

            <div className="mt-6 flex gap-3">
              <button
                onClick={() => {
                  if (!token) return;
                  navigate("/success", {
                    state: {
                      tokenNumber: token,
                      patientName: agentState.full_name,
                      department: agentState.department_final,
                      phoneNumber: agentState.phone_number,
                    },
                  });
                }}
                disabled={!queueInfo || !token}
                className="btn-primary flex-1"
              >
                View queue details
              </button>
              <button onClick={() => navigate("/")} className="btn-secondary">
                Start new
              </button>
            </div>
          </div>
        );
      }

      default:
        return (
          <div className="card text-center py-8">
            <p className="text-gray-600">Unknown step: {currentStep}</p>
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Progress Indicator */}
      <StepIndicator currentStep={currentStep} />

      {/* Error Display */}
      <ErrorMessage message={error} onClose={() => setError("")} />

      {/* Current Step Content */}
      {renderCurrentStep()}

      {/* Debug Info - Remove in production */}
      {process.env.NODE_ENV === "development" && (
        <div className="mt-8 p-4 bg-gray-100 rounded-lg">
          <details>
            <summary className="font-medium text-gray-700 cursor-pointer">
              Debug Info (Dev Only)
            </summary>
            <div className="mt-2 space-y-2">
              <div>
                <span className="font-medium">Session ID:</span>
                <code className="ml-2 text-xs bg-white px-2 py-1 rounded">
                  {sessionId || "Not started"}
                </code>
              </div>
              <div>
                <span className="font-medium">Current Step:</span>
                <code className="ml-2 text-xs bg-white px-2 py-1 rounded">
                  {currentStep}
                </code>
              </div>
              <div>
                <span className="font-medium">Agent State:</span>
                <pre className="mt-1 text-xs bg-white p-2 rounded overflow-auto">
                  {JSON.stringify(agentState, null, 2)}
                </pre>
              </div>
            </div>
          </details>
        </div>
      )}
    </div>
  );
};

export default RegistrationPage;
