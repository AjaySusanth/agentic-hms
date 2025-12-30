import { useState } from 'react';
import { UserCircle, Star, CheckCircle2 } from 'lucide-react';

const DoctorStep = ({ onSubmit, isLoading, doctors = [] }) => {
  const [selectedDoctor, setSelectedDoctor] = useState(null);

  const handleSubmit = () => {
    if (selectedDoctor) {
      onSubmit({ doctor_id: selectedDoctor.id });
    }
  };

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-primary-100 p-3 rounded-lg">
          <UserCircle className="w-6 h-6 text-primary-600" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            Select a Doctor
          </h2>
          <p className="text-sm text-gray-600">
            Choose from available doctors
          </p>
        </div>
      </div>

      {doctors.length > 0 ? (
        <>
          <div className="mb-6 space-y-3">
            {doctors.map((doctor) => (
              <div
                key={doctor.id}
                onClick={() => !isLoading && setSelectedDoctor(doctor)}
                className={`relative p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  selectedDoctor?.id === doctor.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <div className="flex items-start gap-4">
                  {/* Doctor Avatar */}
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0">
                    {doctor.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                  </div>

                  {/* Doctor Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-gray-900">
                        {doctor.name}
                      </h3>
                      {selectedDoctor?.id === doctor.id && (
                        <CheckCircle2 className="w-5 h-5 text-primary-600 flex-shrink-0" />
                      )}
                    </div>
                    
                    {doctor.specialization && (
                      <p className="text-sm text-gray-600 mb-2">
                        {doctor.specialization}
                      </p>
                    )}

                    {/* Mock rating - can be removed or made dynamic */}
                    <div className="flex items-center gap-1">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className="w-4 h-4 fill-yellow-400 text-yellow-400"
                        />
                      ))}
                      <span className="text-xs text-gray-500 ml-1">
                        (4.8)
                      </span>
                    </div>
                  </div>

                  {/* Selection Radio */}
                  <div className="flex-shrink-0">
                    <div
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                        selectedDoctor?.id === doctor.id
                          ? 'border-primary-600 bg-primary-600'
                          : 'border-gray-300'
                      }`}
                    >
                      {selectedDoctor?.id === doctor.id && (
                        <div className="w-2 h-2 bg-white rounded-full" />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={isLoading || !selectedDoctor}
            className="btn-primary w-full"
          >
            {isLoading ? 'Booking...' : 'Book Appointment'}
          </button>
        </>
      ) : (
        <div className="text-center py-8">
          <UserCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-600 font-medium mb-2">
            No doctors available
          </p>
          <p className="text-sm text-gray-500">
            Please try again later or contact support
          </p>
        </div>
      )}
    </div>
  );
};

export default DoctorStep;
