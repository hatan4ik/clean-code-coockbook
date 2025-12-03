*   **Concurrency with Goroutines and Channels:** We will explore Go's powerful and simple concurrency model.
    *   **Philosophy:** "Do not communicate by sharing memory; instead, share memory by communicating."
    *   **Pattern (Worker Pool):** A common and powerful pattern is the worker pool, where a fixed number of goroutines (workers) process tasks from a channel. This is a great way to control concurrency and resource usage.
    *   **Example (Worker Pool):**
        ```go
        func worker(id int, jobs <-chan int, results chan<- int) {
            for j := range jobs {
                fmt.Println("worker", id, "started job", j)
                time.Sleep(time.Second) // Simulate work
                fmt.Println("worker", id, "finished job", j)
                results <- j * 2
            }
        }

        func main() {
            numJobs := 5
            jobs := make(chan int, numJobs)
            results := make(chan int, numJobs)

            for w := 1; w <= 3; w++ {
                go worker(w, jobs, results)
            }

            for j := 1; j <= numJobs; j++ {
                jobs <- j
            }
            close(jobs)

            for a := 1; a <= numJobs; a++ {
                <-results
            }
        }
        ```