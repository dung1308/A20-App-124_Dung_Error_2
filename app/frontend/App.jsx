import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import WizardPage from './pages/WizardPage';
import ReportPage from './pages/ReportPage';
import DashboardPage from './pages/DashboardPage';
import ConsultantPage from './pages/ConsultantPage';
import AuthPage from './pages/AuthPage';
import ProfilePage from './pages/ProfilePage';
import TokenUsagePage from './pages/TokenUsagePage';
import DatabaseManagementPage from './pages/DatabaseManagementPage';
import PricingPage from './pages/PricingPage';
import AuthenticatedLayout from './layouts/AuthenticatedLayout';

function App() {
  return (
    <div className="app-container">
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<AuthPage />} />
        <Route path="/wizard" element={<WizardPage />} />

        {/* Protected Routes sharing sidebar and navigation */}
        <Route element={<AuthenticatedLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/consultant" element={<ConsultantPage />} />
          <Route path="/report" element={<ReportPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/system/tokens" element={<TokenUsagePage />} />
          <Route path="/system/database" element={<DatabaseManagementPage />} />
        </Route>
      </Routes>
    </div>
  );
}

export default App;