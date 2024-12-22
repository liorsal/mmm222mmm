import React from 'react';

function Overview() {
  return (
    <section id="overview">
      <h2>Health Overview</h2>
      <div className="overview-grid">
        <div className="metric-card">
          <h3>Recent Reports</h3>
          <p>No reports uploaded yet</p>
        </div>
        <div className="metric-card">
          <h3>Health Score</h3>
          <p>Upload a report to see your score</p>
        </div>
        <div className="metric-card">
          <h3>Recommendations</h3>
          <p>Personalized recommendations will appear here</p>
        </div>
      </div>
    </section>
  );
}

export default Overview; 