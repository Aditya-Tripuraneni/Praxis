import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { Layout } from "./components/Layout";
import ProtectedRoute from "./components/Auth/ProtectedRoute";
import { useSubscription } from "./context/SubscriptionContext";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Generate from "./pages/Generate";
import Preview from "./pages/Preview";
import VerifySuccess from "./pages/VerifySuccess";
import VerifyEmail from "./pages/VerifyEmail";
import OAuthCallback from "./pages/OAuthCallback";
import CheckoutSuccess from "./pages/CheckoutSuccess";
import CheckoutCancel from "./pages/CheckoutCancel";
import SamplePreview from "./pages/SamplePreview";
import AboutPraxis from "./pages/AboutPraxis";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import SavedTestReplay from "./pages/SavedTestReplay";
import NotFound from "./pages/NotFound";

function SubscriptionGate({ children }: { children: React.ReactNode }) {
  const { isSubscribed, isLoading } = useSubscription();
  const location = useLocation();

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: "2rem" }} role="status" aria-label="Loading">
        Loading...
      </div>
    );
  }

  if (!isSubscribed) {
    return <Navigate to="/dashboard" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        {/* Public routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/sample-preview" element={<SamplePreview />} />
        <Route path="/about-praxis" element={<AboutPraxis />} />
        <Route path="/auth/forgot-password" element={<ForgotPassword />} />
        <Route path="/auth/reset-password" element={<ResetPassword />} />
        <Route path="/auth/verify-success" element={<VerifySuccess />} />
        <Route path="/auth/verify-email" element={<VerifyEmail />} />
        <Route path="/auth/callback" element={<OAuthCallback />} />

        {/* Protected routes */}
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/generate" element={<ProtectedRoute><SubscriptionGate><Generate /></SubscriptionGate></ProtectedRoute>} />
        <Route path="/preview/:testId" element={<ProtectedRoute><SubscriptionGate><Preview /></SubscriptionGate></ProtectedRoute>} />
        <Route path="/saved-test/:id" element={
          <ProtectedRoute>
            <SubscriptionGate>
              <SavedTestReplay />
            </SubscriptionGate>
          </ProtectedRoute>
        } />

        {/* Checkout routes */}
        <Route path="/checkout/success" element={<ProtectedRoute><CheckoutSuccess /></ProtectedRoute>} />
        <Route path="/checkout/cancel" element={<ProtectedRoute><CheckoutCancel /></ProtectedRoute>} />

        {/* Fallback */}
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

export default App;
