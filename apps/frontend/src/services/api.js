import axios from 'axios';

// BACKEND CONNECTION: Update this URL to match your backend server
const API_BASE_URL = '/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Add request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url, config.data);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.config.url, response.status, response.data);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Registration Agent API Service
 * Maps to: POST /agents/registration/message
 */
class RegistrationService {
  /**
   * Send message to registration agent
   * @param {Object} payload - Request payload
   * @param {string|null} payload.session_id - Session ID (null for new session)
   * @param {Object} payload.input - User input data
   * @returns {Promise<Object>} Response with session_id, response, and state
   */
  static async sendMessage(payload) {
    try {
      // BACKEND CONNECTION: This endpoint should match your FastAPI router
      // Backend endpoint: POST /agents/registration/message
      const response = await apiClient.post('/agents/registration/message', payload);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Start new registration session
   * @param {string} phoneNumber - 10-digit phone number
   * @returns {Promise<Object>} Initial session response
   */
  static async startRegistration(phoneNumber) {
    return this.sendMessage({
      session_id: null,
      input: {
        phone_number: phoneNumber
      }
    });
  }

  /**
   * Continue existing registration session
   * @param {string} sessionId - Existing session ID
   * @param {Object} input - User input for current step
   * @returns {Promise<Object>} Session response
   */
  static async continueRegistration(sessionId, input) {
    return this.sendMessage({
      session_id: sessionId,
      input: input
    });
  }

  /**
   * Handle API errors
   * @private
   */
  static _handleError(error) {
    if (error.response) {
      // Server responded with error status
      return {
        message: error.response.data?.detail || error.response.data?.message || 'Server error occurred',
        status: error.response.status,
        data: error.response.data
      };
    } else if (error.request) {
      // Request made but no response
      return {
        message: 'No response from server. Please check your connection.',
        status: 0
      };
    } else {
      // Error in request setup
      return {
        message: error.message || 'An unexpected error occurred',
        status: -1
      };
    }
  }
}

/**
 * Mock service for development/testing without backend
 * Remove this when connecting to real backend
 */
class MockRegistrationService {
  static mockSession = null;
  static mockStep = 'collect_phone';
  static mockData = {};

  static async sendMessage(payload) {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 500));

    if (!payload.session_id) {
      // Start new session
      this.mockSession = this._generateSessionId();
      this.mockStep = 'collect_phone';
      this.mockData = {};
    }

    const input = payload.input;

    // Simulate step-by-step flow
    switch (this.mockStep) {
      case 'collect_phone':
        if (input.phone_number) {
          this.mockData.phone_number = input.phone_number;
          // Simulate existing patient (for demo)
          const isExisting = input.phone_number.startsWith('98'); // Mock: numbers starting with 98 are existing
          
          if (isExisting) {
            this.mockStep = 'collect_symptoms';
            this.mockData.patient_id = this._generateUUID();
            this.mockData.full_name = 'John Doe';
            this.mockData.age = 35;
            return this._createResponse('Please describe your symptoms.');
          } else {
            this.mockStep = 'collect_patient_details';
            return this._createResponse('Please provide your full name and age.');
          }
        }
        break;

      case 'collect_patient_details':
        if (input.full_name && input.age) {
          this.mockData.full_name = input.full_name;
          this.mockData.age = input.age;
          this.mockData.patient_id = this._generateUUID();
          this.mockStep = 'collect_symptoms';
          return this._createResponse('Please describe your symptoms.');
        }
        break;

      case 'collect_symptoms':
        if (input.symptoms) {
          this.mockData.symptoms = input.symptoms;
          this.mockStep = 'resolve_department';
          
          // Mock department suggestion
          const department = this._mockDepartmentResolver(input.symptoms, this.mockData.age);
          this.mockData.department_suggested = department.name;
          this.mockData.department_confidence = department.confidence;
          
          return this._createResponse(
            `We recommend ${department.name}. Do you want to proceed?`,
            {
              suggested_department: department.name,
              confidence: department.confidence,
              reasoning: department.reasoning,
              expected_input: ['confirm', 'department_override'],
              departments: ['Cardiology', 'General Medicine', 'Pediatrics', 'Orthopedics', 'ENT']
            }
          );
        }
        break;

      case 'resolve_department':
        if (input.confirm) {
          this.mockData.department_final = this.mockData.department_suggested;
          this.mockData.department_id = this._generateUUID();
          this.mockStep = 'select_doctor';
          
          return this._createResponse(
            'Please select a doctor.',
            {
              doctors: [
                { id: this._generateUUID(), name: 'Dr. Sarah Johnson', specialization: 'Senior Physician' },
                { id: this._generateUUID(), name: 'Dr. Michael Chen', specialization: 'Consultant' },
                { id: this._generateUUID(), name: 'Dr. Emily Rodriguez', specialization: 'Specialist' }
              ]
            }
          );
        } else if (input.department_override) {
          this.mockData.department_final = input.department_override;
          this.mockData.department_id = this._generateUUID();
          this.mockStep = 'select_doctor';
          
          return this._createResponse(
            'Please select a doctor.',
            {
              doctors: [
                { id: this._generateUUID(), name: 'Dr. Sarah Johnson', specialization: 'Senior Physician' },
                { id: this._generateUUID(), name: 'Dr. Michael Chen', specialization: 'Consultant' }
              ]
            }
          );
        }
        break;

      case 'select_doctor':
        if (input.doctor_id) {
          this.mockData.doctor_id = input.doctor_id;
          this.mockData.visit_id = this._generateUUID();
          this.mockData.token_number = Math.floor(Math.random() * 100) + 1;
          this.mockStep = 'handoff_complete';
          
          return this._createResponse(
            `Visit registered successfully. Token number: ${this.mockData.token_number}`,
            {
              token_number: this.mockData.token_number,
              handoff_status: 'complete'
            }
          );
        }
        break;
    }

    return this._createResponse('Invalid input. Please try again.');
  }

  static _createResponse(message, additionalData = {}) {
    return {
      session_id: this.mockSession,
      response: {
        message,
        ...additionalData
      },
      state: {
        agent_name: 'registration_agent',
        step: this.mockStep,
        ...this.mockData
      }
    };
  }

  static _generateSessionId() {
    return 'mock-session-' + Math.random().toString(36).substring(7);
  }

  static _generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  static _mockDepartmentResolver(symptoms, age) {
    if (age < 18) {
      return {
        name: 'Pediatrics',
        confidence: 1.0,
        reasoning: ['Patient is under 18 years old']
      };
    }

    const lowerSymptoms = symptoms.toLowerCase();
    
    if (lowerSymptoms.includes('chest') || lowerSymptoms.includes('heart')) {
      return {
        name: 'Cardiology',
        confidence: 0.85,
        reasoning: ['Symptoms indicate potential cardiac issues']
      };
    }
    
    if (lowerSymptoms.includes('bone') || lowerSymptoms.includes('joint') || lowerSymptoms.includes('fracture')) {
      return {
        name: 'Orthopedics',
        confidence: 0.8,
        reasoning: ['Symptoms related to musculoskeletal system']
      };
    }
    
    if (lowerSymptoms.includes('ear') || lowerSymptoms.includes('nose') || lowerSymptoms.includes('throat')) {
      return {
        name: 'ENT',
        confidence: 0.9,
        reasoning: ['Symptoms related to ear, nose, or throat']
      };
    }

    return {
      name: 'General Medicine',
      confidence: 0.7,
      reasoning: ['General symptoms requiring medical consultation']
    };
  }

  static async startRegistration(phoneNumber) {
    return this.sendMessage({
      session_id: null,
      input: { phone_number: phoneNumber }
    });
  }

  static async continueRegistration(sessionId, input) {
    return this.sendMessage({
      session_id: sessionId,
      input: input
    });
  }
}

// BACKEND CONNECTION: Switch between mock and real service
// Set USE_MOCK_API to false when backend is ready
const USE_MOCK_API = false; // Change to false to use real backend

export default USE_MOCK_API ? MockRegistrationService : RegistrationService;
