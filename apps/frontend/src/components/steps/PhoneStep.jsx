import { useState } from 'react';
import { Phone } from 'lucide-react';

const PhoneStep = ({ onSubmit, isLoading }) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [error, setError] = useState('');

  const validatePhone = (phone) => {
    const phoneRegex = /^\d{10}$/;
    return phoneRegex.test(phone);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!validatePhone(phoneNumber)) {
      setError('Please enter a valid 10-digit phone number');
      return;
    }

    onSubmit({ phone_number: phoneNumber });
  };

  const handlePhoneChange = (e) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 10);
    setPhoneNumber(value);
    if (error) setError('');
  };

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-primary-100 p-3 rounded-lg">
          <Phone className="w-6 h-6 text-primary-600" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            Enter Phone Number
          </h2>
          <p className="text-sm text-gray-600">
            We'll check if you're already registered
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="mb-6">
          <label
            htmlFor="phone"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Phone Number <span className="text-red-500">*</span>
          </label>
          <input
            type="tel"
            id="phone"
            value={phoneNumber}
            onChange={handlePhoneChange}
            placeholder="Enter 10-digit phone number"
            className={`input-field ${error ? 'border-red-500' : ''}`}
            disabled={isLoading}
            autoFocus
          />
          {error && (
            <p className="mt-2 text-sm text-red-600">{error}</p>
          )}
          <p className="mt-2 text-xs text-gray-500">
            Example: 9876543210
          </p>
        </div>

        <button
          type="submit"
          disabled={isLoading || !phoneNumber}
          className="btn-primary w-full"
        >
          {isLoading ? 'Checking...' : 'Continue'}
        </button>
      </form>
    </div>
  );
};

export default PhoneStep;
