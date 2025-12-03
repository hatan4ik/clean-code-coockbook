package ports

import (
	"context"

	"github.com/clean-code-coockbook/catalog/internal/domain"
)

type InventoryClient interface {
	Get(ctx context.Context, productID string) (domain.Inventory, error)
}

type PricingClient interface {
	Get(ctx context.Context, productID string) (domain.Price, error)
}

type ReviewsClient interface {
	Get(ctx context.Context, productID string) ([]string, error)
}
