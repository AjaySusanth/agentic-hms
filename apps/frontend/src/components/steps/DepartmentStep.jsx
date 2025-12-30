import { useState } from 'react';
import { Building2, CheckCircle2, AlertCircle } from 'lucide-react';

const DepartmentStep = ({ 
  onSubmit, 
  isLoading, 
  suggestedDepartment,
  confidence,
  reasoning,
  departments = []
}) => {
  const [selectedDepartment, setSelectedDepartment] = useState(suggestedDepartment || '');
  const [showOverride, setShowOverride] = useState(false);

  const handleConfirm = () => {
    onSubmit({ confirm: true });
  };

  const handleOverride = () => {
    if (selectedDepartment && selectedDepartment !== suggestedDepartment) {
      onSubmit({ department_override: selectedDepartment });
    }
  };

  const getConfidenceColor = (conf) => {
    if (conf >= 0.8) return 'text-green-600 bg-green-50';
    if (conf >= 0.6) return 'text-yellow-600 bg-yellow-50';
    return 'text-orange-600 bg-orange-50';
  };

  const getConfidenceLabel = (conf) => {
    if (conf >= 0.8) return 'High Confidence';
    if (conf >= 0.6) return 'Medium Confidence';
    return 'Low Confidence';
  };

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-primary-100 p-3 rounded-lg">
          <Building2 className="w-6 h-6 text-primary-600" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            Department Selection
          </h2>
          <p className="text-sm text-gray-600">
            Based on your symptoms
          </p>
        </div>
      </div>

      {/* AI Suggestion */}
      {suggestedDepartment && (
        <div className="mb-6 border-2 border-primary-200 bg-primary-50 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gray-900">
                  Recommended Department
                </h3>
                {confidence && (
                  <span className={`text-xs font-medium px-2 py-1 rounded-full ${getConfidenceColor(confidence)}`}>
                    {getConfidenceLabel(confidence)} ({Math.round(confidence * 100)}%)
                  </span>
                )}
              </div>
              
              <p className="text-lg font-medium text-primary-700 mb-2">
                {suggestedDepartment}
              </p>

              {reasoning && reasoning.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm font-medium text-gray-700 mb-1">Reasoning:</p>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {reasoning.map((reason, index) => (
                      <li key={index}>• {reason}</li>
                    ))}
                  </ul>
                </div>
              )}

              {!showOverride && (
                <div className="mt-4 flex gap-3">
                  <button
                    onClick={handleConfirm}
                    disabled={isLoading}
                    className="btn-primary flex-1"
                  >
                    {isLoading ? 'Processing...' : 'Confirm & Continue'}
                  </button>
                  <button
                    onClick={() => setShowOverride(true)}
                    disabled={isLoading}
                    className="btn-secondary"
                  >
                    Choose Different
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Department Override Selection */}
      {(showOverride || !suggestedDepartment) && departments.length > 0 && (
        <div>
          {showOverride && (
            <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-yellow-800">
                Please select a department from the list below
              </p>
            </div>
          )}

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select Department <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-1 gap-3">
              {departments.map((dept) => (
                <label
                  key={dept}
                  className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    selectedDepartment === dept
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                >
                  <input
                    type="radio"
                    name="department"
                    value={dept}
                    checked={selectedDepartment === dept}
                    onChange={(e) => setSelectedDepartment(e.target.value)}
                    className="w-4 h-4 text-primary-600"
                    disabled={isLoading}
                  />
                  <span className="ml-3 font-medium text-gray-900">
                    {dept}
                  </span>
                  {dept === suggestedDepartment && (
                    <span className="ml-auto text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded-full">
                      Recommended
                    </span>
                  )}
                </label>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleOverride}
              disabled={isLoading || !selectedDepartment}
              className="btn-primary flex-1"
            >
              {isLoading ? 'Processing...' : 'Continue with Selected Department'}
            </button>
            {showOverride && (
              <button
                onClick={() => {
                  setShowOverride(false);
                  setSelectedDepartment(suggestedDepartment);
                }}
                disabled={isLoading}
                className="btn-secondary"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      )}

      {/* No departments available */}
      {departments.length === 0 && !suggestedDepartment && (
        <div className="text-center py-8">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600">No departments available</p>
        </div>
      )}
    </div>
  );
};

export default DepartmentStep;
