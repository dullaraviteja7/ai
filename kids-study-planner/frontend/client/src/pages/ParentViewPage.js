import React, { useState, useEffect, useCallback } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ParentViewPage = () => {
  const [kidsList, setKidsList] = useState([]);
  const [selectedKidId, setSelectedKidId] = useState('');
  const [selectedKidData, setSelectedKidData] = useState(null);
  const [message, setMessage] = useState('');
  const [isLoadingKids, setIsLoadingKids] = useState(false);
  const [isLoadingKidData, setIsLoadingKidData] = useState(false);
  const [isGeneratingInsights, setIsGeneratingInsights] = useState(false);

  // State variables for performance chart filtering
  const [performanceStartDate, setPerformanceStartDate] = useState('');
  const [performanceEndDate, setPerformanceEndDate] = useState('');
  const [performanceSubjectFilter, setPerformanceSubjectFilter] = useState(''); // Default to 'All' or empty
  const [uniqueSubjectsForFilter, setUniqueSubjectsForFilter] = useState(['All']);
  const [filteredPerformanceData, setFilteredPerformanceData] = useState([]);


  // Fetch all kids for the selector
  useEffect(() => {
    const fetchKids = async () => {
      setIsLoadingKids(true);
      setMessage('');
      setKidsList([]);
      try {
        const response = await fetch('http://localhost:5000/api/kids');
        if (!response.ok) {
          let errorMsg = `HTTP error ${response.status}`;
          try {
            const errorData = await response.json();
            errorMsg = errorData.error || errorMsg;
          } catch (jsonError) { /* Ignore */ }
          throw new Error(`Failed to fetch kids: ${errorMsg}`);
        }
        const data = await response.json();
        setKidsList(data.kids || []);
        if (!data.kids || data.kids.length === 0) {
          setMessage('No kids found. Please register a kid first.');
        }
      } catch (error) {
        setMessage(`Error fetching kids list: ${error.message}`);
        setKidsList([]);
      } finally {
        setIsLoadingKids(false);
      }
    };
    fetchKids();
  }, []);

  // Fetch data for the selected kid
  const fetchKidData = useCallback(async (kidId) => {
    if (!kidId) {
      setSelectedKidData(null);
      setUniqueSubjectsForFilter(['All']);
      setFilteredPerformanceData([]);
      return;
    }
    setIsLoadingKidData(true);
    if (!message.includes("AI insights")) setMessage('');
    try {
      const response = await fetch(`http://localhost:5000/api/kids/${kidId}`);
      if (!response.ok) {
        let errorMsg = `HTTP error ${response.status}`;
        try {
            const errorData = await response.json();
            errorMsg = errorData.error || errorMsg;
        } catch(e) { /* Ignore */ }
        throw new Error(errorMsg);
      }
      const data = await response.json();
      setSelectedKidData(data);

      // Extract unique subjects for filter dropdown
      if (data && data.exams) {
        const subjects = ['All', ...new Set(data.exams.map(exam => exam.subject))];
        setUniqueSubjectsForFilter(subjects);
        // Initially, performance data is all exams for the kid
        // setFilteredPerformanceData(getExamPerformanceData(data.exams)); // Will be handled by useEffect on selectedKidData
      } else {
        setUniqueSubjectsForFilter(['All']);
        // setFilteredPerformanceData([]);
      }

    } catch (error) {
      setMessage(`Error fetching data for kid ${kidId}: ${error.message}`);
      setSelectedKidData(null);
      setUniqueSubjectsForFilter(['All']);
      // setFilteredPerformanceData([]);
    } finally {
      setIsLoadingKidData(false);
    }
  }, [message]);

  useEffect(() => {
    if (selectedKidId) {
      fetchKidData(selectedKidId);
    } else {
      setSelectedKidData(null); 
      setPerformanceStartDate('');
      setPerformanceEndDate('');
      setPerformanceSubjectFilter('');
      setUniqueSubjectsForFilter(['All']);
      setFilteredPerformanceData([]);
    }
  }, [selectedKidId, fetchKidData]);
  
  // Recalculate filtered performance data when filters or selectedKidData changes
  useEffect(() => {
    if (selectedKidData && selectedKidData.exams) {
      const data = getExamPerformanceData(
        selectedKidData.exams, 
        performanceStartDate, 
        performanceEndDate, 
        performanceSubjectFilter
      );
      setFilteredPerformanceData(data);
    } else {
      setFilteredPerformanceData([]);
    }
  }, [selectedKidData, performanceStartDate, performanceEndDate, performanceSubjectFilter]);

  const handleKidSelectionChange = (e) => {
    setSelectedKidId(e.target.value);
    setMessage(''); // Clear messages when kid selection changes
  };

  const handleGenerateInsights = async () => {
    if (!selectedKidId) {
      setMessage('Please select a kid first to generate insights.');
      return;
    }
    setIsGeneratingInsights(true);
    setMessage('');
    try {
      const response = await fetch(`http://localhost:5000/api/kids/${selectedKidId}/ai-insights`, { method: 'POST' });
      const responseData = await response.json(); // Must await this before checking response.ok
      if (!response.ok) {
        throw new Error(responseData.error || `Failed to generate AI insights. Status: ${response.status}`);
      }
      
      setMessage('AI insights generated/refreshed successfully!');
      setSelectedKidData(prevData => ({
        ...prevData,
        ai_insights: responseData 
      }));
    } catch (error) {
      setMessage(`Error generating AI insights: ${error.message}`);
    } finally {
      setIsGeneratingInsights(false);
    }
  };

  const renderKidDetails = (data) => {
    if (!data) return null;
    return (
      <section>
        <h4>Registration Details</h4>
        <p><strong>Name:</strong> {data.name}</p>
        <p><strong>Age:</strong> {data.age}</p>
        <p><strong>Grade:</strong> {data.grade}</p>
        <p><strong>Subjects:</strong> {Array.isArray(data.subjects) ? data.subjects.join(', ') : 'N/A'}</p>
        {data.school_name && <p><strong>School Name:</strong> {data.school_name}</p>}
        {data.school_timings && <p><strong>School Timings:</strong> {data.school_timings}</p>}
        {data.preferred_study_hours && <p><strong>Preferred Study Hours:</strong> {data.preferred_study_hours}</p>}
        {data.improvement_areas && data.improvement_areas.length > 0 && <p><strong>Improvement Areas:</strong> {data.improvement_areas.join(', ')}</p>}
        {data.preferred_subjects && data.preferred_subjects.length > 0 && <p><strong>Preferred Subjects:</strong> {data.preferred_subjects.join(', ')}</p>}
      </section>
    );
  };

  const renderExamHistory = (exams) => {
    if (!exams || exams.length === 0) return <p>No exam history found.</p>;
    return (
      <section>
        <h4>Exam History</h4>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={tableHeaderStyle}>Exam Name</th>
              <th style={tableHeaderStyle}>Date</th>
              <th style={tableHeaderStyle}>Subject</th>
              <th style={tableHeaderStyle}>Marks (%)</th>
              <th style={tableHeaderStyle}>Class Top (%)</th>
            </tr>
          </thead>
          <tbody>
            {exams.map(exam => (
              <tr key={exam.exam_id}>
                <td style={tableCellStyle}>{exam.exam_name}</td>
                <td style={tableCellStyle}>{exam.exam_date}</td>
                <td style={tableCellStyle}>{exam.subject}</td>
                <td style={tableCellStyle}>{exam.marks_obtained_percentage}</td>
                <td style={tableCellStyle}>{exam.class_top_percentage !== undefined && exam.class_top_percentage !== null ? exam.class_top_percentage : 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    );
  };

  const renderAIInsights = (insights) => {
    if (!insights || Object.keys(insights).length === 0) return <p>No AI insights available. Click the button above to generate them.</p>;
    return (
      <section>
        <h4>AI Insights (Last Updated: {new Date(insights.last_updated).toLocaleString()})</h4>
        <p><strong>Progress Analysis:</strong> {insights.progress_analysis}</p>
        <h5>Schedules:</h5>
        {insights.schedules && (
          <>
            <p><strong>Daily:</strong> {insights.schedules.daily.join('; ')}</p>
            <p><strong>Weekly:</strong> {insights.schedules.weekly.join('; ')}</p>
            <p><strong>Monthly:</strong> {insights.schedules.monthly.join('; ')}</p>
          </>
        )}
        <h5>Suggestions:</h5>
        <ul>
          {insights.suggestions && insights.suggestions.map((s, index) => <li key={index}>{s}</li>)}
        </ul>
      </section>
    );
  };

  // Data preparation for charts
  const getAverageMarksPerSubject = (exams) => {
    if (!exams || exams.length === 0) return [];
    const subjectData = {}; // { Math: { total: 0, count: 0 }, ... }
    exams.forEach(exam => {
      if (!subjectData[exam.subject]) {
        subjectData[exam.subject] = { total: 0, count: 0 };
      }
      subjectData[exam.subject].total += parseFloat(exam.marks_obtained_percentage);
      subjectData[exam.subject].count++;
    });
    return Object.entries(subjectData).map(([subject, data]) => ({
      subject,
      averageMarks: parseFloat((data.total / data.count).toFixed(2)) // Keep 2 decimal places
    }));
  };

  const getExamPerformanceData = (exams, startDate, endDate, subjectFilter) => {
    if (!exams || exams.length === 0) return [];
    
    let filteredExams = exams;

    if (startDate) {
      filteredExams = filteredExams.filter(exam => new Date(exam.exam_date) >= new Date(startDate));
    }
    if (endDate) {
      filteredExams = filteredExams.filter(exam => new Date(exam.exam_date) <= new Date(endDate));
    }
    if (subjectFilter && subjectFilter !== 'All') {
      filteredExams = filteredExams.filter(exam => exam.subject === subjectFilter);
    }

    return filteredExams
      .map(exam => ({
        date: exam.exam_date,
        name: `${exam.exam_name} (${exam.subject} - ${exam.exam_date})`,
        marks: parseFloat(exam.marks_obtained_percentage),
        class_top_percentage: exam.class_top_percentage !== undefined && exam.class_top_percentage !== null ? parseFloat(exam.class_top_percentage) : null,
        subject: exam.subject 
      }))
      .sort((a, b) => new Date(a.date) - new Date(b.date));
  };

  const handleApplyPerformanceFilters = () => {
    // This function is more of a conceptual trigger if we weren't using useEffect for direct changes.
    // Since performanceStartDate, performanceEndDate, performanceSubjectFilter are state variables,
    // and useEffect recalculates filteredPerformanceData when they change,
    // this button is not strictly necessary for functionality if inputs directly set state.
    // However, it can be kept for explicit user action if preferred.
    // For now, the useEffect handles it, so this function can be empty or log action.
    console.log("Applying filters (though useEffect handles this automatically on state change)");
  };
  
  const renderPerformanceChartFilters = () => {
    return (
      <div style={{ display: 'flex', gap: '15px', alignItems: 'center', marginBottom: '15px', flexWrap: 'wrap' }}>
        <div>
          <label htmlFor="perfStartDate" style={{ marginRight: '5px' }}>Start Date:</label>
          <input type="date" id="perfStartDate" value={performanceStartDate} onChange={e => setPerformanceStartDate(e.target.value)} style={{ padding: '5px' }}/>
        </div>
        <div>
          <label htmlFor="perfEndDate" style={{ marginRight: '5px' }}>End Date:</label>
          <input type="date" id="perfEndDate" value={performanceEndDate} onChange={e => setPerformanceEndDate(e.target.value)} style={{ padding: '5px' }}/>
        </div>
        <div>
          <label htmlFor="perfSubject" style={{ marginRight: '5px' }}>Subject:</label>
          <select id="perfSubject" value={performanceSubjectFilter} onChange={e => setPerformanceSubjectFilter(e.target.value)} style={{ padding: '5px' }}>
            {uniqueSubjectsForFilter.map(subject => (
              <option key={subject} value={subject}>{subject}</option>
            ))}
          </select>
        </div>
        {/* <button onClick={handleApplyPerformanceFilters} style={{ padding: '5px 10px' }}>Apply Filters</button> */}
        {/* Button is optional as useEffect applies filters on state change */}
      </div>
    );
  };

  const renderCharts = (kidData) => {
    if (!kidData || !kidData.exams || kidData.exams.length === 0) {
      return <p>No exam data available to display charts.</p>;
    }

    const averageMarksData = getAverageMarksPerSubject(kidData.exams);
    // const performanceData = getExamPerformanceData(kidData.exams); // Now using filteredPerformanceData from state

    // Scatter plot data
    const marksVsClassTopData = kidData.exams
        .filter(exam => exam.marks_obtained_percentage !== null && exam.class_top_percentage !== null && exam.class_top_percentage !== undefined)
        .map(exam => ({
            name: `${exam.exam_name} (${exam.subject})`,
            marks: parseFloat(exam.marks_obtained_percentage),
            classTop: parseFloat(exam.class_top_percentage)
        }));


    return (
      <section style={{ marginTop: '30px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
        <h3>Progress Visualizations</h3>
        
        {averageMarksData.length > 0 && (
          <div style={{ marginBottom: '30px' }}>
            <h4>Average Marks Per Subject</h4>
            <ResponsiveContainer width="95%" height={300}>
              <BarChart data={averageMarksData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="subject" />
                <YAxis />
                <Tooltip formatter={(value, name) => [value + '%', name === 'averageMarks' ? "Average Marks" : name]}/>
                <Legend />
                <Bar dataKey="averageMarks" fill="#8884d8" name="Average Marks (%)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Performance Line Chart with Filters */}
        <div style={{ marginBottom: '30px' }}>
          <h4>Exam Performance Over Time</h4>
          {renderPerformanceChartFilters()}
          {filteredPerformanceData.length > 0 ? (
            <ResponsiveContainer width="95%" height={300}>
              <LineChart data={filteredPerformanceData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                    dataKey="name" 
                    angle={-20} 
                    textAnchor="end" 
                    height={80} 
                    interval="preserveStartEnd"
                    tickFormatter={(tick) => {
                        const namePart = tick.substring(0, tick.lastIndexOf('(') -1);
                        const datePart = tick.substring(tick.lastIndexOf('-') + 1, tick.lastIndexOf(')'));
                        return `${namePart} (${datePart})`; // Show exam name and just day of date
                    }}
                />
                <YAxis domain={[0, 100]} />
                <Tooltip 
                  formatter={(value, name, props) => {
                    if (name === 'marks') {
                      const classTop = props.payload.class_top_percentage;
                      return [`${value}% (Class Top: ${classTop !== null ? classTop + '%' : 'N/A'})`, `Marks - ${props.payload.subject}`];
                    }
                    return [value, name];
                  }}
                  labelFormatter={(label) => {
                     // label here is the full 'name' key from data object
                     const datePart = label.substring(label.lastIndexOf('(') +1, label.lastIndexOf(')'));
                     const examNamePart = label.substring(0, label.lastIndexOf('(') -1);
                     const subjectPart = label.substring(label.indexOf('(') + 1, label.indexOf(' -'));
                     return `${examNamePart} (${subjectPart}) - ${datePart}`;
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="marks" stroke="#82ca9d" name="Marks Obtained (%)" activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p>No exam data matches the current filters.</p>
          )}
        </div>

        {/* Optional Scatter Plot */}
        {marksVsClassTopData.length > 0 && (
            <div style={{ marginBottom: '30px' }}>
                <h4>Marks vs. Class Top Percentage</h4>
                <ResponsiveContainer width="95%" height={400}>
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                        <CartesianGrid />
                        <XAxis type="number" dataKey="marks" name="Student Marks" unit="%" domain={[0, 100]} />
                        <YAxis type="number" dataKey="classTop" name="Class Top Marks" unit="%" domain={[0, 100]} />
                        <Tooltip 
                            cursor={{ strokeDasharray: '3 3' }} 
                            formatter={(value, name, props) => {
                                if (name === "Student Marks" || name === "Class Top Marks") {
                                    return [`${value}%`, name];
                                }
                                return [value, name];
                            }}
                            labelFormatter={(label) => props.payload && props.payload.name ? props.payload.name : ""} // Needs fixing, label is index
                        />
                        <Legend />
                        <Scatter name="Exams" data={marksVsClassTopData} fill="#8884d8" />
                    </ScatterChart>
                </ResponsiveContainer>
            </div>
        )}
      </section>
    );
  };


  const tableHeaderStyle = { border: '1px solid #ddd', padding: '8px', textAlign: 'left', backgroundColor: '#f2f2f2' };
  const tableCellStyle = { border: '1px solid #ddd', padding: '8px', textAlign: 'left' };

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '20px' }}>
      <h2>Parent View Page</h2>
      
      <div>
        <label htmlFor="kid-select-parent" style={{ marginRight: '10px' }}>Select Kid:</label>
        <select id="kid-select-parent" value={selectedKidId} onChange={handleKidSelectionChange} disabled={isLoadingKids || kidsList.length === 0}
          style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}>
          <option value="">-- Select a Kid --</option>
          {kidsList.map(kid => (
            <option key={kid.id} value={kid.id}>{kid.name} (ID: {kid.id})</option>
          ))}
        </select>
        {isLoadingKids && <p>Loading kids list...</p>}
        {!isLoadingKids && kidsList.length === 0 && !message.includes("Error fetching kids list") && <p>No kids available to select.</p>}
      </div>

      {message && <p style={{ 
          marginTop: '15px', 
          padding: '10px', 
          border: `1px solid ${message.toLowerCase().includes('error') ? 'red' : 'green'}`, 
          color: message.toLowerCase().includes('error') ? 'red' : 'green',
          backgroundColor: message.toLowerCase().includes('error') ? '#ffebee' : '#e8f5e9',
          borderRadius: '4px'
        }}>{message}</p>}

      {isLoadingKidData && <p>Loading kid's data...</p>}

      {selectedKidData && !isLoadingKidData && (
        <div style={{ marginTop: '20px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
          <h3>Details for {selectedKidData.name}</h3>
          
          {renderKidDetails(selectedKidData)}
          {renderExamHistory(selectedKidData.exams)}
          {renderCharts(selectedKidData)}
          
          <div style={{ marginTop: '20px', marginBottom: '20px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
            <button onClick={handleGenerateInsights} disabled={isGeneratingInsights || isLoadingKidData}
              style={{ padding: '10px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '1em' }}>
              {isGeneratingInsights ? 'Generating Insights...' : 'Generate/Refresh AI Insights'}
            </button>
          </div>
          
          {renderAIInsights(selectedKidData.ai_insights)}
        </div>
      )}
    </div>
  );
};

export default ParentViewPage;
