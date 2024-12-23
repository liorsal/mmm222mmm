import React, { useState, useRef } from 'react';
import axios from 'axios';
import { testCategories } from '../data/testCategories';

function BloodTestAnalyzer() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setAnalysis(null);
      handleUpload(file); // Automatically upload when file is selected
    }
  };

  const handleUpload = async (file) => {
    setIsLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(
        'http://localhost:8000/api/analyze-report',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        }
      );

      if (response.data.success) {
        setAnalysis(response.data);
      } else {
        throw new Error(response.data.error);
      }
    } catch (error) {
      setError(error.message);
    }

    setIsLoading(false);
  };

  const getTestStatus = (result) => {
    const abnormalTest = analysis.evaluation.abnormal_tests.find(
      test => test.test === result["Test Name"]
    );
    return abnormalTest ? 'abnormal' : 'normal';
  };

  return (
    <div className="analyzer-container">
      <section className="hero-section">
        <h2>אנליזת בדיקות דם מהירה ומדויקת</h2>
        <p className="subtitle">העלה את קובץ בדיקת הדם שלך וקבל תובנות מיידיות</p>
      </section>

      <section className="test-categories">
        <h3>בדיקות שניתן לנתח</h3>
        <div className="categories-grid">
          {Object.entries(testCategories).map(([key, category]) => (
            <div key={key} className="category-card">
              <h4>{category.title}</h4>
              <ul>
                {category.tests.map((test, index) => (
                  <li key={index}>{test}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section className="upload-card">
        <div className="upload-section">
          <h2>העלאת קובץ PDF של בדיקת דם</h2>
          <p className="subtitle">לחץ על הכפתור להעלאת הקובץ</p>
          
          <div className="file-upload">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              style={{ display: 'none' }}
              disabled={isLoading}
            />
            
            <button 
              className="upload-button"
              onClick={() => fileInputRef.current.click()}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <svg className="spinner" viewBox="0 0 50 50">
                    <circle cx="25" cy="25" r="20" fill="none" strokeWidth="5"></circle>
                  </svg>
                  מנתח...
                </>
              ) : (
                <>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                  העלאת קובץ PDF
                </>
              )}
            </button>
            
            {selectedFile && (
              <div className="selected-file">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
                  <polyline points="13 2 13 9 20 9" />
                </svg>
                {selectedFile.name}
              </div>
            )}
          </div>
        </div>
      </section>

      {error && (
        <div className="error-message">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12" y2="16" />
          </svg>
          {error}
        </div>
      )}

      {analysis && (
        <section className="results-card">
          <h3>תוצאות הניתוח</h3>
          
          <div className={`status-card ${analysis.evaluation.status.toLowerCase()}`}>
            <div className="status-icon">
              {analysis.evaluation.status === 'Good' ? (
                <div className="checkmark-wrapper">
                  <div className="checkmark-circle"></div>
                  <div className="checkmark-stem"></div>
                  <div className="checkmark-kick"></div>
                </div>
              ) : (
                <div className="cross-wrapper">
                  <div className="cross-line1"></div>
                  <div className="cross-line2"></div>
                </div>
              )}
            </div>
            <div className="status-text">
              <h4>סטטוס כללי</h4>
              <p className="status-result">
                {analysis.evaluation.status === 'Good' ? 'תקין' : 'דורש בדיקה'}
              </p>
            </div>
          </div>

          <div className="all-results">
            <h4>כל תוצאות הבדיקות</h4>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>בדיקה</th>
                    <th>ערך</th>
                    <th>יחידות</th>
                    <th>סטטוס</th>
                  </tr>
                </thead>
                <tbody>
                  {analysis.results.map((result, index) => {
                    const status = getTestStatus(result);
                    return (
                      <tr key={index} className={status}>
                        <td>{result["Test Name"]}</td>
                        <td>{result.Value}</td>
                        <td>{result.Unit}</td>
                        <td>
                          <span className={`status-indicator ${status}`}>
                            {status === 'normal' ? '✓ תקין' : '⚠ חריג'}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      )}

      <footer className="disclaimer">
        <p>כלי זה הוא למטרות מידע בלבד. יש להתייעץ תמיד עם ספק שירותי בריאות.</p>
      </footer>
    </div>
  );
}

export default BloodTestAnalyzer; 