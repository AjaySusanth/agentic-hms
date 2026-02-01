import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { LogIn, User, Loader } from "lucide-react";
import { DoctorService } from "../services/api";
import ErrorMessage from "../components/ErrorMessage";

const DoctorLoginPage = () => {
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Please enter your name");
      return;
    }

    setLoading(true);

    try {
      const doctorData = await DoctorService.login(name);
      
      // Store doctor info in localStorage for the session
      localStorage.setItem("doctorId", doctorData.doctor_id);
      localStorage.setItem("doctorName", doctorData.name);
      localStorage.setItem("doctorSpecialization", doctorData.specialization || "");
      localStorage.setItem("doctorDepartment", doctorData.department_name || "");
      
      // Navigate to doctor dashboard
      navigate("/doctor");
    } catch (err) {
      console.error("Login error:", err);
      setError(err.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
        <div className="text-center mb-8">
          <div className="bg-indigo-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <User size={32} className="text-indigo-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Doctor Login
          </h1>
          <p className="text-gray-500">
            Enter your name to access the dashboard
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Doctor Name
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Dr. Smith"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
              disabled={loading}
            />
          </div>

          {error && <ErrorMessage message={error} />}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader size={20} className="animate-spin" />
                Logging in...
              </>
            ) : (
              <>
                <LogIn size={20} />
                Login
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Simplified login for MVP</p>
          <p className="mt-1">Enter any part of the doctor's name</p>
        </div>
      </div>
    </div>
  );
};

export default DoctorLoginPage;
