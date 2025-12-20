PY_SRC=python/services/catalog
GO_SRC=go/services/catalog

.PHONY: py.lint py.test py.type go.fmt go.test all proto

all: py.lint py.type py.test go.fmt go.test

proto: ## Generate Go and Python code from proto files
	mkdir -p proto/gen/go
	protoc -I proto \
		--go_out=proto/gen/go --go_opt=paths=source_relative \
		--go-grpc_out=proto/gen/go --go-grpc_opt=paths=source_relative \
		proto/user_bridge.proto
	python -m grpc_tools.protoc -I proto \
		--python_out=clean_python/src \
		--grpc_python_out=clean_python/src \
		proto/user_bridge.proto


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
