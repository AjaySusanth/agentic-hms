import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Building2, LogIn, Loader } from "lucide-react";
import { HospitalService } from "../services/api";
import ErrorMessage from "../components/ErrorMessage";

const HospitalLoginPage = () => {
  const [hospitals, setHospitals] = useState([]);
  const [selectedCode, setSelectedCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetchingList, setFetchingList] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Fetch hospital list on mount
  useEffect(() => {
    const fetchHospitals = async () => {
      try {
        const data = await HospitalService.list();
        setHospitals(data);
      } catch (err) {
        setError("Failed to load hospitals. Please refresh.");
      } finally {
        setFetchingList(false);
      }
    };
    fetchHospitals();
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);

    if (!selectedCode) {
      setError("Please select a hospital");
      return;
    }

    setLoading(true);

    try {
      const hospital = await HospitalService.login(selectedCode);

      // Store hospital context in localStorage
      localStorage.setItem("hospital_id", hospital.id);
      localStorage.setItem("hospital_name", hospital.name);
      localStorage.setItem("hospital_code", hospital.code);
      localStorage.setItem("hospital_location", hospital.location);

      // Navigate to registration (home)
      navigate("/");
    } catch (err) {
      setError(err.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
        <div className="text-center mb-8">
          <div className="bg-indigo-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Building2 size={32} className="text-indigo-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Hospital HMS
          </h1>
          <p className="text-gray-500">
            Select your hospital to access the management system
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label
              htmlFor="hospital"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Hospital
            </label>
            {fetchingList ? (
              <div className="flex items-center justify-center py-3 text-gray-400">
                <Loader size={20} className="animate-spin mr-2" />
                Loading hospitals...
              </div>
            ) : (
              <select
                id="hospital"
                value={selectedCode}
                onChange={(e) => setSelectedCode(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition bg-white"
                disabled={loading}
              >
                <option value="">— Select a hospital —</option>
                {hospitals.map((h) => (
                  <option key={h.id} value={h.code}>
                    {h.name} ({h.location})
                  </option>
                ))}
              </select>
            )}
          </div>

          {error && <ErrorMessage message={error} />}

          <button
            type="submit"
            disabled={loading || fetchingList || !selectedCode}
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
                Enter Hospital
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Multi-Hospital Management System</p>
        </div>
      </div>
    </div>
  );
};

export default HospitalLoginPage;
