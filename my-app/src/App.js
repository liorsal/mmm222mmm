import './App.css';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
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
          <Switch>
            <Route path="/upload" component={UploadReport} />
            <Route path="/insights" component={Insights} />
            <Route path="/" component={Overview} />
          </Switch>
        </main>
      </div>
    </Router>
  );
}

export default App;
