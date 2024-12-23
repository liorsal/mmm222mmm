import React from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import BloodTestAnalyzer from './components/BloodTestAnalyzer';
import Insights from './components/Insights';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <div className="header-content">
            <h1>Blood Test Analyzer</h1>
            <nav>
              <a href="/">Analyze</a>
              <a href="/insights">Insights</a>
            </nav>
          </div>
        </header>
        
        <main>
          <Routes>
            <Route path="/insights" element={<Insights />} />
            <Route path="/" element={<BloodTestAnalyzer />} />
          </Routes>
        </main>

        <footer className="App-footer">
          <div className="footer-content">
            <p>© 2024 Blood Test Analyzer. All rights reserved.</p>
            <div className="footer-links">
              <a href="/disclaimer">Disclaimer</a>
              <a href="/contact">Contact</a>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
