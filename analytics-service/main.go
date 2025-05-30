package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"analytics-service/config"
	"analytics-service/db"
	"analytics-service/handlers"
	"analytics-service/kafka" // Import the new kafka package
	// "github.com/gorilla/mux" // Example if using mux
)

func main() {
	// Load configuration
	cfg := config.LoadConfig()

	// Initialize MongoDB connection
	if err := db.Connect(cfg); err != nil { // Connect now returns only error
		log.Fatalf("Failed to connect to MongoDB: %v", err)
	}
	// db.GetDB() can now be used by handlers or other parts of the app safely.


	// Create a cancellable context for the application
	appCtx, appCancel := context.WithCancel(context.Background())
	defer appCancel() // Ensure cancellation on exit

	// Start Kafka Consumer in a goroutine
	go kafka.StartExamEventConsumer(cfg, appCtx)


	// Setup router (using net/http default ServeMux for now)
	// router := mux.NewRouter() // Example if using mux
	http.HandleFunc("/api/analytics/health", handlers.HealthHandler)
	http.HandleFunc("/api/analytics/aggregate", handlers.TriggerAnalyticsAggregationHandler)
	http.HandleFunc("/api/analytics/subject-averages", handlers.GetAggregatedAnalyticsHandler)
	// TODO: Add specific kid analytics endpoints later if needed


	// Start server
	serverAddr := ":" + cfg.ServerPort
	log.Printf("Analytics Service starting on port %s", cfg.ServerPort)

	srv := &http.Server{
		Addr:    serverAddr,
		// Good practice to set timeouts to avoid Slowloris attacks.
		WriteTimeout: time.Second * 15,
		ReadTimeout:  time.Second * 15,
		IdleTimeout:  time.Second * 60,
		Handler:      nil, // Pass router here if using mux or chi, nil uses http.DefaultServeMux
	}

	// Run server in a goroutine so that it doesn't block.
	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("ListenAndServe(): %v", err)
		}
	}()
	log.Printf("Server started on %s", serverAddr)

	// Graceful shutdown
	quit := make(chan os.Signal, 1)
	// signal.Notify for Ctrl+C or kill signals
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit // Block until a signal is received.
	log.Println("Shutting down server...")

	// Create a deadline to wait for.
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// Doesn't block if no connections, but will otherwise wait
	// until the timeout deadline.
	// Use a new context for server shutdown, not the appCtx which might be cancelled earlier
	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 10*time.Second) // Increased for shutdown
	defer shutdownCancel()

	if err := srv.Shutdown(shutdownCtx); err != nil {
		log.Fatalf("Server Shutdown Failed:%+v", err)
	}
	
	// Signal Kafka consumer to stop by cancelling its context (appCancel was deferred)
	log.Println("Signalling Kafka consumer to stop...")
	appCancel() // This will cause appCtx.Done() in consumer

	// Close MongoDB connection
	db.Close(shutdownCtx) // Use shutdownCtx for DB closure as well

	log.Println("Server exited gracefully")
}
```
