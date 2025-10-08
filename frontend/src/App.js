import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import '@/App.css';
import LandingPage from '@/pages/LandingPage';
import LoginPage from '@/pages/LoginPage';
import ManagerDashboard from '@/pages/ManagerDashboard';
import EmployeeDashboard from '@/pages/EmployeeDashboard';
import ClientDashboard from '@/pages/ClientDashboard';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { Toaster } from 'sonner';

function PrivateRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/manager/*"
        element={
          <PrivateRoute allowedRoles={['MANAGER']}>
            <ManagerDashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/employee/*"
        element={
          <PrivateRoute allowedRoles={['EMPLOYEE']}>
            <EmployeeDashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/client/*"
        element={
          <PrivateRoute allowedRoles={['CLIENT']}>
            <ClientDashboard />
          </PrivateRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
          <Toaster position="top-right" richColors />
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
