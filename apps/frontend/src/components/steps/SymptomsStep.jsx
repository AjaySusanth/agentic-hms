import { useState } from 'react';
import { FileText } from 'lucide-react';

const SymptomsStep = ({ onSubmit, isLoading, patientName }) => {
  const [symptoms, setSymptoms] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!symptoms.trim() || symptoms.trim().length < 5) {
      setError('Please describe your symptoms clearly (at least 5 characters)');
      return;
    }

    onSubmit({ symptoms: symptoms.trim() });
  };

  const handleChange = (e) => {
    setSymptoms(e.target.value);
    if (error) setError('');
  };

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-primary-100 p-3 rounded-lg">
          <FileText className="w-6 h-6 text-primary-600" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            Describe Your Symptoms
          </h2>
          {patientName && (
            <p className="text-sm text-gray-600">
              Welcome back, {patientName}!
            </p>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="mb-6">
          <label
            htmlFor="symptoms"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            What brings you to the hospital today? <span className="text-red-500">*</span>
          </label>
          <textarea
            id="symptoms"
            value={symptoms}
            onChange={handleChange}
            placeholder="Please describe your symptoms in detail..."
            rows={6}
            className={`input-field resize-none ${error ? 'border-red-500' : ''}`}
            disabled={isLoading}
            autoFocus
          />
          {error && (
            <p className="mt-2 text-sm text-red-600">{error}</p>
          )}
          <div className="mt-2 flex justify-between items-center text-xs text-gray-500">
            <span>Be as detailed as possible to help us assist you better</span>
            <span>{symptoms.length} characters</span>
          </div>
        </div>

        {/* Example Prompts */}
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <p className="text-sm font-medium text-gray-700 mb-2">Examples:</p>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• "I have been experiencing chest pain and shortness of breath for the past 2 days"</li>
            <li>• "Severe headache with fever and body ache since yesterday"</li>
            <li>• "Injured my ankle while playing sports, swelling and pain"</li>
          </ul>
        </div>

        <button
          type="submit"
          disabled={isLoading || !symptoms.trim()}
          className="btn-primary w-full"
        >
          {isLoading ? 'Analyzing...' : 'Continue'}
        </button>
      </form>
    </div>
  );
};

export default SymptomsStep;
