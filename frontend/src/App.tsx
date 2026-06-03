import { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "./lib/firebase";
import { useAuthStore } from "./store/authStore";
import Onboarding from "./screens/Onboarding";
import WatchList from "./screens/WatchList";
import CreateWatch from "./screens/CreateWatch";
import AlertInbox from "./screens/AlertInbox";
import AlertDetail from "./screens/AlertDetail";
import type { ReactNode } from "react";

function PrivateRoute({ children }: { children: ReactNode }) {
  const user = useAuthStore((s) => s.user);
  const loading = useAuthStore((s) => s.loading);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f7f8fc] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#1a1f4e] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) return <Navigate to="/" replace />;
  return <>{children}</>;
}

export default function App() {
  const setUser = useAuthStore((s) => s.setUser);
  const setLoading = useAuthStore((s) => s.setLoading);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });
    return unsubscribe;
  }, [setUser, setLoading]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Onboarding />} />
        <Route
          path="/watches"
          element={
            <PrivateRoute>
              <WatchList />
            </PrivateRoute>
          }
        />
        <Route
          path="/watches/new"
          element={
            <PrivateRoute>
              <CreateWatch />
            </PrivateRoute>
          }
        />
        <Route
          path="/alerts"
          element={
            <PrivateRoute>
              <AlertInbox />
            </PrivateRoute>
          }
        />
        <Route
          path="/alerts/:alertId"
          element={
            <PrivateRoute>
              <AlertDetail />
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
