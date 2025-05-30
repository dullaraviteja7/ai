import React, { useState, useEffect } from 'react';

const KidExamUpdatePage = () => {
  const [kidsList, setKidsList] = useState([]);
  const [selectedKidId, setSelectedKidId] = useState('');
  const initialExamFormData = {
    exam_name: '',
    exam_date: '',
    subject: '',
    marks_obtained_percentage: '',
    class_top_percentage: ''
  };
  const [examFormData, setExamFormData] = useState(initialExamFormData);
  const [message, setMessage] = useState(''); // For general messages and submit success/error
  const [isLoadingKids, setIsLoadingKids] = useState(false);
  const [isSubmittingExam, setIsSubmittingExam] = useState(false);

  // New state variables for OCR
  const [selectedFile, setSelectedFile] = useState(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [ocrMessage, setOcrMessage] = useState(''); // For OCR specific messages

  // Fetch kids on component mount
  useEffect(() => {
    const fetchKids = async () => {
      setIsLoadingKids(true);
      setMessage('');
      setKidsList([]); // Clear previous list
      try {
        const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:4000';
        const response = await fetch(`${API_BASE_URL}/api/kids`);
        if (!response.ok) {
          // Try to get error from backend response body if possible
          let errorMsg = `HTTP error ${response.status}`;
          try {
              const errorData = await response.json();
              errorMsg = errorData.error || errorMsg;
          } catch (jsonError) {
              // Ignore if response is not JSON
          }
          throw new Error(`Failed to fetch kids: ${errorMsg}`);
        }
        const data = await response.json();
        setKidsList(data.kids || []); // data.kids should be the array
        if (!data.kids || data.kids.length === 0) {
          setMessage('No kids found. Register a kid first.');
        }
      } catch (error) {
        setMessage(`Error fetching kids: ${error.message}`);
        setKidsList([]); 
      } finally {
        setIsLoadingKids(false);
      }
    };
    fetchKids();
  }, []);

  const handleKidSelectionChange = (e) => {
    setSelectedKidId(e.target.value);
    setMessage(''); // Clear general messages
    setOcrMessage(''); // Clear OCR messages
    setExamFormData(initialExamFormData); // Reset exam form when kid changes
    setSelectedFile(null); // Reset selected file
  };

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setOcrMessage(''); // Clear OCR messages on new file selection
  };

  const handleImageUploadAndExtract = async () => {
    if (!selectedFile || !selectedKidId) {
      setOcrMessage('Please select a kid and an image file first.');
      return;
    }

    setIsExtracting(true);
    setOcrMessage('Extracting data from image...');
    setMessage(''); // Clear general messages

    const formData = new FormData();
    formData.append('marks_sheet_image', selectedFile);

    try {
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:4000';
      const response = await fetch(`${API_BASE_URL}/api/kids/${selectedKidId}/exams/upload_image`, {
        method: 'POST',
        body: formData,
        // Do NOT set Content-Type header manually for FormData
      });

      const responseData = await response.json(); // Attempt to parse JSON regardless of response.ok

      if (response.ok) {
        if (responseData.extracted_data) {
          const extracted = responseData.extracted_data;
          setExamFormData(prev => ({
            ...prev,
            exam_name: extracted.exam_name || prev.exam_name,
            subject: extracted.subject || prev.subject,
            // Ensure marks are strings for the input field, and handle potential undefined
            marks_obtained_percentage: extracted.marks_obtained_percentage !== undefined ? String(extracted.marks_obtained_percentage) : prev.marks_obtained_percentage,
            // exam_date might not be extracted by basic OCR, so keep existing or leave blank
          }));
          setOcrMessage('Data extracted successfully. Please review and correct if necessary, then submit the form.');
          setMessage(''); // Clear any previous main message
        } else if (responseData.error) {
          setOcrMessage(`Error extracting data: ${responseData.error}`);
        } else {
          setOcrMessage('Extraction completed, but no specific data found in response.');
        }
      } else {
        // Handle HTTP errors (e.g., 400, 404, 500)
        setOcrMessage(`Error extracting data: ${responseData.error || response.statusText || 'Failed to extract data from image.'}`);
      }
    } catch (error) {
      console.error('Image upload/extract error:', error);
      setOcrMessage(`Network or client-side error during extraction: ${error.message}. Ensure the backend is running.`);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleExamFormChange = (e) => {
    const { name, value } = e.target;
    setExamFormData(prevState => ({ ...prevState, [name]: value }));
  };

  const handleExamSubmit = async (e) => {
    e.preventDefault();
    setMessage(''); // Clear previous messages

    if (!selectedKidId) {
      setMessage('Error: Please select a kid first.');
      return;
    }
    
    const { exam_name, exam_date, subject, marks_obtained_percentage } = examFormData;
    if (!exam_name.trim() || !exam_date.trim() || !subject.trim() || marks_obtained_percentage === '') {
      setMessage('Error: Exam Name, Date, Subject, and Marks Obtained are required.');
      return;
    }

    const marks = parseFloat(marks_obtained_percentage);
    if (isNaN(marks) || marks < 0 || marks > 100) {
      setMessage('Error: Marks Obtained must be a number between 0 and 100.');
      return;
    }

    let classTop = null;
    if (examFormData.class_top_percentage !== '') {
      classTop = parseFloat(examFormData.class_top_percentage);
      if (isNaN(classTop) || classTop < 0 || classTop > 100) {
        setMessage('Error: Class Top Percentage must be a number between 0 and 100, if provided.');
        return;
      }
    }

    setIsSubmittingExam(true);

    const payload = {
      exam_name: exam_name.trim(),
      exam_date: exam_date.trim(),
      subject: subject.trim(),
      marks_obtained_percentage: marks,
    };
    if (classTop !== null) {
      payload.class_top_percentage = classTop;
    }

    try {
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:4000';
      const response = await fetch(`${API_BASE_URL}/api/kids/${selectedKidId}/exams`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const responseData = await response.json();
      if (response.ok) { // Typically 201 for POST success
        setMessage(`Exam data added successfully for kid ID ${selectedKidId}! Exam ID: ${responseData.exam_id}`);
        setExamFormData(initialExamFormData); // Clear form on success
      } else {
        setMessage(`Error: ${responseData.error || response.statusText || 'An unknown error occurred'}`);
      }
    } catch (error) {
      setMessage(`Error submitting exam data: ${error.message}. Ensure the backend server is running.`);
    } finally {
      setIsSubmittingExam(false);
    }
  };
  
  const selectedKidName = kidsList.find(k => k.id === selectedKidId)?.name || 'Selected Kid';

  return (
    <div>
      <h2>Kid Exam Update Page</h2>
      
      <div>
        <label htmlFor="kid-select">Select Kid:</label>
        <select id="kid-select" value={selectedKidId} onChange={handleKidSelectionChange} disabled={isLoadingKids || kidsList.length === 0}>
          <option value="">-- Select a Kid --</option>
          {kidsList.map(kid => (
            <option key={kid.id} value={kid.id}>{kid.name} (ID: {kid.id})</option>
          ))}
        </select>
        {isLoadingKids && <p>Loading kids list...</p>}
        {!isLoadingKids && kidsList.length === 0 && !message.includes("Error fetching kids") && <p>No kids found or failed to load.</p>}
      </div>

      {selectedKidId && (
        <form onSubmit={handleExamSubmit} style={{ marginTop: '20px', border: '1px solid #eee', padding: '15px', borderRadius: '5px' }}>
          <h3>Add Exam for: {selectedKidName}</h3>

          {/* File Upload Section */}
          <div style={{ marginBottom: '20px', padding: '10px', border: '1px dashed #ccc' }}>
            <h4>Optional: Upload Exam Result Image for OCR</h4>
            <div>
              <label htmlFor="exam_image_upload">Select Image:</label>
              <input 
                type="file" 
                id="exam_image_upload" 
                accept="image/*" 
                onChange={handleFileChange} 
                disabled={!selectedKidId || isExtracting}
              />
            </div>
            <button 
              type="button" 
              onClick={handleImageUploadAndExtract} 
              disabled={!selectedFile || !selectedKidId || isExtracting}
              style={{ marginTop: '10px', backgroundColor: '#6c757d' }}
            >
              {isExtracting ? 'Extracting...' : 'Upload & Extract Data from Image'}
            </button>
            {ocrMessage && <p style={{ marginTop: '10px', color: ocrMessage.startsWith('Error') ? 'red' : 'blue' }}>{ocrMessage}</p>}
          </div>
          
          {/* Exam Details Form - can be pre-filled by OCR */}
          <h4>Exam Details:</h4>
          <div>
            <label htmlFor="exam_name">Exam Name:</label>
            <input type="text" id="exam_name" name="exam_name" value={examFormData.exam_name} onChange={handleExamFormChange} required />
          </div>
          <div>
            <label htmlFor="exam_date">Exam Date:</label>
            <input type="date" id="exam_date" name="exam_date" value={examFormData.exam_date} onChange={handleExamFormChange} required />
          </div>
          <div>
            <label htmlFor="subject">Subject:</label>
            <input type="text" id="subject" name="subject" value={examFormData.subject} onChange={handleExamFormChange} required />
          </div>
          <div>
            <label htmlFor="marks_obtained_percentage">Marks Obtained (%):</label>
            <input type="number" id="marks_obtained_percentage" name="marks_obtained_percentage" value={examFormData.marks_obtained_percentage} onChange={handleExamFormChange} required min="0" max="100" step="0.01" />
          </div>
          <div>
            <label htmlFor="class_top_percentage">Class Top Percentage (Optional, %):</label>
            <input type="number" id="class_top_percentage" name="class_top_percentage" value={examFormData.class_top_percentage} onChange={handleExamFormChange} min="0" max="100" step="0.01" />
          </div>
          <button type="submit" disabled={isSubmittingExam} style={{ marginTop: '10px' }}>
            {isSubmittingExam ? 'Submitting Exam...' : 'Add Exam Data'}
          </button>
        </form>
      )}
      {message && <p style={{ marginTop: '15px', padding: '10px', border: '1px solid', borderColor: message.startsWith('Error:') ? 'red' : 'green', color: message.startsWith('Error:') ? 'red' : 'green', borderRadius: '4px' }}>{message}</p>}
      <style jsx>{`
        div {
          margin-bottom: 10px;
        }
        label {
          display: block;
          margin-bottom: 5px;
          font-weight: bold;
        }
        input[type="text"], input[type="number"], input[type="date"], select {
          width: 100%;
          padding: 8px;
          border: 1px solid #ccc;
          border-radius: 4px;
          box-sizing: border-box;
        }
        button {
          padding: 10px 15px;
          background-color: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 1em;
        }
        button:disabled {
          background-color: #ccc;
        }
        input[type="file"] {
          padding: 8px 0; /* Adjust padding for file input */
        }
      `}</style>
    </div>
  );
};

export default KidExamUpdatePage;
