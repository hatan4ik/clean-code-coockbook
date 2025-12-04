# Observability: Logging, Metrics, and Tracing

Observability is the ability to understand the internal state of a system from its external outputs. In modern, complex systems, observability is not a luxury; it's a necessity. It's how you debug problems in production, understand system performance, and identify bottlenecks.

The three pillars of observability are:

1. **Logging:** For recording discrete events.
2. **Metrics:** For tracking and aggregating measurements.
3. **Tracing:** For understanding the lifecycle of a request as it flows through your system.

## 1. Logging

Structured, machine-readable logs are essential for effective observability. They allow you to easily search, filter, and analyze your logs.

### Go: `slog`

Go 1.21 introduced a new structured logging package, `slog`.

```go
import (
    "log/slog"
    "os"
)

func main() {
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
    logger.Info("user logged in", "user_id", 123, "ip_address", "127.0.0.1")
}
```

This will produce a JSON log entry like this:

```json
{"time":"2023-10-27T10:00:00.000Z","level":"INFO","msg":"user logged in","user_id":123,"ip_address":"127.0.0.1"}
```

### Python: `structlog`

`structlog` is a popular structured logging library for Python.

```python
import structlog

log = structlog.get_logger()
log.info("user.login", user_id=123, ip_address="127.0.0.1")
```

## 2. Metrics

Metrics are a way of aggregating measurements over time. They are great for monitoring the overall health of your system. The "Four Golden Signals" are a great starting point for what to measure:

- **Latency:** The time it takes to service a request.
- **Traffic:** The amount of demand being placed on your system.
- **Errors:** The rate of requests that are failing.
- **Saturation:** How "full" your system is.

### Prometheus

Prometheus is a popular open-source monitoring system that is a great fit for collecting metrics from Go and Python services.

#### Go with Prometheus

```go
import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "net/http"
)

var (
    httpRequestsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "code"},
    )
)

func main() {
    prometheus.MustRegister(httpRequestsTotal)
    http.Handle("/metrics", promhttp.Handler())
    // ...
}
```

#### Python with Prometheus

```python
from prometheus_client import start_http_server, Counter

c = Counter('my_failures_total', 'Description of counter')
c.inc()

start_http_server(8000)
```

## 3. Tracing

Distributed tracing allows you to follow a single request as it flows through multiple services. This is essential for debugging problems in a microservices architecture.

### OpenTelemetry

OpenTelemetry is an open-source observability framework that provides a single set of APIs and libraries for collecting traces, metrics, and logs.

#### Go with OpenTelemetry

```go
import (
    "context"
    "go.opentelemetry.io/otel"
)

var tracer = otel.Tracer("my-app")

func myHandler(ctx context.Context) {
    ctx, span := tracer.Start(ctx, "myHandler")
    defer span.End()

    // ... do work ...
}
```

#### Python with OpenTelemetry

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("myHandler"):
    # ... do work ...
```

By using these three pillars together, you can gain a deep understanding of your system's behavior and quickly diagnose and fix problems when they arise.
