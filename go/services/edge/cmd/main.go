package main

import (
	"context"
	"log"
	"time"

	adapter "clean-code-cookbook/go/services/edge/internal/adapter/grpc"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func main() {
	// 1. Establish connection to the Python "Brains" service
	// Using insecure for demo; production should use mTLS
	conn, err := grpc.Dial("localhost:50051", grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()

	client := adapter.NewUserClient(conn)
	ctx := context.Background()

	// 2. Demonstrate RegisterUser
	log.Println("--- 1. Registering User ---")
	regResp, err := client.RegisterUser(ctx, "alice@example.com", "alice_wonder")
	if err != nil {
		log.Printf("Error registering: %v", err)
	} else {
		log.Printf("Success! User ID: %s, Status: %s", regResp.Id, regResp.Status)
	}

	// 3. Demonstrate GetUser
	log.Println("\n--- 2. Fetching User ---")
	getResp, err := client.GetUser(ctx, "alice@example.com")
	if err != nil {
		log.Printf("Error fetching user: %v", err)
	} else {
		log.Printf("Found User: %s (Active: %v)", getResp.User.Username, getResp.User.IsActive)
	}

	// 4. Demonstrate Streaming
	log.Println("\n--- 3. Streaming Events ---")
	// Run in a goroutine or blocking? Blocking for demo.
	go func() {
		if err := client.StreamEvents(ctx); err != nil {
			log.Printf("Streaming ended: %v", err)
		}
	}()

	// Keep main alive for a bit to receive events
	time.Sleep(3 * time.Second)
	log.Println("Done.")
}
