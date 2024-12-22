const express = require('express');
const multer = require('multer');
const path = require('path');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/api/upload', upload.single('report'), (req, res) => {
  res.send({ message: 'File uploaded successfully', file: req.file });
});

app.listen(5000, () => {
  console.log('Server is running on port 5000');
}); 