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
import RegistrationService from '../services/api';

const RegistrationPage = () => {
  const navigate = useNavigate();
  
  // Core state
  const [sessionId, setSessionId] = useState(null);
  const [currentStep, setCurrentStep] = useState('collect_phone');
  const [agentState, setAgentState] = useState({});
  const [responseData, setResponseData] = useState({});
  
  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  /**
   * Main function to communicate with backend
   * BACKEND CONNECTION: This sends requests to the registration agent
   */
  const handleStepSubmit = async (input) => {
    setIsLoading(true);
    setError('');

    try {
      let response;

      // First interaction - start new session
      if (!sessionId) {
        response = await RegistrationService.startRegistration(input.phone_number);
      } 
      // Subsequent interactions - continue existing session
      else {
        response = await RegistrationService.continueRegistration(sessionId, input);
      }

      console.log('Agent Response:', response);

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

        // Check if registration is complete
        if (response.state?.step === 'handoff_complete' && response.response.token_number) {
          // Navigate to success page with registration details
          navigate('/success', {
            state: {
              tokenNumber: response.response.token_number,
              patientName: response.state.full_name,
              department: response.state.department_final,
              phoneNumber: response.state.phone_number
            }
          });
        }
      }

      // Handle error messages from backend
      if (response.response?.message && response.response.message.includes('Invalid')) {
        setError(response.response.message);
      }

    } catch (err) {
      console.error('Registration Error:', err);
      setError(
        err.message || 
        'An error occurred. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Render appropriate step based on current agent state
   */
  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'collect_phone':
      case 'patient_lookup':
        return (
          <PhoneStep
            onSubmit={handleStepSubmit}
            isLoading={isLoading}
          />
        );

      case 'collect_patient_details':
        return (
          <PatientDetailsStep
            onSubmit={handleStepSubmit}
            isLoading={isLoading}
          />
        );

      case 'collect_symptoms':
        return (
          <SymptomsStep
            onSubmit={handleStepSubmit}
            isLoading={isLoading}
            patientName={agentState.full_name}
          />
        );

      case 'resolve_department':
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

      case 'select_doctor':
        return (
          <DoctorStep
            onSubmit={handleStepSubmit}
            isLoading={isLoading}
            doctors={responseData.doctors || []}
          />
        );

      case 'create_visit':
        return (
          <div className="card">
            <LoadingSpinner message="Creating your appointment..." />
          </div>
        );

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
      <ErrorMessage 
        message={error} 
        onClose={() => setError('')} 
      />

      {/* Current Step Content */}
      {renderCurrentStep()}

      {/* Debug Info - Remove in production */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-8 p-4 bg-gray-100 rounded-lg">
          <details>
            <summary className="font-medium text-gray-700 cursor-pointer">
              Debug Info (Dev Only)
            </summary>
            <div className="mt-2 space-y-2">
              <div>
                <span className="font-medium">Session ID:</span>
                <code className="ml-2 text-xs bg-white px-2 py-1 rounded">
                  {sessionId || 'Not started'}
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
