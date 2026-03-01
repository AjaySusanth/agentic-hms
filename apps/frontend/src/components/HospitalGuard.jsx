import { Navigate } from "react-router-dom";

/**
 * Route guard that redirects to /login if no hospital_id is in localStorage.
 * Wraps protected routes to enforce hospital login.
 */
const HospitalGuard = ({ children }) => {
  const hospitalId = localStorage.getItem("hospital_id");

  if (!hospitalId) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default HospitalGuard;
