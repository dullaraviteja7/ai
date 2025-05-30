package handlers

import (
	"encoding/json"
	"net/http"
)

// HealthCheckResponse is the structure for the health check endpoint
type HealthCheckResponse struct {
	Status string `json:"status"`
}

// HealthHandler handles requests to the health check endpoint
func HealthHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	response := HealthCheckResponse{Status: "Analytics Service is running"}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(response); err != nil {
		// This error is tricky to handle if headers are already written,
		// but good to log if possible.
		http.Error(w, "Failed to write response", http.StatusInternalServerError)
	}
}
```
