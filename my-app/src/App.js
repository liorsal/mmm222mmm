import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import UploadReport from './components/UploadReport';
import Insights from './components/Insights';
import Overview from './components/Overview';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Personal Health Report Analysis</h1>
          <nav>
            <a href="/">Home</a>
            <a href="/upload">Upload Report</a>
            <a href="/insights">Insights</a>
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/upload" element={<UploadReport />} />
            <Route path="/insights" element={<Insights />} />
            <Route path="/" element={<Overview />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
