import React from 'react';
import './App.css';

function App() {
  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <img src="./logo.svg" alt="App Logo" style={styles.logo} />
        <h1 style={styles.title}>Welcome to My React App</h1>
        <p style={styles.description}>
          Edit <code style={styles.code}>src/App.js</code> and save to reload.
        </p>
        <a
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
          style={styles.link}
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

const styles = {
  container: {
    textAlign: 'center',
    fontFamily: "'Arial', sans-serif",
    backgroundColor: '#f0f2f5',
    height: '100vh',
    margin: '0',
  },
  header: {
    padding: '20px',
    backgroundColor: '#282c34',
    color: 'white',
    borderRadius: '10px',
    margin: '20px',
  },
  logo: {
    height: '100px',
    animation: 'spin infinite 20s linear',
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: 'bold',
    margin: '10px 0',
  },
  description: {
    fontSize: '1.2rem',
    margin: '10px 0',
  },
  code: {
    backgroundColor: '#222',
    color: '#61dafb',
    padding: '2px 5px',
    borderRadius: '3px',
  },
  link: {
    textDecoration: 'none',
    color: '#61dafb',
    fontSize: '1.2rem',
    marginTop: '15px',
    display: 'inline-block',
    padding: '10px 20px',
    border: '1px solid #61dafb',
    borderRadius: '5px',
    transition: 'all 0.3s ease',
  },
};

export default App;
