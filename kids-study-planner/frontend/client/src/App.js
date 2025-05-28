import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import KidRegistrationPage from './pages/KidRegistrationPage';
import KidExamUpdatePage from './pages/KidExamUpdatePage';
import ParentViewPage from './pages/ParentViewPage';
import './App.css';

function App() {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/register">Register Kid</Link></li>
            <li><Link to="/update-exam">Update Exam Info</Link></li>
            <li><Link to="/parent-view">Parent View</Link></li>
          </ul>
        </nav>
        <hr />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/register" element={<KidRegistrationPage />} />
          <Route path="/update-exam" element={<KidExamUpdatePage />} />
          <Route path="/parent-view" element={<ParentViewPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
