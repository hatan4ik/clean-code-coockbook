# Concurrency in Go: Goroutines and Channels

Go's concurrency model is one of its most famous and powerful features. Instead of using threads and locks, Go provides two simple but powerful primitives: goroutines and channels.

## 1. The Core Philosophy: "Share Memory by Communicating"

This is the central idea behind Go's concurrency model. Instead of having multiple threads share the same memory and using locks to synchronize access, Go encourages you to pass data between goroutines using channels. This leads to code that is less prone to race conditions and deadlocks.

### Bad: Communicating by Sharing Memory (using mutexes)

```go
import "sync"

type Counter struct {
    mu    sync.Mutex
    value int
}

func (c *Counter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.value++
}
```

This works, but it's easy to make mistakes. Forgetting to lock or unlock the mutex can lead to race conditions.

### Good: Sharing Memory by Communicating (using channels)

```go
func counter(out chan<- int) {
    count := 0
    for {
        out <- count
        count++
    }
}
```

In this version, the `counter` goroutine owns the `count` variable. No other goroutine can access it directly. To get the current count, a goroutine would read from the `out` channel. This is inherently safe.

## 2. Goroutines and Channels Explained

### Goroutines

A goroutine is a lightweight thread of execution. They are multiplexed onto a small number of OS threads, so you can have hundreds of thousands of them running concurrently. Starting a goroutine is simple: just use the `go` keyword.

```go
go myFunction() // This will run myFunction in a new goroutine
```

### Channels

A channel is a typed conduit through which you can send and receive values with the `<-` operator.

```go
ch := make(chan int) // Create a new channel of type int

ch <- 10      // Send a value into the channel
value := <-ch // Receive a value from the channel
```

By default, sends and receives block until the other side is ready. This allows goroutines to synchronize without explicit locks or condition variables.

## 3. Common Concurrency Patterns

### Worker Pool

A worker pool is a common pattern for controlling the number of concurrent workers.

```go
func worker(id int, jobs <-chan int, results chan<- int, wg *sync.WaitGroup) {
    defer wg.Done()
    for j := range jobs {
        // ... do work ...
        results <- j * 2
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    var wg sync.WaitGroup
    for w := 1; w <= 3; w++ {
        wg.Add(1)
        go worker(w, jobs, results, &wg)
    }

    for j := 1; j <= 5; j++ {
        jobs <- j
    }
    close(jobs)

    wg.Wait() // Wait for all workers to finish
}
```

### Fan-out, Fan-in

This pattern is used to parallelize a set of tasks. A "fan-out" goroutine distributes the tasks to a set of workers, and a "fan-in" goroutine collects the results. The `errgroup` package is a great tool for this.

### Rate Limiting

You can use a ticker to limit the rate of execution.

```go
rate := time.Second / 10 // 10 requests per second
ticker := time.NewTicker(rate)
defer ticker.Stop()

for range ticker.C {
    // do work
}
```

### The `select` Statement

The `select` statement lets a goroutine wait on multiple channel operations.

```go
select {
case msg1 := <-ch1:
    fmt.Println("received", msg1)
case msg2 := <-ch2:
    fmt.Println("received", msg2)
case <-time.After(time.Second):
    fmt.Println("timed out")
}
```

`select` is a powerful tool for implementing timeouts, cancellations, and other complex concurrency patterns.

## 4. `sync.WaitGroup`

A `WaitGroup` waits for a collection of goroutines to finish. The main goroutine calls `Add` to set the number of goroutines to wait for. Then each of the goroutines runs and calls `Done` when finished. At the same time, `Wait` can be used to block until all goroutines have finished.
