import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import PostsPage from './pages/PostsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import TestPage from './pages/TestPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/posts" element={<PostsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/test" element={<TestPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
