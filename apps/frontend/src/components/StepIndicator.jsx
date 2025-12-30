import { Check } from 'lucide-react';

const StepIndicator = ({ currentStep, totalSteps }) => {
  const steps = [
    { number: 1, label: 'Phone', key: 'collect_phone' },
    { number: 2, label: 'Details', key: 'collect_patient_details' },
    { number: 3, label: 'Symptoms', key: 'collect_symptoms' },
    { number: 4, label: 'Department', key: 'resolve_department' },
    { number: 5, label: 'Doctor', key: 'select_doctor' },
    { number: 6, label: 'Confirm', key: 'create_visit' }
  ];

  const stepOrder = [
    'collect_phone',
    'patient_lookup',
    'collect_patient_details',
    'collect_symptoms',
    'resolve_department',
    'select_doctor',
    'create_visit',
    'handoff_complete'
  ];

  const currentStepIndex = stepOrder.indexOf(currentStep);

  const getStepStatus = (stepIndex) => {
    if (stepIndex < currentStepIndex) return 'completed';
    if (stepIndex === currentStepIndex) return 'active';
    return 'inactive';
  };

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const status = getStepStatus(stepOrder.indexOf(step.key));
          
          return (
            <div key={step.number} className="flex items-center flex-1">
              {/* Step Circle */}
              <div className="flex flex-col items-center">
                <div
                  className={`step-indicator ${status}`}
                >
                  {status === 'completed' ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    step.number
                  )}
                </div>
                <span
                  className={`mt-2 text-xs font-medium ${
                    status === 'active'
                      ? 'text-primary-600'
                      : status === 'completed'
                      ? 'text-green-600'
                      : 'text-gray-400'
                  }`}
                >
                  {step.label}
                </span>
              </div>

              {/* Connector Line */}
              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-2 ${
                    status === 'completed'
                      ? 'bg-green-500'
                      : 'bg-gray-300'
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default StepIndicator;
