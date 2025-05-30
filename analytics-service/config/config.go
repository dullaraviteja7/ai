package config

import (
	"log"
	"os"
	"sync"

	"github.com/joho/godotenv"
)

// AppConfig holds the application configuration
type AppConfig struct {
	MongoURI                string
	MongoDbNameAnalytics    string
	ServerPort              string
	ExamServiceURL          string
	KafkaBootstrapServers string
	KafkaExamTopic          string
	KafkaConsumerGroupID    string
	// Add other service URLs as needed
}

var (
	instance *AppConfig
	once     sync.Once
)

// LoadConfig loads environment variables from .env file (if it exists)
// and then from actual environment variables.
func LoadConfig() *AppConfig {
	once.Do(func() {
		// Attempt to load .env file, but don't fail if it's not present
		// as environment variables might be set directly (e.g., in Docker/Kubernetes)
		err := godotenv.Load()
		if err != nil {
			log.Println("No .env file found or error loading .env, relying on environment variables.")
		}

		instance = &AppConfig{
			MongoURI:                getEnv("MONGO_URI", "mongodb://localhost:27017"),
			MongoDbNameAnalytics:    getEnv("MONGO_DB_NAME_ANALYTICS", "analytics_service_db"),
			ServerPort:              getEnv("SERVER_PORT", "5003"),
			ExamServiceURL:          getEnv("EXAM_SERVICE_URL", "http://localhost:5001/api/exams"),
			KafkaBootstrapServers: getEnv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
			KafkaExamTopic:          getEnv("KAFKA_EXAM_TOPIC", "exam_events"),
			KafkaConsumerGroupID:    getEnv("KAFKA_CONSUMER_GROUP_ID", "analytics_service_group"),
		}
		log.Println("Configuration loaded successfully.")
	})
	return instance
}

// getEnv retrieves an environment variable or returns a default value
func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}
```
