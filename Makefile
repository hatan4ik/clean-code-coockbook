PY_SRC=python/services/catalog
GO_SRC=go/services/catalog

.PHONY: py.lint py.test py.type go.fmt go.test all

all: py.lint py.type py.test go.fmt go.test

py.lint:
	ruff check $(PY_SRC)
	ruff format --check $(PY_SRC)

py.type:
	mypy --strict $(PY_SRC)

py.test:
	pytest $(PY_SRC)/tests -q

go.fmt:
	cd $(GO_SRC) && go fmt ./...

go.test:
	cd $(GO_SRC) && go test ./...
