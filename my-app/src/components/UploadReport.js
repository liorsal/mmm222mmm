import React, { useState } from 'react';
import axios from 'axios';

function UploadReport() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Please select a file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('report', selectedFile);

    setUploadStatus('Uploading...');

    try {
      const response = await axios.post('/api/upload', formData);
      setUploadStatus('Upload Successful');
      console.log(response.data);
    } catch (error) {
      setUploadStatus('Upload Failed');
      console.error(error);
    }
  };

  return (
    <section id="upload-report">
      <h2>Upload Your Health Report</h2>
      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>
      <p>{uploadStatus}</p>
      {selectedFile && (
        <div>
          <h3>File Details:</h3>
          <p>Name: {selectedFile.name}</p>
          <p>Type: {selectedFile.type}</p>
          <p>Size: {selectedFile.size} bytes</p>
        </div>
      )}
    </section>
  );
}

export default UploadReport; 