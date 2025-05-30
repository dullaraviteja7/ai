package kafka

import (
	"analytics-service/config"
	"analytics-service/handlers" // To call the aggregation logic (or a refactored version)
	"context"
	"encoding/json"
	"log"
	"strings"
	"time"

	"github.com/segmentio/kafka-go"
	// "net/http" // For making a request to our own handler if not refactoring
)

// ExamEvent represents the expected structure from Kafka
type ExamEvent struct {
	EventType               string  `json:"event_type"`
	ExamID                  string  `json:"exam_id"`
	KidID                   string  `json:"kid_id"`
	Subject                 string  `json:"subject"`
	MarksObtainedPercentage float64 `json:"marks_obtained_percentage"`
	ExamDate                string  `json:"exam_date"` // Assuming ISO string date
	Timestamp               string  `json:"timestamp"`
}

var reader *kafka.Reader // Make reader accessible for graceful shutdown

// StartExamEventConsumer starts the Kafka consumer in a goroutine.
func StartExamEventConsumer(cfg *config.AppConfig, appCtx context.Context) {
	log.Println("Initializing Kafka consumer...")
	brokers := strings.Split(cfg.KafkaBootstrapServers, ",")

	reader = kafka.NewReader(kafka.ReaderConfig{
		Brokers:        brokers,
		GroupID:        cfg.KafkaConsumerGroupID,
		Topic:          cfg.KafkaExamTopic,
		MinBytes:       10e3, // 10KB
		MaxBytes:       10e6, // 10MB
		CommitInterval: time.Second, // Commit offsets every second
		MaxWait:        3 * time.Second, // Max time to wait for new messages before returning from ReadMessage
	})

	log.Printf("Kafka consumer configured for topic %s, group %s", cfg.KafkaExamTopic, cfg.KafkaConsumerGroupID)

	go func() {
		defer func() {
			if err := reader.Close(); err != nil {
				log.Printf("Error closing Kafka reader: %v", err)
			} else {
				log.Println("Kafka reader closed.")
			}
		}()

		log.Println("Kafka consumer goroutine started, listening for messages...")
		for {
			// Check if the parent context is done (application shutting down)
			select {
			case <-appCtx.Done():
				log.Println("Application shutdown signal received, stopping Kafka consumer...")
				return
			default:
				// Continue reading messages
			}
			
			m, err := reader.ReadMessage(appCtx) // Use appCtx for cancellable reads
			if err != nil {
				if err == context.Canceled || err == context.DeadlineExceeded {
					log.Printf("Context error in Kafka reader, shutting down: %v", err)
					return // Exit goroutine if context is cancelled or deadline exceeded
				}
				log.Printf("Error reading message from Kafka: %v. Retrying...", err)
				time.Sleep(5 * time.Second) // Wait before retrying on other errors
				continue
			}

			log.Printf("Received message from Kafka: Topic %s, Partition %d, Offset %d, Key: %s",
				m.Topic, m.Partition, m.Offset, string(m.Key))

			var event ExamEvent
			if err := json.Unmarshal(m.Value, &event); err != nil {
				log.Printf("Error unmarshalling Kafka message value: %v. Message: %s", err, string(m.Value))
				// Optionally commit the message even if unmarshalling fails to avoid reprocessing bad messages
				if err := reader.CommitMessages(appCtx, m); err != nil {
                    log.Printf("Error committing message after unmarshal error: %v", err)
                }
				continue
			}

			log.Printf("Successfully unmarshalled exam event: %+v", event)

			// Trigger analytics aggregation
			// For now, this will call the existing HTTP handler's logic (which is mocked).
			// Ideally, the core aggregation logic would be refactored into a service function.
			// This is a simplified way to trigger it without making an actual HTTP call to itself.
			// It assumes the aggregation handler doesn't strictly depend on http.ResponseWriter and *http.Request.
			// If it does, an internal HTTP call or refactoring is needed.
			
			// Simple approach for now: Log and simulate triggering the aggregation.
			// In a real scenario, you'd call the refactored aggregation logic here.
			log.Printf("Kafka consumer received exam event for kid %s, subject %s. Triggering analytics aggregation.", event.KidID, event.Subject)
			
			// --- Refactored approach would be: ---
			// err = services.AggregateAnalyticsForKid(appCtx, cfg, event.KidID) // or for all data if event is just a trigger
			// if err != nil {
			//     log.Printf("Error during event-triggered aggregation for kid %s: %v", event.KidID, err)
			// } else {
			//     log.Printf("Successfully completed event-triggered aggregation for kid %s.", event.KidID)
			// }
			// For this subtask, we'll use the existing handler's logic path by calling it (or its core part).
			// Since handlers.TriggerAnalyticsAggregationHandler expects (w,r), we can't directly call it.
			// The simplest way for this subtask is to log that it *would* trigger it.
			// A more direct approach for this subtask, if the handler logic is simple enough and doesn't rely heavily on w,r:
			// handlers.PerformAggregation(cfg) // Assuming PerformAggregation is the refactored logic
			
			// For this subtask, we'll just print a message indicating the trigger.
			// The actual aggregation is mocked within TriggerAnalyticsAggregationHandler.
			// If we wanted to call the HTTP endpoint internally:
			// _, httpErr := http.Post(fmt.Sprintf("http://localhost:%s/api/analytics/aggregate", cfg.ServerPort), "application/json", nil)
			// if httpErr != nil {
			//     log.Printf("Error triggering aggregation via internal HTTP call: %v", httpErr)
			// } else {
			//     log.Println("Successfully triggered aggregation via internal HTTP call.")
			// }
			// For now, just log. The next step will be to properly refactor.
			log.Println("INFO: (Mock) Aggregation triggered by Kafka event.")


			// Commit the message
			if err := reader.CommitMessages(appCtx, m); err != nil {
				log.Printf("Error committing message: %v", err)
			}
		}
	}()
}

// StopExamEventConsumer can be called on application shutdown.
func StopExamEventConsumer() {
	if reader != nil {
		log.Println("Attempting to close Kafka reader...")
		if err := reader.Close(); err != nil {
			log.Printf("Error closing Kafka reader: %v", err)
		} else {
			log.Println("Kafka reader closed successfully.")
		}
	}
}
```
