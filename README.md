# Module 1: The Async Mental Model
## "Stop Waiting, Start Reacting"

### 1. The Problem: The Cost of Blocking
In traditional Python (WSGI/Flask/Django Sync), the concurrency model is **"One Thread per Request."**

* **Scenario:** A user requests a report. The server queries the DB (taking 2 seconds).
* **The Reality:** The operating system thread sits **idle** for those 2 seconds, blocked, doing absolutely nothing but holding onto memory.
* **The Cost:**
    * **Memory Overhead:** Each thread requires a stack (approx. 4MB-8MB). 1,000 threads = ~4GB RAM.
    * **Context Switching:** The CPU wastes cycles saving/loading thread states instead of executing code.

$$\text{Throughput} \approx \frac{\text{Total Threads}}{\text{Avg Latency}}$$

If you are limited by RAM to 500 threads, and your latency is 1 second, your max throughput is a measly 500 RPS (Requests Per Second), regardless of how fast your CPU is.

### 2. The Solution: The Event Loop (Cooperative Multitasking)
AsyncIO swaps the **Thread-per-Request** model for a **Task-per-Request** model using a single thread.

* **The Concept:** Imagine a chess master playing 50 opponents simultaneously. He doesn't wait for Opponent A to move before looking at Opponent B. He makes a move, walks to the next board, makes a move, and cycles through.
* **The Mechanism:** When your code hits `await database_query()`, it yields control back to the **Event Loop**. The Loop immediately finds another task that is ready to run.
* **The Win:** 10,000 concurrent connections can live on **one thread** with minimal RAM overhead.

### 3. Real-World Example: The "Sleep" Test

#### A. The Blocking Way (Don't do this)
This script will take 5 seconds to complete because it runs sequentially.

```python
import time

def brew_coffee():
    print("☕ Starting coffee...")
    time.sleep(1)  # BLOCKS the entire thread!
    print("☕ Coffee ready!")

def toast_bread():
    print("🍞 Starting toast...")
    time.sleep(1)
    print("🍞 Toast ready!")

def main():
    start = time.time()
    # These happen one after another
    brew_coffee()
    toast_bread()
    brew_coffee()
    toast_bread()
    brew_coffee()
    print(f"Total time: {time.time() - start:.2f}s")

if __name__ == "__main__":
    main()