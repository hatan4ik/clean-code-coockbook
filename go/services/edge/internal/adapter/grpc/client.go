package grpc

import (
	"context"
	"fmt"
	"io"
	"log"
	"time"

	// In a real scenario, this import path must match the generated code location.
	// We are assuming the proto definition's go_package option is respected.
	pb "github.com/clean-code-coockbook/proto/gen/go/users/v1"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type UserClient struct {
	client pb.UserServiceClient
}

func NewUserClient(conn *grpc.ClientConn) *UserClient {
	return &UserClient{
		client: pb.NewUserServiceClient(conn),
	}
}

func (c *UserClient) RegisterUser(ctx context.Context, email, username string) (*pb.RegisterUserResponse, error) {
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	req := &pb.RegisterUserRequest{
		Email:    email,
		Username: username,
	}

	return c.client.RegisterUser(ctx, req)
}

func (c *UserClient) GetUser(ctx context.Context, email string) (*pb.GetUserResponse, error) {
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	return c.client.GetUser(ctx, &pb.GetUserRequest{Email: email})
}

func (c *UserClient) StreamEvents(ctx context.Context) error {
	stream, err := c.client.StreamUserEvents(ctx, &pb.UserEventsRequest{})
	if err != nil {
		return fmt.Errorf("failed to start stream: %w", err)
	}

	log.Println("Started listening for user events...")
	for {
		event, err := stream.Recv()
		if err == io.EOF {
			break
		}
		if err != nil {
			return fmt.Errorf("stream error: %w", err)
		}
		log.Printf("Received Event: Type=%s, User=%s, Time=%s", 
			event.Type, event.Payload.Username, event.OccurredAt)
	}
	return nil
}
