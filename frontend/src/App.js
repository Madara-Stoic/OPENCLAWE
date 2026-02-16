import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { useState, useEffect } from "react";
import { LandingPage } from "@/pages/LandingPage";
import { PatientDashboard } from "@/pages/PatientDashboard";
import { DoctorDashboard } from "@/pages/DoctorDashboard";
import { OrganizationDashboard } from "@/pages/OrganizationDashboard";
import { AuthContext } from "@/context/AuthContext";

function App() {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for stored auth
    const storedUser = localStorage.getItem('omnihealth_user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = (userData) => {
    setUser(userData);
    localStorage.setItem('omnihealth_user', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('omnihealth_user');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      <div className="App min-h-screen bg-background">
        <BrowserRouter>
          <Routes>
            <Route 
              path="/" 
              element={user ? <Navigate to={`/${user.role}`} replace /> : <LandingPage />} 
            />
            <Route 
              path="/patient" 
              element={user?.role === 'patient' ? <PatientDashboard /> : <Navigate to="/" replace />} 
            />
            <Route 
              path="/doctor" 
              element={user?.role === 'doctor' ? <DoctorDashboard /> : <Navigate to="/" replace />} 
            />
            <Route 
              path="/organization" 
              element={user?.role === 'organization' ? <OrganizationDashboard /> : <Navigate to="/" replace />} 
            />
          </Routes>
        </BrowserRouter>
        <Toaster position="top-right" theme="dark" />
      </div>
    </AuthContext.Provider>
  );
}

export default App;
