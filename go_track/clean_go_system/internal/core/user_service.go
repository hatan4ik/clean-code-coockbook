package core

import (
	"context"
	"fmt"
	"time"

	"clean_go_system/internal/domain"
	"github.com/google/uuid"
)

// UserService contains the business logic
type UserService struct {
	repo domain.UserRepository
}

// NewUserService is a constructor (Factory)
func NewUserService(repo domain.UserRepository) *UserService {
	return &UserService{repo: repo}
}

// Register handles the user creation flow
func (s *UserService) Register(ctx context.Context, email, username string) (*domain.User, error) {
	// 1. Check existence
	existing, err := s.repo.GetByEmail(ctx, email)
	if err != nil && err != domain.ErrUserNotFound {
		return nil, fmt.Errorf("failed to check user: %w", err)
	}
	if existing != nil {
		return nil, fmt.Errorf("user already exists")
	}

	// 2. Create Entity
	newUser := domain.User{
		ID:        uuid.New(),
		Email:     email,
		Username:  username,
		CreatedAt: time.Now(),
	}

	// 3. Persist
	if err := s.repo.Save(ctx, newUser); err != nil {
		return nil, fmt.Errorf("failed to save user: %w", err)
	}

	return &newUser, nil
}