package domain

type Inventory struct {
	Available int
}

type Price struct {
	Currency string
	Amount   float64
}

type Product struct {
	ID        string
	Inventory Inventory
	Price     Price
	Reviews   []string
}
