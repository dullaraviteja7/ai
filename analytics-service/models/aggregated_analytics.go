package models

import (
	"time"
	"go.mongodb.org/mongo-driver/bson/primitive" // For MongoDB's _id
)

// SubjectAverage stores the aggregated average marks for a specific subject.
// This will be stored in a MongoDB collection, e.g., "subject_analytics".
type SubjectAverage struct {
	ID           primitive.ObjectID `json:"id,omitempty" bson:"_id,omitempty"`       // MongoDB's primary key
	SubjectName  string             `json:"subject_name" bson:"subject_name"`        // e.g., "Mathematics", "Science"
	AverageMarks float64            `json:"average_marks" bson:"average_marks"`      // Calculated average percentage
	TotalExams   int                `json:"total_exams" bson:"total_exams"`          // Count of exams included in this average
	LastUpdated  time.Time          `json:"last_updated" bson:"last_updated"`        // When this average was last calculated
	// KidID        string             `json:"kid_id,omitempty" bson:"kid_id,omitempty"` // Uncomment if aggregating per kid
}


// AggregatedAnalytics could be a more comprehensive structure if needed later,
// for example, combining multiple types of analytics.
// For now, the focus is on SubjectAverage.
type AggregatedAnalytics struct {
	ID                   primitive.ObjectID `json:"id,omitempty" bson:"_id,omitempty"`
	AnalyticsID          string             `json:"analytics_id" bson:"analytics_id"`  // Application-specific unique ID for a report/aggregation run
	KidID                *string            `json:"kid_id,omitempty" bson:"kid_id,omitempty"` // Optional: if analytics are specific to a kid
	GeneratedDate        time.Time          `json:"generated_date" bson:"generated_date"`
	OverallPerformance   *string            `json:"overall_performance,omitempty" bson:"overall_performance,omitempty"`
	SubjectWiseAnalytics *map[string]SubjectAnalyticsDetails `json:"subject_wise_analytics,omitempty" bson:"subject_wise_analytics,omitempty"` // More detailed than SubjectAverage
	TrendAnalysis        *string            `json:"trend_analysis,omitempty" bson:"trend_analysis,omitempty"` 
	Recommendations      []string           `json:"recommendations,omitempty" bson:"recommendations,omitempty"`
}

// SubjectAnalyticsDetails provides more detailed analytics for a subject.
type SubjectAnalyticsDetails struct {
	AverageMarks      float64 `json:"average_marks" bson:"average_marks"`
	Trend             string  `json:"trend" bson:"trend"` 
	RecentExamCount   int     `json:"recent_exam_count" bson:"recent_exam_count"`
	HighestMark       float64 `json:"highest_mark" bson:"highest_mark"`
	LowestMark        float64 `json:"lowest_mark" bson:"lowest_mark"`
}
```
