package app

import (
	"context"
	"errors"
	"time"

	"github.com/clean-code-coockbook/catalog/internal/domain"
	"github.com/clean-code-coockbook/catalog/internal/ports"
	"golang.org/x/sync/errgroup"
)

var ErrUpstreamTimeout = errors.New("upstream timed out")

type Service struct {
	Inventory ports.InventoryClient
	Pricing   ports.PricingClient
	Reviews   ports.ReviewsClient
	Timeout   time.Duration
}

// FetchProduct fan-outs to three upstreams with a shared deadline and cancels siblings on error.
func (s Service) FetchProduct(ctx context.Context, id string) (domain.Product, error) {
	timeout := s.Timeout
	if timeout == 0 {
		timeout = 200 * time.Millisecond
	}
	ctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	group, ctx := errgroup.WithContext(ctx)
	var inv domain.Inventory
	var price domain.Price
	var reviews []string

	group.Go(func() error {
		var err error
		inv, err = s.Inventory.Get(ctx, id)
		return err
	})
	group.Go(func() error {
		var err error
		price, err = s.Pricing.Get(ctx, id)
		return err
	})
	group.Go(func() error {
		var err error
		reviews, err = s.Reviews.Get(ctx, id)
		return err
	})

	if err := group.Wait(); err != nil {
		if errors.Is(err, context.DeadlineExceeded) || errors.Is(ctx.Err(), context.DeadlineExceeded) {
			return domain.Product{}, ErrUpstreamTimeout
		}
		return domain.Product{}, err
	}

	return domain.Product{
		ID:        id,
		Inventory: inv,
		Price:     price,
		Reviews:   reviews,
	}, nil
}
