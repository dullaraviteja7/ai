package db

import (
	"context"
	"log"
	"sync"
	"time"

	"analytics-service/config" // Import the local config package
	"analytics-service/models" // Import for SubjectAverage model

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/readpref"
)

var (
	clientInstance *mongo.Client
	dbInstance     *mongo.Database
	clientOnce     sync.Once
	connectErr     error // Stores connection error
)

// ConnectDB establishes a connection to MongoDB and sets up clientInstance and dbInstance.
// This should be called once at application startup.
func Connect(cfg *config.AppConfig) error {
	clientOnce.Do(func() {
		log.Println("Attempting to connect to MongoDB...")

		clientOptions := options.Client().ApplyURI(cfg.MongoURI)
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		client, err := mongo.Connect(ctx, clientOptions)
		if err != nil {
			connectErr = err
			log.Printf("Error connecting to MongoDB: %v", err)
			return
		}

		if err := client.Ping(ctx, readpref.Primary()); err != nil {
			connectErr = err
			log.Printf("Error pinging MongoDB: %v", err)
			// Attempt to clean up client if ping fails
			if discErr := client.Disconnect(ctx); discErr != nil {
				log.Printf("Error disconnecting client after ping failure: %v", discErr)
			}
			return
		}

		clientInstance = client
		dbInstance = client.Database(cfg.MongoDbNameAnalytics)
		log.Printf("Successfully connected to MongoDB database: %s", cfg.MongoDbNameAnalytics)
	})
	return connectErr
}

// GetDB returns the database instance. Panics if not connected.
func GetDB() *mongo.Database {
	if dbInstance == nil {
		log.Panic("MongoDB not connected. Ensure Connect() was called successfully at startup.")
	}
	return dbInstance
}

// GetClient returns the MongoDB client instance. Panics if not connected.
func GetClient() *mongo.Client {
	if clientInstance == nil {
		log.Panic("MongoDB not connected. Ensure Connect() was called successfully at startup.")
	}
	return clientInstance
}

// CloseDB closes the MongoDB connection.
func Close(ctx context.Context) {
	if clientInstance != nil {
		log.Println("Closing MongoDB connection...")
		if err := clientInstance.Disconnect(ctx); err != nil {
			log.Printf("Error closing MongoDB connection: %v", err)
		} else {
			log.Println("MongoDB connection closed successfully.")
			clientInstance = nil
			dbInstance = nil
			connectErr = nil
			clientOnce = sync.Once{} // Reset for potential re-connection (e.g. in tests)
		}
	}
}

// --- CRUD functions for SubjectAverages ---

// GetSubjectAveragesCollection helper
func GetSubjectAveragesCollection() *mongo.Collection {
	return GetDB().Collection("subject_averages")
}

// SaveSubjectAverages stores a list of subject averages.
// It performs an upsert operation for each subject based on SubjectName.
func SaveSubjectAverages(averages []models.SubjectAverage) error {
	collection := GetSubjectAveragesCollection()
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second) // Increased timeout for multiple operations
	defer cancel()

	var errorOccurred bool
	for _, avg := range averages {
		avg.LastUpdated = time.Now().UTC() // Ensure LastUpdated is current UTC time
		if avg.ID.IsZero() { // Ensure new documents get a new MongoDB _id
		    avg.ID = primitive.NewObjectID()
        }

		filter := bson.M{"subject_name": avg.SubjectName}
		// If aggregating per kid in the future, KidID should be part of the filter:
		// filter := bson.M{"subject_name": avg.SubjectName, "kid_id": avg.KidID}
		
		update := bson.M{"$set": avg}
		opts := options.Update().SetUpsert(true)
		
		_, err := collection.UpdateOne(ctx, filter, update, opts)
		if err != nil {
			log.Printf("Error upserting subject average for %s: %v", avg.SubjectName, err)
			// Continue processing others, but flag that an error occurred
			errorOccurred = true 
		}
	}

	if errorOccurred {
		return fmt.Errorf("one or more errors occurred while saving subject averages")
	}
	log.Printf("Successfully saved/updated %d subject average records.", len(averages))
	return nil
}

// GetSubjectAverages retrieves all stored subject averages.
func GetSubjectAverages() ([]models.SubjectAverage, error) {
	collection := GetSubjectAveragesCollection()
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	cursor, err := collection.Find(ctx, bson.M{})
	if err != nil {
		log.Printf("Error finding subject averages: %v", err)
		return nil, err
	}
	defer cursor.Close(ctx)

	var results []models.SubjectAverage
	if err = cursor.All(ctx, &results); err != nil {
		log.Printf("Error decoding subject averages: %v", err)
		return nil, err
	}
	return results, nil
}
```
