import React from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Chat from './components/Chat';
import Insights from './components/Insights';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Medical AI Assistant</h1>
          <nav>
            <a href="/">Chat</a>
            <a href="/insights">Insights</a>
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/insights" element={<Insights />} />
            <Route path="/" element={<Chat />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
