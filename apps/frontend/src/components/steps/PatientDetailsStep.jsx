import { useState } from 'react';
import { User } from 'lucide-react';

const PatientDetailsStep = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    full_name: '',
    age: ''
  });
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};

    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
    } else if (formData.full_name.trim().length < 2) {
      newErrors.full_name = 'Name must be at least 2 characters';
    }

    const age = parseInt(formData.age);
    if (!formData.age) {
      newErrors.age = 'Age is required';
    } else if (isNaN(age) || age < 0 || age > 150) {
      newErrors.age = 'Please enter a valid age';
    }

    return newErrors;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const validationErrors = validateForm();

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    onSubmit({
      full_name: formData.full_name.trim(),
      age: parseInt(formData.age)
    });
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleAgeChange = (e) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 3);
    handleChange('age', value);
  };

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-primary-100 p-3 rounded-lg">
          <User className="w-6 h-6 text-primary-600" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            Patient Details
          </h2>
          <p className="text-sm text-gray-600">
            Please provide your basic information
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="space-y-4 mb-6">
          {/* Full Name */}
          <div>
            <label
              htmlFor="full_name"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Full Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="full_name"
              value={formData.full_name}
              onChange={(e) => handleChange('full_name', e.target.value)}
              placeholder="Enter your full name"
              className={`input-field ${errors.full_name ? 'border-red-500' : ''}`}
              disabled={isLoading}
              autoFocus
            />
            {errors.full_name && (
              <p className="mt-2 text-sm text-red-600">{errors.full_name}</p>
            )}
          </div>

          {/* Age */}
          <div>
            <label
              htmlFor="age"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Age <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="age"
              value={formData.age}
              onChange={handleAgeChange}
              placeholder="Enter your age"
              className={`input-field ${errors.age ? 'border-red-500' : ''}`}
              disabled={isLoading}
            />
            {errors.age && (
              <p className="mt-2 text-sm text-red-600">{errors.age}</p>
            )}
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading || !formData.full_name || !formData.age}
          className="btn-primary w-full"
        >
          {isLoading ? 'Saving...' : 'Continue'}
        </button>
      </form>
    </div>
  );
};

export default PatientDetailsStep;
