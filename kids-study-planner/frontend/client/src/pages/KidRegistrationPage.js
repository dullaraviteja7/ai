import React, { useState } from 'react';

const KidRegistrationPage = () => {
  const initialFormData = {
    name: '',
    age: '',
    grade: '',
    subjects: '', // Comma-separated string
    school_name: '',
    school_timings: '',
    preferred_study_hours: '',
    improvement_areas: '', // Comma-separated
    preferred_subjects: '' // Comma-separated
  };
  const [formData, setFormData] = useState(initialFormData);
  const [message, setMessage] = useState(''); // For success/error messages
  const [isLoading, setIsLoading] = useState(false); // For loading state

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setIsLoading(true);

    // Basic client-side validation
    if (!formData.name.trim() || !formData.age.trim() || !formData.grade.trim() || !formData.subjects.trim()) {
      setMessage('Error: Name, Age, Grade, and Subjects are required.');
      setIsLoading(false);
      return;
    }

    const payload = {
      ...formData,
      name: formData.name.trim(),
      age: parseInt(formData.age, 10),
      grade: formData.grade.trim(),
      subjects: formData.subjects.split(',').map(s => s.trim()).filter(s => s),
      school_name: formData.school_name.trim() || null,
      school_timings: formData.school_timings.trim() || null,
      preferred_study_hours: formData.preferred_study_hours.trim() || null,
      improvement_areas: formData.improvement_areas.split(',').map(s => s.trim()).filter(s => s).length > 0 ? formData.improvement_areas.split(',').map(s => s.trim()).filter(s => s) : [],
      preferred_subjects: formData.preferred_subjects.split(',').map(s => s.trim()).filter(s => s).length > 0 ? formData.preferred_subjects.split(',').map(s => s.trim()).filter(s => s) : []
    };
    
    // Ensure age is a valid number
    if (isNaN(payload.age) || payload.age <= 0) {
        setMessage('Error: Age must be a positive number.');
        setIsLoading(false);
        return;
    }


    try {
      const response = await fetch('http://localhost:5000/api/kids/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const responseData = await response.json();

      if (response.ok) {
        setMessage(`Kid registered successfully! ID: ${responseData.id}`);
        setFormData(initialFormData); // Clear form on success
      } else {
        setMessage(`Error: ${responseData.error || response.statusText || 'An unknown error occurred'}`);
      }
    } catch (error) {
      setMessage(`Error: ${error.message}. Ensure the backend server is running.`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2>Kid Registration Page</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="name">Name:</label>
          <input type="text" id="name" name="name" value={formData.name} onChange={handleChange} required />
        </div>
        <div>
          <label htmlFor="age">Age:</label>
          <input type="number" id="age" name="age" value={formData.age} onChange={handleChange} required />
        </div>
        <div>
          <label htmlFor="grade">Grade:</label>
          <input type="text" id="grade" name="grade" value={formData.grade} onChange={handleChange} required />
        </div>
        <div>
          <label htmlFor="subjects">Subjects (comma-separated):</label>
          <input type="text" id="subjects" name="subjects" value={formData.subjects} onChange={handleChange} required />
          <small>E.g., Math, Science, English</small>
        </div>
        <div>
          <label htmlFor="school_name">School Name (Optional):</label>
          <input type="text" id="school_name" name="school_name" value={formData.school_name} onChange={handleChange} />
        </div>
        <div>
          <label htmlFor="school_timings">School Timings (Optional):</label>
          <input type="text" id="school_timings" name="school_timings" value={formData.school_timings} onChange={handleChange} />
          <small>E.g., 9 AM - 3 PM</small>
        </div>
        <div>
          <label htmlFor="preferred_study_hours">Preferred Study Hours (Optional):</label>
          <input type="text" id="preferred_study_hours" name="preferred_study_hours" value={formData.preferred_study_hours} onChange={handleChange} />
          <small>E.g., 5 PM - 7 PM</small>
        </div>
        <div>
          <label htmlFor="improvement_areas">Areas for Improvement (comma-separated, Optional):</label>
          <input type="text" id="improvement_areas" name="improvement_areas" value={formData.improvement_areas} onChange={handleChange} />
          <small>E.g., Algebra, Reading Comprehension</small>
        </div>
        <div>
          <label htmlFor="preferred_subjects">Preferred Subjects (comma-separated, Optional):</label>
          <input type="text" id="preferred_subjects" name="preferred_subjects" value={formData.preferred_subjects} onChange={handleChange} />
          <small>E.g., History, Art</small>
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Registering...' : 'Register Kid'}
        </button>
      </form>
      {message && <p>{message}</p>}
      <style jsx>{`
        div {
          margin-bottom: 10px;
        }
        label {
          display: block;
          margin-bottom: 5px;
          font-weight: bold;
        }
        input[type="text"], input[type="number"] {
          width: 100%;
          padding: 8px;
          border: 1px solid #ccc;
          border-radius: 4px;
          box-sizing: border-box;
        }
        small {
          display: block;
          font-size: 0.8em;
          color: #666;
          margin-top: 3px;
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
        p {
          margin-top: 15px;
          padding: 10px;
          border-radius: 4px;
        }
        p[class*="Error:"] { /* Heuristic for error messages */
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        p:not([class*="Error:"]) { /* Heuristic for success messages */
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
      `}</style>
    </div>
  );
};

export default KidRegistrationPage;
