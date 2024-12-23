import React from 'react';
import UploadReport from './UploadReport';

function Overview({ recentReports = [], onUpload }) {
  const renderBloodTestResults = (analysis) => {
    if (!analysis.blood_test_results || analysis.blood_test_results.length === 0) {
      return null;
    }

    return (
      <div className="blood-test-results">
        <h4>Blood Test Results</h4>
        <table className="results-table">
          <thead>
            <tr>
              <th>Test</th>
              <th>Value</th>
              <th>Reference Range</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {analysis.blood_test_results.map((test, index) => (
              <tr key={index} className={`status-${test.status}`}>
                <td>{test.test.toUpperCase()}</td>
                <td>{test.value} {test.unit}</td>
                <td>{test.reference_range}</td>
                <td>{test.status.toUpperCase()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="overview-container">
      <section id="overview">
        <h2>Health Overview</h2>
        <div className="overview-grid">
          <div className="metric-card">
            <h3>Recent Reports</h3>
            {recentReports.length > 0 ? (
              <ul className="reports-list">
                {recentReports.map((report, index) => (
                  <li key={index} className="report-item">
                    <div className="report-name">{report.name}</div>
                    <div className="report-date">{report.date}</div>
                    <div className="report-status">
                      Status: {report.analysis ? 'Analyzed' : 'Processing'}
                    </div>
                    {report.analysis && (
                      <div className="report-summary">
                        {report.analysis.summary.substring(0, 100)}...
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <p>No reports uploaded yet</p>
            )}
          </div>
          <div className="metric-card">
            <h3>Health Score</h3>
            <p>{recentReports.length > 0 ? 'Based on your latest report' : 'Upload a report to see your score'}</p>
            {recentReports.length > 0 && recentReports[0].analysis && (
              <div className="health-score">
                {recentReports[0].analysis.classification.label}
                <span className="confidence">
                  ({(recentReports[0].analysis.classification.confidence * 100).toFixed(1)}%)
                </span>
              </div>
            )}
          </div>
          <div className="metric-card">
            <h3>Recommendations</h3>
            {recentReports.length > 0 && recentReports[0].analysis ? (
              <ul className="recommendations-list">
                {recentReports[0].analysis.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            ) : (
              <p>Upload a report to get personalized recommendations</p>
            )}
          </div>
          {recentReports.length > 0 && recentReports[0].analysis && (
            <div className="metric-card">
              <h3>Latest Blood Test Results</h3>
              {renderBloodTestResults(recentReports[0].analysis)}
            </div>
          )}
        </div>
      </section>

      <section id="upload-section">
        <UploadReport onUpload={onUpload} />
      </section>
    </div>
  );
}

export default Overview; 