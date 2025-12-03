package tests

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/clean-code-coockbook/catalog/internal/app"
	"github.com/clean-code-coockbook/catalog/internal/domain"
)

type stubClient[T any] struct {
	value T
	delay time.Duration
	err   error
}

func (s stubClient[T]) Get(ctx context.Context, _ string) (T, error) {
	if s.delay > 0 {
		select {
		case <-time.After(s.delay):
		case <-ctx.Done():
			var zero T
			return zero, ctx.Err()
		}
	}
	if s.err != nil {
		var zero T
		return zero, s.err
	}
	return s.value, nil
}

func TestFetchProductHappyPath(t *testing.T) {
	svc := app.Service{
		Inventory: stubClient[domain.Inventory]{value: domain.Inventory{Available: 3}},
		Pricing:   stubClient[domain.Price]{value: domain.Price{Currency: "USD", Amount: 9.99}},
		Reviews:   stubClient[[]string]{value: []string{"ok", "great"}},
		Timeout:   200 * time.Millisecond,
	}

	product, err := svc.FetchProduct(context.Background(), "p1")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if product.ID != "p1" || product.Inventory.Available != 3 || product.Price.Amount != 9.99 {
		t.Fatalf("unexpected product: %+v", product)
	}
	if len(product.Reviews) != 2 {
		t.Fatalf("unexpected reviews: %+v", product.Reviews)
	}
}

func TestFetchProductTimeout(t *testing.T) {
	svc := app.Service{
		Inventory: stubClient[domain.Inventory]{value: domain.Inventory{Available: 3}, delay: 300 * time.Millisecond},
		Pricing:   stubClient[domain.Price]{value: domain.Price{Currency: "USD", Amount: 9.99}},
		Reviews:   stubClient[[]string]{value: []string{"ok"}},
		Timeout:   100 * time.Millisecond,
	}

	_, err := svc.FetchProduct(context.Background(), "p1")
	if !errors.Is(err, app.ErrUpstreamTimeout) {
		t.Fatalf("expected timeout error, got %v", err)
	}
}
