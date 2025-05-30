package models

import "time"

// ExamData represents the structure of exam data fetched from the Exam Service.
// This structure is used for deserializing the JSON response from Exam Service.
type ExamData struct {
	// Assuming Exam Service returns _id as string, exam_id as the application's unique ID
	// For analytics, we primarily care about kid_id, subject, marks, and date.
	ID                      string    `json:"_id,omitempty"` // MongoDB's _id from Exam service, if provided
	ExamID                  string    `json:"exam_id"`
	KidID                   string    `json:"kid_id"`
	ExamName                string    `json:"exam_name"`
	ExamDateStr             string    `json:"exam_date"` // Expecting "YYYY-MM-DD" string from Exam Service
	Subject                 string    `json:"subject"`
	MarksObtainedPercentage float64   `json:"marks_obtained_percentage"`
	ClassTopPercentage      *float64  `json:"class_top_percentage,omitempty"` // Optional
	// Add CreatedAt/UpdatedAt if Exam Service provides them and they are useful
}

// ExamDataInternal can be used if we need to parse ExamDateStr into time.Time
// for internal processing within Analytics service.
type ExamDataInternal struct {
	ExamID                  string
	KidID                   string
	ExamName                string
	ExamDate                time.Time 
	Subject                 string
	MarksObtainedPercentage float64
	ClassTopPercentage      *float64
}

// Helper function to convert ExamData to ExamDataInternal
func (ed *ExamData) ToInternal() (ExamDataInternal, error) {
	parsedDate, err := time.Parse("2006-01-02", ed.ExamDateStr)
	if err != nil {
		// Attempt to parse with timezone info if present (e.g. from MongoDB via User/Exam service)
		parsedDate, err = time.Parse(time.RFC3339Nano, ed.ExamDateStr)
		if err != nil {
			return ExamDataInternal{}, err
		}
	}
	return ExamDataInternal{
		ExamID:                  ed.ExamID,
		KidID:                   ed.KidID,
		ExamName:                ed.ExamName,
		ExamDate:                parsedDate,
		Subject:                 ed.Subject,
		MarksObtainedPercentage: ed.MarksObtainedPercentage,
		ClassTopPercentage:      ed.ClassTopPercentage,
	}, nil
}
```
