package app

import (
	"context"
	"fmt"
	"clean-code-cookbook/go/services/catalog/internal/domain"
	"clean-code-cookbook/go/services/catalog/internal/ports"
)

// FetchProductQuery is a use case that fetches a product.
// It holds a reference to the ProductFetcher port, but is unaware of the
// concrete implementation (e.g., HTTP client, gRPC client, DB repository).
type FetchProductQuery struct {
	ProductFetcher ports.ProductFetcher
}

// Execute runs the use case.
// It takes the necessary parameters and returns a domain model or an error.
func (q *FetchProductQuery) Execute(ctx context.Context, id string) (*domain.Product, error) {
	product, err := q.ProductFetcher.FetchProductByID(ctx, id)
	if err != nil {
		// In a real application, you might want to add more structured logging here.
		return nil, fmt.Errorf("failed to fetch product with id %s: %w", id, err)
	}

	// Here you could add more business logic, for example:
	// - Checking if the product is in stock.
	// - Applying a discount.
	// - Checking user permissions.

	return product, nil
}