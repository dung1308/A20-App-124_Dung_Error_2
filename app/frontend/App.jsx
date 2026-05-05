import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import WizardPage from './pages/WizardPage';
import ReportPage from './pages/ReportPage';
import DashboardPage from './pages/DashboardPage';
import ConsultantPage from './pages/ConsultantPage';
import AuthPage from './pages/AuthPage';

function App() {
  return (
    <div className="app-container">
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<AuthPage />} />
        <Route path="/wizard" element={<WizardPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/consultant" element={<ConsultantPage />} />
        <Route path="/report" element={<ReportPage />} />
      </Routes>
    </div>
  );
}

export default App;