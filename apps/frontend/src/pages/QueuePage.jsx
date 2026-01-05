import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  CheckCircle2,
  Clock,
  Users,
  MapPin,
  Phone,
  Calendar,
  User,
  Building2,
  Stethoscope,
  RefreshCw,
  Bell,
  BellOff,
  HelpCircle,
  Home,
} from "lucide-react";
import RegistrationService, { QueueService } from "../services/api";

const QueuePage = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Queue data from registration
  const queueData = location.state || {};

  // State
  const [queueStatus, setQueueStatus] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isCheckingIn, setIsCheckingIn] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);
  const [error, setError] = useState("");

  // Redirect if no queue data
  useEffect(() => {
    if (!queueData.tokenNumber || !queueData.visitId || !queueData.doctorId) {
      navigate("/");
    }
  }, [queueData, navigate]);

  // Fetch queue status
  const fetchQueueStatus = async (showLoader = false) => {
    if (showLoader) setIsRefreshing(true);
    setError("");

    try {
      const status = await QueueService.getQueueStatus({
        visit_id: queueData.visitId,
        doctor_id: queueData.doctorId,
        queue_date:
          queueData.queueDate || new Date().toISOString().split("T")[0],
        role: "patient",
      });

      setQueueStatus(status);
    } catch (err) {
      console.error("Queue status error:", err);
      setError(err.message || "Unable to fetch queue status");
    } finally {
      if (showLoader) setIsRefreshing(false);
    }
  };

  // Auto-poll every 10 seconds
  useEffect(() => {
    if (!queueData.visitId) return;

    fetchQueueStatus(true);
    const interval = setInterval(() => fetchQueueStatus(false), 10000);

    return () => clearInterval(interval);
  }, [queueData.visitId]);

  // Redirect to home when consultation is completed
  useEffect(() => {
    if (queueStatus?.status === "completed") {
      const timer = setTimeout(() => {
        navigate("/", { replace: true });
      }, 3000); // Show completed status for 3 seconds before redirecting

      return () => clearTimeout(timer);
    }
  }, [queueStatus?.status, navigate]);

  // Handle check-in
  const handleCheckIn = async () => {
    setIsCheckingIn(true);
    setError("");

    try {
      await QueueService.checkIn({
        visit_id: queueData.visitId,
        queue_date:
          queueData.queueDate || new Date().toISOString().split("T")[0],
      });

      // Refresh status
      await fetchQueueStatus(false);
    } catch (err) {
      console.error("Check-in error:", err);
      setError(err.message || "Check-in failed");
    } finally {
      setIsCheckingIn(false);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      waiting: { color: "bg-yellow-100 text-yellow-700", label: "Waiting" },
      present: { color: "bg-green-100 text-green-700", label: "Present" },
      called: { color: "bg-blue-100 text-blue-700", label: "Called" },
      in_consultation: {
        color: "bg-purple-100 text-purple-700",
        label: "In Consultation",
      },
      completed: { color: "bg-gray-100 text-gray-700", label: "Completed" },
      skipped: { color: "bg-red-100 text-red-700", label: "Skipped" },
    };

    const badge = badges[status] || badges.waiting;
    return (
      <span
        className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${badge.color}`}
      >
        {badge.label}
      </span>
    );
  };

  const getProgressSteps = () => {
    const steps = [
      { key: "waiting", label: "Booked" },
      { key: "present", label: "Checked In" },
      { key: "called", label: "Called" },
      { key: "in_consultation", label: "In Consultation" },
    ];

    const currentStatus = queueStatus?.status || "waiting";
    const statusOrder = [
      "waiting",
      "present",
      "called",
      "in_consultation",
      "completed",
    ];
    const currentIndex = statusOrder.indexOf(currentStatus);

    return steps.map((step, index) => {
      const stepIndex = statusOrder.indexOf(step.key);
      const isCompleted = stepIndex < currentIndex;
      const isActive = stepIndex === currentIndex;

      return { ...step, isCompleted, isActive };
    });
  };

  if (!queueData.tokenNumber) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Hero Card */}
      <div className="card bg-gradient-to-br from-primary-50 to-indigo-50 border-2 border-primary-200">
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-sm font-semibold text-primary-700 uppercase tracking-wide mb-1">
              You're in the queue
            </p>
            <h1 className="text-3xl font-bold text-gray-900">
              Token #{queueData.tokenNumber}
            </h1>
            <p className="text-sm text-gray-600 mt-2">
              I've secured your spot; I'll keep this updated for you.
            </p>
          </div>
          {queueStatus && getStatusBadge(queueStatus.status)}
        </div>

        {/* Visit Info Grid */}
        <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-primary-200">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-primary-600" />
            <div>
              <p className="text-xs text-gray-600">Patient</p>
              <p className="text-sm font-medium text-gray-900">
                {queueData.patientName}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-primary-600" />
            <div>
              <p className="text-xs text-gray-600">Department</p>
              <p className="text-sm font-medium text-gray-900">
                {queueData.department}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Stethoscope className="w-4 h-4 text-primary-600" />
            <div>
              <p className="text-xs text-gray-600">Doctor</p>
              <p className="text-sm font-medium text-gray-900">
                {queueData.doctorName || "Assigned"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-primary-600" />
            <div>
              <p className="text-xs text-gray-600">Date</p>
              <p className="text-sm font-medium text-gray-900">
                {new Date().toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                })}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Live Status Card */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Live Queue Status
          </h2>
          <button
            onClick={() => fetchQueueStatus(true)}
            disabled={isRefreshing}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Refresh status"
          >
            <RefreshCw
              className={`w-5 h-5 text-gray-600 ${
                isRefreshing ? "animate-spin" : ""
              }`}
            />
          </button>
        </div>

        {queueStatus ? (
          <div className="space-y-4">
            {/* Current Progress */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg text-center">
                <Clock className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                <p className="text-xs text-gray-600 mb-1">Current Token</p>
                <p className="text-2xl font-bold text-blue-700">
                  {queueStatus.current_token || "—"}
                </p>
              </div>

              <div className="bg-green-50 p-4 rounded-lg text-center">
                <CheckCircle2 className="w-6 h-6 text-green-600 mx-auto mb-2" />
                <p className="text-xs text-gray-600 mb-1">Present Ahead</p>
                <p className="text-2xl font-bold text-green-700">
                  {queueStatus.present_ahead ??
                    queueStatus.patients_ahead ??
                    "—"}
                </p>
                <p className="text-xs text-gray-500 mt-1">Checked in</p>
              </div>

              <div className="bg-yellow-50 p-4 rounded-lg text-center">
                <Users className="w-6 h-6 text-yellow-600 mx-auto mb-2" />
                <p className="text-xs text-gray-600 mb-1">Waiting Ahead</p>
                <p className="text-2xl font-bold text-yellow-700">
                  {queueStatus.waiting_ahead ?? "—"}
                </p>
                <p className="text-xs text-gray-500 mt-1">Not checked in</p>
              </div>
            </div>

            {/* Status explanation */}
            {queueStatus.status === "present" && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start gap-2">
                <CheckCircle2 className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-blue-800">
                  <p className="font-medium">You're checked in and ready!</p>
                  <p className="mt-1">
                    {queueStatus.estimated_wait_minutes
                      ? `I estimate ~${queueStatus.estimated_wait_minutes} minutes until you're called.`
                      : "You'll be called after those checked in before you."}
                  </p>
                </div>
              </div>
            )}

            {/* Agent Message */}
            {queueStatus.message && (
              <div className="bg-primary-50 border border-primary-200 rounded-lg p-3">
                <p className="text-sm text-primary-800">
                  {queueStatus.message}
                </p>
              </div>
            )}

            {/* Check-in CTA */}
            {queueStatus.status === "waiting" && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800 mb-3">
                  Please check in when you arrive at the hospital
                </p>
                <button
                  onClick={handleCheckIn}
                  disabled={isCheckingIn}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  <MapPin className="w-4 h-4" />
                  {isCheckingIn ? "Checking in..." : "I'm here"}
                </button>
              </div>
            )}

            {/* Called State */}
            {queueStatus.status === "called" && (
              <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4 text-center animate-pulse">
                <CheckCircle2 className="w-12 h-12 text-blue-600 mx-auto mb-2" />
                <p className="text-lg font-semibold text-blue-900">
                  You've been called!
                </p>
                <p className="text-sm text-blue-700 mt-1">
                  Please proceed to the consultation room
                </p>
              </div>
            )}

            {/* Completed State */}
            {queueStatus.status === "completed" && (
              <div className="bg-green-50 border-2 border-green-300 rounded-lg p-4 text-center">
                <CheckCircle2 className="w-12 h-12 text-green-600 mx-auto mb-2" />
                <p className="text-lg font-semibold text-green-900">
                  Consultation Complete!
                </p>
                <p className="text-sm text-green-700 mt-1">
                  Thank you for your visit. Redirecting to home...
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="animate-spin w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full mx-auto mb-3"></div>
            <p className="text-sm text-gray-600">Loading queue status...</p>
          </div>
        )}

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}
      </div>

      {/* Progress Timeline */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Your Progress
        </h2>
        <div className="flex items-center justify-between">
          {getProgressSteps().map((step, index) => (
            <div key={step.key} className="flex items-center flex-1">
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all ${
                    step.isCompleted
                      ? "bg-green-500 text-white"
                      : step.isActive
                      ? "bg-primary-600 text-white ring-4 ring-primary-200"
                      : "bg-gray-200 text-gray-500"
                  }`}
                >
                  {step.isCompleted ? (
                    <CheckCircle2 className="w-5 h-5" />
                  ) : (
                    index + 1
                  )}
                </div>
                <span
                  className={`mt-2 text-xs font-medium text-center ${
                    step.isActive
                      ? "text-primary-700"
                      : step.isCompleted
                      ? "text-green-700"
                      : "text-gray-500"
                  }`}
                >
                  {step.label}
                </span>
              </div>
              {index < getProgressSteps().length - 1 && (
                <div
                  className={`flex-1 h-1 mx-2 transition-all ${
                    step.isCompleted ? "bg-green-500" : "bg-gray-200"
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Notifications & Options */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Stay Updated
        </h2>

        {/* Notifications Toggle */}
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg mb-4">
          <div className="flex items-center gap-3">
            {notificationsEnabled ? (
              <Bell className="w-5 h-5 text-primary-600" />
            ) : (
              <BellOff className="w-5 h-5 text-gray-400" />
            )}
            <div>
              <p className="font-medium text-gray-900">Enable Notifications</p>
              <p className="text-xs text-gray-600">
                Get alerts when you're called
              </p>
            </div>
          </div>
          <button
            onClick={() => setNotificationsEnabled(!notificationsEnabled)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              notificationsEnabled ? "bg-primary-600" : "bg-gray-300"
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                notificationsEnabled ? "translate-x-6" : "translate-x-1"
              }`}
            />
          </button>
        </div>

        {/* Help Options */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button className="flex items-center gap-2 p-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            <Phone className="w-4 h-4 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">
              Contact Reception
            </span>
          </button>
          <button className="flex items-center gap-2 p-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            <HelpCircle className="w-4 h-4 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">
              Need Help?
            </span>
          </button>
        </div>
      </div>

      {/* New Registration */}
      <div className="text-center">
        <button
          onClick={() => navigate("/")}
          className="btn-secondary inline-flex items-center gap-2"
        >
          <Home className="w-4 h-4" />
          Start New Registration
        </button>
      </div>
    </div>
  );
};

export default QueuePage;
