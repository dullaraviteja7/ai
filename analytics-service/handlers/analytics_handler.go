package handlers

import (
	"analytics-service/config"
	"analytics-service/db"
	"analytics-service/models"
	"encoding/json"
	"log"
	"net/http"
	"time"
	"fmt"
	// "github.com/gorilla/mux" // Or your chosen router
)

// TriggerAnalyticsAggregationHandler handles requests to trigger analytics aggregation.
func TriggerAnalyticsAggregationHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	cfg := config.LoadConfig() // Load config to get ExamServiceURL

	// 1. Fetch Exam Data (Mocked)
	log.Println("Fetching exam data from Exam Service (mocked)...")
	// examServiceURL := cfg.ExamServiceURL + "/internal/all" // Assumed endpoint
	// In a real scenario:
	// resp, err := http.Get(examServiceURL)
	// if err != nil {
	// 	log.Printf("Error fetching exam data: %v", err)
	// 	http.Error(w, "Failed to fetch exam data", http.StatusInternalServerError)
	// 	return
	// }
	// defer resp.Body.Close()
	// if resp.StatusCode != http.StatusOK {
	// 	log.Printf("Exam Service returned non-OK status: %d", resp.StatusCode)
	// 	http.Error(w, "Failed to fetch exam data from Exam Service", resp.StatusCode)
	// 	return
	// }
	// var allExams []models.ExamData
	// if err := json.NewDecoder(resp.Body).Decode(&allExams); err != nil {
	// 	log.Printf("Error decoding exam data: %v", err)
	// 	http.Error(w, "Failed to decode exam data", http.StatusInternalServerError)
	// 	return
	// }

	// Mocked exam data
	allExams := []models.ExamData{
		{ExamID: "exam1", KidID: "kid1", ExamName: "Midterm Math", ExamDateStr: "2023-10-15", Subject: "Mathematics", MarksObtainedPercentage: 85.0},
		{ExamID: "exam2", KidID: "kid1", ExamName: "Final Science", ExamDateStr: "2023-12-05", Subject: "Science", MarksObtainedPercentage: 92.5},
		{ExamID: "exam3", KidID: "kid2", ExamName: "Midterm Math", ExamDateStr: "2023-10-15", Subject: "Mathematics", MarksObtainedPercentage: 78.0},
		{ExamID: "exam4", KidID: "kid1", ExamName: "Unit Test Math", ExamDateStr: "2023-11-01", Subject: "Mathematics", MarksObtainedPercentage: 90.0},
		{ExamID: "exam5", KidID: "kid2", ExamName: "Midterm Science", ExamDateStr: "2023-10-20", Subject: "Science", MarksObtainedPercentage: 88.0},
		{ExamID: "exam6", KidID: "kid3", ExamName: "Midterm History", ExamDateStr: "2023-10-25", Subject: "History", MarksObtainedPercentage: 75.0},
	}
	log.Printf("Successfully fetched/mocked %d exam records.", len(allExams))

	// 2. Perform Aggregation
	subjectAggregates := make(map[string]struct {
		TotalMarks float64
		ExamCount  int
	})

	for _, exam := _, err := exam.ToInternal(); err == nil { // Convert to internal model to use parsed date if needed
		// For subject average, we might not need the parsed date from ExamDataInternal yet,
		// but it's good practice if future analytics depend on it.
		// Using exam.Subject and exam.MarksObtainedPercentage directly from models.ExamData for now.
		
		agg := subjectAggregates[exam.Subject]
		agg.TotalMarks += exam.MarksObtainedPercentage
		agg.ExamCount++
		subjectAggregates[exam.Subject] = agg
	} else {
		log.Printf("Warning: Could not parse exam date for exam_id %s: %v. Skipping this record for date-dependent analytics if any.", exam.ExamID, err)
		// For current aggregation, we can still use marks and subject if date parsing fails
		agg := subjectAggregates[exam.Subject]
		agg.TotalMarks += exam.MarksObtainedPercentage
		agg.ExamCount++
		subjectAggregates[exam.Subject] = agg
	}


	var subjectAverages []models.SubjectAverage
	for subjectName, data := range subjectAggregates {
		if data.ExamCount > 0 {
			avg := models.SubjectAverage{
				SubjectName:  subjectName,
				AverageMarks: data.TotalMarks / float64(data.ExamCount),
				TotalExams:   data.ExamCount,
				LastUpdated:  time.Now().UTC(), // Will be set again in SaveSubjectAverages
			}
			subjectAverages = append(subjectAverages, avg)
		}
	}

	// 3. Store Aggregated Data
	if err := db.SaveSubjectAverages(cfg, subjectAverages); err != nil {
		log.Printf("Error saving subject averages: %v", err)
		http.Error(w, "Failed to save analytics data", http.StatusInternalServerError)
		return
	}

	responseMessage := fmt.Sprintf("Successfully aggregated and saved analytics for %d subjects.", len(subjectAverages))
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"message": responseMessage, "subjects_processed": fmt.Sprintf("%d", len(subjectAverages))})
}

// GetAggregatedAnalyticsHandler handles requests to retrieve aggregated subject averages.
func GetAggregatedAnalyticsHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}
	cfg := config.LoadConfig() // Needed for GetSubjectAverages if it internally needs config

	averages, err := db.GetSubjectAverages(cfg)
	if err != nil {
		log.Printf("Error retrieving subject averages: %v", err)
		http.Error(w, "Failed to retrieve analytics data", http.StatusInternalServerError)
		return
	}

	if averages == nil { // db.GetSubjectAverages might return nil slice if collection is empty
		averages = []models.SubjectAverage{}
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(averages); err != nil {
		log.Printf("Error encoding analytics data: %v", err)
		http.Error(w, "Failed to write response", http.StatusInternalServerError)
	}
}
```
