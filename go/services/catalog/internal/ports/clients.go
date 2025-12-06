package ports

import (
	"context"
	"clean-code-cookbook/go/services/catalog/internal/domain"
)

// ProductFetcher is a port that defines the contract for fetching product data
// from an external source, such as another microservice or a database.
type ProductFetcher interface {
	// FetchProductByID fetches a single product by its ID.
	// It uses a context for cancellation and deadlines.
	FetchProductByID(ctx context.Context, id string) (*domain.Product, error)
}